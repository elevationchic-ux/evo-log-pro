"""Modeles admin-saas (expansion approfondie generee).

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

class AdmCSubscriptionPlan_periode(str, enum.Enum):
    MENSUEL = "mensuel"
    TRIMESTRIEL = "trimestriel"
    ANNUEL = "annuel"


class AdmCSubscriptionPlan_statut(str, enum.Enum):
    ACTIF = "actif"
    ANCIEN = "ancien"
    BETA = "beta"


class AdmCTenantInvite_role_propose(str, enum.Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    OPERATEUR = "operateur"
    LECTURE = "lecture"


class AdmCTenantInvite_statut(str, enum.Enum):
    EN_ATTENTE = "en_attente"
    ACCEPTEE = "acceptee"
    EXPIREE = "expiree"
    REVOQUEE = "revoquee"


class AdmCApiToken_portee(str, enum.Enum):
    LECTURE = "lecture"
    ECRITURE = "ecriture"
    ADMIN = "admin"


class AdmCApiToken_statut(str, enum.Enum):
    ACTIF = "actif"
    REVOQUE = "revoque"
    EXPIRE = "expire"


class AdmCBillingInvoice_periode_facturee(str, enum.Enum):
    MENSUELLE = "mensuelle"
    TRIMESTRIELLE = "trimestrielle"
    ANNUELLE = "annuelle"


class AdmCBillingInvoice_statut(str, enum.Enum):
    BROUILLON = "brouillon"
    EMISE = "emise"
    PAYEE = "payee"
    EN_RETARD = "en_retard"
    ANNULEE = "annulee"


class AdmCUsageMetering_ressource(str, enum.Enum):
    API_CALLS = "api_calls"
    STOCKAGE_GO = "stockage_go"
    TRANSACTION = "transaction"
    SIEGE_MOIS = "siege_mois"


class AdmCUsageMetering_periode(str, enum.Enum):
    MENSUEL = "mensuel"
    TRIMESTRIEL = "trimestriel"
    ANNUEL = "annuel"


class AdmCUsageMetering_statut(str, enum.Enum):
    COLLECTE = "collecte"
    VALIDE = "valide"
    FACTURE = "facture"
    ANOMALIE = "anomalie"


# ─── Modeles ──────────────────────────────────────────────────────────────────

class AdmCSubscriptionPlan(Base):
    """Plans d' abonnement."""
    __tablename__ = "admc_subscription_plans"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_admc_subscription_pl_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    nom = Column(String(150), nullable=True)
    prix_mensuel = Column(Numeric, nullable=True)
    nb_utilisateurs = Column(Integer, nullable=True)
    nb_modules = Column(Integer, nullable=True)
    periode = Column(String(150), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class AdmCTenantInvite(Base):
    """Invitations des locataires."""
    __tablename__ = "admc_tenant_invites"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_admc_tenant_invites_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    email = Column(String(150), nullable=True)
    tenant = Column(String(150), nullable=True)
    role_propose = Column(String(150), nullable=True)
    invite_par = Column(String(150), nullable=True)
    date_expiration = Column(DateTime(timezone=True), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class AdmCApiToken(Base):
    """Jeton d' API."""
    __tablename__ = "admc_api_tokens"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_admc_api_tokens_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    nom = Column(String(150), nullable=True)
    tenant = Column(String(150), nullable=True)
    portee = Column(String(150), nullable=True)
    cree_le = Column(DateTime(timezone=True), nullable=True)
    expire_le = Column(DateTime(timezone=True), nullable=True)
    derniere_utilisation = Column(DateTime(timezone=True), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class AdmCBillingInvoice(Base):
    """Factures d' abonnement."""
    __tablename__ = "admc_billing_invoices"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_admc_billing_invoice_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    tenant = Column(String(150), nullable=True)
    periode_facturee = Column(String(150), nullable=True)
    montant_ht = Column(Numeric, nullable=True)
    tva = Column(Numeric, nullable=True)
    montant_ttc = Column(Numeric, nullable=True)
    date_echeance = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class AdmCUsageMetering(Base):
    """Mesure d' usage."""
    __tablename__ = "admc_usage_metering"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_admc_usage_metering_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    tenant = Column(String(150), nullable=True)
    ressource = Column(String(150), nullable=True)
    unite = Column(String(150), nullable=True)
    quantite_consommee = Column(Numeric, nullable=True)
    periode = Column(String(150), nullable=True)
    date_releve = Column(DateTime(timezone=True), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

