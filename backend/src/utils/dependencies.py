"""
Dependency injection functions for FastAPI
"""
from fastapi import HTTPException, Request, Header
from typing import Optional
from src.services.user_service import UserService
from google.auth.transport import requests
from src.types.auth import User
from src.utils.security import decode_access_token

google_auth_request = requests.Request()



user_service: UserService = None



def get_google_auth_request() -> requests.Request:
    """Returns a cached request object for Google Auth."""
    return google_auth_request



async def get_user_service() -> UserService:
    return user_service


async def get_current_user(request: Request) -> User:
    """
    Dependency to get the current user from the request state.
    The JWTAuthMiddleware must be applied to the endpoints using this dependency.
    """
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated or user information not found in token",
        )

    return User(**user)


async def get_current_user_id(authorization: Optional[str] = Header(None)) -> str:
    """
    Extract and validate token from Authorization header, return user ID
    
    Args:
        authorization: Authorization header (format: "Bearer <token>")
        
    Returns:
        User ID string
        
    Raises:
        HTTPException: If token is invalid or missing
    """
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authorization header missing"
        )
    
    # 验证格式: "Bearer <token>"
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization header format. Expected: Bearer <token>"
        )
    
    token = parts[1]
    user_id = decode_access_token(token)
    
    # Check if user_id is valid (not None, empty string, or string "None")
    if not user_id or user_id == "None":
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )
    
    return user_id 