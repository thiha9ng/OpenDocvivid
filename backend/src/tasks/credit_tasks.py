"""
Credit and subscription related Celery tasks
积分和订阅相关的定时任务
"""
from celery import Task
from sqlalchemy import select
from datetime import datetime, timezone

from src.celery_app import celery_app
from src.models import (
    get_sync_db,
    Subscription,
    SubscriptionStatus,
)
from src.services.credit_service import SyncCreditService
from src.utils.logger import get_logger

logger = get_logger(__name__)


class DatabaseTask(Task):
    """Base task with database session"""
    _db = None

    @property
    def db(self):
        if self._db is None:
            self._db = get_sync_db()
        return self._db


@celery_app.task(base=DatabaseTask, bind=True, name="grant_monthly_credits")
def grant_monthly_credits(self):
    """
    定时任务：赠送月度积分
    建议每天运行一次，检查并赠送月度积分
    
    Crontab: 0 0 * * *  (每天凌晨0点执行)
    """
    logger.info("Starting monthly credits grant task")
    
    try:
        db = self.db
        
        # 查询所有激活的订阅
        stmt = select(Subscription).where(
            Subscription.status == SubscriptionStatus.ACTIVE.value
        )
        result = db.execute(stmt)
        subscriptions = result.scalars().all()
        
        success_count = 0
        skip_count = 0
        error_count = 0
        
        for subscription in subscriptions:
            try:
                # 使用同步版本的赠送积分方法
                transaction = SyncCreditService.grant_monthly_subscription_credit_sync(
                    db=db,
                    subscription=subscription
                )
                
                # 如果本月已赠送过，跳过
                if transaction is None:
                    skip_count += 1
                    continue
                
                success_count += 1
                logger.info(
                    f"Granted {subscription.monthly_credits} credits to user {subscription.user_id} "
                    f"for subscription {subscription.id}"
                )
                
            except Exception as e:
                db.rollback()
                error_count += 1
                logger.error(
                    f"Failed to grant credits for subscription {subscription.id}: {e}",
                    exc_info=True
                )
        
        logger.info(
            f"Monthly credits grant task completed. "
            f"Success: {success_count}, Skip: {skip_count}, Error: {error_count}"
        )
        
        return {
            "success_count": success_count,
            "skip_count": skip_count,
            "error_count": error_count
        }
        
    except Exception as e:
        logger.error(f"Monthly credits grant task failed: {e}", exc_info=True)
        raise
    finally:
        if hasattr(self, '_db') and self._db:
            self._db.close()
            self._db = None


@celery_app.task(base=DatabaseTask, bind=True, name="check_expired_subscriptions")
def check_expired_subscriptions(self):
    """
    定时任务：检查并过期到期的订阅
    建议每天运行一次
    
    Crontab: 0 1 * * *  (每天凌晨1点执行)
    """
    logger.info("Starting expired subscriptions check task")
    
    try:
        db = self.db
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        
        # 查询到期的激活订阅
        stmt = select(Subscription).where(
            Subscription.status == SubscriptionStatus.ACTIVE.value,
            Subscription.end_date <= now
        )
        result = db.execute(stmt)
        expired_subscriptions = result.scalars().all()
        
        count = 0
        for subscription in expired_subscriptions:
            try:
                subscription.status = SubscriptionStatus.EXPIRED.value
                count += 1
                logger.info(f"Expired subscription {subscription.id}")
            except Exception as e:
                logger.error(f"Failed to expire subscription {subscription.id}: {e}")
        
        db.commit()
        
        logger.info(f"Expired subscriptions check task completed. Expired: {count}")
        
        return {
            "expired_count": count
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Expired subscriptions check task failed: {e}", exc_info=True)
        raise
    finally:
        if hasattr(self, '_db') and self._db:
            self._db.close()
            self._db = None


@celery_app.task(base=DatabaseTask, bind=True, name="check_subscription_renewal")
def check_subscription_renewal(self):
    """
    定时任务：检查即将到期的订阅，发送续费提醒
    建议每天运行一次
    
    Crontab: 0 9 * * *  (每天上午9点执行)
    """
    logger.info("Starting subscription renewal check task")
    
    try:
        db = self.db
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        
        from datetime import timedelta
        # 查询7天内到期的订阅
        seven_days_later = now + timedelta(days=7)
        
        stmt = select(Subscription).where(
            Subscription.status == SubscriptionStatus.ACTIVE.value,
            Subscription.end_date > now,
            Subscription.end_date <= seven_days_later
        )
        result = db.execute(stmt)
        expiring_subscriptions = result.scalars().all()
        
        count = 0
        for subscription in expiring_subscriptions:
            try:
                # TODO: 发送邮件或推送通知提醒用户续费
                logger.info(
                    f"Subscription {subscription.id} for user {subscription.user_id} "
                    f"will expire on {subscription.end_date}"
                )
                count += 1
                
                # 这里可以调用邮件服务、短信服务或推送通知服务
                # await send_renewal_reminder_email(subscription)
                
            except Exception as e:
                logger.error(
                    f"Failed to send renewal reminder for subscription {subscription.id}: {e}"
                )
        
        logger.info(f"Subscription renewal check task completed. Reminded: {count}")
        
        return {
            "reminded_count": count
        }
        
    except Exception as e:
        logger.error(f"Subscription renewal check task failed: {e}", exc_info=True)
        raise
    finally:
        if hasattr(self, '_db') and self._db:
            self._db.close()
            self._db = None


@celery_app.task(base=DatabaseTask, bind=True, name="cleanup_expired_pending_subscriptions")
def cleanup_expired_pending_subscriptions(self):
    """
    定时任务：清理超过24小时未支付的 PENDING 订单
    建议每小时运行一次
    
    Crontab: 0 * * * *  (每小时执行)
    """
    logger.info("Starting cleanup expired pending subscriptions task")
    
    try:
        db = self.db
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        
        # 计算24小时前的时间
        from datetime import timedelta
        expired_time = now - timedelta(hours=24)
        
        # 查询超过24小时的 PENDING 订单
        stmt = select(Subscription).where(
            Subscription.status == SubscriptionStatus.PENDING.value,
            Subscription.created_at < expired_time
        )
        result = db.execute(stmt)
        expired_pending_subs = result.scalars().all()
        
        count = 0
        for subscription in expired_pending_subs:
            try:
                subscription.status = SubscriptionStatus.DELETED.value
                subscription.cancelled_at = now
                count += 1
                logger.info(f"Deleted expired pending subscription {subscription.id}")
            except Exception as e:
                logger.error(f"Failed to cancel pending subscription {subscription.id}: {e}")
        
        db.commit()
        
        logger.info(f"Cleanup expired pending subscriptions task completed. Cancelled: {count}")
        
        return {
            "cancelled_count": count
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Cleanup expired pending subscriptions task failed: {e}", exc_info=True)
        raise
    finally:
        if hasattr(self, '_db') and self._db:
            self._db.close()
            self._db = None

