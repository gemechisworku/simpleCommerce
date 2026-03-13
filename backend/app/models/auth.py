"""
Authentication models (OTP, Refresh Tokens)
"""
from sqlalchemy import Column, String, Text, BigInteger, ForeignKey, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models.base import Base
import enum


class OTPType(str, enum.Enum):
    """OTP type enum (values match PostgreSQL otptype: uppercase)."""
    PHONE = "PHONE"
    EMAIL = "EMAIL"


class OTPPurpose(str, enum.Enum):
    """OTP purpose enum (values match PostgreSQL otppurpose: uppercase)."""
    LOGIN = "LOGIN"
    VERIFICATION = "VERIFICATION"
    PASSWORD_RESET = "PASSWORD_RESET"


class OTPCode(Base):
    """OTP code model"""
    __tablename__ = "otp_codes"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    identifier = Column(String(255), nullable=False, index=True)  # Phone or email
    code = Column(String(10), nullable=False, index=True)
    type = Column(SQLEnum(OTPType, values_callable=lambda x: [e.value for e in x]), nullable=False)
    purpose = Column(SQLEnum(OTPPurpose, values_callable=lambda x: [e.value for e in x]), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    used_at = Column(DateTime(timezone=True), nullable=True)
    ip_address = Column(String(45), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self):
        return f"<OTPCode(id={self.id}, identifier={self.identifier}, type={self.type}, used={self.used_at is not None})>"


class RefreshToken(Base):
    """Refresh token model"""
    __tablename__ = "refresh_tokens"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token = Column(String(500), nullable=False, unique=True, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    user = relationship("User", backref="refresh_tokens")

    def __repr__(self):
        return f"<RefreshToken(id={self.id}, user_id={self.user_id}, revoked={self.revoked_at is not None})>"

