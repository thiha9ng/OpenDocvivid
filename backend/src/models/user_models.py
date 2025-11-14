from datetime import datetime, timezone
import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import (
    Column, String, Boolean, DateTime, Integer, Index, UniqueConstraint
)
from sqlalchemy.orm import relationship
from .base import Base, utc_now

class User(Base):
    """User table"""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    username = Column(String(100), unique=False,
                      nullable=True, index=True)  # Username is optional, only for display
    avatar_url = Column(String(255), nullable=True)
    google_open_id = Column(String(255), nullable=True)
    email = Column(String(255), unique=True, nullable=False,
                   index=True)  # Email is unique and required, OAuth login primary key
    full_name = Column(String(255), nullable=True)
    password = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    # Whether user is admin
    is_admin = Column(Boolean, default=False)
    # Credit system
    credit_balance = Column[int](Integer, nullable=False, default=0)  # Current credit balance
    
    created_at = Column(DateTime, nullable=False, default=utc_now)
    updated_at = Column(DateTime, nullable=False, default=utc_now, onupdate=utc_now)

    # Relationships
    subscriptions = relationship("Subscription", back_populates="user", cascade="all, delete-orphan")
    credit_transactions = relationship("CreditTransaction", back_populates="user", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_users_created_at', 'created_at'),
        Index('idx_users_email', 'email'),
        UniqueConstraint('email', name='uq_users_email'),
    )