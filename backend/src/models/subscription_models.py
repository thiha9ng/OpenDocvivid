import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, Integer, ForeignKey, Numeric, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from .base import Base, utc_now


class SubscriptionType(PyEnum):
    """Subscription type enumeration"""
    BASIC = "basic"
    PRO = "pro"


class SubscriptionPeriod(PyEnum):
    """Subscription period enumeration"""
    MONTHLY = "monthly"   # Monthly subscription
    YEARLY = "yearly"     # Yearly subscription


class SubscriptionStatus(PyEnum):
    """Subscription status enumeration"""
    ACTIVE = "active"          # Active
    CANCELLED = "cancelled"    # Cancelled (no renewal after expiration)
    EXPIRED = "expired"        # Expired
    PENDING = "pending"        # Pending payment
    DELETED = "deleted"        # Deleted


class TransactionType(PyEnum):
    """Credit transaction type enumeration"""
    MONTHLY_GRANT = "monthly_grant"    # Monthly grant
    MONTHLY_RECLAIM = "monthly_reclaim"  # Monthly credit reclaim (clear unused credits from last month)
    TASK_CONSUME = "task_consume"      # Task consumption
    REFUND = "refund"                  # Refund
    ADMIN_ADJUST = "admin_adjust"      # Admin adjustment
    PURCHASE = "purchase"              # Purchase
    REDEEM_CODE = "redeem_code"        # Redeem code redemption


# Subscription plan configuration
SUBSCRIPTION_PLANS = {
    SubscriptionType.BASIC: {
        "name": "Basic Plan",
        "monthly_credits": 1000,
        "description": "basic plan, monthly 1000 credits",
        "periods": {
            SubscriptionPeriod.MONTHLY: {
                "product_id": "payment_product_id",
                "price": 12.00,
                "billing_cycle_months": 1,
            },
            SubscriptionPeriod.YEARLY: {
                "price": 9.00,  # Average monthly price
                "billing_cycle_months": 12,
                "total_price": 108.00,  # Annual total price
                "product_id": "payment_product_id",
            }
        }
    },
    SubscriptionType.PRO: {
        "name": "Pro Plan",
        "monthly_credits": 2200,
        "description": "pro plan, monthly 2200 credits",
        "periods": {
            SubscriptionPeriod.MONTHLY: {
                "product_id": "payment_product_id",
                "price": 24.00,
                "billing_cycle_months": 1,
            },
            SubscriptionPeriod.YEARLY: {
                "price": 19.00,  # Average monthly price
                "product_id": "payment_product_id",
                "billing_cycle_months": 12,
                "total_price": 228.00,  # Annual total price
            }
        }
    }
}


class Subscription(Base):
    """
    User subscription table
    """
    __tablename__ = "subscriptions"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # User ID
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    
    # Subscription information
    subscription_type = Column(String(50), nullable=False, index=True)  # basic, pro
    subscription_period = Column(String(50), nullable=False, index=True)  # monthly, yearly
    status = Column(String(50), nullable=False, default=SubscriptionStatus.PENDING.value, index=True)
    
    # Pricing information
    price = Column(Numeric(10, 2), nullable=False)  # Subscription price (average monthly price)
    billing_amount = Column(Numeric(10, 2), nullable=False)  # Billing amount per charge (monthly or annual total)
    currency = Column(String(10), nullable=False, default="USD")  # Currency type
    
    # Period information
    start_date = Column(DateTime, nullable=True)  # Subscription start date
    end_date = Column(DateTime, nullable=True)    # Subscription end date
    next_billing_date = Column(DateTime, nullable=True)  # Next billing date
    
    # Credit grant records
    monthly_credits = Column(Integer, nullable=False)  # Monthly granted credits
    last_credit_grant_date = Column(DateTime, nullable=True)  # Last credit grant date
    
    # Payment information (optional, for payment system integration)
    payment_method = Column(String(50), nullable=True)  # stripe, paypal, etc.
    external_subscription_id = Column(String(255), nullable=True)  # Third-party subscription ID
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=utc_now)
    updated_at = Column(DateTime, nullable=False, default=utc_now, onupdate=utc_now)
    cancelled_at = Column(DateTime, nullable=True)  # Cancellation time
    
    # Relationships
    user = relationship("User", back_populates="subscriptions")
    
    def __repr__(self):
        return f"<Subscription(id={self.id}, user_id={self.user_id}, type={self.subscription_type}, status={self.status})>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "subscription_type": self.subscription_type,
            "subscription_period": self.subscription_period,
            "status": self.status,
            "price": float(self.price) if self.price else None,
            "billing_amount": float(self.billing_amount) if self.billing_amount else None,
            "currency": self.currency,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "next_billing_date": self.next_billing_date.isoformat() if self.next_billing_date else None,
            "monthly_credits": self.monthly_credits,
            "last_credit_grant_date": self.last_credit_grant_date.isoformat() if self.last_credit_grant_date else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "cancelled_at": self.cancelled_at.isoformat() if self.cancelled_at else None,
        }
    
    @property
    def is_active(self) -> bool:
        """Check if subscription is active"""
        return self.status == SubscriptionStatus.ACTIVE.value and (
            self.end_date is None or self.end_date > datetime.now(timezone.utc).replace(tzinfo=None)
        )


