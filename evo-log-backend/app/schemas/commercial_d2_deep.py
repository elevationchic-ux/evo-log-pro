"""Schemas Pydantic pour portail-commercial (genere)."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date


class CommCompetitorNoteCreate(BaseModel):
    reference: str
    concurrent: Optional[str] = None
    fait_observe: Optional[str] = None
    marche: Optional[str] = None
    date: Optional[date] = None
    statut: Optional[str] = None


class CommCompetitorNoteUpdate(BaseModel):
    reference: Optional[str] = None
    concurrent: Optional[str] = None
    fait_observe: Optional[str] = None
    marche: Optional[str] = None
    date: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class CommCompetitorNoteOut(BaseModel):
    id: int
    company_id: int
    reference: str
    concurrent: Optional[str] = None
    fait_observe: Optional[str] = None
    marche: Optional[str] = None
    date: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}

