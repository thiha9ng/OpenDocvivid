"""
Subscription management service
处理用户订阅相关的业务逻辑
"""
import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc
import bagelpay
from bagelpay import BagelPayClient, CheckoutRequest, Customer

from src.configs.config import settings
from src.types.auth import User as AuthUser
from src.models import (
    User,
    Subscription,
    SubscriptionType,
    SubscriptionPeriod,
    SubscriptionStatus,
    SUBSCRIPTION_PLANS,
    get_subscription_plan
)
from src.services.credit_service import CreditService
from src.utils.logger import get_logger
from src.utils.exceptions import (
    BadRequestException,
    NotFoundException,
    ConflictException,
    ForbiddenException,
    InternalServerException
)

logger = get_logger(__name__)


class SubscriptionService:
    """订阅服务"""

    @classmethod
    async def _create_subscription(
        cls,
        db: AsyncSession,
        user_id: uuid.UUID,
        subscription_type: str,
        subscription_period: str,
        payment_method: Optional[str] = None,
        external_subscription_id: Optional[str] = None
    ) -> Subscription:
        """
        创建订阅（内部方法）

        Args:
            db: 数据库会话
            user_id: 用户ID
            subscription_type: 订阅类型 (basic/pro)
            subscription_period: 订阅周期 (monthly/yearly)
            payment_method: 支付方式
            external_subscription_id: 第三方订阅ID

        Returns:
            订阅对象
        """
        try:
            # 验证订阅类型
            if subscription_type not in [st.value for st in SubscriptionType]:
                raise BadRequestException(
                    detail=f"invalid subscription type: {subscription_type}"
                )

            # 验证订阅周期
            if subscription_period not in [sp.value for sp in SubscriptionPeriod]:
                raise BadRequestException(
                    detail=f"invalid subscription period: {subscription_period}"
                )

            # 获取订阅计划配置
            plan = get_subscription_plan(
                SubscriptionType(subscription_type),
                SubscriptionPeriod(subscription_period)
            )

            # 检查用户是否存在
            stmt = select(User).where(User.id == user_id)
            result = await db.execute(stmt)
            user = result.scalar_one_or_none()

            if not user:
                raise NotFoundException(
                    detail="user not found"
                )

            # 检查用户是否已有激活的订阅
            existing_subscription = await cls.get_active_subscription(db, user_id)
            if existing_subscription:
                raise ConflictException(
                    detail="user already has an active subscription"
                )

            # 创建订阅
            subscription = Subscription(
                user_id=user_id,
                subscription_type=subscription_type,
                subscription_period=subscription_period,
                status=SubscriptionStatus.PENDING.value,
                price=plan["price"],
                billing_amount=plan["billing_amount"],
                currency="USD",
                monthly_credits=plan["monthly_credits"],
                payment_method=payment_method,
                external_subscription_id=external_subscription_id
            )

            db.add(subscription)
            await db.commit()
            await db.refresh(subscription)

            logger.info(
                f"Created subscription {subscription.id} for user {user_id}, type: {subscription_type}, period: {subscription_period}")

            return subscription

        except (BadRequestException, NotFoundException, ConflictException):
            await db.rollback()
            raise
        except Exception as e:
            await db.rollback()
            logger.error(
                f"Failed to create subscription for user {user_id}: {e}")
            raise InternalServerException(
                detail="failed to create subscription"
            )

    @staticmethod
    async def activate_subscription(
        db: AsyncSession,
        subscription_id: uuid.UUID,
        user_id: uuid.UUID
    ) -> Subscription:
        """
        激活订阅（支付成功后调用）

        Args:
            db: 数据库会话
            subscription_id: 订阅ID

        Returns:
            订阅对象
        """
        try:
            # 查询订阅
            stmt = select(Subscription).where(
                Subscription.id == subscription_id)
            result = await db.execute(stmt)
            subscription = result.scalar_one_or_none()

            if not subscription:
                raise NotFoundException(
                    detail="subscription not found"
                )

            # 验证订阅属于当前用户
            if subscription.user_id != user_id:
                raise ForbiddenException(
                    detail="not authorized to operate this subscription"
                )

            # 设置订阅周期
            now = datetime.now(timezone.utc).replace(tzinfo=None)
            subscription.status = SubscriptionStatus.ACTIVE.value
            subscription.start_date = now

            # 根据订阅周期计算结束日期
            if subscription.subscription_period == SubscriptionPeriod.YEARLY.value:
                # 年度订阅：365天
                subscription.end_date = now + timedelta(days=365)
            else:
                # 月度订阅：30天
                subscription.end_date = now + timedelta(days=30)

            subscription.next_billing_date = subscription.end_date

            await db.commit()

            # 赠送首月积分
            await CreditService.grant_monthly_subscription_credit(db, subscription)

            logger.info(f"Activated subscription {subscription_id}")

            await db.refresh(subscription)
            return subscription

        except (NotFoundException, ForbiddenException):
            await db.rollback()
            raise
        except Exception as e:
            await db.rollback()
            logger.error(
                f"Failed to activate subscription {subscription_id}: {e}")
            raise InternalServerException(
                detail="failed to activate subscription"
            )

    @staticmethod
    async def cancel_subscription(
        db: AsyncSession,
        user_id: uuid.UUID,
        subscription_id: uuid.UUID
    ) -> Subscription:
        """
        取消订阅

        Args:
            db: 数据库会话
            user_id: 用户ID
            subscription_id: 订阅ID

        Returns:
            订阅对象
        """
        try:
            # 查询订阅
            stmt = select(Subscription).where(
                and_(
                    Subscription.id == subscription_id,
                    Subscription.user_id == user_id
                )
            )
            result = await db.execute(stmt)
            subscription = result.scalar_one_or_none()

            if not subscription:
                raise NotFoundException(
                    detail="subscription not found"
                )

            # 更新订阅状态
            now = datetime.now(timezone.utc).replace(tzinfo=None)
            subscription.status = SubscriptionStatus.CANCELLED.value
            subscription.cancelled_at = now

            await db.commit()
            await db.refresh(subscription)

            logger.info(
                f"Cancelled subscription {subscription_id} for user {user_id}")

            return subscription

        except NotFoundException:
            await db.rollback()
            raise
        except Exception as e:
            await db.rollback()
            logger.error(
                f"Failed to cancel subscription {subscription_id}: {e}")
            raise InternalServerException(
                detail="failed to cancel subscription"
            )

    @staticmethod
    async def get_active_subscription(
        db: AsyncSession,
        user_id: uuid.UUID
    ) -> Optional[Subscription]:
        """
        获取用户的激活订阅

        Args:
            db: 数据库会话
            user_id: 用户ID

        Returns:
            订阅对象或None
        """
        try:
            now = datetime.now(timezone.utc).replace(tzinfo=None)

            stmt = select(Subscription).where(
                and_(
                    Subscription.user_id == user_id,
                    Subscription.status == SubscriptionStatus.ACTIVE.value,
                    Subscription.end_date > now
                )
            ).order_by(desc(Subscription.created_at))

            result = await db.execute(stmt)
            subscription = result.scalar_one_or_none()

            return subscription

        except Exception as e:
            logger.error(
                f"Failed to get active subscription for user {user_id}: {e}")
            return None

    @staticmethod
    async def get_user_subscriptions(
        db: AsyncSession,
        user_id: uuid.UUID,
        limit: int = 50,
        offset: int = 0
    ) -> List[Subscription]:
        """
        获取用户的所有订阅记录

        Args:
            db: 数据库会话
            user_id: 用户ID
            limit: 返回数量限制
            offset: 偏移量

        Returns:
            订阅列表
        """
        try:
            stmt = (
                select(Subscription)
                .where(Subscription.user_id == user_id)
                .order_by(desc(Subscription.created_at))
                .limit(limit)
                .offset(offset)
            )

            result = await db.execute(stmt)
            subscriptions = result.scalars().all()

            return list(subscriptions)

        except Exception as e:
            logger.error(
                f"Failed to get subscriptions for user {user_id}: {e}")
            raise InternalServerException(
                detail="failed to get subscriptions"
            )

    @staticmethod
    async def renew_subscription(
        db: AsyncSession,
        subscription_id: uuid.UUID
    ) -> Subscription:
        """
        续订订阅（自动续费或手动续费时调用）

        Args:
            db: 数据库会话
            subscription_id: 订阅ID

        Returns:
            订阅对象
        """
        try:
            # 查询订阅
            stmt = select(Subscription).where(
                Subscription.id == subscription_id)
            result = await db.execute(stmt)
            subscription = result.scalar_one_or_none()

            if not subscription:
                raise NotFoundException(
                    detail="subscription not found"
                )

            # 更新订阅周期
            now = datetime.now(timezone.utc).replace(tzinfo=None)

            # 根据订阅周期计算延长时长
            if subscription.subscription_period == SubscriptionPeriod.YEARLY.value:
                renewal_days = 365  # 年度订阅
            else:
                renewal_days = 30  # 月度订阅

            # 如果订阅已过期，从现在开始计算
            if subscription.end_date and subscription.end_date < now:
                subscription.start_date = now
                subscription.end_date = now + timedelta(days=renewal_days)
            else:
                # 如果订阅未过期，从原结束日期延长
                subscription.end_date = subscription.end_date + \
                    timedelta(days=renewal_days)

            subscription.next_billing_date = subscription.end_date
            subscription.status = SubscriptionStatus.ACTIVE.value

            await db.commit()

            # 赠送新一期的积分
            await CreditService.grant_monthly_subscription_credit(db, subscription)

            logger.info(f"Renewed subscription {subscription_id}")

            await db.refresh(subscription)
            return subscription

        except NotFoundException:
            await db.rollback()
            raise
        except Exception as e:
            await db.rollback()
            logger.error(
                f"Failed to renew subscription {subscription_id}: {e}")
            raise InternalServerException(
                detail="failed to renew subscription"
            )

    @staticmethod
    async def check_and_expire_subscriptions(db: AsyncSession) -> int:
        """
        检查并过期到期的订阅（定时任务调用）

        Args:
            db: 数据库会话

        Returns:
            过期的订阅数量
        """
        try:
            now = datetime.now(timezone.utc).replace(tzinfo=None)

            # 查询到期的激活订阅
            stmt = select(Subscription).where(
                and_(
                    Subscription.status == SubscriptionStatus.ACTIVE.value,
                    Subscription.end_date <= now
                )
            )

            result = await db.execute(stmt)
            expired_subscriptions = result.scalars().all()

            count = 0
            for subscription in expired_subscriptions:
                subscription.status = SubscriptionStatus.EXPIRED.value
                count += 1
                logger.info(f"Expired subscription {subscription.id}")

            await db.commit()

            return count

        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to check and expire subscriptions: {e}")
            raise InternalServerException(
                detail="failed to check and expire subscriptions"
            )

    @classmethod
    async def get_subscription_payment_url(
        cls,
        db: AsyncSession,
        user: AuthUser,
        product_id: str,
        subscription_type: SubscriptionType,
        subscription_period: SubscriptionPeriod
    ) -> str:
        """
        获取订阅支付URL
        """
        try:
            # 先在数据库中创建订阅记录（状态为PENDING）
            subscription = await cls._create_subscription(
                db=db,
                user_id=uuid.UUID(user.id),
                subscription_type=subscription_type.value,
                subscription_period=subscription_period.value,
                payment_method="bagelpay"
            )

            logger.info(f"Created pending subscription {subscription.id} for user {user.id}")

            # 使用订阅ID作为request_id创建支付链接
            client = BagelPayClient(api_key=settings.payment_api_key, test_mode=True)
            advanced_checkout = CheckoutRequest(
                product_id=product_id,
                request_id=str(subscription.id),
                units="1",
                customer=Customer(
                    email=user.email
                ),
                success_url="https://aidocvivid.com/",
                metadata={
                    # Subscription tracking
                    "subscription_type": subscription_type.value,
                    "subscription_period": subscription_period.value,
                    "subscription_id": str(subscription.id),

                    # User context
                    "user_id": str(user.id),
                }
            )

            response = client.create_checkout(advanced_checkout)

            logger.info(f"User {user.id} subscription payment URL: {response}")
            checkout_url = response.checkout_url
            return checkout_url
        except (ConflictException, BadRequestException, NotFoundException):
            raise
        except Exception as e:
            logger.error(f"Failed to get subscription payment URL: {e}")
            raise InternalServerException(
                detail="failed to get subscription payment url")
