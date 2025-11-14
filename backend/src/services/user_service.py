"""
混合存储服务
结合 PostgreSQL 持久化存储和 Redis 缓存
提供高性能的数据访问和持久化保证
"""

import json
import logging
from typing import Dict, Optional, Any, Union
import uuid
from src import schemas
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.clients.redis import redis_client
from src.libs.postgresql_transactional import transactional
from src.models.user_models import User
from src.utils.security import get_password_hash


class UserService:
    """
    混合存储服务
    核心功能：
    1. PostgreSQL 作为主存储，保证数据持久化
    2. Redis 作为缓存层，提供高性能访问
    3. 自动同步机制，确保数据一致性
    4. 智能缓存策略，优化性能
    """

    def __init__(self):
        self.redis_client = redis_client
        self.logger = logging.getLogger("UserService")

        # 缓存配置
        self.cache_ttl = 3600  # 1小时
        self.cache_prefix = "docvivid"

    async def _get_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        """
        Get user by email
        """
        result = await db.execute(select(User).filter(User.email == email))
        return result.scalar_one_or_none()

    async def _get_by_google_id(self, db: AsyncSession, google_id: str) -> Optional[User]:
        """
        Get user by Google ID
        """
        result = await db.execute(select(User).filter(User.google_open_id == google_id))
        return result.scalar_one_or_none()

    @transactional()
    async def _update_user(
        self, db: AsyncSession, *, db_obj: User, obj_in: Union[schemas.UserUpdate, Dict[str, Any]]
    ) -> User:
        """
        Update user
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        if update_data.get("password"):
            hashed_password = get_password_hash(update_data["password"])
            update_data["password"] = hashed_password
        for field in update_data:
            setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        return db_obj

    @transactional()
    async def get_or_create_google_user(self, db: AsyncSession, email: str, google_id: str, name: Optional[str] = None) -> User:
        """
        Get user by Google ID, create new user if not exists
        """
        # First try to find by Google ID
        user = await self._get_by_google_id(db, google_id)
        if user:
            # Ensure user information is up to date
            update_data = {}
            if name and user.full_name != name:
                update_data["full_name"] = name
            if update_data:
                user = await self._update_user(db, db_obj=user, obj_in=update_data)
            return user

        # Then try to find by email
        user = await self._get_by_email(db, email=email)
        if user:
            # Update user's Google ID and name
            update_data = {"google_id": google_id}
            if name and user.full_name != name:
                update_data["full_name"] = name
            user = await self._update_user(db, db_obj=user, obj_in=update_data)
            return user

        # If user doesn't exist, create a new one
        # Generate random password for Google login user
        random_password = uuid.uuid4().hex
        new_user = User(
            email=email,
            google_open_id=google_id,
            password=get_password_hash(random_password),
            full_name=name or "",
            is_active=True
        )
        db.add(new_user)
        await db.flush()  # Flush to generate user.id before returning
        return new_user
