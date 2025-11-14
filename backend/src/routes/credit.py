"""
Credit and Subscription API routes
"""
import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import SubscriptionPeriod, get_db, SUBSCRIPTION_PLANS, SubscriptionType, calculate_segment_credit
from src.services.credit_service import CreditService
from src.services.subscription_service import SubscriptionService
from src.schemas.credit import (
    CreateSubscriptionRequest,
    CancelSubscriptionRequest,
    GrantCreditRequest,
    RedeemCodeRequest,
)
from src.types.auth import User
from src.utils.dependencies import get_current_user, get_current_user_id
from src.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


# ===== Credit related endpoints =====

@router.get("/balance")
async def get_credit_balance(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current user's credit balance
    """

    # Get credit balance
    balance = await CreditService.get_user_credit_balance(db, current_user.id)

    # Get active subscription
    subscription = await SubscriptionService.get_active_subscription(db, current_user.id)

    return {
        "status": "success",
        "message": "Credit balance retrieved successfully",
        "data": {
            "user_id": str(current_user.id),
            "credit_balance": balance,
            "has_active_subscription": subscription is not None,
            "subscription_type": subscription.subscription_type if subscription else None
        }
    }


@router.get("/transactions")
async def get_credit_transactions(
    limit: int = Query(50, ge=1, le=100, description="Number of records to return"),
    offset: int = Query(0, ge=0, description="Offset"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current user's credit transaction records
    """

    # Get transaction records
    transactions = await CreditService.get_credit_transactions(
        db, current_user.id, limit, offset
    )

    # Get current balance
    balance = await CreditService.get_user_credit_balance(db, current_user.id)

    return {
        "status": "success",
        "message": "Credit transactions retrieved successfully",
        "data": {
            "total": len(transactions),
            "transactions": [
                {
                    "id": str(t.id),
                    "user_id": str(t.user_id),
                    "task_id": str(t.task_id) if t.task_id else None,
                    "subscription_id": str(t.subscription_id) if t.subscription_id else None,
                    "transaction_type": t.transaction_type,
                    "amount": t.amount,
                    "balance_after": t.balance_after,
                    "description": t.description,
                    "created_at": t.created_at.isoformat()
                }
                for t in transactions
            ],
            "current_balance": balance
        }
    }

# Redeem code redemption

@router.post("/redeem")
async def redeem_code(
    request: RedeemCodeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Redeem credits with redeem code
    Currently supports redeeming 1000 credits, code becomes invalid after use
    Each user can only use a 1000 credit redeem code once, codes with other amounts (such as subscription redeem codes) are not subject to this limitation
    """
    transaction = await CreditService.redeem_code(
        db=db,
        user_id=current_user.id,
        code=request.code.strip()
    )
    
    return {
        "status": "success",
        "message": "Redeem code successfully",
        "data": {
            "transaction_id": str(transaction.id),
            "credit_amount": transaction.amount,
            "balance_after": transaction.balance_after,
            "code": request.code
        }
    }

# ===== Subscription related endpoints =====

@router.get("/subscription/plans")
async def get_subscription_plans():
    """
    Get all subscription plans (including monthly and yearly subscriptions)
    """

    plans = []
    for sub_type, plan_info in SUBSCRIPTION_PLANS.items():
        # Build period options list
        periods = []
        for period, period_info in plan_info["periods"].items():
            periods.append({
                "period": period.value,
                "price": period_info["price"],
                "product_id": period_info.get("product_id"),
                "billing_cycle_months": period_info["billing_cycle_months"],
                "billing_amount": period_info.get("total_price", period_info["price"]),
                "billing_description": "yearly" if period.value == "yearly" else "monthly"
            })
        
        plans.append({
            "type": sub_type.value,
            "name": plan_info["name"],
            "monthly_credits": plan_info["monthly_credits"],
            "description": plan_info["description"],
            "periods": periods
        })

    return {
        "status": "success",
        "message": "Subscription plans retrieved successfully",
        "data": {
            "plans": plans
        }
    }

@router.get("/subscription/payment/create")
async def create_subscription_payment(
    product_id: str,
    subscription_type: SubscriptionType,
    subscription_period: SubscriptionPeriod,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get subscription payment URL
    """

    payment_url = await SubscriptionService.get_subscription_payment_url(
        db, 
        current_user,
        product_id,
        subscription_type,
        subscription_period
    )

    return {
        "status": "success",
        "message": "Subscription payment URL generated successfully",
        "data": {
            "payment_url": payment_url
        }
    }

@router.get("/subscription/active")
async def get_active_subscription(
    current_user: User = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current active subscription
    """

    subscription = await SubscriptionService.get_active_subscription(db, current_user.id)

    if not subscription:
        raise HTTPException(status_code=404, detail="no active subscription")

    return {
        "status": "success",
        "message": "Active subscription retrieved successfully",
        "data": subscription.to_dict()
    }


@router.get("/subscription/list")
async def get_subscriptions(
    limit: int = Query(50, ge=1, le=100, description="Number of records to return"),
    offset: int = Query(0, ge=0, description="Offset"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all subscription records of user
    """

    # Get all subscriptions
    subscriptions = await SubscriptionService.get_user_subscriptions(
        db, current_user.id, limit, offset
    )

    # Get active subscription
    active_subscription = await SubscriptionService.get_active_subscription(db, current_user.id)

    return {
        "status": "success",
        "message": "Subscriptions retrieved successfully",
        "data": {
            "total": len(subscriptions),
            "subscriptions": [s.to_dict() for s in subscriptions],
            "active_subscription": active_subscription.to_dict() if active_subscription else None
        }
    }


# ===== Admin endpoints =====

@router.post("/admin/grant")
async def admin_grant_credit(
    request: GrantCreditRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Admin grant credits
    """

    # Verify if current user is admin
    if not current_user.is_admin:
         raise HTTPException(status_code=403, detail="need admin permission")

    from src.models import TransactionType

    transaction = await CreditService.grant_credit(
        db=db,
        user_id=uuid.UUID(request.user_id),
        amount=request.amount,
        transaction_type=TransactionType.ADMIN_ADJUST,
        description=request.description or "admin grant credits"
    )

    return {
        "status": "success",
        "message": "Credit granted successfully",
        "data": transaction.to_dict()
    }
