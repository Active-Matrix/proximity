from torch import no_grad
import asyncio
import signal
from pydantic import BaseModel
import logging
import json

from rec_1 import recommendationModel
from rabbitmq_client import RabbitMQAsyncClient
from mq import VectorStoreQueue

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# To validate the JSON
class JSONData(BaseModel):
    NewsTitle: str
    NewsTLDR: str
    Liked: str

class RecommendationService:
    def __init__(self):

        # Hyperparameters
        self.batch = 1
        self.timesteps = 5
        self.head_dim = 64
        self.num_heads = 12
        self.hidden_dim = 128
        self.num_layers = 2
        self.embedding_dim = 768  # Dimension of BERT embeddings

        # Model
        self.model = None

        # RabbitMQ
        self.stop_event = asyncio.Event()
        self.client = None

        self.MAX_RETRIES = 3
        self.RETRY_DELAY = 5  # seconds
        self.BACKOFF_FACTOR = 2  # exponential backoff factor

        # Set up signal handlers for graceful shutdown
        for sig in (signal.SIGINT, signal.SIGTERM):
            signal.signal(sig, self._handle_shutdown_signal)

    def load_model(self):
        """Load the recommendation model"""
        if self.model:
            logging.info("Model already loaded.")
            return
        try:
            self.model = recommendationModel(batch=self.batch,
                                            timesteps=self.timesteps,
                                            head_dim=self.head_dim,
                                            num_heads=self.num_heads,
                                            hidden_dim=self.hidden_dim,
                                            num_layers=self.num_layers,
                                            output_dim=self.embedding_dim)
            
            logging.info("Recommendation model loaded successfully.")
        except Exception as e:
            logging.error(f"Error loading model: {e}")
            raise RuntimeError("Failed to load recommendation model")
    
    # TODO: Improve prompt
    def apply_prompt(self, d):

        template = "Head line: {NewsTitle}\nSummary: {NewsTLDR}\nLiked: {Liked}"
        apply = lambda data: template.format(
            NewsTitle=data.NewsTitle,
            NewsTLDR=data.NewsTLDR,
            Liked=data.Liked
        )

        if not isinstance(d, list):
            raise ValueError("Input data must be a list")
        
        if not all(isinstance(item, JSONData) for item in d):
            for item in d:
                if isinstance(item, dict):
                    try:
                        d[d.index(item)] = JSONData(**item)
                    except Exception as e:
                        logging.error(f"Error converting dict to JSONData: {e}")
                        raise ValueError("Invalid dict format for JSONData conversion")
                else:
                    raise ValueError("List contains invalid data type")
            return [apply(data) for data in d]
        
        else:
            logging.info("All items in the list are valid JSONData instances.")
            return [apply(data) for data in d]

    def _handle_shutdown_signal(self, sig):
        """Handle signals for graceful shutdown"""

        logging.info(f"Received signal {sig}. Initiating graceful shutdown...")
        self.stop_event.set()

    async def recommend(self, data: list[JSONData]):
        try:
            with no_grad():
                if self.model:

                    # Generate embeddings
                    embed = self.model(self.apply_prompt(data))
                    
                else:
                    logger.error("Attempt to recommend without loading model")
                    raise RuntimeError("Model is not loaded. Please load the model before making recommendations.")


            # NOTE: number of news recommending, k = timeseries
            payload = json.dumps({
                "embedding": embed.squeeze(0).tolist(),  # Convert tensor to list for JSON serialization
                "top_k": self.timesteps
            })

            await self._publish_message(payload, VectorStoreQueue)

        except Exception as e:
            logger.error(f"Error in recommendation process: {e}")

    async def _publish_message(self, message, queue_name):
        try:
            await self.client.publish_message(
                exchange="", routing_key=queue_name, message=message
            )
            logging.info(f"Published to {queue_name}")
        except Exception as e:
            logging.error(f"Error publishing response: {str(e)}")


    async def _connect_with_backoff(self, host):
        """Connect to RabbitMQ with exponential backoff"""
        max_retries = 5
        retry_count = 0

        while retry_count < max_retries:
            try:
                logging.info(f"Attempting to connect to RabbitMQ at {host}...")
                self.client = RabbitMQAsyncClient(host)
                await self.client.create_connection()

                # Ensure channel is open and ready before returning
                # Wait for the channel to be ready (could be async in the RabbitMQAsyncClient)
                retry_channel = 0
                while retry_channel < self.MAX_RETRIES:
                    if (
                        hasattr(self.client, "channel")
                        and self.client.channel
                        and self.client.channel.is_open
                        ):


                        logging.info(
                            "Connected to RabbitMQ successfully with open channel"
                                    )
                        
                        return True
                    
                    logging.info("Waiting for channel to open...")
                    await asyncio.sleep(1)  # Wait for channel to be ready
                    retry_channel += 1

                if not (
                    hasattr(self.client, "channel")
                    and self.client.channel
                    and self.client.channel.is_open
                        ):
                    

                    logging.error("Channel not open after connection")
                    # Close and retry
                    await self.client.close()
                    raise Exception("Channel failed to open")

                return True
            
            except Exception as e:
                retry_count += 1
                backoff_time = min(
                    self.BACKOFF_FACTOR**retry_count, self.RETRY_DELAY
                )  # Exponential backoff capped at 5 seconds
                logging.error(
                    f"Connection error (attempt {retry_count}/{max_retries}): {str(e)}. "
                    f"Retrying in {backoff_time} seconds..."
                            )

                if retry_count < max_retries:
                    await asyncio.sleep(backoff_time)
                else:
                    logging.critical("Max retry attempts reached. Giving up.")
                    return False

    async def start_service(self, host, queue_name):
        # Connect with exponential backoff instead of hardcoded wait
        connection_success = await self._connect_with_backoff(host)
        if not connection_success:
            logging.error("Failed to connect to RabbitMQ. Exiting.")
            return

        # Ensure we have an open channel before setting up consumer
        if not (
            hasattr(self.client, "channel")
            and self.client.channel
            and self.client.channel.is_open
        ):
            logging.error("Cannot set up consumer - channel not open")
            return

        # Set up consumer
        try:
            await self.client.setup_consumer(queue_name, self._generate_and_publish)
            logging.info(f"Consumer set up for queue: {queue_name}")

            # Verify consumer was set up correctly
            # This might need to be adjusted based on your RabbitMQAsyncClient implementation
            if not hasattr(self.client, "consumer_tag"):
                logging.warning(
                    "Consumer might not be properly registered - no consumer tag found"
                )

            # Run until stop event is set
            while not self.stop_event.is_set():
                await asyncio.sleep(1)  # Check for stop event periodically

            logging.info("Stop event detected, shutting down...")
        except Exception as e:
            logging.error(f"Error setting up consumer: {str(e)}")
        finally:
            if self.client:
                await self.client.close()
                logging.info("RabbitMQ connection closed")

    async def shutdown(self):
        """Gracefully shutdown the service"""
        logging.info("Shutting down service...")
        self.stop_event.set()


async def main():

    # data = ""

    # # Initialize the recommendation service
    # recommendation_service = RecommendationService()
    # recommendation_service.load_model()

    # result = await recommendation_service.recommend(data)
    pass


if __name__ == "__main__": 
    asyncio.run(main())