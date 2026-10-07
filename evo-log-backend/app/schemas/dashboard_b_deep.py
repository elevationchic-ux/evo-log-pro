"""Schemas Pydantic pour dashboard (genere)."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date


class DashboardbOperationalKpiCreate(BaseModel):
    reference: str
    libelle: Optional[str] = None
    module_source: Optional[str] = None
    valeur: Optional[float] = None
    unite: Optional[str] = None
    periode: Optional[date] = None
    objectif: Optional[float] = None
    statut: Optional[str] = None


class DashboardbOperationalKpiUpdate(BaseModel):
    reference: Optional[str] = None
    libelle: Optional[str] = None
    module_source: Optional[str] = None
    valeur: Optional[float] = None
    unite: Optional[str] = None
    periode: Optional[date] = None
    objectif: Optional[float] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class DashboardbOperationalKpiOut(BaseModel):
    id: int
    company_id: int
    reference: str
    libelle: Optional[str] = None
    module_source: Optional[str] = None
    valeur: Optional[float] = None
    unite: Optional[str] = None
    periode: Optional[date] = None
    objectif: Optional[float] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class DashboardbScorecardCreate(BaseModel):
    reference: str
    direction: Optional[str] = None
    periode: Optional[date] = None
    score_global: Optional[float] = None
    nb_indicateurs: Optional[int] = None
    tendance: Optional[str] = None
    statut: Optional[str] = None


class DashboardbScorecardUpdate(BaseModel):
    reference: Optional[str] = None
    direction: Optional[str] = None
    periode: Optional[date] = None
    score_global: Optional[float] = None
    nb_indicateurs: Optional[int] = None
    tendance: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class DashboardbScorecardOut(BaseModel):
    id: int
    company_id: int
    reference: str
    direction: Optional[str] = None
    periode: Optional[date] = None
    score_global: Optional[float] = None
    nb_indicateurs: Optional[int] = None
    tendance: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class DashboardbAlertRuleCreate(BaseModel):
    reference: str
    indicateur: Optional[str] = None
    condition: Optional[str] = None
    seuil: Optional[float] = None
    destinataires: Optional[str] = None
    canal: Optional[str] = None
    actif: Optional[bool] = None
    statut: Optional[str] = None


class DashboardbAlertRuleUpdate(BaseModel):
    reference: Optional[str] = None
    indicateur: Optional[str] = None
    condition: Optional[str] = None
    seuil: Optional[float] = None
    destinataires: Optional[str] = None
    canal: Optional[str] = None
    actif: Optional[bool] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class DashboardbAlertRuleOut(BaseModel):
    id: int
    company_id: int
    reference: str
    indicateur: Optional[str] = None
    condition: Optional[str] = None
    seuil: Optional[float] = None
    destinataires: Optional[str] = None
    canal: Optional[str] = None
    actif: Optional[bool] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class DashboardbRefreshJobCreate(BaseModel):
    reference: str
    source: Optional[str] = None
    frequence: Optional[str] = None
    derniere_execution: Optional[datetime] = None
    duree_sec: Optional[int] = None
    lignes_traitees: Optional[int] = None
    statut: Optional[str] = None


class DashboardbRefreshJobUpdate(BaseModel):
    reference: Optional[str] = None
    source: Optional[str] = None
    frequence: Optional[str] = None
    derniere_execution: Optional[datetime] = None
    duree_sec: Optional[int] = None
    lignes_traitees: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class DashboardbRefreshJobOut(BaseModel):
    id: int
    company_id: int
    reference: str
    source: Optional[str] = None
    frequence: Optional[str] = None
    derniere_execution: Optional[datetime] = None
    duree_sec: Optional[int] = None
    lignes_traitees: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class DashboardbSavedViewCreate(BaseModel):
    reference: str
    nom: Optional[str] = None
    owner: Optional[str] = None
    type_visuel: Optional[str] = None
    filtres: Optional[str] = None
    partage: Optional[bool] = None
    statut: Optional[str] = None


class DashboardbSavedViewUpdate(BaseModel):
    reference: Optional[str] = None
    nom: Optional[str] = None
    owner: Optional[str] = None
    type_visuel: Optional[str] = None
    filtres: Optional[str] = None
    partage: Optional[bool] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class DashboardbSavedViewOut(BaseModel):
    id: int
    company_id: int
    reference: str
    nom: Optional[str] = None
    owner: Optional[str] = None
    type_visuel: Optional[str] = None
    filtres: Optional[str] = None
    partage: Optional[bool] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}

