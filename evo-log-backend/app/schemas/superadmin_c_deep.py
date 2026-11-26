"""Schemas Pydantic pour superadmin-cadc (genere)."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date


class SaCAuditLogReviewCreate(BaseModel):
    reference: str
    perimetre: Optional[str] = None
    date_debut: Optional[datetime] = None
    date_fin: Optional[datetime] = None
    evenements_examines: Optional[int] = None
    reviewer: Optional[str] = None
    verdict: Optional[str] = None
    statut: Optional[str] = None


class SaCAuditLogReviewUpdate(BaseModel):
    reference: Optional[str] = None
    perimetre: Optional[str] = None
    date_debut: Optional[datetime] = None
    date_fin: Optional[datetime] = None
    evenements_examines: Optional[int] = None
    reviewer: Optional[str] = None
    verdict: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class SaCAuditLogReviewOut(BaseModel):
    id: int
    company_id: int
    reference: str
    perimetre: Optional[str] = None
    date_debut: Optional[datetime] = None
    date_fin: Optional[datetime] = None
    evenements_examines: Optional[int] = None
    reviewer: Optional[str] = None
    verdict: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class SaCSystemParameterCreate(BaseModel):
    reference: str
    valeur: Optional[str] = None
    categorie: Optional[str] = None
    portee: Optional[str] = None
    modifie_par: Optional[str] = None
    date_modification: Optional[datetime] = None
    statut: Optional[str] = None


class SaCSystemParameterUpdate(BaseModel):
    reference: Optional[str] = None
    valeur: Optional[str] = None
    categorie: Optional[str] = None
    portee: Optional[str] = None
    modifie_par: Optional[str] = None
    date_modification: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class SaCSystemParameterOut(BaseModel):
    id: int
    company_id: int
    reference: str
    valeur: Optional[str] = None
    categorie: Optional[str] = None
    portee: Optional[str] = None
    modifie_par: Optional[str] = None
    date_modification: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class SaCPlatformAlertCreate(BaseModel):
    reference: str
    titre: Optional[str] = None
    source: Optional[str] = None
    severite: Optional[str] = None
    date_detection: Optional[datetime] = None
    acquitte_par: Optional[str] = None
    statut: Optional[str] = None


class SaCPlatformAlertUpdate(BaseModel):
    reference: Optional[str] = None
    titre: Optional[str] = None
    source: Optional[str] = None
    severite: Optional[str] = None
    date_detection: Optional[datetime] = None
    acquitte_par: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class SaCPlatformAlertOut(BaseModel):
    id: int
    company_id: int
    reference: str
    titre: Optional[str] = None
    source: Optional[str] = None
    severite: Optional[str] = None
    date_detection: Optional[datetime] = None
    acquitte_par: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class SaCMigrationRunCreate(BaseModel):
    reference: str
    revision: Optional[str] = None
    environnement: Optional[str] = None
    lance_par: Optional[str] = None
    date_debut: Optional[datetime] = None
    duree_sec: Optional[int] = None
    statut: Optional[str] = None


class SaCMigrationRunUpdate(BaseModel):
    reference: Optional[str] = None
    revision: Optional[str] = None
    environnement: Optional[str] = None
    lance_par: Optional[str] = None
    date_debut: Optional[datetime] = None
    duree_sec: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class SaCMigrationRunOut(BaseModel):
    id: int
    company_id: int
    reference: str
    revision: Optional[str] = None
    environnement: Optional[str] = None
    lance_par: Optional[str] = None
    date_debut: Optional[datetime] = None
    duree_sec: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class SaCLicenseKeyCreate(BaseModel):
    reference: str
    produit: Optional[str] = None
    titulaire: Optional[str] = None
    sieges_licencies: Optional[int] = None
    date_activation: Optional[date] = None
    date_expiration: Optional[date] = None
    statut: Optional[str] = None


class SaCLicenseKeyUpdate(BaseModel):
    reference: Optional[str] = None
    produit: Optional[str] = None
    titulaire: Optional[str] = None
    sieges_licencies: Optional[int] = None
    date_activation: Optional[date] = None
    date_expiration: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class SaCLicenseKeyOut(BaseModel):
    id: int
    company_id: int
    reference: str
    produit: Optional[str] = None
    titulaire: Optional[str] = None
    sieges_licencies: Optional[int] = None
    date_activation: Optional[date] = None
    date_expiration: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}

