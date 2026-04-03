from datetime import datetime, timezone
import secrets
from typing import Optional

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import RedirectResponse

from database import payment_collection
from models import PaymentCreate, PaymentUpdate

app = FastAPI(
    title="Payment Service",
    description="Manages hotel payments - part of Hotel Microservices",
    version="1.0.0",
    docs_url="/payment"
)

@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/payment")

def payment_serializer(payment) -> dict:
    return {
        "id": str(payment["_id"]),
        "payment_ref": payment["payment_ref"],
        "booking_id": payment["booking_id"],
        "guest_id": payment["guest_id"],
        "amount": payment["amount"],
        "currency": payment["currency"],
        "method": payment["method"],
        "status": payment["status"],
        "paid_at": payment.get("paid_at"),
        "transaction_id": payment.get("transaction_id"),
        "notes": payment.get("notes"),
        "created_at": payment["created_at"],
        "updated_at": payment["updated_at"],
    }


def generate_payment_ref() -> str:
    date_part = datetime.now(timezone.utc).strftime("%Y%m%d")
    random_part = secrets.token_hex(3).upper()
    return f"PAY-{date_part}-{random_part}"


async def ensure_unique_payment_ref() -> str:
    for _ in range(5):
        payment_ref = generate_payment_ref()
        exists = await payment_collection.find_one({"payment_ref": payment_ref})
        if not exists:
            return payment_ref
    raise HTTPException(status_code=500, detail="Could not generate unique payment reference")


@app.on_event("startup")
async def startup_tasks():
    await payment_collection.create_index("payment_ref", unique=True)


@app.get("/health", tags=["Health"])
def health():
    return {"status": "online", "service": "payment-service"}


@app.post("/payments", status_code=201, tags=["Payments"])
async def create_payment(payment: PaymentCreate):
    payload = payment.model_dump(mode="python")
    now = datetime.now(timezone.utc)
    payload["payment_ref"] = await ensure_unique_payment_ref()
    payload["created_at"] = now
    payload["updated_at"] = now

    if payload["status"] == "paid" and payload.get("paid_at") is None:
        payload["paid_at"] = now

    result = await payment_collection.insert_one(payload)
    new_payment = await payment_collection.find_one({"_id": result.inserted_id})
    return payment_serializer(new_payment)


@app.get("/payments", tags=["Payments"])
async def get_all_payments(
    booking_id: Optional[str] = Query(default=None),
    guest_id: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None),
    method: Optional[str] = Query(default=None),
):
    query = {}
    if booking_id:
        query["booking_id"] = booking_id
    if guest_id:
        query["guest_id"] = guest_id
    if status:
        query["status"] = status
    if method:
        query["method"] = method

    payments = []
    async for payment in payment_collection.find(query).sort("created_at", -1):
        payments.append(payment_serializer(payment))
    return payments


@app.get("/payments/{payment_id}", tags=["Payments"])
async def get_payment(payment_id: str):
    payment = None
    try:
        object_id = ObjectId(payment_id)
        payment = await payment_collection.find_one({"_id": object_id})
    except InvalidId:
        payment = await payment_collection.find_one({"payment_ref": payment_id})

    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment_serializer(payment)


@app.get("/payments/ref/{payment_ref}", tags=["Payments"])
async def get_payment_by_ref(payment_ref: str):
    payment = await payment_collection.find_one({"payment_ref": payment_ref})
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment_serializer(payment)


@app.put("/payments/{payment_id}", tags=["Payments"])
async def update_payment(payment_id: str, data: PaymentUpdate):
    update_data = {k: v for k, v in data.model_dump(mode="python").items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    query = {}
    try:
        query = {"_id": ObjectId(payment_id)}
    except InvalidId:
        query = {"payment_ref": payment_id}

    existing = await payment_collection.find_one(query)
    if not existing:
        raise HTTPException(status_code=404, detail="Payment not found")

    if update_data.get("status") == "paid" and update_data.get("paid_at") is None:
        update_data["paid_at"] = datetime.now(timezone.utc)

    update_data["updated_at"] = datetime.now(timezone.utc)
    await payment_collection.update_one(query, {"$set": update_data})
    updated = await payment_collection.find_one({"_id": existing["_id"]})
    return payment_serializer(updated)


@app.delete("/payments/{payment_id}", tags=["Payments"])
async def delete_payment(payment_id: str):
    query = {}
    try:
        query = {"_id": ObjectId(payment_id)}
    except InvalidId:
        query = {"payment_ref": payment_id}

    result = await payment_collection.delete_one(query)
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Payment not found")
    return {"message": f"Payment {payment_id} deleted successfully"}
