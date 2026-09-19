"""
Agency schemas
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class AgencyBase(BaseModel):
    """Base agency schema"""
    code: str = Field(..., min_length=2, max_length=20)
    name: str = Field(..., min_length=2, max_length=100)
    address: Optional[str] = None
    city: Optional[str] = None
    country: str = "Cameroun"
    phone: Optional[str] = None
    email: Optional[str] = None
    is_active: bool = True
    is_headquarters: bool = False


class AgencyCreate(AgencyBase):
    """Schema for agency creation"""
    pass


class AgencyUpdate(BaseModel):
    """Schema for agency update"""
    name: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    is_active: Optional[bool] = None
    is_headquarters: Optional[bool] = None


class AgencyResponse(AgencyBase):
    """Schema for agency response"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True