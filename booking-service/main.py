from datetime import datetime, timezone
import secrets
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from bson import ObjectId
from bson.errors import InvalidId

from database import booking_collection
from models import BookingCreate, BookingUpdate

app = FastAPI(
    title="Booking Service",
    description="Manages hotel bookings - part of Hotel Microservices",
    version="1.0.0",
)


def booking_serializer(booking) -> dict:
    return {
        "id": str(booking["_id"]),
        "booking_id": booking["booking_id"],
        "guest_id": booking["guest_id"],
        "room_id": booking["room_id"],
        "check_in": booking["check_in"],
        "check_out": booking["check_out"],
        "adults_count": booking["adults_count"],
        "children_count": booking["children_count"],
        "guests_count": booking["guests_count"],
        "rate_plan_id": booking.get("rate_plan_id"),
        "price_per_night": booking["price_per_night"],
        "total_amount": booking["total_amount"],
        "currency": booking["currency"],
        "payment_status": booking["payment_status"],
        "booking_source": booking["booking_source"],
        "status": booking["status"],
        "special_requests": booking.get("special_requests"),
        "notes": booking.get("notes"),
        "created_at": booking["created_at"],
        "updated_at": booking["updated_at"],
    }


def parse_object_id(id_value: str) -> ObjectId:
    try:
        return ObjectId(id_value)
    except InvalidId as exc:
        raise HTTPException(status_code=400, detail="Invalid booking id format") from exc


def generate_booking_id() -> str:
    date_part = datetime.now(timezone.utc).strftime("%Y%m%d")
    random_part = secrets.token_hex(3).upper()
    return f"BKG-{date_part}-{random_part}"


async def ensure_unique_booking_id() -> str:
    for _ in range(5):
        booking_id = generate_booking_id()
        exists = await booking_collection.find_one({"booking_id": booking_id})
        if not exists:
            return booking_id
    raise HTTPException(status_code=500, detail="Could not generate unique booking id")


async def has_room_conflict(
    room_id: str,
    check_in: datetime,
    check_out: datetime,
    exclude_id: Optional[ObjectId] = None,
) -> bool:
    query = {
        "room_id": room_id,
        "status": {"$ne": "cancelled"},
        "check_in": {"$lt": check_out},
        "check_out": {"$gt": check_in},
    }
    if exclude_id:
        query["_id"] = {"$ne": exclude_id}
    existing = await booking_collection.find_one(query)
    return existing is not None


@app.on_event("startup")
async def startup_tasks():
    await booking_collection.create_index("booking_id", unique=True)


@app.get("/health", tags=["Health"])
def health():
    return {"status": "online", "service": "booking-service"}


@app.post("/bookings", status_code=201, tags=["Bookings"])
async def create_booking(booking: BookingCreate):
    payload = booking.model_dump(mode="python")
    if await has_room_conflict(payload["room_id"], booking.check_in, booking.check_out):
        raise HTTPException(
            status_code=409,
            detail="Room is already booked for the selected date/time range",
        )

    now = datetime.now(timezone.utc)
    payload["booking_id"] = await ensure_unique_booking_id()
    payload["created_at"] = now
    payload["updated_at"] = now
    result = await booking_collection.insert_one(payload)
    new_booking = await booking_collection.find_one({"_id": result.inserted_id})
    return booking_serializer(new_booking)


@app.get("/bookings", tags=["Bookings"])
async def get_all_bookings(
    guest_id: Optional[str] = Query(default=None),
    room_id: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None),
):
    query = {}
    if guest_id:
        query["guest_id"] = guest_id
    if room_id:
        query["room_id"] = room_id
    if status:
        query["status"] = status

    bookings = []
    async for booking in booking_collection.find(query).sort("created_at", -1):
        bookings.append(booking_serializer(booking))
    return bookings


@app.get("/bookings/{booking_id}", tags=["Bookings"])
async def get_booking(booking_id: str):
    booking = None
    try:
        object_id = ObjectId(booking_id)
        booking = await booking_collection.find_one({"_id": object_id})
    except InvalidId:
        booking = await booking_collection.find_one({"booking_id": booking_id})

    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking_serializer(booking)


@app.get("/bookings/code/{booking_code}", tags=["Bookings"])
async def get_booking_by_booking_code(booking_code: str):
    booking = await booking_collection.find_one({"booking_id": booking_code})
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking_serializer(booking)


@app.put("/bookings/{booking_id}", tags=["Bookings"])
async def update_booking(booking_id: str, data: BookingUpdate):
    update_data = {k: v for k, v in data.model_dump(mode="python").items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    query = {}
    object_id = None
    try:
        object_id = ObjectId(booking_id)
        query = {"_id": object_id}
    except InvalidId:
        query = {"booking_id": booking_id}

    existing = await booking_collection.find_one(query)
    if not existing:
        raise HTTPException(status_code=404, detail="Booking not found")

    # Validate date range when only one date is provided in updates.
    check_in = update_data.get("check_in", existing["check_in"])
    check_out = update_data.get("check_out", existing["check_out"])
    if check_out <= check_in:
        raise HTTPException(
            status_code=400,
            detail="check_out must be later than check_in (same date is allowed with valid times)",
        )

    guests_count = update_data.get("guests_count", existing["guests_count"])
    adults_count = update_data.get("adults_count", existing["adults_count"])
    children_count = update_data.get("children_count", existing["children_count"])
    if adults_count + children_count != guests_count:
        raise HTTPException(
            status_code=400,
            detail="guests_count must equal adults_count + children_count",
        )

    room_id = update_data.get("room_id", existing["room_id"])
    conflict_exclude_id = existing["_id"]
    if await has_room_conflict(room_id, check_in, check_out, exclude_id=conflict_exclude_id):
        raise HTTPException(
            status_code=409,
            detail="Room is already booked for the selected date/time range",
        )

    update_data["updated_at"] = datetime.now(timezone.utc)
    await booking_collection.update_one(query, {"$set": update_data})
    updated = await booking_collection.find_one({"_id": existing["_id"]})
    return booking_serializer(updated)


@app.delete("/bookings/{booking_id}", tags=["Bookings"])
async def delete_booking(booking_id: str):
    query = {}
    try:
        query = {"_id": ObjectId(booking_id)}
    except InvalidId:
        query = {"booking_id": booking_id}

    result = await booking_collection.delete_one(query)
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Booking not found")
    return {"message": f"Booking {booking_id} deleted successfully"}
