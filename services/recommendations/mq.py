from dotenv import load_dotenv
import os

load_dotenv()

host = os.getenv("RABBITMQ_HOST")
rabbitmq_user = os.getenv("RABBITMQ_DEFAULT_USER")
rabbitmq_pass = os.getenv("RABBITMQ_DEFAULT_PASS")

VectorStoreQueue = "vector-store-queue"
