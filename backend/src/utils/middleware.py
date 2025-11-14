"""
Authentication middleware for JWT token validation
"""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from src.utils.security import decode_access_token
from src.utils.logger import get_logger
from src.models.base import async_session
from src.models.user_models import User
from sqlalchemy import select
from uuid import UUID

logger = get_logger(__name__)


class JWTAuthMiddleware(BaseHTTPMiddleware):
    """
    JWT authentication middleware
    Extract token from Authorization header, validate and store user info in request.state
    """
    
    # Paths that don't require authentication (exact match or prefix match)
    EXCLUDED_PATHS = [
        "/docs",
        "/openapi.json",
        "/redoc",
        "/api/v1/auth/login",
        "/api/v1/auth/register",
        "/api/v1/auth/google",
        "/api/v1/webhook/",  # Webhook paths typically don't need JWT authentication
    ]
    
    # Exact match paths (no prefix matching)
    EXACT_MATCH_PATHS = [
        "/",
    ]
    
    async def dispatch(self, request: Request, call_next):
        """
        Process each request
        """
        path = request.url.path
        logger.info(f"Processing request: {request.method} {path}")
        
        # 检查是否是排除的路径
        if self._is_excluded_path(path):
            logger.info(f"Path excluded from auth: {path}")
            return await call_next(request)
        
        # 获取Authorization header
        authorization = request.headers.get("Authorization")
        logger.info(f"Authorization header present: {authorization is not None}")
        
        if authorization:
            try:
                # 验证格式: "Bearer <token>"
                parts = authorization.split()
                if len(parts) == 2 and parts[0].lower() == "bearer":
                    token = parts[1]
                    logger.info(f"Decoding token: {token[:20]}...")
                    user_id = decode_access_token(token)
                    logger.info(f"Decoded user_id: {user_id}")
                    
                    if user_id:
                        # 从数据库获取用户信息
                        async with async_session() as db:
                            try:
                                user = await self._get_user_from_db(db, user_id)
                                logger.info(f"User from DB: {user is not None}")
                                if user:
                                    # 将用户信息存储到request.state
                                    request.state.user = {
                                        "id": str(user.id),
                                        "email": user.email,
                                        "username": user.username,
                                        "is_admin": user.is_admin,
                                        "is_active": user.is_active,
                                    }
                                    logger.info(f"User authenticated: {user.email}")
                                else:
                                    logger.warning(f"User not found for ID: {user_id}")
                            except Exception as db_error:
                                logger.error(f"Database error: {str(db_error)}", exc_info=True)
                    else:
                        logger.warning("Invalid or expired token")
                else:
                    logger.warning(f"Invalid authorization header format: {len(parts)} parts")
            except Exception as e:
                logger.error(f"Error processing authentication: {str(e)}", exc_info=True)
        else:
            logger.warning(f"No authorization header for path: {path}")
        
        # 继续处理请求
        response = await call_next(request)
        return response
    
    def _is_excluded_path(self, path: str) -> bool:
        """
        Check if path is in exclusion list
        """
        # Check exact match
        if path in self.EXACT_MATCH_PATHS:
            return True
        
        # Check prefix match
        for excluded in self.EXCLUDED_PATHS:
            if path.startswith(excluded):
                return True
        
        return False
    
    async def _get_user_from_db(self, db, user_id: str):
        """
        Get user information from database
        """
        result = await db.execute(
            select(User).where(User.id == UUID(user_id))
        )
        return result.scalar_one_or_none()

