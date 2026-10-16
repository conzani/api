from pydantic import BaseModel, EmailStr
from datetime import datetime, date
from typing import Optional


class AddressBase(BaseModel):
    address: Optional[str] = None
    county: Optional[str] = None
    region: Optional[str] = None
    district: Optional[str] = None
    current_location: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None


class AddressCreate(AddressBase):
    pass


class AddressUpdate(BaseModel):
    address: Optional[str] = None
    county: Optional[str] = None
    region: Optional[str] = None
    district: Optional[str] = None
    current_location: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None


class AddressResponse(AddressBase):
    id: int  # Address doesn't have public_id, keeping as is
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CustomerBase(BaseModel):
    customer_type: Optional[str] = None
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    status: str = "active"


class CustomerCreate(CustomerBase):
    auth_id: Optional[int] = None
    business_id: Optional[int] = None
    address_id: Optional[int] = None


class CustomerUpdate(BaseModel):
    customer_type: Optional[str] = None
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    status: Optional[str] = None
    address_id: Optional[int] = None


class CustomerResponse(BaseModel):
    id: str  # This is the public_id
    customer_type: Optional[str] = None
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    status: str
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True
