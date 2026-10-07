"""Modeles chat (expansion approfondie generee).

3 entites de gestion, chacune scoped par company_id.
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

class ChtAnnouncement_statut(str, enum.Enum):
    BROUILLON = "brouillon"
    PUBLIEE = "publiee"
    EPINGLEE = "epinglee"
    DEPUBLEE = "depublee"


class ChtChannel_statut(str, enum.Enum):
    ACTIF = "actif"
    ARCHIVE = "archive"
    PRIVE = "prive"
    PUBLIC = "public"


class ChtContentReport_motif(str, enum.Enum):
    HARCELEMENT = "harcelement"
    INFORMATION_INTERDITE = "information_interdite"
    HORS_SUJET = "hors_sujet"
    ABUS = "abus"


class ChtContentReport_severite(str, enum.Enum):
    BENIN = "benin"
    SERIEUX = "serieux"
    CRITIQUE = "critique"


class ChtContentReport_statut(str, enum.Enum):
    OUVERT = "ouvert"
    EN_COURS = "en_cours"
    IGNORE = "ignore"
    SANCTIONNE = "sanctionne"


# ─── Modeles ──────────────────────────────────────────────────────────────────

class ChtAnnouncement(Base):
    """Communiques officiels."""
    __tablename__ = "cht_announcements"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_cht_announcements_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    titre = Column(String(150), index=True, nullable=True)
    contenu = Column(Text(2000), nullable=True)
    cible = Column(String(150), nullable=True)
    auteur = Column(String(150), nullable=True)
    epingle = Column(Boolean, nullable=True)
    date_publication = Column(DateTime(timezone=True), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ChtChannel(Base):
    """Canaux thematiques."""
    __tablename__ = "cht_channels"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_cht_channels_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    nom = Column(String(150), index=True, nullable=True)
    thematique = Column(String(150), nullable=True)
    description = Column(Text(2000), nullable=True)
    createur = Column(String(150), nullable=True)
    membres = Column(Integer, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ChtContentReport(Base):
    """Signalements de contenu."""
    __tablename__ = "cht_content_reports"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_cht_content_reports_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    signalant = Column(String(150), nullable=True)
    contenu_signale = Column(Text(2000), nullable=True)
    motif = Column(String(150), nullable=True)
    severite = Column(String(150), nullable=True)
    date_signalement = Column(DateTime(timezone=True), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