class CreditTransaction(Base):
    """
    Credit transaction history table
    """
    __tablename__ = "credit_transactions"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # User ID
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    
    # Associated task (if task consumption)
    task_id = Column(UUID(as_uuid=True), ForeignKey('video_generate_tasks.id'), nullable=True, index=True)
    
    # Associated subscription (if subscription grant)
    subscription_id = Column(UUID(as_uuid=True), ForeignKey('subscriptions.id'), nullable=True, index=True)
    
    # Transaction information
    transaction_type = Column(String(50), nullable=False, index=True)  # monthly_grant, task_consume, refund, etc.
    amount = Column(Integer, nullable=False)  # Credit amount, positive for gain, negative for consumption
    balance_after = Column(Integer, nullable=False)  # Credit balance after transaction
    
    # Description information
    description = Column(Text, nullable=True)  # Transaction description
    extra_metadata = Column(Text, nullable=True)  # Extra metadata (JSON format)
    
    # Timestamp
    created_at = Column(DateTime, nullable=False, default=utc_now, index=True)
    
    # Relationships
    user = relationship("User", back_populates="credit_transactions")
    task = relationship("VideoGenerateTask", foreign_keys=[task_id])
    subscription = relationship("Subscription", foreign_keys=[subscription_id])
    
    def __repr__(self):
        return f"<CreditTransaction(id={self.id}, user_id={self.user_id}, type={self.transaction_type}, amount={self.amount})>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "task_id": str(self.task_id) if self.task_id else None,
            "subscription_id": str(self.subscription_id) if self.subscription_id else None,
            "transaction_type": self.transaction_type,
            "amount": self.amount,
            "balance_after": self.balance_after,
            "description": self.description,
            "extra_metadata": self.extra_metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


def get_subscription_plan(subscription_type: SubscriptionType, period: SubscriptionPeriod) -> dict:
    """
    Get subscription plan information
    
    Args:
        subscription_type: Subscription type (BASIC or PRO)
        period: Subscription period (MONTHLY or YEARLY)
    
    Returns:
        Dictionary containing plan details
    """
    plan = SUBSCRIPTION_PLANS.get(subscription_type)
    if not plan:
        raise ValueError(f"Invalid subscription type: {subscription_type}")
    
    period_info = plan["periods"].get(period)
    if not period_info:
        raise ValueError(f"Invalid subscription period: {period}")
    
    return {
        "name": plan["name"],
        "monthly_credits": plan["monthly_credits"],
        "description": plan["description"],
        "price": period_info["price"],
        "billing_cycle_months": period_info["billing_cycle_months"],
        "billing_amount": period_info.get("total_price", period_info["price"]),
    }


def calculate_segment_credit(duration_seconds: int) -> int:
    """
    Calculate required credits based on segment duration
    
    Args:
        duration_seconds: Segment duration (seconds)
    
    Returns:
        Required credits
    """
    if duration_seconds > 60:
        return 45
    elif duration_seconds >= 45:
        return 40
    elif duration_seconds >= 30:
        return 35
    else:
        return 30


def calculate_task_credit(segments_duration: list) -> int:
    """
    Calculate total credits required for entire task
    
    Args:
        segments_duration: List of segment durations (seconds)
    
    Returns:
        Total credits
    """
    return sum(calculate_segment_credit(duration) for duration in segments_duration)


class RedeemCode(Base):
    """
    Redeem code table
    """
    __tablename__ = "redeem_codes"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Redeem code information
    code = Column(String(100), unique=True, nullable=False, index=True)  # Redeem code (unique)
    credit_amount = Column(Integer, nullable=False, default=1000)  # Credits to redeem
    
    # Usage information
    is_used = Column(Boolean, nullable=False, default=False)  # Whether it has been used
    used_by = Column(UUID(as_uuid=True), nullable=True, index=True)  # User ID who used it
    used_at = Column(DateTime, nullable=True)  # Usage time
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=utc_now)
    updated_at = Column(DateTime, nullable=False, default=utc_now, onupdate=utc_now)
    
    def __repr__(self):
        return f"<RedeemCode(id={self.id}, code={self.code}, is_used={self.is_used})>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": str(self.id),
            "code": self.code,
            "credit_amount": self.credit_amount,
            "is_used": self.is_used,
            "used_by": str(self.used_by) if self.used_by else None,
            "used_at": self.used_at.isoformat() if self.used_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

