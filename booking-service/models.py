from datetime import datetime
from typing import Optional, Literal

from pydantic import BaseModel, Field, model_validator


BookingStatus = Literal["pending", "confirmed", "cancelled", "completed"]
PaymentStatus = Literal["unpaid", "partial", "paid", "refunded"]
BookingSource = Literal["online", "walk-in", "phone", "agent"]


class BookingBase(BaseModel):
    guest_id: str = Field(..., min_length=3, description="Guest identifier")
    room_id: str = Field(..., min_length=2, description="Room identifier")
    check_in: datetime = Field(..., description="Check-in datetime in ISO format")
    check_out: datetime = Field(..., description="Check-out datetime in ISO format")
    adults_count: int = Field(default=1, ge=1, description="Number of adults")
    children_count: int = Field(default=0, ge=0, description="Number of children")
    guests_count: int = Field(..., ge=1, description="Total number of guests")
    rate_plan_id: Optional[str] = Field(default=None, description="Rate plan identifier")
    price_per_night: float = Field(..., ge=0, description="Price per night snapshot")
    total_amount: float = Field(..., ge=0, description="Total booking amount")
    currency: str = Field(default="LKR", min_length=3, max_length=3, description="ISO currency code")
    payment_status: PaymentStatus = "unpaid"
    booking_source: BookingSource = "online"
    status: BookingStatus = "pending"
    special_requests: Optional[str] = None
    notes: Optional[str] = None

    @model_validator(mode="after")
    def validate_dates(self):
        if self.check_out <= self.check_in:
            raise ValueError("check_out must be later than check_in (same date is allowed with valid times)")
        if self.adults_count + self.children_count != self.guests_count:
            raise ValueError("guests_count must equal adults_count + children_count")
        self.currency = self.currency.upper()
        return self


class BookingCreate(BookingBase):
    pass


class BookingUpdate(BaseModel):
    guest_id: Optional[str] = None
    room_id: Optional[str] = None
    check_in: Optional[datetime] = None
    check_out: Optional[datetime] = None
    guests_count: Optional[int] = Field(default=None, ge=1)
    adults_count: Optional[int] = Field(default=None, ge=1)
    children_count: Optional[int] = Field(default=None, ge=0)
    rate_plan_id: Optional[str] = None
    price_per_night: Optional[float] = Field(default=None, ge=0)
    total_amount: Optional[float] = Field(default=None, ge=0)
    currency: Optional[str] = Field(default=None, min_length=3, max_length=3)
    payment_status: Optional[PaymentStatus] = None
    booking_source: Optional[BookingSource] = None
    status: Optional[BookingStatus] = None
    special_requests: Optional[str] = None
    notes: Optional[str] = None

    @model_validator(mode="after")
    def validate_dates(self):
        if self.check_in and self.check_out and self.check_out <= self.check_in:
            raise ValueError("check_out must be later than check_in (same date is allowed with valid times)")
        if self.currency:
            self.currency = self.currency.upper()
        return self
