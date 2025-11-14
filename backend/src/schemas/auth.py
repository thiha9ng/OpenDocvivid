from pydantic import BaseModel, EmailStr
from typing import Optional


class SyncUserRequest(BaseModel):
    """
    Request model for syncing user information after Google login
    """
    email: EmailStr
    google_id: str
    name: Optional[str] = None