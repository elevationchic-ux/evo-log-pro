"""Schemas Pydantic pour amenagement-portuaire (genere)."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date


class AmgtbDredgingProjectCreate(BaseModel):
    reference: str
    zone: Optional[str] = None
    objectif_tirant_eau_m: Optional[int] = None
    volume_a_draguer_m3: Optional[int] = None
    volume_rejete_m3: Optional[int] = None
    entreprise: Optional[str] = None
    date_debut: Optional[date] = None
    date_fin: Optional[date] = None
    statut: Optional[str] = None


class AmgtbDredgingProjectUpdate(BaseModel):
    reference: Optional[str] = None
    zone: Optional[str] = None
    objectif_tirant_eau_m: Optional[int] = None
    volume_a_draguer_m3: Optional[int] = None
    volume_rejete_m3: Optional[int] = None
    entreprise: Optional[str] = None
    date_debut: Optional[date] = None
    date_fin: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class AmgtbDredgingProjectOut(BaseModel):
    id: int
    company_id: int
    reference: str
    zone: Optional[str] = None
    objectif_tirant_eau_m: Optional[int] = None
    volume_a_draguer_m3: Optional[int] = None
    volume_rejete_m3: Optional[int] = None
    entreprise: Optional[str] = None
    date_debut: Optional[date] = None
    date_fin: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class AmgtbConcessionPlotCreate(BaseModel):
    reference: str
    designation: Optional[str] = None
    superficie_m2: Optional[int] = None
    concessionnaire: Optional[str] = None
    date_debut: Optional[date] = None
    date_echeance: Optional[date] = None
    redevance_annuelle: Optional[float] = None
    statut: Optional[str] = None


class AmgtbConcessionPlotUpdate(BaseModel):
    reference: Optional[str] = None
    designation: Optional[str] = None
    superficie_m2: Optional[int] = None
    concessionnaire: Optional[str] = None
    date_debut: Optional[date] = None
    date_echeance: Optional[date] = None
    redevance_annuelle: Optional[float] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class AmgtbConcessionPlotOut(BaseModel):
    id: int
    company_id: int
    reference: str
    designation: Optional[str] = None
    superficie_m2: Optional[int] = None
    concessionnaire: Optional[str] = None
    date_debut: Optional[date] = None
    date_echeance: Optional[date] = None
    redevance_annuelle: Optional[float] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}

