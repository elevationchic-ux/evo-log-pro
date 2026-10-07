"""Schemas Pydantic pour admin-tenant (genere)."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date


class AdmtDomainConfigCreate(BaseModel):
    reference: str
    tenant: Optional[str] = None
    domaine: Optional[str] = None
    type: Optional[str] = None
    certificat_ssl: Optional[bool] = None
    statut: Optional[str] = None


class AdmtDomainConfigUpdate(BaseModel):
    reference: Optional[str] = None
    tenant: Optional[str] = None
    domaine: Optional[str] = None
    type: Optional[str] = None
    certificat_ssl: Optional[bool] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class AdmtDomainConfigOut(BaseModel):
    id: int
    company_id: int
    reference: str
    tenant: Optional[str] = None
    domaine: Optional[str] = None
    type: Optional[str] = None
    certificat_ssl: Optional[bool] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class AdmtDnsRecordCreate(BaseModel):
    reference: str
    nom_hote: Optional[str] = None
    type_enregistrement: Optional[str] = None
    valeur: Optional[str] = None
    ttl_secondes: Optional[int] = None
    statut: Optional[str] = None


class AdmtDnsRecordUpdate(BaseModel):
    reference: Optional[str] = None
    nom_hote: Optional[str] = None
    type_enregistrement: Optional[str] = None
    valeur: Optional[str] = None
    ttl_secondes: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class AdmtDnsRecordOut(BaseModel):
    id: int
    company_id: int
    reference: str
    nom_hote: Optional[str] = None
    type_enregistrement: Optional[str] = None
    valeur: Optional[str] = None
    ttl_secondes: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class AdmtDataResidencyCreate(BaseModel):
    reference: str
    tenant: Optional[str] = None
    region: Optional[str] = None
    hebergeur: Optional[str] = None
    certification_conforme: Optional[bool] = None
    statut: Optional[str] = None


class AdmtDataResidencyUpdate(BaseModel):
    reference: Optional[str] = None
    tenant: Optional[str] = None
    region: Optional[str] = None
    hebergeur: Optional[str] = None
    certification_conforme: Optional[bool] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class AdmtDataResidencyOut(BaseModel):
    id: int
    company_id: int
    reference: str
    tenant: Optional[str] = None
    region: Optional[str] = None
    hebergeur: Optional[str] = None
    certification_conforme: Optional[bool] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class AdmtFeatureEntitlementCreate(BaseModel):
    reference: str
    module: Optional[str] = None
    actif: Optional[bool] = None
    limite: Optional[int] = None
    date_expiration: Optional[date] = None
    statut: Optional[str] = None


class AdmtFeatureEntitlementUpdate(BaseModel):
    reference: Optional[str] = None
    module: Optional[str] = None
    actif: Optional[bool] = None
    limite: Optional[int] = None
    date_expiration: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class AdmtFeatureEntitlementOut(BaseModel):
    id: int
    company_id: int
    reference: str
    module: Optional[str] = None
    actif: Optional[bool] = None
    limite: Optional[int] = None
    date_expiration: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class AdmtUsageQuotaCreate(BaseModel):
    reference: str
    ressource: Optional[str] = None
    quota_autorise: Optional[int] = None
    consomme: Optional[int] = None
    periode: Optional[str] = None
    statut: Optional[str] = None


class AdmtUsageQuotaUpdate(BaseModel):
    reference: Optional[str] = None
    ressource: Optional[str] = None
    quota_autorise: Optional[int] = None
    consomme: Optional[int] = None
    periode: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class AdmtUsageQuotaOut(BaseModel):
    id: int
    company_id: int
    reference: str
    ressource: Optional[str] = None
    quota_autorise: Optional[int] = None
    consomme: Optional[int] = None
    periode: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class AdmtImpersonationLogCreate(BaseModel):
    reference: str
    admin: Optional[str] = None
    cible_tenant: Optional[str] = None
    motif: Optional[str] = None
    debut: Optional[datetime] = None
    fin: Optional[datetime] = None
    statut: Optional[str] = None


class AdmtImpersonationLogUpdate(BaseModel):
    reference: Optional[str] = None
    admin: Optional[str] = None
    cible_tenant: Optional[str] = None
    motif: Optional[str] = None
    debut: Optional[datetime] = None
    fin: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class AdmtImpersonationLogOut(BaseModel):
    id: int
    company_id: int
    reference: str
    admin: Optional[str] = None
    cible_tenant: Optional[str] = None
    motif: Optional[str] = None
    debut: Optional[datetime] = None
    fin: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class AdmtOnboardingStepCreate(BaseModel):
    reference: str
    tenant: Optional[str] = None
    etape: Optional[str] = None
    ordre: Optional[int] = None
    responsable: Optional[str] = None
    date_completion: Optional[date] = None
    statut: Optional[str] = None


class AdmtOnboardingStepUpdate(BaseModel):
    reference: Optional[str] = None
    tenant: Optional[str] = None
    etape: Optional[str] = None
    ordre: Optional[int] = None
    responsable: Optional[str] = None
    date_completion: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class AdmtOnboardingStepOut(BaseModel):
    id: int
    company_id: int
    reference: str
    tenant: Optional[str] = None
    etape: Optional[str] = None
    ordre: Optional[int] = None
    responsable: Optional[str] = None
    date_completion: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class AdmtWhiteLabelConfigCreate(BaseModel):
    reference: str
    tenant: Optional[str] = None
    nom_affiche: Optional[str] = None
    logo_url: Optional[str] = None
    couleur_principale: Optional[str] = None
    statut: Optional[str] = None


class AdmtWhiteLabelConfigUpdate(BaseModel):
    reference: Optional[str] = None
    tenant: Optional[str] = None
    nom_affiche: Optional[str] = None
    logo_url: Optional[str] = None
    couleur_principale: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class AdmtWhiteLabelConfigOut(BaseModel):
    id: int
    company_id: int
    reference: str
    tenant: Optional[str] = None
    nom_affiche: Optional[str] = None
    logo_url: Optional[str] = None
    couleur_principale: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class AdmtTenantBackupCreate(BaseModel):
    reference: str
    tenant: Optional[str] = None
    taille_octets: Optional[int] = None
    frequence: Optional[str] = None
    derniere_reussite: Optional[datetime] = None
    statut: Optional[str] = None


class AdmtTenantBackupUpdate(BaseModel):
    reference: Optional[str] = None
    tenant: Optional[str] = None
    taille_octets: Optional[int] = None
    frequence: Optional[str] = None
    derniere_reussite: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class AdmtTenantBackupOut(BaseModel):
    id: int
    company_id: int
    reference: str
    tenant: Optional[str] = None
    taille_octets: Optional[int] = None
    frequence: Optional[str] = None
    derniere_reussite: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class AdmtIntegrationWebhookCreate(BaseModel):
    reference: str
    tenant: Optional[str] = None
    url_cible: Optional[str] = None
    evenement: Optional[str] = None
    actif: Optional[bool] = None
    statut: Optional[str] = None


class AdmtIntegrationWebhookUpdate(BaseModel):
    reference: Optional[str] = None
    tenant: Optional[str] = None
    url_cible: Optional[str] = None
    evenement: Optional[str] = None
    actif: Optional[bool] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class AdmtIntegrationWebhookOut(BaseModel):
    id: int
    company_id: int
    reference: str
    tenant: Optional[str] = None
    url_cible: Optional[str] = None
    evenement: Optional[str] = None
    actif: Optional[bool] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}

