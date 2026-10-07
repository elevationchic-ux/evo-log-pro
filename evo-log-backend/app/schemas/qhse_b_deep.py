"""Schemas Pydantic pour qhse-securite (genere)."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date


class QhseNearMissCreate(BaseModel):
    reference: str
    site: Optional[str] = None
    date_evenement: Optional[datetime] = None
    zone: Optional[str] = None
    description: Optional[str] = None
    gravite_potentielle: Optional[str] = None
    statut: Optional[str] = None


class QhseNearMissUpdate(BaseModel):
    reference: Optional[str] = None
    site: Optional[str] = None
    date_evenement: Optional[datetime] = None
    zone: Optional[str] = None
    description: Optional[str] = None
    gravite_potentielle: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class QhseNearMissOut(BaseModel):
    id: int
    company_id: int
    reference: str
    site: Optional[str] = None
    date_evenement: Optional[datetime] = None
    zone: Optional[str] = None
    description: Optional[str] = None
    gravite_potentielle: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class QhseCalibrationCreate(BaseModel):
    numero_instrument: str
    designation: Optional[str] = None
    service: Optional[str] = None
    date_etallonage: Optional[date] = None
    date_prochaine: Optional[date] = None
    ecart_constate: Optional[float] = None
    statut: Optional[str] = None


class QhseCalibrationUpdate(BaseModel):
    numero_instrument: Optional[str] = None
    designation: Optional[str] = None
    service: Optional[str] = None
    date_etallonage: Optional[date] = None
    date_prochaine: Optional[date] = None
    ecart_constate: Optional[float] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class QhseCalibrationOut(BaseModel):
    id: int
    company_id: int
    numero_instrument: str
    designation: Optional[str] = None
    service: Optional[str] = None
    date_etallonage: Optional[date] = None
    date_prochaine: Optional[date] = None
    ecart_constate: Optional[float] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class QhseWasteManifestCreate(BaseModel):
    numero_bsd: str
    site: Optional[str] = None
    type_dechet: Optional[str] = None
    dangerosite: Optional[str] = None
    quantite_tonnes: Optional[float] = None
    destination: Optional[str] = None
    date_enlevement: Optional[date] = None
    statut: Optional[str] = None


class QhseWasteManifestUpdate(BaseModel):
    numero_bsd: Optional[str] = None
    site: Optional[str] = None
    type_dechet: Optional[str] = None
    dangerosite: Optional[str] = None
    quantite_tonnes: Optional[float] = None
    destination: Optional[str] = None
    date_enlevement: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class QhseWasteManifestOut(BaseModel):
    id: int
    company_id: int
    numero_bsd: str
    site: Optional[str] = None
    type_dechet: Optional[str] = None
    dangerosite: Optional[str] = None
    quantite_tonnes: Optional[float] = None
    destination: Optional[str] = None
    date_enlevement: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class QhseTrainingRecordCreate(BaseModel):
    reference: str
    collaborateur: Optional[str] = None
    type_habilitation: Optional[str] = None
    date_formation: Optional[date] = None
    date_validite: Optional[date] = None
    formateur: Optional[str] = None
    statut: Optional[str] = None


class QhseTrainingRecordUpdate(BaseModel):
    reference: Optional[str] = None
    collaborateur: Optional[str] = None
    type_habilitation: Optional[str] = None
    date_formation: Optional[date] = None
    date_validite: Optional[date] = None
    formateur: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class QhseTrainingRecordOut(BaseModel):
    id: int
    company_id: int
    reference: str
    collaborateur: Optional[str] = None
    type_habilitation: Optional[str] = None
    date_formation: Optional[date] = None
    date_validite: Optional[date] = None
    formateur: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class QhseWorkPermitCreate(BaseModel):
    numero_ptw: str
    site: Optional[str] = None
    type_travaux: Optional[str] = None
    zone_travail: Optional[str] = None
    demandeur: Optional[str] = None
    date_debut: Optional[datetime] = None
    date_fin: Optional[datetime] = None
    statut: Optional[str] = None


class QhseWorkPermitUpdate(BaseModel):
    numero_ptw: Optional[str] = None
    site: Optional[str] = None
    type_travaux: Optional[str] = None
    zone_travail: Optional[str] = None
    demandeur: Optional[str] = None
    date_debut: Optional[datetime] = None
    date_fin: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class QhseWorkPermitOut(BaseModel):
    id: int
    company_id: int
    numero_ptw: str
    site: Optional[str] = None
    type_travaux: Optional[str] = None
    zone_travail: Optional[str] = None
    demandeur: Optional[str] = None
    date_debut: Optional[datetime] = None
    date_fin: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}

