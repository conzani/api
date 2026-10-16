import secrets
from sqlalchemy import Column, BigInteger, String, DateTime, Date, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


def generate_public_id():
    """Generate a 16-character UUID-like public ID."""
    return secrets.token_hex(8)  # 16 hex characters


class Address(Base):
    __tablename__ = "address"

    id = Column(BigInteger, primary_key=True, index=True)
    address = Column(String(255))
    county = Column(String(100))
    region = Column(String(100))
    district = Column(String(100))
    current_location = Column(String(255))
    country = Column(String(100))
    postal_code = Column(String(20))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    customers = relationship("Customer", back_populates="address")
    businesses = relationship("Business", back_populates="address")


class Customer(Base):
    __tablename__ = "customer"

    id = Column(BigInteger, primary_key=True, index=True)
    public_id = Column(String(16), unique=True, index=True, default=generate_public_id)
    auth_id = Column(BigInteger, ForeignKey("auth.id"), unique=True)
    business_id = Column(BigInteger, ForeignKey("business.id"))
    address_id = Column(BigInteger, ForeignKey("address.id"))
    customer_type = Column(String(50))
    firstname = Column(String(100))
    lastname = Column(String(100))
    date_of_birth = Column(Date)
    gender = Column(String(20))
    phone = Column(String(20))
    email = Column(String(255))
    status = Column(String(50), default="active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    auth = relationship("Auth", backref="customer")
    address = relationship("Address", back_populates="customers")
    business = relationship("Business", back_populates="customers")