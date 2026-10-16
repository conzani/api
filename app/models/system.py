import secrets
from sqlalchemy import Column, BigInteger, String, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


def generate_public_id():
    """Generate a 16-character UUID-like public ID."""
    return secrets.token_hex(8)  # 16 hex characters


class Session(Base):
    __tablename__ = "session"

    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id"))
    refresh_token_hash = Column(String(255))
    device = Column(String(100))
    ip_address = Column(String(50))
    expires_at = Column(DateTime(timezone=True))
    revoked_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", backref="sessions")


class VerificationToken(Base):
    __tablename__ = "verification_token"

    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id"))
    purpose = Column(String(50))  # email, phone, reset
    token_hash = Column(Integer)  # 6-digit code stored as integer
    expires_at = Column(DateTime(timezone=True))
    used_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", backref="verification_tokens")


class Invitation(Base):
    __tablename__ = "invitation"

    id = Column(BigInteger, primary_key=True, index=True)
    business_id = Column(BigInteger, ForeignKey("business.id"))
    role_id = Column(BigInteger, ForeignKey("roles.id"))
    email = Column(String(255))
    token_hash = Column(String(16))  # 16-character invitation code
    expires_at = Column(DateTime(timezone=True))
    accepted_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    business = relationship("Business", backref="invitations")
    role = relationship("Role", backref="invitations")


class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(BigInteger, primary_key=True, index=True)
    business_id = Column(BigInteger, ForeignKey("business.id"))
    user_id = Column(BigInteger, ForeignKey("users.id"))
    action = Column(String(100))
    entity_type = Column(String(100))
    entity_id = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    business = relationship("Business", backref="audit_logs")
    user = relationship("User", backref="audit_logs")