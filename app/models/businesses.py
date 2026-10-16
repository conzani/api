import secrets
from sqlalchemy import Column, BigInteger, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


def generate_public_id():
    """Generate a 16-character UUID-like public ID."""
    return secrets.token_hex(8)  # 16 hex characters


class BusinessType(Base):
    __tablename__ = "business_type"

    id = Column(BigInteger, primary_key=True, index=True)
    public_id = Column(String(16), unique=True, index=True, default=generate_public_id)
    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)


class Business(Base):
    __tablename__ = "business"

    id = Column(BigInteger, primary_key=True, index=True)
    public_id = Column(String(16), unique=True, index=True, default=generate_public_id)
    owner_id = Column(BigInteger, ForeignKey("users.id"))
    address_id = Column(BigInteger, ForeignKey("address.id"))
    business_type_id = Column(BigInteger, ForeignKey("business_type.id"))
    name = Column(String(255), nullable=False)
    description = Column(String(500))
    slogan = Column(String(255))
    registration_number = Column(String(100))
    t_pin_number = Column(String(100))
    slug = Column(String(255), unique=True, index=True)
    timezone = Column(String(50))
    currency = Column(String(10))
    status = Column(String(50), default="active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    owner = relationship("User", backref="owned_businesses")
    address = relationship("Address", back_populates="businesses")
    business_type = relationship("BusinessType", backref="businesses")
    customers = relationship("Customer", back_populates="business")
    business_users = relationship("BusinessUser", back_populates="business")
    roles = relationship("Role", backref="business")


class BusinessUser(Base):
    __tablename__ = "business_user"

    id = Column(BigInteger, primary_key=True, index=True)
    business_id = Column(BigInteger, ForeignKey("business.id"))
    user_id = Column(BigInteger, ForeignKey("users.id"))
    status = Column(String(50), default="active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    business = relationship("Business", back_populates="business_users")
    user = relationship("User", backref="business_memberships")