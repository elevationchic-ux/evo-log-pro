"""Schemas du domaine juridique (contrats, contentieux, echeances)."""
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field


class ContratJuridiqueBase(BaseModel):
    reference: str
    type_contrat: str
    objet: str
    partie_adverse: Optional[str] = None
    montant: Optional[Decimal] = None
    devise: str = "XAF"
    date_debut: date
    date_fin: Optional[date] = None
    reconduction: str = "non"
    preavis_jours: int = 0
    statut: str = "actif"
    document_url: Optional[str] = None
    document_hash: Optional[str] = None
    notes: Optional[str] = None
    company_id: Optional[int] = None


class ContratJuridiqueCreate(ContratJuridiqueBase):
    pass


class ContratJuridiqueResponse(ContratJuridiqueBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    nb_contentieux: Optional[int] = None

    class Config:
        from_attributes = True


class ContentieuxJuridiqueBase(BaseModel):
    reference: str
    contrat_id: Optional[int] = None
    type_contentieux: str
    description: str
    montant_reclame: Optional[Decimal] = None
    montant_obtenu: Optional[Decimal] = None
    date_declaration: date
    date_echeance: Optional[date] = None
    juridiction: Optional[str] = None
    statut: str = "ouvert"
    date_cloture: Optional[date] = None
    notes: Optional[str] = None
    company_id: Optional[int] = None


class ContentieuxJuridiqueCreate(ContentieuxJuridiqueBase):
    pass


class ContentieuxJuridiqueResponse(ContentieuxJuridiqueBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class EcheanceContrat(BaseModel):
    contrat_id: int
    reference: str
    objet: str
    date_fin: Optional[date] = None
    jours_restants: Optional[int] = None
    preavis_a_notifier_avant_le: Optional[date] = None
    motif: str
