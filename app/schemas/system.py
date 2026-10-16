from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class SessionCreate(BaseModel):
    user_id: int
    refresh_token_hash: str
    device: Optional[str] = None
    ip_address: Optional[str] = None
    expires_at: datetime


class SessionResponse(BaseModel):
    id: int
    user_id: int
    device: Optional[str] = None
    ip_address: Optional[str] = None
    expires_at: datetime
    revoked_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class VerificationTokenCreate(BaseModel):
    user_id: int
    purpose: str  # email, phone, reset
    token_hash: int  # 6-digit code as integer
    expires_at: datetime


class VerificationTokenResponse(BaseModel):
    id: int
    user_id: int
    purpose: str
    expires_at: datetime
    used_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class InvitationCreate(BaseModel):
    business_id: int
    role_id: int
    email: EmailStr
    token_hash: str  # 16-character code
    expires_at: datetime


class InvitationResponse(BaseModel):
    id: int
    business_id: int
    role_id: int
    email: str
    expires_at: datetime
    accepted_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AuditLogCreate(BaseModel):
    business_id: int
    user_id: int
    action: str
    entity_type: str
    entity_id: str


class AuditLogResponse(BaseModel):
    id: int
    business_id: int
    user_id: int
    action: str
    entity_type: str
    entity_id: str
    created_at: datetime

    class Config:
        from_attributes = True
