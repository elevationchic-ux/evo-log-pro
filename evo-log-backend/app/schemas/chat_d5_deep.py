"""Schemas Pydantic pour chat (genere)."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date


class ChtAnnouncementCreate(BaseModel):
    reference: str
    titre: Optional[str] = None
    contenu: Optional[str] = None
    cible: Optional[str] = None
    auteur: Optional[str] = None
    epingle: Optional[bool] = None
    date_publication: Optional[datetime] = None
    statut: Optional[str] = None


class ChtAnnouncementUpdate(BaseModel):
    reference: Optional[str] = None
    titre: Optional[str] = None
    contenu: Optional[str] = None
    cible: Optional[str] = None
    auteur: Optional[str] = None
    epingle: Optional[bool] = None
    date_publication: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class ChtAnnouncementOut(BaseModel):
    id: int
    company_id: int
    reference: str
    titre: Optional[str] = None
    contenu: Optional[str] = None
    cible: Optional[str] = None
    auteur: Optional[str] = None
    epingle: Optional[bool] = None
    date_publication: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class ChtChannelCreate(BaseModel):
    reference: str
    nom: Optional[str] = None
    thematique: Optional[str] = None
    description: Optional[str] = None
    createur: Optional[str] = None
    membres: Optional[int] = None
    statut: Optional[str] = None


class ChtChannelUpdate(BaseModel):
    reference: Optional[str] = None
    nom: Optional[str] = None
    thematique: Optional[str] = None
    description: Optional[str] = None
    createur: Optional[str] = None
    membres: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class ChtChannelOut(BaseModel):
    id: int
    company_id: int
    reference: str
    nom: Optional[str] = None
    thematique: Optional[str] = None
    description: Optional[str] = None
    createur: Optional[str] = None
    membres: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class ChtContentReportCreate(BaseModel):
    reference: str
    signalant: Optional[str] = None
    contenu_signale: Optional[str] = None
    motif: Optional[str] = None
    severite: Optional[str] = None
    date_signalement: Optional[datetime] = None
    statut: Optional[str] = None


class ChtContentReportUpdate(BaseModel):
    reference: Optional[str] = None
    signalant: Optional[str] = None
    contenu_signale: Optional[str] = None
    motif: Optional[str] = None
    severite: Optional[str] = None
    date_signalement: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class ChtContentReportOut(BaseModel):
    id: int
    company_id: int
    reference: str
    signalant: Optional[str] = None
    contenu_signale: Optional[str] = None
    motif: Optional[str] = None
    severite: Optional[str] = None
    date_signalement: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}

