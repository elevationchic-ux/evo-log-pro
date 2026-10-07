"""Modeles superadmin-cadc (expansion approfondie generee).

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

class SaCAuditLogReview_verdict(str, enum.Enum):
    CONFORME = "conforme"
    ANOMALIE = "anomalie"
    INVESTIGATION = "investigation"


class SaCAuditLogReview_statut(str, enum.Enum):
    PLANIFIEE = "planifiee"
    EN_COURS = "en_cours"
    CLOTUREE = "cloturee"


class SaCSystemParameter_categorie(str, enum.Enum):
    SECURITE = "securite"
    PERFORMANCE = "performance"
    CONFINEMENT = "confinement"
    INTEGRATION = "integration"


class SaCSystemParameter_portee(str, enum.Enum):
    GLOBAL = "global"
    TENANT = "tenant"


class SaCSystemParameter_statut(str, enum.Enum):
    ACTIF = "actif"
    DESACTIVE = "desactive"
    A_REVALIDER = "a_revalider"


class SaCPlatformAlert_severite(str, enum.Enum):
    INFO = "info"
    WARNING = "warning"
    CRITIQUE = "critique"
    BLOQUANT = "bloquant"


class SaCPlatformAlert_statut(str, enum.Enum):
    NOUVELLE = "nouvelle"
    ACQUITTEE = "acquittee"
    RESOLUE = "resolue"
    FAUSSE_ALARME = "fausse_alarme"


class SaCMigrationRun_environnement(str, enum.Enum):
    DEV = "dev"
    STAGING = "staging"
    PROD = "prod"


class SaCMigrationRun_statut(str, enum.Enum):
    EN_COURS = "en_cours"
    SUCCES = "succes"
    ECHEC = "echec"
    RETOUR_ARRIERE = "retour_arriere"


class SaCLicenseKey_statut(str, enum.Enum):
    INACTIVE = "inactive"
    ACTIVE = "active"
    EXPIREE = "expiree"
    RESILIEE = "resiliee"
    SUSPENDUE = "suspendue"


# ─── Modeles ──────────────────────────────────────────────────────────────────

class SaCAuditLogReview(Base):
    """Revues des journaux d' audit."""
    __tablename__ = "sac_audit_log_reviews"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_sac_audit_log_review_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    perimetre = Column(String(150), nullable=True)
    date_debut = Column(DateTime(timezone=True), nullable=True)
    date_fin = Column(DateTime(timezone=True), nullable=True)
    evenements_examines = Column(Integer, nullable=True)
    reviewer = Column(String(150), nullable=True)
    verdict = Column(String(150), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class SaCSystemParameter(Base):
    """Parametres systeme."""
    __tablename__ = "sac_system_parameters"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_sac_system_parameter_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    valeur = Column(Text(2000), nullable=True)
    categorie = Column(String(150), nullable=True)
    portee = Column(String(150), nullable=True)
    modifie_par = Column(String(150), nullable=True)
    date_modification = Column(DateTime(timezone=True), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class SaCPlatformAlert(Base):
    """Alertes plateforme."""
    __tablename__ = "sac_platform_alerts"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_sac_platform_alerts_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    titre = Column(String(150), nullable=True)
    source = Column(String(150), nullable=True)
    severite = Column(String(150), nullable=True)
    date_detection = Column(DateTime(timezone=True), nullable=True)
    acquitte_par = Column(String(150), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class SaCMigrationRun(Base):
    """Executions de migration."""
    __tablename__ = "sac_migration_runs"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_sac_migration_runs_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    revision = Column(String(150), nullable=True)
    environnement = Column(String(150), nullable=True)
    lance_par = Column(String(150), nullable=True)
    date_debut = Column(DateTime(timezone=True), nullable=True)
    duree_sec = Column(Integer, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class SaCLicenseKey(Base):
    """Cles de licence."""
    __tablename__ = "sac_license_keys"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_sac_license_keys_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    produit = Column(String(150), nullable=True)
    titulaire = Column(String(150), nullable=True)
    sieges_licencies = Column(Integer, nullable=True)
    date_activation = Column(Date, nullable=True)
    date_expiration = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

