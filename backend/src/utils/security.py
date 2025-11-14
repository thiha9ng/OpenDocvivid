from datetime import datetime, timedelta, timezone
from typing import Any, Union, Optional

from jose import jwt, JWTError
from passlib.context import CryptContext

from src.configs.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(
    subject: Union[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create JWT access token
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify password
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Get password hash
    bcrypt has a 72-byte limit, so we truncate the password
    """
    # Truncate password to 72 bytes to avoid bcrypt limitation
    password_bytes = password.encode('utf-8')[:72]
    return pwd_context.hash(password_bytes.decode('utf-8', errors='ignore'))


def decode_access_token(token: str) -> Optional[str]:
    """
    Decode JWT access token and return user ID
    
    Args:
        token: JWT token string
        
    Returns:
        User ID (string), return None if token is invalid
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id: str = payload.get("sub")
        # Check if user_id is None or string "None"
        if user_id is None or user_id == "None" or not user_id.strip():
            return None
        return user_id
    except JWTError:
        return None


def get_user_id_from_token(token: str) -> Optional[str]:
    """
    Get user ID from JWT token (convenience function)
    
    Args:
        token: JWT token string
        
    Returns:
        User ID (string), return None if token is invalid
    """
    return decode_access_token(token) 