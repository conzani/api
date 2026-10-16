import secrets
from sqlalchemy import Column, BigInteger, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


def generate_public_id():
    """Generate a 16-character UUID-like public ID."""
    return secrets.token_hex(8)  # 16 hex characters


class Role(Base):
    __tablename__ = "roles"

    id = Column(BigInteger, primary_key=True, index=True)
    public_id = Column(String(16), unique=True, index=True, default=generate_public_id)
    business_id = Column(BigInteger, ForeignKey("business.id"), nullable=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    is_system = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user_roles = relationship("UserRole", back_populates="role")
    permission_groups = relationship("RolePermissionGroup", back_populates="role")


class Permission(Base):
    __tablename__ = "permission"

    id = Column(BigInteger, primary_key=True, index=True)
    public_id = Column(String(16), unique=True, index=True, default=generate_public_id)
    code = Column(String(100), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    permission_groups = relationship("RolePermissionGroup", back_populates="permission")


class RolePermissionGroup(Base):
    __tablename__ = "role_permission_group"

    id = Column(BigInteger, primary_key=True, index=True)
    role_id = Column(BigInteger, ForeignKey("roles.id"))
    permission_id = Column(BigInteger, ForeignKey("permission.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    role = relationship("Role", back_populates="permission_groups")
    permission = relationship("Permission", back_populates="permission_groups")