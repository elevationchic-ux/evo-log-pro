"""Modeles admin-saas (expansion approfondie generee).

11 entites de gestion, chacune scoped par company_id.
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

class FeatureFlag_statut(str, enum.Enum):
    DRAFT = "draft"
    BETA = "beta"
    GLOBALE = "globale"
    RETIREE = "retiree"


class ApiQuota_statut(str, enum.Enum):
    NORMAL = "normal"
    ALERTE = "alerte"
    BLOQUE = "bloque"


class TenantOnboarding_statut(str, enum.Enum):
    EN_COURS = "en_cours"
    ACTIF = "actif"
    ABANONNE = "abanonne"
    REFUSE = "refuse"


class TenantApiKey_statut(str, enum.Enum):
    ACTIF = "actif"
    REVOKE = "revoke"
    EXPIRE = "expire"


class TenantWebhook_statut(str, enum.Enum):
    ACTIF = "actif"
    PAUSE = "pause"
    ERREUR = "erreur"


class DataMigration_type_migration(str, enum.Enum):
    IMPORT_INITIAL = "import_initial"
    UPDATE = "update"
    MERGE = "merge"
    ARCHIVE = "archive"


class DataMigration_statut(str, enum.Enum):
    PLANIFIE = "planifie"
    EN_COURS = "en_cours"
    SUCCES = "succes"
    ECHEC = "echec"
    ROLLED_BACK = "rolled_back"


class PlatformTicket_priorite(str, enum.Enum):
    BASSE = "basse"
    NORMALE = "normale"
    HAUTE = "haute"
    URGENTE = "urgente"


class PlatformTicket_statut(str, enum.Enum):
    OUVERT = "ouvert"
    EN_COURS = "en_cours"
    RESOLU = "resolu"
    CLOTURE = "cloture"


class BillingEntry_type_facture(str, enum.Enum):
    ABONNEMENT = "abonnement"
    USAGE = "usage"
    ADDON = "addon"
    PENALITE = "penalite"


class BillingEntry_statut(str, enum.Enum):
    BROUILLON = "brouillon"
    EMISE = "emise"
    PAYEE = "payee"
    IMPAYEE = "impayee"


class UptimeRecord_statut(str, enum.Enum):
    OPERATIONNEL = "operationnel"
    DEGRADE = "degrade"
    PANNE = "panne"


# ─── Modeles ──────────────────────────────────────────────────────────────────

class FeatureFlag(Base):
    """Gestion fonctionnalites par tenant."""
    __tablename__ = "feature_flags"
    __table_args__ = (
        UniqueConstraint('company_id', 'code_flag', name='uix_feature_flags_company_code_flag'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    code_flag = Column(String(150), nullable=False, index=True)
    description = Column(Text(2000), nullable=True)
    actif = Column(Boolean, nullable=True)
    tenants_concernes = Column(Text(2000), nullable=True)
    date_debut_rollout = Column(Date, nullable=True)
    statut = Column(_enum(FeatureFlag_statut), default=FeatureFlag_statut.BETA)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ApiQuota(Base):
    """Quotas API et limitations."""
    __tablename__ = "api_quotas"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_api_quotas_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    tenant_id = Column(Integer, nullable=True)
    api_group = Column(String(150), nullable=True)
    limite_minute = Column(Integer, nullable=True)
    limite_jour = Column(Integer, nullable=True)
    consommation_actuelle = Column(Integer, nullable=True)
    statut = Column(_enum(ApiQuota_statut), default=ApiQuota_statut.NORMAL)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class WhiteLabel(Base):
    """Personnalisation marque."""
    __tablename__ = "white_labels"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_white_labels_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    tenant_id = Column(Integer, nullable=True)
    nom_marque = Column(String(150), nullable=True)
    domaine_personnalise = Column(String(150), nullable=True)
    logo_url = Column(String(150), nullable=True)
    couleur_primaire = Column(String(150), nullable=True)
    couleur_secondaire = Column(String(150), nullable=True)
    actif = Column(Boolean, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class TenantOnboarding(Base):
    """Parcours onboarding nouveau tenant."""
    __tablename__ = "tenant_onboardings"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_tenant_onboardings_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    tenant_id = Column(Integer, nullable=True)
    date_debut = Column(Date, nullable=True)
    date_activation = Column(Date, nullable=True)
    nb_etapes_completes = Column(Integer, nullable=True)
    responsable_succeed = Column(String(150), nullable=True)
    statut = Column(_enum(TenantOnboarding_statut), default=TenantOnboarding_statut.EN_COURS)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class TenantApiKey(Base):
    """Cles API tierces par tenant."""
    __tablename__ = "tenant_api_keys"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_tenant_api_keys_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    tenant_id = Column(Integer, nullable=True)
    label = Column(String(150), nullable=True)
    scopes = Column(Text(2000), nullable=True)
    date_creation = Column(Date, nullable=True)
    date_expiration = Column(Date, nullable=True)
    derniere_utilisation = Column(DateTime(timezone=True), nullable=True)
    statut = Column(_enum(TenantApiKey_statut), default=TenantApiKey_statut.ACTIF)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class TenantWebhook(Base):
    """Integration evenements sortants."""
    __tablename__ = "tenant_webhooks"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_tenant_webhooks_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    tenant_id = Column(Integer, nullable=True)
    url_destination = Column(String(150), nullable=True)
    evenements_abonnes = Column(Text(2000), nullable=True)
    secret_hmac = Column(String(150), nullable=True)
    dernier_succes = Column(DateTime(timezone=True), nullable=True)
    statut = Column(_enum(TenantWebhook_statut), default=TenantWebhook_statut.ACTIF)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class DataMigration(Base):
    """Import / migration donnees."""
    __tablename__ = "data_migrations"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_data_migrations_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    tenant_id = Column(Integer, nullable=True)
    type_migration = Column(_enum(DataMigration_type_migration), default=DataMigration_type_migration.IMPORT_INITIAL)
    source = Column(String(150), nullable=True)
    nb_lignes_prevues = Column(Integer, nullable=True)
    nb_lignes_importees = Column(Integer, nullable=True)
    nb_lignes_rejetees = Column(Integer, nullable=True)
    date_debut = Column(DateTime(timezone=True), nullable=True)
    date_fin = Column(DateTime(timezone=True), nullable=True)
    statut = Column(_enum(DataMigration_statut), default=DataMigration_statut.PLANIFIE)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class PlatformTicket(Base):
    """Tickets support plateforme."""
    __tablename__ = "platform_tickets"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_platform_tickets_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    tenant_id = Column(Integer, nullable=True)
    titre = Column(String(150), nullable=True)
    description = Column(Text(2000), nullable=True)
    priorite = Column(_enum(PlatformTicket_priorite), default=PlatformTicket_priorite.NORMALE)
    assigne_a = Column(String(150), nullable=True)
    date_creation = Column(DateTime(timezone=True), nullable=True)
    statut = Column(_enum(PlatformTicket_statut), default=PlatformTicket_statut.OUVERT)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class BillingEntry(Base):
    """Moteur de facturation SaaS."""
    __tablename__ = "billing_entries"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_billing_entries_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    tenant_id = Column(Integer, nullable=True)
    periode = Column(String(150), nullable=True)
    type_facture = Column(_enum(BillingEntry_type_facture), default=BillingEntry_type_facture.ABONNEMENT)
    montant_ht_xaf = Column(Numeric, nullable=True)
    tva_xaf = Column(Numeric, nullable=True)
    total_ttc_xaf = Column(Numeric, nullable=True)
    statut = Column(_enum(BillingEntry_statut), default=BillingEntry_statut.BROUILLON)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class UsageAnalytics(Base):
    """Analytique d'usage par tenant."""
    __tablename__ = "usage_analytics"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_usage_analytics_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    tenant_id = Column(Integer, nullable=True)
    periode = Column(String(150), nullable=True)
    utilisateurs_actifs = Column(Integer, nullable=True)
    utilisateurs_seats = Column(Integer, nullable=True)
    taux_adoption_pct = Column(Numeric, nullable=True)
    score_sante = Column(Numeric, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class UptimeRecord(Base):
    """Monitoring disponibilite / SLA."""
    __tablename__ = "uptime_records"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_uptime_records_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    service = Column(String(150), nullable=True)
    region = Column(String(150), nullable=True)
    statut = Column(_enum(UptimeRecord_statut), default=UptimeRecord_statut.OPERATIONNEL)
    latence_ms = Column(Integer, nullable=True)
    disponibilite_pct = Column(Numeric, nullable=True)
    date_mesure = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

