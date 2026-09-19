"""
Transit schemas for customs and transit operations
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class DossierTransitStatus(str, Enum):
    """Enumeration for transit dossier status"""
    OUVERT = "ouvert"
    EN_COURS = "en_cours"
    EN_DOUANE = "en_douane"
    DELIVRE = "delivre"
    CLOTURE = "cloture"
    ANNULE = "annule"


class DossierTransitBase(BaseModel):
    """Base transit dossier schema"""
    client_id: Optional[int] = None
    transitaire_id: Optional[int] = None
    type_transit: Optional[str] = None
    statut: DossierTransitStatus = DossierTransitStatus.OUVERT
    marchandise: Optional[str] = None
    valeur_marchandise: Optional[float] = None
    poids_brut: Optional[float] = None
    poids_net: Optional[float] = None
    nombre_colis: Optional[int] = None
    origine: Optional[str] = None
    destination: Optional[str] = None
    moyen_transport: Optional[str] = None
    numero_connaisse: Optional[str] = None
    taux_change: float = 1.0
    montant_frais: Optional[float] = None
    montant_droits: Optional[float] = None
    montant_tva: Optional[float] = None
    montant_total: Optional[float] = None
    notes: Optional[str] = None


class DossierTransitCreate(DossierTransitBase):
    """Schema for transit dossier creation"""
    pass


class DossierTransitUpdate(BaseModel):
    """Schema for transit dossier update"""
    statut: Optional[DossierTransitStatus] = None
    marchandise: Optional[str] = None
    valeur_marchandise: Optional[float] = None
    poids_brut: Optional[float] = None
    poids_net: Optional[float] = None
    nombre_colis: Optional[int] = None
    origine: Optional[str] = None
    destination: Optional[str] = None
    moyen_transport: Optional[str] = None
    numero_connaisse: Optional[str] = None
    taux_change: Optional[float] = None
    montant_frais: Optional[float] = None
    montant_droits: Optional[float] = None
    montant_tva: Optional[float] = None
    montant_total: Optional[float] = None
    notes: Optional[str] = None


class DossierTransitResponse(DossierTransitBase):
    """Schema for transit dossier response"""
    id: int
    numero_dossier: str
    date_ouverture: datetime
    date_cloture: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class DeclarationDouaniereBase(BaseModel):
    """Base customs declaration schema - SYDONIA+ integration"""
    dossier_transit_id: Optional[int] = None
    regime_douanier: Optional[str] = None
    bureau_douane: Optional[str] = None
    date_enregistrement: Optional[datetime] = None
    date_validation: Optional[datetime] = None
    date_acquittement: Optional[datetime] = None
    valeur_declaree: Optional[float] = None
    poids_declare: Optional[float] = None
    taux_droit: Optional[float] = None
    montant_droit: Optional[float] = None
    taux_tva: Optional[float] = None
    montant_tva: Optional[float] = None
    autres_taxes: Optional[float] = None
    total_taxes: Optional[float] = None
    numero_b7: Optional[str] = None
    numero_quitus: Optional[str] = None
    statut: str = "brouillon"
    notes: Optional[str] = None


class DeclarationDouaniereCreate(DeclarationDouaniereBase):
    """Schema for customs declaration creation"""
    pass


class DeclarationDouaniereResponse(DeclarationDouaniereBase):
    """Schema for customs declaration response"""
    id: int
    numero_declaration: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True