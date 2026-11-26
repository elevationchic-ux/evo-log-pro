"""Schemas Pydantic pour parc-vehicules (genere)."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date


class ParcDriverAssignmentCreate(BaseModel):
    reference: str
    immatriculation: Optional[str] = None
    chauffeur: Optional[str] = None
    date_debut: Optional[date] = None
    date_fin: Optional[date] = None
    kilometrage_debut: Optional[int] = None
    statut: Optional[str] = None


class ParcDriverAssignmentUpdate(BaseModel):
    reference: Optional[str] = None
    immatriculation: Optional[str] = None
    chauffeur: Optional[str] = None
    date_debut: Optional[date] = None
    date_fin: Optional[date] = None
    kilometrage_debut: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class ParcDriverAssignmentOut(BaseModel):
    id: int
    company_id: int
    reference: str
    immatriculation: Optional[str] = None
    chauffeur: Optional[str] = None
    date_debut: Optional[date] = None
    date_fin: Optional[date] = None
    kilometrage_debut: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class ParcGeofenceZoneCreate(BaseModel):
    code_zone: str
    nom_zone: Optional[str] = None
    centre_lat: Optional[str] = None
    centre_lng: Optional[str] = None
    rayon_m: Optional[int] = None
    alerte_sortie: Optional[bool] = None
    statut: Optional[str] = None


class ParcGeofenceZoneUpdate(BaseModel):
    code_zone: Optional[str] = None
    nom_zone: Optional[str] = None
    centre_lat: Optional[str] = None
    centre_lng: Optional[str] = None
    rayon_m: Optional[int] = None
    alerte_sortie: Optional[bool] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class ParcGeofenceZoneOut(BaseModel):
    id: int
    company_id: int
    code_zone: str
    nom_zone: Optional[str] = None
    centre_lat: Optional[str] = None
    centre_lng: Optional[str] = None
    rayon_m: Optional[int] = None
    alerte_sortie: Optional[bool] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class ParcInspectionChecklistCreate(BaseModel):
    reference: str
    immatriculation: Optional[str] = None
    chauffeur: Optional[str] = None
    date_controle: Optional[datetime] = None
    points_controles: Optional[int] = None
    anomalies_nb: Optional[int] = None
    statut: Optional[str] = None


class ParcInspectionChecklistUpdate(BaseModel):
    reference: Optional[str] = None
    immatriculation: Optional[str] = None
    chauffeur: Optional[str] = None
    date_controle: Optional[datetime] = None
    points_controles: Optional[int] = None
    anomalies_nb: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class ParcInspectionChecklistOut(BaseModel):
    id: int
    company_id: int
    reference: str
    immatriculation: Optional[str] = None
    chauffeur: Optional[str] = None
    date_controle: Optional[datetime] = None
    points_controles: Optional[int] = None
    anomalies_nb: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class ParcLeaseContractCreate(BaseModel):
    numero_contrat: str
    loueur: Optional[str] = None
    immatriculation: Optional[str] = None
    loyer_mensuel_xaf: Optional[int] = None
    date_debut: Optional[date] = None
    date_fin: Optional[date] = None
    statut: Optional[str] = None


class ParcLeaseContractUpdate(BaseModel):
    numero_contrat: Optional[str] = None
    loueur: Optional[str] = None
    immatriculation: Optional[str] = None
    loyer_mensuel_xaf: Optional[int] = None
    date_debut: Optional[date] = None
    date_fin: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class ParcLeaseContractOut(BaseModel):
    id: int
    company_id: int
    numero_contrat: str
    loueur: Optional[str] = None
    immatriculation: Optional[str] = None
    loyer_mensuel_xaf: Optional[int] = None
    date_debut: Optional[date] = None
    date_fin: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class ParcTollPassCreate(BaseModel):
    numero_badge: str
    immatriculation: Optional[str] = None
    operateur: Optional[str] = None
    solde_xaf: Optional[int] = None
    date_expiration: Optional[date] = None
    statut: Optional[str] = None


class ParcTollPassUpdate(BaseModel):
    numero_badge: Optional[str] = None
    immatriculation: Optional[str] = None
    operateur: Optional[str] = None
    solde_xaf: Optional[int] = None
    date_expiration: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class ParcTollPassOut(BaseModel):
    id: int
    company_id: int
    numero_badge: str
    immatriculation: Optional[str] = None
    operateur: Optional[str] = None
    solde_xaf: Optional[int] = None
    date_expiration: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}

