"""Modeles dashboard (expansion approfondie generee).

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

class DashboardbOperationalKpi_statut(str, enum.Enum):
    NORMAL = "normal"
    ATTENTION = "attention"
    CRITIQUE = "critique"


class DashboardbScorecard_tendance(str, enum.Enum):
    HAUSSE = "hausse"
    BAISSE = "baisse"
    STABLE = "stable"


class DashboardbScorecard_statut(str, enum.Enum):
    BROUILLON = "brouillon"
    PUBLIE = "publie"
    ARCHEVE = "archeve"


class DashboardbAlertRule_condition(str, enum.Enum):
    SUPERIEUR = "superieur"
    INFERIEUR = "inferieur"
    EGAL = "egal"


class DashboardbAlertRule_canal(str, enum.Enum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    NOTIFICATION = "notification"


class DashboardbAlertRule_statut(str, enum.Enum):
    ACTIVE = "active"
    SUSPENDUE = "suspendue"
    EN_TEST = "en_test"


class DashboardbRefreshJob_frequence(str, enum.Enum):
    MANUEL = "manuel"
    HOURLY = "hourly"
    QUOTIDIEN = "quotidien"
    HEBDOMADAIRE = "hebdomadaire"


class DashboardbRefreshJob_statut(str, enum.Enum):
    EN_ATTENTE = "en_attente"
    EN_COURS = "en_cours"
    SUCCES = "succes"
    ECHEC = "echec"


class DashboardbSavedView_type_visuel(str, enum.Enum):
    TABLEAU = "tableau"
    GRAPIQUE = "grapique"
    CARTE = "carte"
    LISTE = "liste"


class DashboardbSavedView_statut(str, enum.Enum):
    PRIVE = "prive"
    PARTAGE = "partage"


# ─── Modeles ──────────────────────────────────────────────────────────────────

class DashboardbOperationalKpi(Base):
    """Indicateurs de performance operationnelle."""
    __tablename__ = "dashb_operational_kpis"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_dashb_operational_kp_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    libelle = Column(String(150), nullable=True)
    module_source = Column(String(150), nullable=True)
    valeur = Column(Numeric, nullable=True)
    unite = Column(String(150), nullable=True)
    periode = Column(Date, nullable=True)
    objectif = Column(Numeric, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class DashboardbScorecard(Base):
    """Tableaux de bord direction."""
    __tablename__ = "dashb_scorecards"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_dashb_scorecards_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    direction = Column(String(150), nullable=True)
    periode = Column(Date, nullable=True)
    score_global = Column(Numeric, nullable=True)
    nb_indicateurs = Column(Integer, nullable=True)
    tendance = Column(String(150), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class DashboardbAlertRule(Base):
    """Regles d'alerte."""
    __tablename__ = "dashb_alert_rules"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_dashb_alert_rules_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    indicateur = Column(String(150), nullable=True)
    condition = Column(String(150), nullable=True)
    seuil = Column(Numeric, nullable=True)
    destinataires = Column(String(150), nullable=True)
    canal = Column(String(150), nullable=True)
    actif = Column(Boolean, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class DashboardbRefreshJob(Base):
    """Taches de rafraichissement."""
    __tablename__ = "dashb_refresh_jobs"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_dashb_refresh_jobs_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    source = Column(String(150), nullable=True)
    frequence = Column(String(150), nullable=True)
    derniere_execution = Column(DateTime(timezone=True), nullable=True)
    duree_sec = Column(Integer, nullable=True)
    lignes_traitees = Column(Integer, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class DashboardbSavedView(Base):
    """Vues enregistrees."""
    __tablename__ = "dashb_saved_views"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_dashb_saved_views_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    nom = Column(String(150), nullable=True)
    owner = Column(String(150), nullable=True)
    type_visuel = Column(String(150), nullable=True)
    filtres = Column(Text, nullable=True)
    partage = Column(Boolean, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

