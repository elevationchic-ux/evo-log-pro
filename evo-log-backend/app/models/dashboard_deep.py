"""Modeles dashboard (expansion approfondie generee).

10 entites de gestion, chacune scoped par company_id.
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

class ModuleHealth_etat(str, enum.Enum):
    OPERATIONNEL = "operationnel"
    DEGRADE = "degrade"
    HORS_SERVICE = "hors_service"


class UnifiedTask_priorite(str, enum.Enum):
    BASSE = "basse"
    NORMALE = "normale"
    HAUTE = "haute"
    URGENTE = "urgente"


class UnifiedTask_statut(str, enum.Enum):
    A_FAIRE = "a_faire"
    EN_COURS = "en_cours"
    FAIT = "fait"
    ANNULEE = "annulee"


class OperationalAlert_niveau(str, enum.Enum):
    INFO = "info"
    WARNING = "warning"
    CRITIQUE = "critique"


class OperationalAlert_statut(str, enum.Enum):
    OUVERTE = "ouverte"
    PRISE_EN_CHARGE = "prise_en_charge"
    RESOLUE = "resolue"


class RecentDocument_partage(str, enum.Enum):
    PRIVE = "prive"
    EQUIPE = "equipe"
    TENANT = "tenant"
    PUBLIC = "public"


# ─── Modeles ──────────────────────────────────────────────────────────────────

class ModuleHealth(Base):
    """Sante fonctionnelle des modules."""
    __tablename__ = "module_healths"
    __table_args__ = (
        UniqueConstraint('company_id', 'code_module', name='uix_module_healths_company_code_module'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    code_module = Column(String(150), nullable=False, index=True)
    etat = Column(_enum(ModuleHealth_etat), default=ModuleHealth_etat.OPERATIONNEL)
    nombre_requetes_jour = Column(Integer, nullable=True)
    taux_erreur_pct = Column(Numeric, nullable=True)
    latence_p95_ms = Column(Integer, nullable=True)
    dernier_incident = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ActivityRecord(Base):
    """Flux d'activite recent."""
    __tablename__ = "activity_records"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_activity_records_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    module_source = Column(String(150), nullable=True)
    type_action = Column(String(150), nullable=True)
    utilisateur = Column(String(150), nullable=True)
    entite = Column(String(150), nullable=True)
    horodatage = Column(DateTime(timezone=True), nullable=True)
    resume = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class UnifiedTask(Base):
    """Centre de taches / to-do unifie."""
    __tablename__ = "unified_tasks"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_unified_tasks_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    titre = Column(String(150), nullable=True)
    module_source = Column(String(150), nullable=True)
    entite_id = Column(Integer, nullable=True)
    assigne_a = Column(Integer, nullable=True)
    date_echeance = Column(DateTime(timezone=True), nullable=True)
    priorite = Column(_enum(UnifiedTask_priorite), default=UnifiedTask_priorite.NORMALE)
    statut = Column(_enum(UnifiedTask_statut), default=UnifiedTask_statut.A_FAIRE)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class QuickAction(Base):
    """Raccourcis operationnels config.."""
    __tablename__ = "quick_actions"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_quick_actions_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    libelle = Column(String(150), nullable=True)
    module_source = Column(String(150), nullable=True)
    url_action = Column(String(150), nullable=True)
    utilisateur_id = Column(Integer, nullable=True)
    ordre = Column(Integer, nullable=True)
    actif = Column(Boolean, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class TeamPerformance(Base):
    """Performance et productivite equipes."""
    __tablename__ = "team_performances"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_team_performances_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    equipe = Column(String(150), nullable=True)
    periode = Column(String(150), nullable=True)
    objectifs_atteints_pct = Column(Numeric, nullable=True)
    volume_traite = Column(Numeric, nullable=True)
    qualite_score = Column(Numeric, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class FinancialSummary(Base):
    """Synthese financiere consolidee."""
    __tablename__ = "financial_summaries"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_financial_summaries_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    periode = Column(String(150), nullable=True)
    ca_consolide_xaf = Column(Numeric, nullable=True)
    marge_brute_xaf = Column(Numeric, nullable=True)
    ebitda_xaf = Column(Numeric, nullable=True)
    bfr_xaf = Column(Numeric, nullable=True)
    tresorerie_xaf = Column(Numeric, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class OperationalAlert(Base):
    """Alertes operationnelles croisees."""
    __tablename__ = "operational_alerts"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_operational_alerts_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    module_source = Column(String(150), nullable=True)
    niveau = Column(_enum(OperationalAlert_niveau), default=OperationalAlert_niveau.WARNING)
    description = Column(Text, nullable=True)
    date_alerte = Column(DateTime(timezone=True), nullable=True)
    destinataire = Column(String(150), nullable=True)
    statut = Column(_enum(OperationalAlert_statut), default=OperationalAlert_statut.OUVERTE)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class RecentDocument(Base):
    """Centre documents recents / partages."""
    __tablename__ = "recent_documents"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_recent_documents_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    titre = Column(String(150), nullable=True)
    module_source = Column(String(150), nullable=True)
    entite_id = Column(Integer, nullable=True)
    url = Column(String(150), nullable=True)
    date_creation = Column(DateTime(timezone=True), nullable=True)
    partage = Column(_enum(RecentDocument_partage), default=RecentDocument_partage.PRIVE)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class UnifiedAgenda(Base):
    """Agenda consolide multi-module."""
    __tablename__ = "unified_agenda"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_unified_agenda_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    titre = Column(String(150), nullable=True)
    module_source = Column(String(150), nullable=True)
    entite_id = Column(Integer, nullable=True)
    date_debut = Column(DateTime(timezone=True), nullable=True)
    date_fin = Column(DateTime(timezone=True), nullable=True)
    invite_par = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class IntegrationStatus(Base):
    """Etat integrations externes."""
    __tablename__ = "integration_statuses"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_integration_statuses_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    nom_integration = Column(String(150), nullable=True)
    url_testee = Column(String(150), nullable=True)
    date_dernier_test = Column(DateTime(timezone=True), nullable=True)
    succes = Column(Boolean, nullable=True)
    latence_ms = Column(Integer, nullable=True)
    message_erreur = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

