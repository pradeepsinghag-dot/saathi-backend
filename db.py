# db.py
import os
import motor.motor_asyncio

# Get MongoDB URL from environment variable
MONGO_URL = os.getenv("MONGO_URL")

if not MONGO_URL:
    raise ValueError("❌ MONGO_URL environment variable not set!")

# Create client
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)

# If DB name is included in MONGO_URL (like /saathi_db), this works:
db = client.get_default_database()

# Optional: if you want to explicitly name DB (in case it's missing from URL)
# db = client["saathi_db"]
