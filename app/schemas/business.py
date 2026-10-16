from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class BusinessTypeBase(BaseModel):
    code: str
    name: str
    description: Optional[str] = None


class BusinessTypeCreate(BusinessTypeBase):
    pass


class BusinessTypeUpdate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None


class BusinessTypeResponse(BaseModel):
    id: str  # This is the public_id
    code: str
    name: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class BusinessBase(BaseModel):
    name: str
    description: Optional[str] = None
    slogan: Optional[str] = None
    registration_number: Optional[str] = None
    t_pin_number: Optional[str] = None
    slug: Optional[str] = None
    timezone: Optional[str] = None
    currency: Optional[str] = None
    status: str = "active"


class BusinessCreate(BusinessBase):
    owner_id: int
    address_id: Optional[int] = None
    business_type_id: Optional[int] = None


class BusinessUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    slogan: Optional[str] = None
    registration_number: Optional[str] = None
    t_pin_number: Optional[str] = None
    slug: Optional[str] = None
    timezone: Optional[str] = None
    currency: Optional[str] = None
    status: Optional[str] = None
    address_id: Optional[int] = None
    business_type_id: Optional[int] = None


class BusinessResponse(BaseModel):
    id: str  # This is the public_id
    name: str
    description: Optional[str] = None
    slogan: Optional[str] = None
    registration_number: Optional[str] = None
    t_pin_number: Optional[str] = None
    slug: Optional[str] = None
    timezone: Optional[str] = None
    currency: Optional[str] = None
    status: str
    business_type: Optional[BusinessTypeResponse] = None
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class BusinessUserCreate(BaseModel):
    business_id: int
    user_id: int
    status: str = "active"


class BusinessUserResponse(BaseModel):
    id: int
    business_id: int
    user_id: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
