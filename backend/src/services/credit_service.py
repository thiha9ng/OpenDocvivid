"""
Credit management service
处理用户积分相关的业务逻辑
"""
import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc
from sqlalchemy.orm import Session

from src.models import (
    User, 
    CreditTransaction, 
    VideoGenerateTask,
    Subscription,
    RedeemCode,
    TransactionType,
    SubscriptionStatus,
    calculate_segment_credit
)
from src.utils.logger import get_logger
from src.utils.exceptions import (
    NotFoundException,
    BadRequestException,
    InternalServerException,
    InsufficientCreditException
)

logger = get_logger(__name__)


class CreditService:
    """积分服务"""
    
    # 创建任务所需的最低积分
    MIN_CREDIT_FOR_TASK = 30
    
    @staticmethod
    async def check_credit_sufficient(
        db: AsyncSession,
        user_id: uuid.UUID,
        required_credit: int = MIN_CREDIT_FOR_TASK
    ) -> bool:
        """
        检查用户积分是否充足
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            required_credit: 所需积分，默认为创建任务的最低积分
        
        Returns:
            积分是否充足
        """
        try:
            # 查询用户
            stmt = select(User).where(User.id == user_id)
            result = await db.execute(stmt)
            user = result.scalar_one_or_none()
            
            if not user:
                raise NotFoundException(detail="User not found")
            
            return user.credit_balance >= required_credit

        except Exception as e:
            logger.error(f"Failed to check credit for user {user_id}: {e}")
            raise InternalServerException(detail="Failed to check credit balance")
    
    @staticmethod
    async def get_user_credit_balance(
        db: AsyncSession,
        user_id: uuid.UUID
    ) -> int:
        """
        获取用户当前积分余额
        
        Args:
            db: 数据库会话
            user_id: 用户ID
        
        Returns:
            积分余额
        """
        try:
            stmt = select(User).where(User.id == user_id)
            result = await db.execute(stmt)
            user = result.scalar_one_or_none()
            
            if not user:
                raise NotFoundException(detail="User not found")
            
            return user.credit_balance

        except Exception as e:
            logger.error(f"Failed to get credit balance for user {user_id}: {e}")
            raise InternalServerException(detail="Failed to get credit balance")
    
    @staticmethod
    async def consume_credit(
        db: AsyncSession,
        user_id: uuid.UUID,
        amount: int,
        task_id: Optional[uuid.UUID] = None,
        description: Optional[str] = None
    ) -> CreditTransaction:
        """
        扣除用户积分
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            amount: 扣除数量（正数）
            task_id: 关联的任务ID
            description: 交易描述
        
        Returns:
            积分交易记录
        """
        try:
            # 查询用户
            stmt = select(User).where(User.id == user_id)
            result = await db.execute(stmt)
            user = result.scalar_one_or_none()
            
            if not user:
                raise NotFoundException(detail="User not found")
            
            # 检查积分是否充足
            if user.credit_balance < amount:
                raise InsufficientCreditException(
                    detail=f"Insufficient credit. Current balance: {user.credit_balance}, required: {amount}"
                )
            
            # 扣除积分
            user.credit_balance -= amount
            
            # 创建交易记录
            transaction = CreditTransaction(
                user_id=user_id,
                task_id=task_id,
                transaction_type=TransactionType.TASK_CONSUME.value,
                amount=-amount,  # 负数表示消耗
                balance_after=user.credit_balance,
                description=description or f"task consume {amount} credits"
            )
            
            db.add(transaction)
            await db.commit()
            await db.refresh(transaction)
            
            logger.info(f"User {user_id} consumed {amount} credits. New balance: {user.credit_balance}")
            
            return transaction
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to consume credit for user {user_id}: {e}")
            raise InternalServerException(detail="Failed to consume credit")
    
    @staticmethod
    async def grant_credit(
        db: AsyncSession,
        user_id: uuid.UUID,
        amount: int,
        transaction_type: TransactionType = TransactionType.ADMIN_ADJUST,
        subscription_id: Optional[uuid.UUID] = None,
        description: Optional[str] = None
    ) -> CreditTransaction:
        """
        赠送用户积分
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            amount: 赠送数量（正数）
            transaction_type: 交易类型
            subscription_id: 关联的订阅ID
            description: 交易描述
        
        Returns:
            积分交易记录
        """
        try:
            # 查询用户
            stmt = select(User).where(User.id == user_id)
            result = await db.execute(stmt)
            user = result.scalar_one_or_none()
            
            if not user:
                raise NotFoundException(detail="User not found")
            
            # 增加积分
            user.credit_balance += amount
            
            # 创建交易记录
            transaction = CreditTransaction(
                user_id=user_id,
                subscription_id=subscription_id,
                transaction_type=transaction_type.value,
                amount=amount,  # 正数表示获得
                balance_after=user.credit_balance,
                description=description or f"grant {amount} credits"
            )
            
            db.add(transaction)
            await db.commit()
            await db.refresh(transaction)
            
            logger.info(f"User {user_id} granted {amount} credits. New balance: {user.credit_balance}")
            
            return transaction
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to grant credit for user {user_id}: {e}")
            raise InternalServerException(detail="Failed to grant credit")
    
    @staticmethod
    async def refund_credit(
        db: AsyncSession,
        user_id: uuid.UUID,
        amount: int,
        task_id: Optional[uuid.UUID] = None,
        description: Optional[str] = None
    ) -> CreditTransaction:
        """
        退还用户积分
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            amount: 退还数量（正数）
            task_id: 关联的任务ID
            description: 交易描述
        
        Returns:
            积分交易记录
        """
        return await CreditService.grant_credit(
            db=db,
            user_id=user_id,
            amount=amount,
            transaction_type=TransactionType.REFUND,
            description=description or f"task refund {amount} credits"
        )
    
    @staticmethod
    async def get_credit_transactions(
        db: AsyncSession,
        user_id: uuid.UUID,
        limit: int = 50,
        offset: int = 0
    ) -> List[CreditTransaction]:
        """
        获取用户的积分流水记录
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            limit: 返回数量限制
            offset: 偏移量
        
        Returns:
            积分交易记录列表
        """
        try:
            stmt = (
                select(CreditTransaction)
                .where(CreditTransaction.user_id == user_id)
                .order_by(desc(CreditTransaction.created_at))
                .limit(limit)
                .offset(offset)
            )
            
            result = await db.execute(stmt)
            transactions = result.scalars().all()
            
            return list(transactions)
            
        except Exception as e:
            logger.error(f"Failed to get credit transactions for user {user_id}: {e}")
            raise InternalServerException(detail="Failed to get credit transactions")
    
    @staticmethod
    async def calculate_and_consume_task_credit(
        db: AsyncSession,
        user_id: uuid.UUID,
        task: VideoGenerateTask,
        segments_duration: List[int]
    ) -> Dict[str, Any]:
        """
        计算任务积分消耗并扣除
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            task: 视频生成任务
            segments_duration: segment时长列表（秒）
        
        Returns:
            包含消耗信息的字典
        """
        try:
            # 计算每个segment的积分
            segment_credits = [calculate_segment_credit(duration) for duration in segments_duration]
            total_credit = sum(segment_credits)
            
            # 检查积分是否充足
            if not await CreditService.check_credit_sufficient(db, user_id, total_credit):
                current_balance = await CreditService.get_user_credit_balance(db, user_id)
                raise InsufficientCreditException(
                    detail=f"Insufficient credit. Required: {total_credit}, current balance: {current_balance}"
                )
            
            # 扣除积分
            transaction = await CreditService.consume_credit(
                db=db,
                user_id=user_id,
                amount=total_credit,
                task_id=task.id,
                description=f"task {task.task_id} consume {total_credit} credits"
            )
            
            # 更新任务的积分消耗记录
            task.credit_cost = total_credit
            await db.commit()
            
            return {
                "total_credit": total_credit,
                "segment_credits": segment_credits,
                "transaction_id": str(transaction.id),
                "balance_after": transaction.balance_after
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate and consume credit for task {task.task_id}: {e}")
            raise InternalServerException(detail="Failed to calculate and consume credit")
    
    @staticmethod
    async def grant_monthly_subscription_credit(
        db: AsyncSession,
        subscription: Subscription
    ) -> Optional[CreditTransaction]:
        """
        赠送订阅的月度积分（清零上月积分后重新赠送）
        
        Args:
            db: 数据库会话
            subscription: 订阅对象
        
        Returns:
            积分交易记录，如果本月已赠送则返回None
        """
        try:
            now = datetime.now(timezone.utc).replace(tzinfo=None)
            
            # 检查是否已经赠送过本月的积分
            if subscription.last_credit_grant_date:
                last_grant = subscription.last_credit_grant_date
                if last_grant.year == now.year and last_grant.month == now.month:
                    logger.info(f"Subscription {subscription.id} already granted credits this month")
                    return None
            
            # 检查订阅是否激活
            if subscription.status != SubscriptionStatus.ACTIVE.value:
                logger.warning(f"Subscription {subscription.id} is not active, skipping credit grant")
                return None
            
            # 查询用户
            stmt = select(User).where(User.id == subscription.user_id)
            result = await db.execute(stmt)
            user = result.scalar_one_or_none()
            
            if not user:
                raise NotFoundException(detail="User not found")
            
            # 如果有上次赠送记录，清零上月赠送的积分
            if subscription.last_credit_grant_date:
                # 查询上次月度赠送的交易记录
                last_grant_stmt = (
                    select(CreditTransaction)
                    .where(
                        and_(
                            CreditTransaction.subscription_id == subscription.id,
                            CreditTransaction.transaction_type == TransactionType.MONTHLY_GRANT.value,
                            CreditTransaction.user_id == subscription.user_id
                        )
                    )
                    .order_by(desc(CreditTransaction.created_at))
                    .limit(1)
                )
                last_grant_result = await db.execute(last_grant_stmt)
                last_grant_transaction = last_grant_result.scalar_one_or_none()
                
                if last_grant_transaction and last_grant_transaction.amount > 0:
                    # 计算应该回收的积分（不能超过用户当前余额）
                    reclaim_amount = min(last_grant_transaction.amount, user.credit_balance)
                    
                    if reclaim_amount > 0:
                        # 扣除上月赠送的积分
                        user.credit_balance -= reclaim_amount
                        
                        # 创建回收记录
                        reclaim_transaction = CreditTransaction(
                            user_id=subscription.user_id,
                            subscription_id=subscription.id,
                            transaction_type=TransactionType.MONTHLY_RECLAIM.value,
                            amount=-reclaim_amount,  # 负数表示扣除
                            balance_after=user.credit_balance,
                            description=f"清零上月未用完的 {reclaim_amount} 积分"
                        )
                        db.add(reclaim_transaction)
                        
                        logger.info(f"Reclaimed {reclaim_amount} credits from user {subscription.user_id} for subscription {subscription.id}")
            
            # 赠送新的月度积分
            user.credit_balance += subscription.monthly_credits
            
            # 创建赠送记录
            grant_transaction = CreditTransaction(
                user_id=subscription.user_id,
                subscription_id=subscription.id,
                transaction_type=TransactionType.MONTHLY_GRANT.value,
                amount=subscription.monthly_credits,  # 正数表示获得
                balance_after=user.credit_balance,
                description=f"monthly grant {subscription.monthly_credits} credits"
            )
            db.add(grant_transaction)
            
            # 更新最后赠送时间
            subscription.last_credit_grant_date = now
            await db.commit()
            await db.refresh(grant_transaction)
            
            logger.info(f"Granted {subscription.monthly_credits} credits to user {subscription.user_id} for subscription {subscription.id}")
            
            return grant_transaction
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to grant monthly credit for subscription {subscription.id}: {e}")
            raise InternalServerException(detail="Failed to grant monthly credit")
    
    @staticmethod
    async def redeem_code(
        db: AsyncSession,
        user_id: uuid.UUID,
        code: str
    ) -> CreditTransaction:
        """
        兑换码兑换积分
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            code: 兑换码
        
        Returns:
            积分交易记录
        """
        try:
            # 查询兑换码
            stmt = select(RedeemCode).where(RedeemCode.code == code)
            result = await db.execute(stmt)
            redeem_code = result.scalar_one_or_none()
            
            if not redeem_code:
                raise BadRequestException(detail="Code not found")
            
            # 检查兑换码是否已使用
            if redeem_code.is_used:
                raise BadRequestException(detail="Code already used")
            
            # 只对1000积分的兑换码进行限制：每个用户只能使用一次1000积分的兑换码
            # 其他金额的兑换码（如订阅会员兑换码）不受此限制
            credit_amount = redeem_code.credit_amount
            if credit_amount == 1000:
                existing_redeem_stmt = (
                    select(CreditTransaction)
                    .where(
                        and_(
                            CreditTransaction.user_id == user_id,
                            CreditTransaction.transaction_type == TransactionType.REDEEM_CODE.value,
                            CreditTransaction.amount == 1000  # 只检查1000积分的兑换记录
                        )
                    )
                    .limit(1)
                )
                existing_redeem_result = await db.execute(existing_redeem_stmt)
                existing_redeem = existing_redeem_result.scalar_one_or_none()
                
                if existing_redeem:
                    raise BadRequestException(detail="You have already used a 1000 credit redeem code. Each user can only redeem 1000 credits once.")
            
            # 查询用户
            user_stmt = select(User).where(User.id == user_id)
            user_result = await db.execute(user_stmt)
            user = user_result.scalar_one_or_none()
            
            if not user:
                raise NotFoundException(detail="User not found")
            
            # 增加积分
            user.credit_balance += credit_amount
            
            # 创建交易记录
            transaction = CreditTransaction(
                user_id=user_id,
                transaction_type=TransactionType.REDEEM_CODE.value,
                amount=credit_amount,  # 正数表示获得
                balance_after=user.credit_balance,
                description=f"Redeem code {code} for {credit_amount} credits"
            )
            
            # 标记兑换码为已使用
            redeem_code.is_used = True
            redeem_code.used_by = user_id
            redeem_code.used_at = datetime.now(timezone.utc).replace(tzinfo=None)
            
            db.add(transaction)
            await db.commit()
            await db.refresh(transaction)
            
            logger.info(f"User {user_id} redeemed code {code} for {credit_amount} credits. New balance: {user.credit_balance}")
            
            return transaction
            
        except BadRequestException:
            raise
        except NotFoundException:
            raise
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to redeem code {code} for user {user_id}: {e}")
            raise InternalServerException(detail="Failed to redeem code")


# 同步版本的服务（用于Celery任务）
class SyncCreditService:
    """同步积分服务（用于Celery）"""
    
    @staticmethod
    def consume_credit_sync(
        db: Session,
        user_id: uuid.UUID,
        amount: int,
        task_id: Optional[uuid.UUID] = None,
        description: Optional[str] = None
    ) -> CreditTransaction:
        """
        同步扣除用户积分
        """
        try:
            # 查询用户
            user = db.query(User).filter(User.id == user_id).first()
            
            if not user:
                raise NotFoundException(detail="User not found")
            
            # 检查积分是否充足
            if user.credit_balance < amount:
                raise InsufficientCreditException(
                    detail=f"Insufficient credit. Current balance: {user.credit_balance}, required: {amount}"
                )
            
            # 扣除积分
            user.credit_balance -= amount
            
            # 创建交易记录
            transaction = CreditTransaction(
                user_id=user_id,
                task_id=task_id,
                transaction_type=TransactionType.TASK_CONSUME.value,
                amount=-amount,
                balance_after=user.credit_balance,
                description=description or f"任务消耗 {amount} 积分"
            )
            
            db.add(transaction)
            db.commit()
            db.refresh(transaction)
            
            logger.info(f"User {user_id} consumed {amount} credits. New balance: {user.credit_balance}")
            
            return transaction
        
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to consume credit for user {user_id}: {e}")
            raise InternalServerException(detail="Failed to consume credit")
    
    @staticmethod
    def refund_credit_sync(
        db: Session,
        user_id: uuid.UUID,
        amount: int,
        task_id: Optional[uuid.UUID] = None,
        description: Optional[str] = None
    ) -> CreditTransaction:
        """
        同步退还用户积分
        """
        try:
            # 查询用户
            user = db.query(User).filter(User.id == user_id).first()
            
            if not user:
                raise NotFoundException(detail="User not found")
            
            # 增加积分
            user.credit_balance += amount
            
            # 创建交易记录
            transaction = CreditTransaction(
                user_id=user_id,
                task_id=task_id,
                transaction_type=TransactionType.REFUND.value,
                amount=amount,
                balance_after=user.credit_balance,
                description=description or f"任务失败退还 {amount} 积分"
            )
            
            db.add(transaction)
            db.commit()
            db.refresh(transaction)
            
            logger.info(f"User {user_id} refunded {amount} credits. New balance: {user.credit_balance}")
            
            return transaction

        except Exception as e:
            db.rollback()
            logger.error(f"Failed to refund credit for user {user_id}: {e}")
            raise InternalServerException(detail="Failed to refund credit")
    
    @staticmethod
    def grant_credit_sync(
        db: Session,
        user_id: uuid.UUID,
        amount: int,
        transaction_type: TransactionType = TransactionType.ADMIN_ADJUST,
        subscription_id: Optional[uuid.UUID] = None,
        description: Optional[str] = None
    ) -> CreditTransaction:
        """
        同步赠送用户积分
        """
        try:
            # 查询用户
            user = db.query(User).filter(User.id == user_id).first()
            
            if not user:
                raise NotFoundException(detail="User not found")
            
            # 增加积分
            user.credit_balance += amount
            
            # 创建交易记录
            transaction = CreditTransaction(
                user_id=user_id,
                subscription_id=subscription_id,
                transaction_type=transaction_type.value,
                amount=amount,
                balance_after=user.credit_balance,
                description=description or f"赠送 {amount} 积分"
            )
            
            db.add(transaction)
            db.commit()
            db.refresh(transaction)
            
            logger.info(f"User {user_id} granted {amount} credits. New balance: {user.credit_balance}")
            
            return transaction
        
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to grant credit for user {user_id}: {e}")
            raise InternalServerException(detail="Failed to grant credit")
    
    @staticmethod
    def grant_monthly_subscription_credit_sync(
        db: Session,
        subscription: Subscription
    ) -> Optional[CreditTransaction]:
        """
        同步赠送订阅的月度积分（清零上月积分后重新赠送）
        
        Args:
            db: 数据库会话
            subscription: 订阅对象
        
        Returns:
            积分交易记录，如果本月已赠送则返回None
        """
        try:
            now = datetime.now(timezone.utc).replace(tzinfo=None)
            
            # 检查是否已经赠送过本月的积分
            if subscription.last_credit_grant_date:
                last_grant = subscription.last_credit_grant_date
                if last_grant.year == now.year and last_grant.month == now.month:
                    logger.info(f"Subscription {subscription.id} already granted credits this month")
                    return None
            
            # 检查订阅是否激活
            if subscription.status != SubscriptionStatus.ACTIVE.value:
                logger.warning(f"Subscription {subscription.id} is not active, skipping credit grant")
                return None
            
            # 查询用户
            user = db.query(User).filter(User.id == subscription.user_id).first()
            
            if not user:
                raise NotFoundException(detail="User not found")
            
            # 如果有上次赠送记录，清零上月赠送的积分
            if subscription.last_credit_grant_date:
                # 查询上次月度赠送的交易记录
                last_grant_transaction = (
                    db.query(CreditTransaction)
                    .filter(
                        CreditTransaction.subscription_id == subscription.id,
                        CreditTransaction.transaction_type == TransactionType.MONTHLY_GRANT.value,
                        CreditTransaction.user_id == subscription.user_id
                    )
                    .order_by(CreditTransaction.created_at.desc())
                    .first()
                )
                
                if last_grant_transaction and last_grant_transaction.amount > 0:
                    # 计算应该回收的积分（不能超过用户当前余额）
                    reclaim_amount = min(last_grant_transaction.amount, user.credit_balance)
                    
                    if reclaim_amount > 0:
                        # 扣除上月赠送的积分
                        user.credit_balance -= reclaim_amount
                        
                        # 创建回收记录
                        reclaim_transaction = CreditTransaction(
                            user_id=subscription.user_id,
                            subscription_id=subscription.id,
                            transaction_type=TransactionType.MONTHLY_RECLAIM.value,
                            amount=-reclaim_amount,  # 负数表示扣除
                            balance_after=user.credit_balance,
                            description=f"清零上月未用完的 {reclaim_amount} 积分"
                        )
                        db.add(reclaim_transaction)
                        
                        logger.info(f"Reclaimed {reclaim_amount} credits from user {subscription.user_id} for subscription {subscription.id}")
            
            # 赠送新的月度积分
            user.credit_balance += subscription.monthly_credits
            
            # 创建赠送记录
            grant_transaction = CreditTransaction(
                user_id=subscription.user_id,
                subscription_id=subscription.id,
                transaction_type=TransactionType.MONTHLY_GRANT.value,
                amount=subscription.monthly_credits,  # 正数表示获得
                balance_after=user.credit_balance,
                description=f"monthly grant {subscription.monthly_credits} credits"
            )
            db.add(grant_transaction)
            
            # 更新最后赠送时间
            subscription.last_credit_grant_date = now
            db.commit()
            db.refresh(grant_transaction)
            
            logger.info(f"Granted {subscription.monthly_credits} credits to user {subscription.user_id} for subscription {subscription.id}")
            
            return grant_transaction
        
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to grant monthly credit for subscription {subscription.id}: {e}")
            raise InternalServerException(detail="Failed to grant monthly credit")

