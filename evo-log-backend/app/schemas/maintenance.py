"""
Maintenance schemas for equipment and vehicle maintenance
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class InterventionStatus(str, Enum):
    """Enumeration for maintenance intervention status"""
    PLANIFIEE = "planifiee"
    EN_COURS = "en_cours"
    TERMINEE = "terminee"
    ANNULEE = "annulee"
    EN_ATTENTE = "en_attente"


class InterventionBase(BaseModel):
    """Base maintenance intervention schema"""
    equipement_id: Optional[int] = None
    type_intervention: Optional[str] = None
    priorite: Optional[str] = None
    statut: InterventionStatus = InterventionStatus.PLANIFIEE
    date_planifiee: Optional[datetime] = None
    date_debut: Optional[datetime] = None
    date_fin: Optional[datetime] = None
    description: Optional[str] = None
    diagnostic: Optional[str] = None
    travaux_realises: Optional[str] = None
    cout_main_oeuvre: Optional[float] = None
    cout_pieces: Optional[float] = None
    cout_total: Optional[float] = None
    technicien: Optional[str] = None
    validateur: Optional[str] = None
    date_validation: Optional[datetime] = None
    notes: Optional[str] = None


class InterventionCreate(InterventionBase):
    """Schema for maintenance intervention creation"""
    created_by: Optional[int] = None


class InterventionUpdate(BaseModel):
    """Schema for maintenance intervention update"""
    equipement_id: Optional[int] = None
    type_intervention: Optional[str] = None
    priorite: Optional[str] = None
    statut: Optional[InterventionStatus] = None
    date_planifiee: Optional[datetime] = None
    date_debut: Optional[datetime] = None
    date_fin: Optional[datetime] = None
    description: Optional[str] = None
    diagnostic: Optional[str] = None
    travaux_realises: Optional[str] = None
    cout_main_oeuvre: Optional[float] = None
    cout_pieces: Optional[float] = None
    cout_total: Optional[float] = None
    technicien: Optional[str] = None
    validateur: Optional[str] = None
    date_validation: Optional[datetime] = None
    notes: Optional[str] = None


class InterventionResponse(InterventionBase):
    """Schema for maintenance intervention response"""
    id: int
    reference: str
    created_at: datetime
    created_by: Optional[int] = None
    
    class Config:
        from_attributes = True


class PieceRechangeBase(BaseModel):
    """Base spare parts schema"""
    code: str = Field(..., min_length=2, max_length=50)
    designation: str = Field(..., min_length=2, max_length=200)
    description: Optional[str] = None
    categorie: Optional[str] = None
    fournisseur: Optional[str] = None
    reference_fournisseur: Optional[str] = None
    prix_unitaire: Optional[float] = None
    quantite_stock: int = 0
    quantite_minimum: Optional[int] = None
    emplacement: Optional[str] = None
    intervention_id: Optional[int] = None
    date_utilisation: Optional[datetime] = None
    is_active: bool = True


class PieceRechangeCreate(PieceRechangeBase):
    """Schema for spare parts creation"""
    pass


class PieceRechangeResponse(PieceRechangeBase):
    """Schema for spare parts response"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True