"""Schemas Pydantic pour finance-ohada (genere)."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date


class FincCashFlowForecastCreate(BaseModel):
    reference: str
    periode: Optional[str] = None
    solde_debut: Optional[float] = None
    entrees_prevues: Optional[float] = None
    sorties_prevues: Optional[float] = None
    position_finale: Optional[float] = None
    horizon_jours: Optional[int] = None
    statut: Optional[str] = None


class FincCashFlowForecastUpdate(BaseModel):
    reference: Optional[str] = None
    periode: Optional[str] = None
    solde_debut: Optional[float] = None
    entrees_prevues: Optional[float] = None
    sorties_prevues: Optional[float] = None
    position_finale: Optional[float] = None
    horizon_jours: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class FincCashFlowForecastOut(BaseModel):
    id: int
    company_id: int
    reference: str
    periode: Optional[str] = None
    solde_debut: Optional[float] = None
    entrees_prevues: Optional[float] = None
    sorties_prevues: Optional[float] = None
    position_finale: Optional[float] = None
    horizon_jours: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class FincInvoiceFinancingCreate(BaseModel):
    reference: str
    affacteur: Optional[str] = None
    facture: Optional[str] = None
    montant_facture: Optional[float] = None
    avance_pct: Optional[int] = None
    commission: Optional[float] = None
    date_echeance: Optional[date] = None
    statut: Optional[str] = None


class FincInvoiceFinancingUpdate(BaseModel):
    reference: Optional[str] = None
    affacteur: Optional[str] = None
    facture: Optional[str] = None
    montant_facture: Optional[float] = None
    avance_pct: Optional[int] = None
    commission: Optional[float] = None
    date_echeance: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class FincInvoiceFinancingOut(BaseModel):
    id: int
    company_id: int
    reference: str
    affacteur: Optional[str] = None
    facture: Optional[str] = None
    montant_facture: Optional[float] = None
    avance_pct: Optional[int] = None
    commission: Optional[float] = None
    date_echeance: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}

