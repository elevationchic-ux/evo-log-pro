"""Modeles port-operations (expansion approfondie generee).

2 entites de gestion, chacune scoped par company_id.
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

class PortbBerthSchedule_type_cargo(str, enum.Enum):
    CONTENEUR = "conteneur"
    VRAQUE_LIQUIDE = "vraque_liquide"
    VRAQUE_SEC = "vraque_sec"
    RO_RO = "ro_ro"
    GENERAL = "general"


class PortbBerthSchedule_statut(str, enum.Enum):
    PLANIFIE = "planifie"
    CONFIRME = "confirme"
    EN_ESCALE = "en_escale"
    LIBERE = "libere"
    ANNULE = "annule"


class PortbVesselTrafficLog_mouvement(str, enum.Enum):
    ENTREE = "entree"
    SORTIE = "sortie"
    TRANSIT = "transit"
    MOUILLE = "mouille"


class PortbVesselTrafficLog_statut(str, enum.Enum):
    ENREGISTRE = "enregistre"
    VERIFIE = "verifie"
    SIGNALE = "signale"
    ARCHEVE = "archeve"


# ─── Modeles ──────────────────────────────────────────────────────────────────

class PortbBerthSchedule(Base):
    """Plans d'escale et postes d'amarrage."""
    __tablename__ = "portb_berth_schedules"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_portb_berth_schedule_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    navire = Column(String(150), nullable=True)
    numero_imo = Column(String(150), nullable=True)
    poste_amarrage = Column(String(150), nullable=True)
    date_arrivee_prevue = Column(DateTime(timezone=True), nullable=True)
    date_depart_prevu = Column(DateTime(timezone=True), nullable=True)
    type_cargo = Column(String(150), nullable=True)
    pilote = Column(String(150), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class PortbVesselTrafficLog(Base):
    """Journal de trafic maritime (VTS)."""
    __tablename__ = "portb_vessel_traffic"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_portb_vessel_traffic_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    nom_navire = Column(String(150), nullable=True)
    numero_imo = Column(String(150), nullable=True)
    mouvement = Column(String(150), nullable=True)
    balise_vts = Column(String(150), nullable=True)
    horodatage = Column(DateTime(timezone=True), nullable=True)
    operateur = Column(String(150), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

