"""Modeles departement (expansion approfondie generee).

4 entites de gestion, chacune scoped par company_id.
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

class DepObjective_statut(str, enum.Enum):
    PLANIFIE = "planifie"
    EN_COURS = "en_cours"
    ATTEINT = "atteint"
    MANQUE = "manque"


class DepServiceMeeting_statut(str, enum.Enum):
    PLANIFIEE = "planifiee"
    TENUE = "tenue"
    REDIGEE = "redigee"
    CLOTUREE = "cloturee"


class DepProject_statut(str, enum.Enum):
    INITIE = "initie"
    EN_COURS = "en_cours"
    SUSPENDU = "suspendu"
    LIVRE = "livre"


class DepServiceRequest_urgence(str, enum.Enum):
    BASSE = "basse"
    MOYENNE = "moyenne"
    HAUTE = "haute"
    CRITIQUE = "critique"


class DepServiceRequest_statut(str, enum.Enum):
    SOUMISE = "soumise"
    TRAITEE = "traitee"
    RETORNEE = "retornee"
    CLOTUREE = "cloturee"


# ─── Modeles ──────────────────────────────────────────────────────────────────

class DepObjective(Base):
    """Objectifs de service."""
    __tablename__ = "dep_objectives"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_dep_objectives_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    libelle = Column(String(150), index=True, nullable=True)
    indicateur = Column(String(150), nullable=True)
    cible = Column(Numeric, nullable=True)
    realise = Column(Numeric, nullable=True)
    trimestre = Column(String(150), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class DepServiceMeeting(Base):
    """Reunions de service."""
    __tablename__ = "dep_service_meetings"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_dep_service_meetings_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    objet = Column(String(150), index=True, nullable=True)
    date = Column(DateTime(timezone=True), nullable=True)
    participants = Column(Integer, nullable=True)
    compte_rendu = Column(Text(2000), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class DepProject(Base):
    """Projets internes du service."""
    __tablename__ = "dep_projects"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_dep_projects_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    nom = Column(String(150), index=True, nullable=True)
    responsable = Column(String(150), nullable=True)
    budget = Column(Numeric, nullable=True)
    echeance = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class DepServiceRequest(Base):
    """Demandes inter-services."""
    __tablename__ = "dep_service_requests"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_dep_service_requests_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    objet = Column(String(150), index=True, nullable=True)
    service_destinataire = Column(String(150), nullable=True)
    urgence = Column(String(150), nullable=True)
    date_demande = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

