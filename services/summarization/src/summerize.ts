import amqp from 'amqplib';
import mq from '@proximity/rabbitmq-config';
import zod from 'zod';
import { logger } from './libs/logger';
import Groq from 'groq-sdk';
import { LLM } from './libs/llm';
import { systemPrompt } from './libs/system-prompt';
import { generatedNewsSchema, scrapedNewsSchema, summerizedNewsSchema } from './schema/summerizer';

export class SummerizerService {
  private connection: amqp.ChannelModel | null = null;
  private channel: amqp.Channel | null = null;
  private groq = new Groq({ apiKey: process.env.GROQ_API_KEY });

  private readonly MAX_RETRIES = 3;
  private readonly RETRY_DELAY = 1000;
  private readonly RATE_LIMIT = 200;
  private processingQueue: Array<amqp.Message> = [];
  private isProcessing = false;

  constructor() {
    logger.info('Initializing ScraperService...');
    this.setupShutdownHandlers();
  }

  private setupShutdownHandlers(): void {
    logger.info('Setting up shutdown handlers...');
    process.on('SIGTERM', async () => await this.shutdown());
    process.on('SIGINT', async () => await this.shutdown());
  }

  private async createConnection(): Promise<amqp.Channel> {
    if (!this.connection || !this.channel) {
      this.connection = await amqp.connect(mq.url);
      this.channel = await this.connection.createChannel();

      this.connection.on('error', async (error) => {
        logger.error('RabbitMQ connection error:', error);
        this.connection = null;
        this.channel = null;
        await new Promise(resolve => setTimeout(resolve, 5000));
        await this.createConnection();
      });

      await this.channel.assertQueue(mq.queues.ScrapedNewsQueue);
      await this.channel.assertQueue(mq.queues.SummarizedNewsQueue);

      await this.channel.prefetch(1);
   }
    return this.channel;
  }

  private async processNextMessage(): Promise<void> {
    if (this.isProcessing) {
      return;
    }

    const message = this.processingQueue.shift();
    if (!message) {
      return;
    }

    this.isProcessing = true;

    try {
      // Process body here
      const summerizedNews = await this.processMessage(message);
      logger.debug(summerizedNews)

      await this.channel.sendToQueue(
        mq.queues.SummarizedNewsQueue,
        Buffer.from(JSON.stringify(summerizedNews))
      );


      // Acknowledge the message after successful processing
      if (this.channel) {
        this.channel.ack(message);
      }

      logger.info(`Processed message. Remaining in queue: ${this.processingQueue.length}`);
    } catch (error) {
      logger.error('Error processing message:', error);

      // Reject and requeue the message on error
      if (this.channel) {
        this.channel.nack(message, false, true);
      }
    }

    // Wait for RATE_LIMIT milliseconds before marking as not processing
    await new Promise(resolve => setTimeout(resolve, this.RATE_LIMIT));

    this.isProcessing = false;

    // Process next message if queue is not empty
    if (this.processingQueue.length > 0) {
      setImmediate(() => this.processNextMessage());
    }
  }

  private async processMessage(message: amqp.Message): Promise<zod.infer<typeof summerizedNewsSchema>> {
    try {
      const body: zod.infer<typeof scrapedNewsSchema> = JSON.parse(message.content.toString());
      const validatedBody = scrapedNewsSchema.safeParse(body);

      if (!validatedBody.success) {
        throw new Error(JSON.stringify({
          error: 'Validation Error for scrapedNewsSchema',
          message: validatedBody.error.message
        }));
      }

      const context = `Title: ${body.title}, Content: ${body.content}`

      const summery: zod.infer<typeof generatedNewsSchema> = await LLM(this.groq, systemPrompt, context)
      const validatedSummery = generatedNewsSchema.safeParse(summery);

      if (!validatedSummery.success) {
        throw new Error(JSON.stringify({
          error: 'Validation Error for generatedNewsSchema',
          message: validatedSummery.error.message
        }));
      }

      const summerizedNews: zod.infer<typeof summerizedNewsSchema> = {
        title: summery.title,
        content: summery.content,
        tags: summery.tags,
        imageUrl: body.imageUrl,
        date: body.date,
        scrapedAt: body.scrapedAt,
        sourceName: body.sourceName,
        sourceUrl: body.sourceUrl,
      }

      return summerizedNews
    }
    catch (error) {
      logger.error(error)
    }
  }

  public async summerize() {
    try {
      const channel = await this.createConnection();
      logger.info("Connection established to MQ");

      channel.consume(mq.queues.ScrapedNewsQueue, async (message) => {
        if (!message) return;

        // Add to processing queue
        this.processingQueue.push(message);

        // Trigger processing if not already processing
        if (!this.isProcessing) {
          this.processNextMessage();
        }
      }, { noAck: false }); // Set noAck to false to manually acknowledge messages

    } catch (error) {
      logger.error('Error during summerize:', error);
    }
  }

  public async shutdown(): Promise<void> {
    try {
      logger.info('Shutting down... Processing remaining messages in queue');

      // Wait for the queue to be processed
      // while (this.processingQueue.length > 0 || this.isProcessing) {
      //   await new Promise(resolve => setTimeout(resolve, 100));
      // }

      if (this.channel) {
        await this.channel.close();
      }
      if (this.connection) {
        await this.connection.close();
      }
      logger.info('Gracefully shut down scraper service');
      process.exit(0);
    } catch (error) {
      logger.error('Error during shutdown:', error);
      process.exit(1);
    }
  }
}
