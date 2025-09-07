import motor.motor_asyncio
import os

# Get MongoDB connection string from environment variable
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")

# Async MongoDB client
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)

# Database name
db = client["saathi_db"]
