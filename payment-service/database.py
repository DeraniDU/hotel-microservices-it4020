import os

import certifi
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")
DATABASE_NAME = os.getenv("DATABASE_NAME", "hotel_db")

if not MONGO_URL:
    raise RuntimeError(
        "MONGO_URL is not set. Create payment-service/.env with MONGO_URL and DATABASE_NAME."
    )

# Atlas TLS fix: use certifi CA bundle for SSL verification.
client = AsyncIOMotorClient(MONGO_URL, tlsCAFile=certifi.where())
db = client[DATABASE_NAME]

payment_collection = db["payments"]
