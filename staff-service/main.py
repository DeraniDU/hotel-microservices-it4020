from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from bson import ObjectId

from database import staff_collection
from models import StaffCreate, StaffUpdate

app = FastAPI(
    title="Staff Service",
    description="Manages hotel staff — part of Hotel Microservices",
    version="1.0.0",
)

@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")

def parse_object_id(value: str) -> ObjectId:
    """Convert MongoDB ObjectId safely to avoid 500s on invalid IDs."""
    try:
        return ObjectId(value)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid staff_id")


def staff_serializer(staff) -> dict:
    return {
        "id": str(staff["_id"]),
        "name": staff["name"],
        "role": staff["role"],
        "department": staff["department"],
        "email": staff["email"],
        "phone": staff["phone"],
        "salary": staff["salary"],
        "currency": staff.get("currency"),
        "employment_status": staff["employment_status"],
    }


@app.get("/health", tags=["Health"])
def health():
    return {"status": "online", "service": "staff-service"}


@app.get("/staff/health", tags=["Health"])
def health_prefixed():
    return {"status": "online", "service": "staff-service"}


@app.post("/staff", status_code=201, tags=["Staff"])
async def create_staff(staff: StaffCreate):
    result = await staff_collection.insert_one(staff.dict())
    new_staff = await staff_collection.find_one({"_id": result.inserted_id})
    return staff_serializer(new_staff)


@app.get("/staff", tags=["Staff"])
async def get_all_staff():
    staff_list = []
    async for s in staff_collection.find():
        staff_list.append(staff_serializer(s))
    return staff_list


@app.get("/staff/{staff_id}", tags=["Staff"])
async def get_staff(staff_id: str):
    staff = await staff_collection.find_one({"_id": parse_object_id(staff_id)})
    if not staff:
        raise HTTPException(status_code=404, detail="Staff not found")
    return staff_serializer(staff)


@app.put("/staff/{staff_id}", tags=["Staff"])
async def update_staff(staff_id: str, data: StaffUpdate):
    # Remove None fields — only update what's provided.
    update_data = {k: v for k, v in data.dict().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    result = await staff_collection.update_one(
        {"_id": parse_object_id(staff_id)},
        {"$set": update_data},
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Staff not found")

    updated = await staff_collection.find_one({"_id": parse_object_id(staff_id)})
    return staff_serializer(updated)


@app.delete("/staff/{staff_id}", tags=["Staff"])
async def delete_staff(staff_id: str):
    result = await staff_collection.delete_one({"_id": parse_object_id(staff_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Staff not found")
    return {"message": f"Staff {staff_id} deleted successfully"}

