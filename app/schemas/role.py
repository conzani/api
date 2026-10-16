from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_system: bool = False


class RoleCreate(RoleBase):
    business_id: Optional[int] = None


class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_system: Optional[bool] = None


class RoleResponse(BaseModel):
    id: str  # This is the public_id
    name: str
    description: Optional[str] = None
    is_system: bool
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PermissionBase(BaseModel):
    code: str
    name: str
    description: Optional[str] = None


class PermissionCreate(PermissionBase):
    pass


class PermissionUpdate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None


class PermissionResponse(PermissionBase):
    id: str  # This is the public_id
    code: str
    name: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class RolePermissionGroupCreate(BaseModel):
    role_id: int
    permission_id: int
