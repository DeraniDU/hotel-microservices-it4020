import os

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv(".env_staff")

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
MONGODB_DB = os.getenv("MONGODB_DB", "hotel")

client = AsyncIOMotorClient(MONGODB_URI)
db = client[MONGODB_DB]

staff_collection = db["staff"]

