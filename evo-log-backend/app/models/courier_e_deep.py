"""Modeles courier-express (expansion approfondie generee).

7 entites de gestion, chacune scoped par company_id.
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

class Cour2RouteScan_etape(str, enum.Enum):
    ENLEVEMENT = "enlevement"
    HUB = "hub"
    TOURNEE = "tournee"
    LIVRAISON = "livraison"


class Cour2RouteScan_statut(str, enum.Enum):
    SCANE = "scane"
    MANQUANT = "manquant"
    TARDIF = "tardif"


class Cour2LastMileHandoff_statut(str, enum.Enum):
    REMIS = "remis"
    EN_ROUTE = "en_route"
    RETOUR_AGENCE = "retour_agence"
    PERDU = "perdu"


class Cour2DeliveryAttempt_motif(str, enum.Enum):
    LIVRE = "livre"
    ABSENT = "absent"
    REFUSE = "refuse"
    ADRESSE_INVALIDE = "adresse_invalide"
    VOLE = "vole"


class Cour2ExceptionParcel_type_exception(str, enum.Enum):
    DAMAGE = "damage"
    ADRESSE = "adresse"
    DOUANE = "douane"
    LOST = "lost"
    REFUS = "refus"


class Cour2ExceptionParcel_statut(str, enum.Enum):
    OUVERTE = "ouverte"
    EN_COURS = "en_cours"
    RESOLUE = "resolue"
    IRRECOVERABLE = "irrecoverable"


class Cour2ReturnToSender_statut(str, enum.Enum):
    PLANIFIE = "planifie"
    EN_RETOUR = "en_retour"
    LIVRE_EXPEDITEUR = "livre_expediteur"
    DECLINE = "decline"


class Cour2CourierShiftLog_statut(str, enum.Enum):
    OUVERTE = "ouverte"
    EN_COURS = "en_cours"
    CLOTUREE = "cloturee"
    ANOMALIE = "anomalie"


class Cour2SlaBreachLog_statut(str, enum.Enum):
    CONSTEEE = "consteee"
    COMPENSE = "compense"
    EXONERE = "exonere"
    CONTESTEE = "contestee"


# ─── Modeles ──────────────────────────────────────────────────────────────────

class Cour2RouteScan(Base):
    """Scans de tournee."""
    __tablename__ = "cour2_route_scans"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_cour2_route_scans_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    colis = Column(String(150), nullable=True)
    etape = Column(String(150), nullable=True)
    lieu = Column(String(150), nullable=True)
    date = Column(DateTime(timezone=True), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Cour2LastMileHandoff(Base):
    """Remises dernier kilometre."""
    __tablename__ = "cour2_last_mile"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_cour2_last_mile_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    colis = Column(String(150), nullable=True)
    livreur = Column(String(150), nullable=True)
    agencer = Column(String(150), nullable=True)
    date = Column(DateTime(timezone=True), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Cour2DeliveryAttempt(Base):
    """Tentatives de livraison."""
    __tablename__ = "cour2_delivery_attempts"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_cour2_delivery_attem_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    colis = Column(String(150), nullable=True)
    livreur = Column(String(150), nullable=True)
    date = Column(DateTime(timezone=True), nullable=True)
    motif = Column(String(150), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Cour2ExceptionParcel(Base):
    """Colis en exception."""
    __tablename__ = "cour2_exceptions"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_cour2_exceptions_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    colis = Column(String(150), nullable=True)
    type_exception = Column(String(150), nullable=True)
    detecte_le = Column(DateTime(timezone=True), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Cour2ReturnToSender(Base):
    """Retours expediteur."""
    __tablename__ = "cour2_returns"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_cour2_returns_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    colis = Column(String(150), nullable=True)
    motif = Column(String(150), nullable=True)
    date_depart = Column(DateTime(timezone=True), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Cour2CourierShiftLog(Base):
    """Journal de vacation livreur."""
    __tablename__ = "cour2_shift_logs"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_cour2_shift_logs_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    livreur = Column(String(150), nullable=True)
    date = Column(Date, nullable=True)
    colis_livres = Column(Integer, nullable=True)
    km = Column(Integer, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Cour2SlaBreachLog(Base):
    """Journaux de rupture SLA."""
    __tablename__ = "cour2_sla_breaches"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_cour2_sla_breaches_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    colis = Column(String(150), nullable=True)
    retard_min = Column(Integer, nullable=True)
    date = Column(DateTime(timezone=True), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

