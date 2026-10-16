from sqlalchemy import Column, BigInteger, String, DateTime, Integer
from sqlalchemy.sql import func
from app.database import Base


class Auth(Base):
    __tablename__ = "auth"

    id = Column(BigInteger, primary_key=True, autoincrement=True, index=True)
    password_hash = Column(String(255), nullable=False)
    password_changed_at = Column(DateTime(timezone=True), nullable=True)
    last_login = Column(DateTime(timezone=True), nullable=True)
    failed_attempts = Column(Integer, nullable=False, default=0)
    locked_until = Column(DateTime(timezone=True), nullable=True)
    email_verified_at = Column(DateTime(timezone=True), nullable=True)
    phone_verified_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)