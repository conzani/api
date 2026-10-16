from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class UserBase(BaseModel):
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    status: Optional[str] = None


class UserResponse(BaseModel):
    id: str  # This is the public_id
    email: EmailStr
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True
