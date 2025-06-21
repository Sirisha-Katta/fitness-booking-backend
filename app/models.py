from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class FitnessClass(BaseModel):
    id: Optional[str]
    class_id: int
    name: str
    datetime: datetime
    instructor: str
    available_slots: int


class FitnessClassInDB(FitnessClass):
    _id: str

class BookingRequest(BaseModel):
    client_name: str = Field(..., alias="name")
    client_email: str = Field(..., alias="email")
    class_id: int
    timezone: str = "Asia/Kolkata"  # Default timezone

class Booking(BaseModel):
    id: Optional[str] = None
    class_id: int
    class_name: str
    datetime: str
    instructor: str
    client_name: str
    client_email: str
    timezone: str = "Asia/Kolkata"

