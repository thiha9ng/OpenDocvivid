"""
Credit and Subscription related schemas
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
from enum import Enum


class SubscriptionTypeEnum(str, Enum):
    """Subscription type enumeration"""
    BASIC = "basic"
    PRO = "pro"


class SubscriptionPeriodEnum(str, Enum):
    """Subscription period enumeration"""
    MONTHLY = "monthly"
    YEARLY = "yearly"


class SubscriptionStatusEnum(str, Enum):
    """Subscription status enumeration"""
    ACTIVE = "active"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    PENDING = "pending"


class TransactionTypeEnum(str, Enum):
    """Transaction type enumeration"""
    MONTHLY_GRANT = "monthly_grant"
    TASK_CONSUME = "task_consume"
    REFUND = "refund"
    ADMIN_ADJUST = "admin_adjust"
    PURCHASE = "purchase"
    REDEEM_CODE = "redeem_code"


# ===== Request Schema =====

class CreateSubscriptionRequest(BaseModel):
    """Create subscription request"""
    subscription_type: SubscriptionTypeEnum = Field(..., description="Subscription type")
    subscription_period: SubscriptionPeriodEnum = Field(..., description="Subscription period")
    payment_method: Optional[str] = Field(None, description="Payment method")
    external_subscription_id: Optional[str] = Field(None, description="Third-party subscription ID")


class CancelSubscriptionRequest(BaseModel):
    """Cancel subscription request"""
    subscription_id: str = Field(..., description="Subscription ID")


class GrantCreditRequest(BaseModel):
    """Grant credit request (admin)"""
    user_id: str = Field(..., description="User ID")
    amount: int = Field(..., gt=0, description="Credit amount")
    description: Optional[str] = Field(None, description="Description")


class ConsumeCreditRequest(BaseModel):
    """Consume credit request"""
    amount: int = Field(..., gt=0, description="Credit amount")
    task_id: Optional[str] = Field(None, description="Task ID")
    description: Optional[str] = Field(None, description="Description")


class RedeemCodeRequest(BaseModel):
    """Redeem code redemption request"""
    code: str = Field(..., min_length=1, description="Redeem code")


# ===== Response Schema =====

class CreditBalanceResponse(BaseModel):
    """Credit balance response"""
    user_id: str = Field(..., description="User ID")
    credit_balance: int = Field(..., description="Current credit balance")
    has_active_subscription: bool = Field(..., description="Whether has active subscription")
    subscription_type: Optional[str] = Field(None, description="Subscription type")
    
    class Config:
        from_attributes = True


class CreditTransactionResponse(BaseModel):
    """Credit transaction response"""
    id: str = Field(..., description="Transaction ID")
    user_id: str = Field(..., description="User ID")
    task_id: Optional[str] = Field(None, description="Task ID")
    subscription_id: Optional[str] = Field(None, description="Subscription ID")
    transaction_type: str = Field(..., description="Transaction type")
    amount: int = Field(..., description="Credit amount (positive for gain, negative for consumption)")
    balance_after: int = Field(..., description="Balance after transaction")
    description: Optional[str] = Field(None, description="Transaction description")
    created_at: datetime = Field(..., description="Transaction time")
    
    class Config:
        from_attributes = True


class CreditTransactionListResponse(BaseModel):
    """Credit transaction list response"""
    total: int = Field(..., description="Total count")
    transactions: List[CreditTransactionResponse] = Field(..., description="Transaction list")
    current_balance: int = Field(..., description="Current balance")


class SubscriptionPeriodInfo(BaseModel):
    """Subscription period information"""
    period: str = Field(..., description="Subscription period")
    price: float = Field(..., description="Average monthly price")
    billing_cycle_months: int = Field(..., description="Billing cycle (months)")
    billing_amount: float = Field(..., description="Amount per billing")
    billing_description: str = Field(..., description="Billing description")


class SubscriptionPlanResponse(BaseModel):
    """Subscription plan response"""
    type: str = Field(..., description="Subscription type")
    name: str = Field(..., description="Plan name")
    monthly_credits: int = Field(..., description="Monthly granted credits")
    description: str = Field(..., description="Description")
    periods: List[SubscriptionPeriodInfo] = Field(..., description="Subscription period options")


class SubscriptionResponse(BaseModel):
    """Subscription response"""
    id: str = Field(..., description="Subscription ID")
    user_id: str = Field(..., description="User ID")
    subscription_type: str = Field(..., description="Subscription type")
    subscription_period: str = Field(..., description="Subscription period")
    status: str = Field(..., description="Subscription status")
    price: Optional[float] = Field(None, description="Average monthly price")
    billing_amount: Optional[float] = Field(None, description="Amount per billing")
    currency: str = Field(..., description="Currency type")
    start_date: Optional[datetime] = Field(None, description="Start date")
    end_date: Optional[datetime] = Field(None, description="End date")
    next_billing_date: Optional[datetime] = Field(None, description="Next billing date")
    monthly_credits: int = Field(..., description="Monthly granted credits")
    last_credit_grant_date: Optional[datetime] = Field(None, description="Last credit grant date")
    created_at: datetime = Field(..., description="Creation time")
    updated_at: datetime = Field(..., description="Update time")
    cancelled_at: Optional[datetime] = Field(None, description="Cancellation time")
    
    class Config:
        from_attributes = True


class SubscriptionListResponse(BaseModel):
    """Subscription list response"""
    total: int = Field(..., description="Total count")
    subscriptions: List[SubscriptionResponse] = Field(..., description="Subscription list")
    active_subscription: Optional[SubscriptionResponse] = Field(None, description="Current active subscription")


class SubscriptionPlansResponse(BaseModel):
    """Subscription plans response"""
    plans: List[SubscriptionPlanResponse] = Field(..., description="Subscription plan list")


class RedeemCodeResponse(BaseModel):
    """Redeem code redemption response"""
    transaction_id: str = Field(..., description="Transaction ID")
    credit_amount: int = Field(..., description="Redeemed credits")
    balance_after: int = Field(..., description="Balance after redemption")
    code: str = Field(..., description="Redeem code")


