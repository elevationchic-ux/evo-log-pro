"""
Schemas Tranche B : parc (zones, emplacements, mouvements gate in/out) et
purchase (requisitions d'achat + workflow d'approbation).

Les create/update sont volontairement permissifs (champs optionnels sauf
stricts minima) : les pages frontend issues des mocks envoient des formes
variables, un 422 sur un champ inattendu serait plus regressif qu'un champ
ignore (extra="ignore" par defaut en Pydantic v2).
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class RequisitionStatut(str, Enum):
    BROUILLON = "brouillon"
    SOUMISE = "soumise"
    APPROUVEE = "approuvee"
    REJETEE = "rejetee"


# ─── Zone parc ───────────────────────────────────────────────────────────────
class ZoneParcBase(BaseModel):
    code: str = Field(..., min_length=1, max_length=30)
    nom: str = Field(..., min_length=1, max_length=100)
    type_zone: Optional[str] = None
    superficie_m2: Optional[float] = None
    capacite: Optional[int] = 0
    statut: Optional[str] = "active"
    description: Optional[str] = None


class ZoneParcCreate(ZoneParcBase):
    pass


class ZoneParcUpdate(BaseModel):
    nom: Optional[str] = None
    type_zone: Optional[str] = None
    superficie_m2: Optional[float] = None
    capacite: Optional[int] = None
    statut: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class ZoneParcResponse(ZoneParcBase):
    id: int
    company_id: Optional[int] = None
    is_active: Optional[bool] = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ─── Emplacement parc ────────────────────────────────────────────────────────
class EmplacementParcBase(BaseModel):
    code: str = Field(..., min_length=1, max_length=30)
    zone_id: Optional[int] = None
    type_emplacement: Optional[str] = None
    statut: Optional[str] = "libre"
    max_weight_kg: Optional[float] = None
    contenu: Optional[str] = None


class EmplacementParcCreate(EmplacementParcBase):
    pass


class EmplacementParcUpdate(BaseModel):
    zone_id: Optional[int] = None
    type_emplacement: Optional[str] = None
    statut: Optional[str] = None
    max_weight_kg: Optional[float] = None
    contenu: Optional[str] = None
    is_active: Optional[bool] = None


class EmplacementParcResponse(EmplacementParcBase):
    id: int
    company_id: Optional[int] = None
    is_active: Optional[bool] = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ─── Mouvement gate in / gate out ────────────────────────────────────────────
class GateMovementCreate(BaseModel):
    numero_conteneur: Optional[str] = None
    type_conteneur: Optional[str] = None
    etat: Optional[str] = None
    poids_tare_kg: Optional[float] = None
    emplacement_id: Optional[int] = None
    immatriculation: Optional[str] = None
    chauffeur: Optional[str] = None
    motif: Optional[str] = None


class MouvementParcResponse(GateMovementCreate):
    id: int
    company_id: Optional[int] = None
    sens: str
    horodatage: Optional[datetime] = None

    class Config:
        from_attributes = True


# ─── Requisition d'achat ─────────────────────────────────────────────────────
class RequisitionBase(BaseModel):
    designation: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    article_id: Optional[int] = None
    quantite: Optional[float] = 0
    prix_estime: Optional[float] = None
    devise: Optional[str] = "XAF"
    demandeur: Optional[str] = None
    service: Optional[str] = None
    urgence: Optional[str] = "normale"


class RequisitionCreate(RequisitionBase):
    reference: Optional[str] = None


class RequisitionUpdate(BaseModel):
    designation: Optional[str] = None
    description: Optional[str] = None
    article_id: Optional[int] = None
    quantite: Optional[float] = None
    prix_estime: Optional[float] = None
    urgence: Optional[str] = None
    service: Optional[str] = None
    demandeur: Optional[str] = None


class RequisitionDecision(BaseModel):
    """Payload d'approve/reject : { notes_approbation }."""
    notes_approbation: Optional[str] = None


class RequisitionResponse(RequisitionBase):
    id: int
    company_id: Optional[int] = None
    reference: str
    statut: RequisitionStatut
    date_soumission: Optional[datetime] = None
    date_decision: Optional[datetime] = None
    approuve_par: Optional[int] = None
    notes_approbation: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
