from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, field_validator


class UserBase(BaseModel):
    """Base schema with common fields"""
    username: str = Field(..., min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_\s]+$")
    email: EmailStr


class UserCreate(UserBase):
    """Schema for creating a user (includes password)"""
    password: str = Field(..., min_length=8, max_length=100)

    @field_validator('password')
    def validate_password(cls, v):
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(char.islower() for char in v):
            raise ValueError('Password must contain at least one lowercase letter')
        return v
    

class UserCreateOAuth(UserBase):
    """Schema for creating a user with OAuth"""
    oauth_id: str
    oauth_provider: str 


class UserUpdate(BaseModel):
    """Schema for updating a user (all fields optional)"""
    username: Optional[str] = Field(
        default=None,
        min_length=3,
        max_length=50,
        pattern=r"^[a-zA-Z0-9_\s]+$"
    )
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(
        default=None,
        min_length=8,
        max_length=100,
        description="New password (will be hashed)"
    )

    @field_validator('password')
    def validate_password_if_present(cls, v):
        if v is None:
            return v
        return UserCreate.validate_password(v)


class UserInDBBase(UserBase):
    """Base schema for stored user (includes DB fields)"""
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class User(UserInDBBase):
    """Schema for returning a user (excludes sensitive data)"""
    pass


class UserInDB(UserInDBBase):
    """Schema for user stored in DB (includes hashed password, oauth, and oauth provider)"""
    oauth_id: Optional[str]
    oauth_provider: Optional[str]
    hashed_password: Optional[str]


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str
    