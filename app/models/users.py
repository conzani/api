import secrets
from sqlalchemy import Column, BigInteger, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


def generate_public_id():
    """Generate a 16-character UUID-like public ID."""
    return secrets.token_hex(8)  # 16 hex characters


class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, index=True)
    public_id = Column(String(16), unique=True, index=True, default=generate_public_id)
    auth_id = Column(BigInteger, ForeignKey("auth.id"), unique=True)
    firstname = Column(String(100))
    lastname = Column(String(100))
    gender = Column(String(20))
    phone = Column(String(20))
    email = Column(String(255), unique=True, index=True)
    status = Column(String(50), default="active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    auth = relationship("Auth", backref="user")
    user_roles = relationship("UserRole", back_populates="user", foreign_keys="UserRole.user_id")


class UserRole(Base):
    __tablename__ = "user_role"

    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id"))
    role_id = Column(BigInteger, ForeignKey("roles.id"))
    business_id = Column(BigInteger, ForeignKey("business.id"), nullable=True)
    assigned_by = Column(BigInteger, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="user_roles", foreign_keys=[user_id])
    role = relationship("Role", back_populates="user_roles")
    assigned_by_user = relationship("User", foreign_keys=[assigned_by], backref="assigned_roles")