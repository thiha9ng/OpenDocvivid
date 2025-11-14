from typing import Any
from fastapi import APIRouter, HTTPException, Depends
from src.services.user_service import UserService
from src.utils.dependencies import get_user_service
from src.types.auth import AuthTokenResponse
from src.types.auth import GoogleLoginRequest
from google.auth.transport import requests
import os
from datetime import datetime, timedelta, timezone
import time
from src.utils.logger import get_logger
from src.configs.config import settings
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.base import get_db
from src import schemas
from ..utils import security
from ..utils.exceptions import UnauthorizedException

logger = get_logger(__name__)

_request = requests.Request()
# Router
router = APIRouter()
user_service = UserService()


@router.post("/sync-user")
async def sync_user(
    *,
    db: AsyncSession = Depends(get_db),
    user_data: schemas.SyncUserRequest
) -> Any:
    """
    Sync user information after Google login, create new user if not exists, return access token
    """
    user = await user_service.get_or_create_google_user(
        db,
        email=user_data.email,
        google_id=user_data.google_id,
        name=user_data.name
    )

    if not user.is_active:
        raise UnauthorizedException(detail="User is not active")

    return {
        "access_token": security.create_access_token(
            user.id, expires_delta=timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        ),
        "user_id": str(user.id),
        "name": user.full_name,
        "email": user.email,
    }

if __name__ == "__main__":
    print(security.create_access_token("88d9b276-774b-4bbc-ab18-7927c30d169e"))