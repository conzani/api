from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


class AuthBase(BaseModel):
    email: EmailStr


class AuthCreate(AuthBase):
    password: str = Field(..., min_length=8)


class AuthResponse(BaseModel):
    id: str  # This is the customer public_id
    email: str
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    customer_type: Optional[str] = None
    status: str
    email_verified_at: Optional[datetime] = None
    phone_verified_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    phone: Optional[str] = None


class VerifyEmailRequest(BaseModel):
    email: EmailStr
    code: str = Field(..., min_length=6, max_length=6)


class ResendVerificationRequest(BaseModel):
    email: EmailStr


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    email: EmailStr
    code: str = Field(..., min_length=6, max_length=6)
    new_password: str = Field(..., min_length=8)


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[str] = None
    public_id: Optional[str] = None
