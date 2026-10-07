"""Modeles parc-vehicules (expansion approfondie generee).

5 entites de gestion, chacune scoped par company_id.
Convention d'honnetete : aucune valeur par defaut, NULL = "non enregistre".
"""
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean, Float,
    ForeignKey, Date, Numeric, UniqueConstraint, Enum as SAEnum,
)
from sqlalchemy.sql import func
import enum

from app.core.database import Base


def _enum(cls):
    return SAEnum(cls, native_enum=False, create_constraint=False,
                  values_callable=lambda x: [e.value for e in x])


# ─── Enums ────────────────────────────────────────────────────────────────────

class ParcDriverAssignment_statut(str, enum.Enum):
    ACTIF = "actif"
    SUSPENDU = "suspendu"
    TERMINE = "termine"


class ParcGeofenceZone_statut(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class ParcInspectionChecklist_statut(str, enum.Enum):
    CONFORME = "conforme"
    ANOMALIE_MINEURE = "anomalie_mineure"
    BLOQUANT = "bloquant"


class ParcLeaseContract_statut(str, enum.Enum):
    EN_COURS = "en_cours"
    RENEGOCIE = "renegocie"
    EXPIRE = "expire"
    RESILIE = "resilie"


class ParcTollPass_statut(str, enum.Enum):
    ACTIF = "actif"
    SOLDE_FAIBLE = "solde_faible"
    BLOQUE = "bloque"
    EXPIRE = "expire"


# ─── Modeles ──────────────────────────────────────────────────────────────────

class ParcDriverAssignment(Base):
    """Affectation chauffeurs."""
    __tablename__ = "parcb_driver_assignments"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_parcb_driver_assignm_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    immatriculation = Column(String(150), nullable=True)
    chauffeur = Column(String(150), nullable=True)
    date_debut = Column(Date, nullable=True)
    date_fin = Column(Date, nullable=True)
    kilometrage_debut = Column(Integer, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ParcGeofenceZone(Base):
    """Zones geoclotees."""
    __tablename__ = "parcb_geofence_zones"
    __table_args__ = (
        UniqueConstraint('company_id', 'code_zone', name='uix_parcb_geofence_zones_company_code_zone'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    code_zone = Column(String(150), nullable=False, index=True)
    nom_zone = Column(String(150), nullable=True)
    centre_lat = Column(String(150), nullable=True)
    centre_lng = Column(String(150), nullable=True)
    rayon_m = Column(Integer, nullable=True)
    alerte_sortie = Column(Boolean, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ParcInspectionChecklist(Base):
    """Checklists de controle."""
    __tablename__ = "parcb_inspection_checklists"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_parcb_inspection_che_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    immatriculation = Column(String(150), nullable=True)
    chauffeur = Column(String(150), nullable=True)
    date_controle = Column(DateTime(timezone=True), nullable=True)
    points_controles = Column(Integer, nullable=True)
    anomalies_nb = Column(Integer, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ParcLeaseContract(Base):
    """Contrats de location / leasing."""
    __tablename__ = "parcb_lease_contracts"
    __table_args__ = (
        UniqueConstraint('company_id', 'numero_contrat', name='uix_parcb_lease_contract_company_numero_contrat'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    numero_contrat = Column(String(150), nullable=False, index=True)
    loueur = Column(String(150), nullable=True)
    immatriculation = Column(String(150), nullable=True)
    loyer_mensuel_xaf = Column(Integer, nullable=True)
    date_debut = Column(Date, nullable=True)
    date_fin = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ParcTollPass(Base):
    """Badges de peage / telepeage."""
    __tablename__ = "parcb_toll_passes"
    __table_args__ = (
        UniqueConstraint('company_id', 'numero_badge', name='uix_parcb_toll_passes_company_numero_badge'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    numero_badge = Column(String(150), nullable=False, index=True)
    immatriculation = Column(String(150), nullable=True)
    operateur = Column(String(150), nullable=True)
    solde_xaf = Column(Integer, nullable=True)
    date_expiration = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

