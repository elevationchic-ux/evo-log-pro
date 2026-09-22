"""
Tiers schemas for clients, suppliers, and partners
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime
from enum import Enum


class TiersType(str, Enum):
    """Enumeration for tiers types"""
    CLIENT = "client"
    FOURNISSEUR = "fournisseur"
    PARTENAIRE = "partenaire"


class TiersBase(BaseModel):
    """Base tiers schema"""
    code: str = Field(..., min_length=2, max_length=20)
    type: TiersType
    name: str = Field(..., min_length=2, max_length=100)
    legal_form: Optional[str] = None
    tax_id: Optional[str] = None
    contact_person: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: str = "Cameroun"
    is_active: bool = True
    credit_limit: int = 0
    balance: int = 0
    payment_terms: Optional[str] = None


class TiersCreate(TiersBase):
    """Schema for tiers creation"""
    pass


class TiersUpdate(BaseModel):
    """Schema for tiers update"""
    name: Optional[str] = None
    legal_form: Optional[str] = None
    tax_id: Optional[str] = None
    contact_person: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    is_active: Optional[bool] = None
    credit_limit: Optional[int] = None
    payment_terms: Optional[str] = None


class TiersResponse(TiersBase):
    """Schema for tiers response"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ClientCreate(TiersBase):
    """Schema for client creation"""
    type: TiersType = TiersType.CLIENT
    industry: Optional[str] = None
    rating: Optional[str] = None


class ClientResponse(TiersResponse):
    """Schema for client response"""
    industry: Optional[str] = None
    customer_since: Optional[datetime] = None
    rating: Optional[str] = None


class FournisseurCreate(TiersBase):
    """Schema for supplier creation"""
    type: TiersType = TiersType.FOURNISSEUR
    industry: Optional[str] = None
    rating: Optional[str] = None


class FournisseurResponse(TiersResponse):
    """Schema for supplier response"""
    industry: Optional[str] = None
    supplier_since: Optional[datetime] = None
    rating: Optional[str] = None
    approved: bool = True