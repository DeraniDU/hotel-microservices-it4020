from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field, model_validator

PaymentMethod = Literal["card", "cash", "bank-transfer", "mobile-wallet"]
PaymentStatus = Literal["pending", "paid", "failed", "refunded"]


class PaymentBase(BaseModel):
    booking_id: str = Field(..., min_length=3, description="Related booking identifier")
    guest_id: str = Field(..., min_length=3, description="Related guest identifier")
    amount: float = Field(..., gt=0, description="Payment amount")
    currency: str = Field(default="LKR", min_length=3, max_length=3)
    method: PaymentMethod
    status: PaymentStatus = "pending"
    paid_at: Optional[datetime] = None
    transaction_id: Optional[str] = Field(
        default=None, description="External payment provider transaction id"
    )
    notes: Optional[str] = None

    @model_validator(mode="after")
    def normalize_fields(self):
        self.currency = self.currency.upper()
        return self


class PaymentCreate(PaymentBase):
    pass


class PaymentUpdate(BaseModel):
    booking_id: Optional[str] = None
    guest_id: Optional[str] = None
    amount: Optional[float] = Field(default=None, gt=0)
    currency: Optional[str] = Field(default=None, min_length=3, max_length=3)
    method: Optional[PaymentMethod] = None
    status: Optional[PaymentStatus] = None
    paid_at: Optional[datetime] = None
    transaction_id: Optional[str] = None
    notes: Optional[str] = None

    @model_validator(mode="after")
    def normalize_fields(self):
        if self.currency:
            self.currency = self.currency.upper()
        return self
