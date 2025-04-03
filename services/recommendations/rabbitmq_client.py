import pika
import logging
import asyncio
from pika.adapters.asyncio_connection import AsyncioConnection

# Configure logging
logging.basicConfig(level=logging.INFO)


class RabbitMQAsyncClient:
    def __init__(self, host: str, max_concurrent_tasks: int = 1):
        self.host = host
        self.connection = None
        self.channel = None
        self._closing = False
        self.rate_limiter = asyncio.Semaphore(max_concurrent_tasks)
        self.connection_ready = asyncio.Event()
        self.channel_ready = asyncio.Event()
        self.declared_queues = set()

    async def create_connection(self):
        """Create a new connection to RabbitMQ."""
        if self.connection is None:
            self.connection_ready.clear()
            self.channel_ready.clear()
            parameters = pika.ConnectionParameters(host=self.host)
            self.connection = AsyncioConnection(
                parameters=parameters,
                on_open_callback=self.on_connection_open,
                on_open_error_callback=self.on_connection_open_error,
                on_close_callback=self.on_connection_closed,
            )
            logging.info(f"Attempting to connect to RabbitMQ at {self.host}...")

    async def ensure_connection(self):
        """Ensure connection and channel are ready before publishing."""
        if self.connection is None:
            await self.create_connection()
            # Wait for connection and channel to be established
            try:
                await asyncio.wait_for(self.connection_ready.wait(), timeout=10.0)
                await asyncio.wait_for(self.channel_ready.wait(), timeout=5.0)
            except asyncio.TimeoutError:
                logging.error("Timed out waiting for connection/channel to be ready")
                return False
        return self.connection is not None and self.channel is not None

    def on_connection_open(self, connection):
        """Callback when the connection is opened."""
        logging.info("Connection opened successfully.")
        self.connection = connection
        self.connection_ready.set()
        self.open_channel()

    def on_connection_open_error(self, _, error):
        """Callback when the connection fails to open."""
        logging.error(f"Connection error: {error}. Retrying...")
        self.connection = None
        self.connection_ready.clear()
        self.channel_ready.clear()
        asyncio.create_task(self.reconnect())  # Attempt to reconnect

    def on_connection_closed(self, _, reason):
        """Callback when the connection is closed."""
        logging.error(f"Connection closed: {reason}. Attempting to reconnect...")
        self.connection = None
        self.channel = None
        self.connection_ready.clear()
        self.channel_ready.clear()
        self.declared_queues.clear()  # Reset declared queues on disconnection
        if not self._closing:
            asyncio.create_task(self.reconnect())  # Attempt to reconnect

    def open_channel(self):
        """Open a new channel."""
        if self.connection and self.channel is None:
            self.channel_ready.clear()
            self.connection.channel(on_open_callback=self.on_channel_open)

    def on_channel_open(self, channel):
        """Callback when the channel is opened."""
        logging.info("Channel opened successfully.")
        self.channel = channel
        self.channel.add_on_close_callback(self.on_channel_closed)
        self.channel_ready.set()

    def on_channel_closed(self, _, reason):
        """Callback when the channel is closed."""
        logging.error(f"Channel closed: {reason}. Reopening channel...")
        self.channel = None
        self.channel_ready.clear()
        self.declared_queues.clear()  # Reset declared queues when channel closes
        if not self._closing and self.connection is not None:
            self.open_channel()  # Attempt to reopen the channel

    async def setup_queue(self, queue_name, durable=True):
        """Set up a queue once during initialization."""
        if not await self.ensure_connection():
            logging.error("Failed to ensure connection for queue setup")
            return False

        if queue_name in self.declared_queues:
            return True

        try:
            self.channel.queue_declare(queue=queue_name, durable=durable)
            self.declared_queues.add(queue_name)
            logging.info(f"Queue {queue_name} declared successfully")
            return True
        except Exception as e:
            logging.error(f"Failed to set up queue {queue_name}: {e}")
            return False

    async def publish_message(self, exchange, routing_key, message, properties=None):
        """Publish a message to RabbitMQ with connection verification."""
        if not await self.ensure_connection():
            logging.error("Failed to establish connection for publishing")
            return False

        # Ensure the queue exists
        if not await self.setup_queue(routing_key):
            logging.error(f"Failed to setup queue {routing_key} for publishing")
            return False

        try:
            self.channel.basic_publish(
                exchange=exchange,
                routing_key=routing_key,
                body=str(message),
                properties=properties
                or pika.BasicProperties(delivery_mode=2),  # persistent delivery mode
            )
            logging.info(
                f"Message published to {exchange} with routing_key {routing_key}"
            )
            return True
        except Exception as e:
            logging.error(f"Failed to publish message: {e}")
            # Mark channel as potentially problematic
            self.channel = None
            self.channel_ready.clear()
            # This will trigger channel reconnection on next publish
            return False

    async def process_message(self, channel, method, _, body, callback):
        """Process a message with rate limiting."""
        async with self.rate_limiter:  # Re-enable rate limiting
            logging.info(f"Processing message: {str(body)[:25]}...")
            try:
                # Call the provided callback with the message
                await callback(
                    body, channel, method
                )  # acknowledgement is handled by the callback
            except Exception as e:
                logging.error(f"Error processing message: {e}")
                # Retry logic or message rejection can be added here
                # Optionally requeue the message
                channel.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    async def setup_consumer(self, queue, callback):
        """Set up a consumer to listen to messages from a queue with rate limiting."""
        if not await self.ensure_connection():
            logging.error("Cannot set up consumer - failed to ensure connection")
            return False

        try:
            # Ensure the queue exists
            if not await self.setup_queue(queue):
                logging.error(f"Failed to setup queue {queue} for consuming")
                return False

            self.channel.basic_qos(prefetch_count=1)  # Process one message at a time
            self.channel.basic_consume(
                queue=queue,
                on_message_callback=lambda ch, method, props, body: asyncio.create_task(
                    self.process_message(ch, method, props, body, callback)
                ),
                auto_ack=False,  # Manual acknowledgment after processing
            )
            logging.info(f"Consuming messages from {queue}")
            return True
        except Exception as e:
            logging.error(f"Failed to set up consumer: {e}")
            return False

    def close(self):
        """Close the connection and channel."""
        if self.connection and not self._closing:
            logging.info("Closing connection...")
            self._closing = True
            self.connection.close()

    async def reconnect(self):
        """Attempt to reconnect to RabbitMQ after a failure."""
        logging.info(f"Attempting reconnection to {self.host}...")
        await asyncio.sleep(5)  # Wait before retrying
        await self.create_connection()
