"""Schemas Pydantic pour transit-douane (genere)."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date


class TransitbIncotermCreate(BaseModel):
    code: str
    libelle: Optional[str] = None
    categorie: Optional[str] = None
    transfert_risque_lieu: Optional[str] = None
    transport_principal: Optional[str] = None
    version: Optional[str] = None
    statut: Optional[str] = None


class TransitbIncotermUpdate(BaseModel):
    code: Optional[str] = None
    libelle: Optional[str] = None
    categorie: Optional[str] = None
    transfert_risque_lieu: Optional[str] = None
    transport_principal: Optional[str] = None
    version: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class TransitbIncotermOut(BaseModel):
    id: int
    company_id: int
    code: str
    libelle: Optional[str] = None
    categorie: Optional[str] = None
    transfert_risque_lieu: Optional[str] = None
    transport_principal: Optional[str] = None
    version: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class TransitbInspectionRecordCreate(BaseModel):
    reference: str
    declaration: Optional[str] = None
    type_visite: Optional[str] = None
    agent: Optional[str] = None
    bureau: Optional[str] = None
    date_inspection: Optional[datetime] = None
    observation: Optional[str] = None
    conformite: Optional[bool] = None
    statut: Optional[str] = None


class TransitbInspectionRecordUpdate(BaseModel):
    reference: Optional[str] = None
    declaration: Optional[str] = None
    type_visite: Optional[str] = None
    agent: Optional[str] = None
    bureau: Optional[str] = None
    date_inspection: Optional[datetime] = None
    observation: Optional[str] = None
    conformite: Optional[bool] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class TransitbInspectionRecordOut(BaseModel):
    id: int
    company_id: int
    reference: str
    declaration: Optional[str] = None
    type_visite: Optional[str] = None
    agent: Optional[str] = None
    bureau: Optional[str] = None
    date_inspection: Optional[datetime] = None
    observation: Optional[str] = None
    conformite: Optional[bool] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}

