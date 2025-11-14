from typing import Optional

from pydantic import BaseModel, EmailStr


# Shared properties
class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = True
    full_name: Optional[str] = None


# Properties required for creating user
class UserCreate(UserBase):
    email: EmailStr
    password: str


# Properties that can be updated when updating user
class UserUpdate(UserBase):
    password: Optional[str] = None