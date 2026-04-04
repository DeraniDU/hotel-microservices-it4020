import os
from pathlib import Path

import certifi
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

_env_dir = Path(__file__).resolve().parent
load_dotenv(_env_dir / ".env")
load_dotenv(_env_dir / ".env_payment", override=True)

MONGO_URL = os.getenv("MONGO_URL")
DATABASE_NAME = os.getenv("DATABASE_NAME", "hotel_db")

if not MONGO_URL:
    raise RuntimeError(
        "MONGO_URL is not set. Add MONGO_URL (and optional DATABASE_NAME) to "
        "payment-service/.env or .env_payment."
    )

# Atlas TLS fix: use certifi CA bundle for SSL verification.
client = AsyncIOMotorClient(MONGO_URL, tlsCAFile=certifi.where())
db = client[DATABASE_NAME]

payment_collection = db["payments"]
