"""
Pydantic models for authentication requests and responses.
"""
from pydantic import BaseModel, EmailStr
from typing import Optional

class GoogleProfile(BaseModel):
    """Represents the user profile information received from Google."""
    email: EmailStr
    name: str
    picture: str
    given_name: Optional[str] = None
    family_name: Optional[str] = None

class GoogleLoginRequest(BaseModel):
    """Represents the request body for the Google login callback."""
    id_token: str
    profile: GoogleProfile

class User(BaseModel):
    """Represents the authenticated user data retrieved from the JWT token."""
    id: str
    email: EmailStr
    username: Optional[str] = None
    is_admin: bool = False
    is_active: bool = True 


class GoogleOAuthLoginRequest(BaseModel):
    token: str  # Google OAuth access token or ID token

class AuthTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: Optional[int] = None
    user_email: EmailStr
