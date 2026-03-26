from pydantic import BaseModel, EmailStr
from typing import Optional


class StaffCreate(BaseModel):
    name: str
    role: str
    department: str

    email: EmailStr
    phone: str

    # Salary details (kept simple: amount + optional currency).
    salary: float
    currency: Optional[str] = None

    # e.g. "active", "terminated", "on_leave"
    employment_status: str


class StaffUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    department: Optional[str] = None

    email: Optional[EmailStr] = None
    phone: Optional[str] = None

    salary: Optional[float] = None
    currency: Optional[str] = None

    employment_status: Optional[str] = None

