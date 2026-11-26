"""Schemas Pydantic pour departement (genere)."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date


class DepObjectiveCreate(BaseModel):
    reference: str
    libelle: Optional[str] = None
    indicateur: Optional[str] = None
    cible: Optional[float] = None
    realise: Optional[float] = None
    trimestre: Optional[str] = None
    statut: Optional[str] = None


class DepObjectiveUpdate(BaseModel):
    reference: Optional[str] = None
    libelle: Optional[str] = None
    indicateur: Optional[str] = None
    cible: Optional[float] = None
    realise: Optional[float] = None
    trimestre: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class DepObjectiveOut(BaseModel):
    id: int
    company_id: int
    reference: str
    libelle: Optional[str] = None
    indicateur: Optional[str] = None
    cible: Optional[float] = None
    realise: Optional[float] = None
    trimestre: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class DepServiceMeetingCreate(BaseModel):
    reference: str
    objet: Optional[str] = None
    date: Optional[datetime] = None
    participants: Optional[int] = None
    compte_rendu: Optional[str] = None
    statut: Optional[str] = None


class DepServiceMeetingUpdate(BaseModel):
    reference: Optional[str] = None
    objet: Optional[str] = None
    date: Optional[datetime] = None
    participants: Optional[int] = None
    compte_rendu: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class DepServiceMeetingOut(BaseModel):
    id: int
    company_id: int
    reference: str
    objet: Optional[str] = None
    date: Optional[datetime] = None
    participants: Optional[int] = None
    compte_rendu: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class DepProjectCreate(BaseModel):
    reference: str
    nom: Optional[str] = None
    responsable: Optional[str] = None
    budget: Optional[float] = None
    echeance: Optional[date] = None
    statut: Optional[str] = None


class DepProjectUpdate(BaseModel):
    reference: Optional[str] = None
    nom: Optional[str] = None
    responsable: Optional[str] = None
    budget: Optional[float] = None
    echeance: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class DepProjectOut(BaseModel):
    id: int
    company_id: int
    reference: str
    nom: Optional[str] = None
    responsable: Optional[str] = None
    budget: Optional[float] = None
    echeance: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class DepServiceRequestCreate(BaseModel):
    reference: str
    objet: Optional[str] = None
    service_destinataire: Optional[str] = None
    urgence: Optional[str] = None
    date_demande: Optional[date] = None
    statut: Optional[str] = None


class DepServiceRequestUpdate(BaseModel):
    reference: Optional[str] = None
    objet: Optional[str] = None
    service_destinataire: Optional[str] = None
    urgence: Optional[str] = None
    date_demande: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class DepServiceRequestOut(BaseModel):
    id: int
    company_id: int
    reference: str
    objet: Optional[str] = None
    service_destinataire: Optional[str] = None
    urgence: Optional[str] = None
    date_demande: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}

