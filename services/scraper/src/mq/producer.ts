import { Channel, connect } from 'amqplib'
import config from '@proximity/rabbitmq-config'

interface IMessage<TData> {
  label: string
  data: TData
}

export const producer = async <TData>(queue: string, message: IMessage<TData>): Promise<void> => {
  const connection = await connect(config.url)
  const channel: Channel = await connection.createChannel()
  await channel.assertQueue(queue)
  await channel.bindQueue(queue, queue)
  await channel.sendToQueue(queue, Buffer.from(JSON.stringify(message)))


}
