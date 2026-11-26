"""
User and authentication schemas
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


class UserBase(BaseModel):
    """Base user schema"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: Optional[str] = None
    phone: Optional[str] = None
    agency_id: Optional[int] = None


class UserCreate(UserBase):
    """Schema for user creation"""
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    """Schema for user update"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None
    agency_id: Optional[int] = None
    must_change_password: Optional[bool] = None


class UserResponse(UserBase):
    """Schema for user response"""
    id: int
    is_active: bool
    is_superuser: bool
    must_change_password: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class RoleBase(BaseModel):
    """Base role schema"""
    name: str = Field(..., min_length=2, max_length=50)
    description: Optional[str] = None
    modules_allowed: Optional[str] = None
    is_active: bool = True


class RoleCreate(RoleBase):
    """Schema for role creation"""
    pass


class RoleResponse(RoleBase):
    """Schema for role response"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class PermissionBase(BaseModel):
    """Base permission schema"""
    name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = None
    resource: Optional[str] = None
    action: Optional[str] = None


class PermissionCreate(PermissionBase):
    """Schema for permission creation"""
    pass


class PermissionResponse(PermissionBase):
    """Schema for permission response"""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """Schema for JWT token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user_id: Optional[int] = None
    username: Optional[str] = None
    email: Optional[str] = None
    roles: Optional[List[str]] = None
    company_id: Optional[int] = None
    company_name: Optional[str] = None
    is_superuser: Optional[bool] = False
    modules_allowed: Optional[List[str]] = None


class TokenData(BaseModel):
    """Schema for token data"""
    user_id: Optional[str] = None
    username: Optional[str] = None