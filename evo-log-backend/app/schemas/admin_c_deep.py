"""Schemas Pydantic pour admin-saas (genere)."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date


class AdmCSubscriptionPlanCreate(BaseModel):
    reference: str
    nom: Optional[str] = None
    prix_mensuel: Optional[float] = None
    nb_utilisateurs: Optional[int] = None
    nb_modules: Optional[int] = None
    periode: Optional[str] = None
    statut: Optional[str] = None


class AdmCSubscriptionPlanUpdate(BaseModel):
    reference: Optional[str] = None
    nom: Optional[str] = None
    prix_mensuel: Optional[float] = None
    nb_utilisateurs: Optional[int] = None
    nb_modules: Optional[int] = None
    periode: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class AdmCSubscriptionPlanOut(BaseModel):
    id: int
    company_id: int
    reference: str
    nom: Optional[str] = None
    prix_mensuel: Optional[float] = None
    nb_utilisateurs: Optional[int] = None
    nb_modules: Optional[int] = None
    periode: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class AdmCTenantInviteCreate(BaseModel):
    reference: str
    email: Optional[str] = None
    tenant: Optional[str] = None
    role_propose: Optional[str] = None
    invite_par: Optional[str] = None
    date_expiration: Optional[datetime] = None
    statut: Optional[str] = None


class AdmCTenantInviteUpdate(BaseModel):
    reference: Optional[str] = None
    email: Optional[str] = None
    tenant: Optional[str] = None
    role_propose: Optional[str] = None
    invite_par: Optional[str] = None
    date_expiration: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class AdmCTenantInviteOut(BaseModel):
    id: int
    company_id: int
    reference: str
    email: Optional[str] = None
    tenant: Optional[str] = None
    role_propose: Optional[str] = None
    invite_par: Optional[str] = None
    date_expiration: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class AdmCApiTokenCreate(BaseModel):
    reference: str
    nom: Optional[str] = None
    tenant: Optional[str] = None
    portee: Optional[str] = None
    cree_le: Optional[datetime] = None
    expire_le: Optional[datetime] = None
    derniere_utilisation: Optional[datetime] = None
    statut: Optional[str] = None


class AdmCApiTokenUpdate(BaseModel):
    reference: Optional[str] = None
    nom: Optional[str] = None
    tenant: Optional[str] = None
    portee: Optional[str] = None
    cree_le: Optional[datetime] = None
    expire_le: Optional[datetime] = None
    derniere_utilisation: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class AdmCApiTokenOut(BaseModel):
    id: int
    company_id: int
    reference: str
    nom: Optional[str] = None
    tenant: Optional[str] = None
    portee: Optional[str] = None
    cree_le: Optional[datetime] = None
    expire_le: Optional[datetime] = None
    derniere_utilisation: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class AdmCBillingInvoiceCreate(BaseModel):
    reference: str
    tenant: Optional[str] = None
    periode_facturee: Optional[str] = None
    montant_ht: Optional[float] = None
    tva: Optional[float] = None
    montant_ttc: Optional[float] = None
    date_echeance: Optional[date] = None
    statut: Optional[str] = None


class AdmCBillingInvoiceUpdate(BaseModel):
    reference: Optional[str] = None
    tenant: Optional[str] = None
    periode_facturee: Optional[str] = None
    montant_ht: Optional[float] = None
    tva: Optional[float] = None
    montant_ttc: Optional[float] = None
    date_echeance: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class AdmCBillingInvoiceOut(BaseModel):
    id: int
    company_id: int
    reference: str
    tenant: Optional[str] = None
    periode_facturee: Optional[str] = None
    montant_ht: Optional[float] = None
    tva: Optional[float] = None
    montant_ttc: Optional[float] = None
    date_echeance: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class AdmCUsageMeteringCreate(BaseModel):
    reference: str
    tenant: Optional[str] = None
    ressource: Optional[str] = None
    unite: Optional[str] = None
    quantite_consommee: Optional[float] = None
    periode: Optional[str] = None
    date_releve: Optional[datetime] = None
    statut: Optional[str] = None


class AdmCUsageMeteringUpdate(BaseModel):
    reference: Optional[str] = None
    tenant: Optional[str] = None
    ressource: Optional[str] = None
    unite: Optional[str] = None
    quantite_consommee: Optional[float] = None
    periode: Optional[str] = None
    date_releve: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class AdmCUsageMeteringOut(BaseModel):
    id: int
    company_id: int
    reference: str
    tenant: Optional[str] = None
    ressource: Optional[str] = None
    unite: Optional[str] = None
    quantite_consommee: Optional[float] = None
    periode: Optional[str] = None
    date_releve: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}

