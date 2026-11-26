"""Modeles transport-flotte (expansion approfondie generee).

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

class TransportbDispatch_statut(str, enum.Enum):
    AFFECTEE = "affectee"
    EN_ROUTE = "en_route"
    LIVREE = "livree"
    RETARD = "retard"
    ANNULEE = "annulee"


class TransportbPod_statut(str, enum.Enum):
    EN_ATTENTE = "en_attente"
    SIGNE = "signe"
    LITIGE = "litige"
    REFUSE = "refuse"


# ─── Modeles ──────────────────────────────────────────────────────────────────

class TransportbDispatch(Base):
    """Bons de mission / affectation."""
    __tablename__ = "transportb_dispatches"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_transportb_dispatche_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    chauffeur = Column(String(150), nullable=True)
    vehicule = Column(String(150), nullable=True)
    point_depart = Column(String(150), nullable=True)
    point_arrivee = Column(String(150), nullable=True)
    date_depart = Column(DateTime(timezone=True), nullable=True)
    date_arrivee = Column(DateTime(timezone=True), nullable=True)
    km_parcourus = Column(Integer, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class TransportbPod(Base):
    """Preuves de livraison (POD)."""
    __tablename__ = "transportb_pods"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_transportb_pods_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    mission = Column(String(150), nullable=True)
    destinataire = Column(String(150), nullable=True)
    date_livraison = Column(DateTime(timezone=True), nullable=True)
    nb_colis_livres = Column(Integer, nullable=True)
    incidents = Column(String(150), nullable=True)
    signature_recu = Column(Boolean, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

