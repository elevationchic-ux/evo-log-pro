"""Modeles admin-tenant (expansion approfondie generee).

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

class AdmtDomainConfig_type(str, enum.Enum):
    PRINCIPAL = "principal"
    SECONDIAIRE = "secondiaire"
    REDIRECTION = "redirection"


class AdmtDomainConfig_statut(str, enum.Enum):
    EN_ATTENTE = "en_attente"
    VERIFIE = "verifie"
    ACTIF = "actif"
    REVOQUE = "revoque"


class AdmtDnsRecord_type_enregistrement(str, enum.Enum):
    A = "a"
    CNAME = "cname"
    MX = "mx"
    TXT = "txt"


class AdmtDnsRecord_statut(str, enum.Enum):
    PROPAGE = "propage"
    EN_ATTENTE = "en_attente"
    SUPPRIME = "supprime"


class AdmtDataResidency_statut(str, enum.Enum):
    CONFORME = "conforme"
    EN_COURS = "en_cours"
    NON_CONFORME = "non_conforme"
    REVISER = "reviser"


class AdmtFeatureEntitlement_statut(str, enum.Enum):
    ACCORD = "accord"
    SUSPENDU = "suspendu"
    EXPIRE = "expire"
    RETIRE = "retire"


class AdmtUsageQuota_periode(str, enum.Enum):
    MENSUEL = "mensuel"
    TRIMESTRIEL = "trimestriel"
    ANNUEL = "annuel"


class AdmtUsageQuota_statut(str, enum.Enum):
    NOMINAL = "nominal"
    PROCHE = "proche"
    DEPASSE = "depasse"
    BLOQUE = "bloque"


class AdmtImpersonationLog_statut(str, enum.Enum):
    EN_COURS = "en_cours"
    TERMINEE = "terminee"
    REVOCABLE = "revocable"
    ANOMALE = "anomale"


class AdmtOnboardingStep_statut(str, enum.Enum):
    A_FAIRE = "a_faire"
    EN_COURS = "en_cours"
    FAITE = "faite"
    BLOQUEE = "bloquee"


class AdmtWhiteLabelConfig_statut(str, enum.Enum):
    BROUILLON = "brouillon"
    PUBLIE = "publie"
    ANCIEN = "ancien"


class AdmtTenantBackup_frequence(str, enum.Enum):
    QUOTIDIEN = "quotidien"
    HEBDOMADAIRE = "hebdomadaire"
    MENSUEL = "mensuel"


class AdmtTenantBackup_statut(str, enum.Enum):
    PROGRAMMEE = "programmee"
    EN_COURS = "en_cours"
    REUSSIE = "reussie"
    ECHEC = "echec"


class AdmtIntegrationWebhook_evenement(str, enum.Enum):
    COMMANDE = "commande"
    LIVRAISON = "livraison"
    FACTURE = "facture"
    TENANT = "tenant"


class AdmtIntegrationWebhook_statut(str, enum.Enum):
    ACTIF = "actif"
    EN_ERREUR = "en_erreur"
    SUSPENDU = "suspendu"
    SUPPRIME = "supprime"


# ─── Modeles ──────────────────────────────────────────────────────────────────

class AdmtDomainConfig(Base):
    """Configurations de domaine."""
    __tablename__ = "admtd_domain_configs"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_admtd_domain_configs_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    tenant = Column(String(150), nullable=True)
    domaine = Column(String(150), nullable=True)
    type = Column(String(150), nullable=True)
    certificat_ssl = Column(Boolean, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class AdmtDnsRecord(Base):
    """Enregistrements DNS."""
    __tablename__ = "admtd_dns_records"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_admtd_dns_records_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    nom_hote = Column(String(150), nullable=True)
    type_enregistrement = Column(String(150), nullable=True)
    valeur = Column(String(150), nullable=True)
    ttl_secondes = Column(Integer, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class AdmtDataResidency(Base):
    """Souverainete des donnees."""
    __tablename__ = "admtd_data_residency"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_admtd_data_residency_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    tenant = Column(String(150), nullable=True)
    region = Column(String(150), nullable=True)
    hebergeur = Column(String(150), nullable=True)
    certification_conforme = Column(Boolean, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class AdmtFeatureEntitlement(Base):
    """Droits fonctionnels."""
    __tablename__ = "admtd_feature_entitlements"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_admtd_feature_entitl_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    module = Column(String(150), nullable=True)
    actif = Column(Boolean, nullable=True)
    limite = Column(Integer, nullable=True)
    date_expiration = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class AdmtUsageQuota(Base):
    """Quotas d' usage."""
    __tablename__ = "admtd_usage_quotas"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_admtd_usage_quotas_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    ressource = Column(String(150), nullable=True)
    quota_autorise = Column(Integer, nullable=True)
    consomme = Column(Integer, nullable=True)
    periode = Column(String(150), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class AdmtImpersonationLog(Base):
    """Journaux d' impersonation."""
    __tablename__ = "admtd_impersonation_logs"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_admtd_impersonation__company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    admin = Column(String(150), nullable=True)
    cible_tenant = Column(String(150), nullable=True)
    motif = Column(Text(2000), nullable=True)
    debut = Column(DateTime(timezone=True), nullable=True)
    fin = Column(DateTime(timezone=True), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class AdmtOnboardingStep(Base):
    """Etapes d' onboarding."""
    __tablename__ = "admtd_onboarding_steps"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_admtd_onboarding_ste_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    tenant = Column(String(150), nullable=True)
    etape = Column(String(150), nullable=True)
    ordre = Column(Integer, nullable=True)
    responsable = Column(String(150), nullable=True)
    date_completion = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class AdmtWhiteLabelConfig(Base):
    """Configurations marque blanche."""
    __tablename__ = "admtd_white_label_configs"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_admtd_white_label_co_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    tenant = Column(String(150), nullable=True)
    nom_affiche = Column(String(150), nullable=True)
    logo_url = Column(String(150), nullable=True)
    couleur_principale = Column(String(150), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class AdmtTenantBackup(Base):
    """Sauvegardes tenant."""
    __tablename__ = "admtd_tenant_backups"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_admtd_tenant_backups_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    tenant = Column(String(150), nullable=True)
    taille_octets = Column(Integer, nullable=True)
    frequence = Column(String(150), nullable=True)
    derniere_reussite = Column(DateTime(timezone=True), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class AdmtIntegrationWebhook(Base):
    """Webhooks d' integration."""
    __tablename__ = "admtd_integration_webhooks"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_admtd_integration_we_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    tenant = Column(String(150), nullable=True)
    url_cible = Column(String(150), nullable=True)
    evenement = Column(String(150), nullable=True)
    actif = Column(Boolean, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

