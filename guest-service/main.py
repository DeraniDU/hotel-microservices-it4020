from fastapi import FastAPI, HTTPException
from bson import ObjectId
from database import guest_collection
from models import GuestCreate, GuestUpdate

app = FastAPI(
    title="Guest Service",
    description="Manages hotel guests — part of Hotel Microservices",
    version="1.0.0"
)

# Helper to convert MongoDB _id to string
def guest_serializer(guest) -> dict:
    return {
        "id": str(guest["_id"]),
        "name": guest["name"],
        "email": guest["email"],
        "phone": guest["phone"],
        "nationality": guest["nationality"],
        "address": guest["address"],
        "check_in": guest["check_in"],
        "check_out": guest["check_out"],
    }

# ── HEALTH ────────────────────────────────────────────────
@app.get("/health", tags=["Health"])
def health():
    return {"status": "online", "service": "guest-service"}

# ── CREATE ────────────────────────────────────────────────
@app.post("/guests", status_code=201, tags=["Guests"])
async def create_guest(guest: GuestCreate):
    try:
        result = await guest_collection.insert_one(guest.dict())
        new_guest = await guest_collection.find_one({"_id": result.inserted_id})
        return guest_serializer(new_guest)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database connection error: {type(e).__name__} - {str(e)}")

# ── READ ALL ──────────────────────────────────────────────
@app.get("/guests", tags=["Guests"])
async def get_all_guests():
    guests = []
    try:
        async for guest in guest_collection.find():
            guests.append(guest_serializer(guest))
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database connection error: {type(e).__name__} - {str(e)}")
    return guests

# ── READ ONE ──────────────────────────────────────────────
@app.get("/guests/{guest_id}", tags=["Guests"])
async def get_guest(guest_id: str):
    try:
        guest = await guest_collection.find_one({"_id": ObjectId(guest_id)})
        if not guest:
            raise HTTPException(status_code=404, detail="Guest not found")
        return guest_serializer(guest)
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=503, detail=f"Database connection error: {type(e).__name__} - {str(e)}")

# ── UPDATE ────────────────────────────────────────────────
@app.put("/guests/{guest_id}", tags=["Guests"])
async def update_guest(guest_id: str, data: GuestUpdate):
    # Remove None fields — only update what's provided
    update_data = {k: v for k, v in data.dict().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    result = await guest_collection.update_one(
        {"_id": ObjectId(guest_id)},
        {"$set": update_data}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Guest not found")
    
    updated = await guest_collection.find_one({"_id": ObjectId(guest_id)})
    return guest_serializer(updated)

# ── DELETE ────────────────────────────────────────────────
@app.delete("/guests/{guest_id}", tags=["Guests"])
async def delete_guest(guest_id: str):
    result = await guest_collection.delete_one({"_id": ObjectId(guest_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Guest not found")
    return {"message": f"Guest {guest_id} deleted successfully"}