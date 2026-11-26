"""Schemas Pydantic pour rh-personnel (genere)."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date


class RhCTrainingPlanCreate(BaseModel):
    reference: str
    intitule: Optional[str] = None
    categorie: Optional[str] = None
    collaborateur: Optional[str] = None
    organisme: Optional[str] = None
    heures_financees: Optional[int] = None
    heures_realisees: Optional[int] = None
    date_debut: Optional[date] = None
    statut: Optional[str] = None


class RhCTrainingPlanUpdate(BaseModel):
    reference: Optional[str] = None
    intitule: Optional[str] = None
    categorie: Optional[str] = None
    collaborateur: Optional[str] = None
    organisme: Optional[str] = None
    heures_financees: Optional[int] = None
    heures_realisees: Optional[int] = None
    date_debut: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class RhCTrainingPlanOut(BaseModel):
    id: int
    company_id: int
    reference: str
    intitule: Optional[str] = None
    categorie: Optional[str] = None
    collaborateur: Optional[str] = None
    organisme: Optional[str] = None
    heures_financees: Optional[int] = None
    heures_realisees: Optional[int] = None
    date_debut: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class RhCDisciplinaryRecordCreate(BaseModel):
    reference: str
    collaborateur: Optional[str] = None
    type_sanction: Optional[str] = None
    motif: Optional[str] = None
    date_effet: Optional[date] = None
    date_fin_effet: Optional[date] = None
    decideur: Optional[str] = None
    statut: Optional[str] = None


class RhCDisciplinaryRecordUpdate(BaseModel):
    reference: Optional[str] = None
    collaborateur: Optional[str] = None
    type_sanction: Optional[str] = None
    motif: Optional[str] = None
    date_effet: Optional[date] = None
    date_fin_effet: Optional[date] = None
    decideur: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class RhCDisciplinaryRecordOut(BaseModel):
    id: int
    company_id: int
    reference: str
    collaborateur: Optional[str] = None
    type_sanction: Optional[str] = None
    motif: Optional[str] = None
    date_effet: Optional[date] = None
    date_fin_effet: Optional[date] = None
    decideur: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}

