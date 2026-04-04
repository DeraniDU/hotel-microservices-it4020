import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import HTTPException
from motor.motor_asyncio import AsyncIOMotorClient

_env_dir = Path(__file__).resolve().parent
load_dotenv(_env_dir / ".env")
load_dotenv(_env_dir / ".env_guest", override=True)

MONGO_URL = os.getenv("MONGO_URL")
DATABASE_NAME = os.getenv("DATABASE_NAME")

if not MONGO_URL:
    raise RuntimeError(
        "MONGO_URL is not set. Add it to guest-service/.env or .env_guest "
        "(and DATABASE_NAME if required)."
    )

client = AsyncIOMotorClient(MONGO_URL, serverSelectionTimeoutMS=5000)
db = client[DATABASE_NAME]
guest_collection = db["guests"]


async def db_op(coro):
    """Wrap any DB coroutine and convert DB errors to clean JSON 503 responses."""
    try:
        return await coro
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Database error: {type(e).__name__} — {str(e)[:200]}"
        )