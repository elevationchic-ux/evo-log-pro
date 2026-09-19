"""Pydantic schemas for Tenant module - Multi-tenant SAAS"""
from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel


# Company schemas
class CompanyBase(BaseModel):
    code: str
    nom: str
    sigle: Optional[str] = None
    legal_form: str
    capital_social: Optional[str] = None
    tax_id: str
    rccm: Optional[str] = None
    agrement_douane: Optional[str] = None
    agrement_pad: Optional[str] = None
    agrement_pak: Optional[str] = None
    rib: Optional[str] = None
    email: str
    telephone: str
    ville: str = "Douala"
    pays: str = "Cameroun"
    adresse: Optional[str] = None
    website: Optional[str] = None


class CompanyCreate(CompanyBase):
    subscription_plan_id: int


class CompanyUpdate(BaseModel):
    nom: Optional[str] = None
    sigle: Optional[str] = None
    legal_form: Optional[str] = None
    capital_social: Optional[str] = None
    tax_id: Optional[str] = None
    rccm: Optional[str] = None
    agrement_douane: Optional[str] = None
    agrement_pad: Optional[str] = None
    agrement_pak: Optional[str] = None
    rib: Optional[str] = None
    email: Optional[str] = None
    telephone: Optional[str] = None
    website: Optional[str] = None
    adresse: Optional[str] = None
    logo_url: Optional[str] = None
    is_active: Optional[bool] = None
    max_users: Optional[int] = None
    max_storage_mb: Optional[int] = None
    max_camions: Optional[int] = None
    modules_actives: Optional[str] = None


class CompanyResponse(CompanyBase):
    id: int
    logo_url: Optional[str] = None
    is_active: bool
    is_verified: bool
    verification_date: Optional[datetime] = None
    suspension_reason: Optional[str] = None
    subscription_plan_id: Optional[int] = None
    subscription_start: Optional[date] = None
    subscription_end: Optional[date] = None
    max_users: int
    max_storage_mb: int
    max_camions: int = 20
    current_users: int
    current_storage_mb: int
    subdomain: Optional[str] = None
    custom_domain: Optional[str] = None
    primary_color: str
    secondary_color: str
    modules_actives: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Subscription Plan schemas
class SubscriptionPlanBase(BaseModel):
    code: str
    nom: str
    type_plan: str
    prix_mensuel: float
    prix_annuel: float
    max_users: int
    max_storage_mb: int


class SubscriptionPlanCreate(SubscriptionPlanBase):
    description: str = ""
    features: str = ""
    modules_inclus: str = ""
    trial_days: int = 14


class SubscriptionPlanUpdate(BaseModel):
    nom: Optional[str] = None
    description: Optional[str] = None
    prix_mensuel: Optional[float] = None
    prix_annuel: Optional[float] = None
    max_users: Optional[int] = None
    max_storage_mb: Optional[int] = None
    is_active: Optional[bool] = None


class SubscriptionPlanResponse(SubscriptionPlanBase):
    id: int
    description: Optional[str] = None
    features: Optional[str] = None
    modules_inclus: Optional[str] = None
    trial_days: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Subscription schemas
class SubscriptionBase(BaseModel):
    company_id: int
    plan_id: int
    start_date: date
    end_date: date
    amount: float


class SubscriptionCreate(SubscriptionBase):
    trial_end_date: Optional[date] = None
    payment_method: str = "card"
    auto_renew: bool = True


class SubscriptionUpdate(BaseModel):
    end_date: Optional[date] = None
    status: Optional[str] = None
    auto_renew: Optional[bool] = None


class SubscriptionResponse(SubscriptionBase):
    id: int
    trial_end_date: Optional[date] = None
    status: str
    currency: str
    payment_method: Optional[str] = None
    payment_reference: Optional[str] = None
    auto_renew: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Department schemas
class DepartmentBase(BaseModel):
    company_id: int
    code: str
    nom: str
    description: str


class DepartmentCreate(DepartmentBase):
    parent_id: int = None
    manager_id: int = None
    modules_allowed: str = ""


class DepartmentUpdate(BaseModel):
    nom: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[int] = None
    manager_id: Optional[int] = None
    modules_allowed: Optional[str] = None
    is_active: Optional[bool] = None


class DepartmentResponse(DepartmentBase):
    id: int
    parent_id: Optional[int] = None
    manager_id: Optional[int] = None
    modules_allowed: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# B2B Portal schemas
class B2BPortalBase(BaseModel):
    company_id: int
    primary_color: str
    secondary_color: str


class B2BPortalCreate(B2BPortalBase):
    subdomain: str = ""
    custom_domain: str = ""
    accent_color: str = "#F59E0B"
    background_color: str = "#FFFFFF"
    text_color: str = "#1F2937"
    enable_chat: bool = True
    enable_quotes: bool = True
    enable_tracking: bool = True
    enable_api: bool = False


class B2BPortalUpdate(BaseModel):
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None
    accent_color: Optional[str] = None
    background_color: Optional[str] = None
    text_color: Optional[str] = None
    logo_url: Optional[str] = None
    banner_url: Optional[str] = None
    favicon_url: Optional[str] = None
    custom_css: Optional[str] = None
    enable_chat: Optional[bool] = None
    enable_quotes: Optional[bool] = None
    enable_tracking: Optional[bool] = None
    enable_api: Optional[bool] = None
    is_active: Optional[bool] = None


class B2BPortalResponse(B2BPortalBase):
    id: int
    subdomain: Optional[str] = None
    custom_domain: Optional[str] = None
    accent_color: str
    background_color: str
    text_color: str
    logo_url: Optional[str] = None
    banner_url: Optional[str] = None
    favicon_url: Optional[str] = None
    custom_css: Optional[str] = None
    custom_js: Optional[str] = None
    enable_chat: bool
    enable_quotes: bool
    enable_tracking: bool
    enable_api: bool
    email_from_name: Optional[str] = None
    email_from_address: Optional[str] = None
    email_signature: Optional[str] = None
    is_active: bool
    published_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Rapports
class RapportCompaniesResponse(BaseModel):
    total_companies: int
    actives: int
    trial: int
    par_plan: dict


class RapportRevenusResponse(BaseModel):
    periode: str
    total_subscriptions: int
    revenu_total: float
    par_statut: dict
