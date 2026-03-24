from pydantic import BaseModel, EmailStr
from typing import Optional

class GuestCreate(BaseModel):
    name: str
    email: str
    phone: str
    nationality: str
    address: str
    check_in: str   # e.g. "2026-03-25"
    check_out: str  # e.g. "2026-03-28"

class GuestUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    nationality: Optional[str] = None
    address: Optional[str] = None
    check_in: Optional[str] = None
    check_out: Optional[str] = None