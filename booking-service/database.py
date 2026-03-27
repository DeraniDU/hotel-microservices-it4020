from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")
DATABASE_NAME = os.getenv("DATABASE_NAME", "hotel_db")

if not MONGO_URL:
    raise RuntimeError(
        "MONGO_URL is not set. Create booking-service/.env with MONGO_URL and DATABASE_NAME."
    )

client = AsyncIOMotorClient(MONGO_URL)
db = client[DATABASE_NAME]

booking_collection = db["bookings"]
