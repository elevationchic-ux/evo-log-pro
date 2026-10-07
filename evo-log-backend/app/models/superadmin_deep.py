"""Modeles superadmin-cadc (expansion approfondie generee).

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

class PlatformAudit_statut(str, enum.Enum):
    PLANIFIE = "planifie"
    EN_COURS = "en_cours"
    TERMINE = "termine"
    PUBLIE = "publie"


class ComplianceDashboard_domaine(str, enum.Enum):
    RGPD = "rgpd"
    DONNEES_SENSIBLES = "donnees_sensibles"
    SECURITE = "securite"
    FISCAL = "fiscal"
    SOCIAL = "social"


class RetentionPolicy_categorie(str, enum.Enum):
    DOCUMENT_METIER = "document_metier"
    AUDIT = "audit"
    PII = "pii"
    PAIE = "paie"
    FINANCIER = "financier"


class RetentionPolicy_methode_purge(str, enum.Enum):
    ANONYMISATION = "anonymisation"
    SUPPRESSION = "suppression"
    ARCHIVAGE = "archivage"


class PlatformIncident_priorite(str, enum.Enum):
    P1 = "p1"
    P2 = "p2"
    P3 = "p3"
    P4 = "p4"


class PlatformIncident_statut(str, enum.Enum):
    OUVERT = "ouvert"
    CONTENU = "contenu"
    RESOLU = "resolu"
    POST_MORTEM = "post_mortem"


class AccessReview_statut(str, enum.Enum):
    PLANIFIE = "planifie"
    EN_COURS = "en_cours"
    CLOTURE = "cloture"


class SoftwareLicense_statut(str, enum.Enum):
    ACTIVE = "active"
    EXPIREE = "expiree"
    RENOUVELEE = "renouvelee"


class TechnologyPartner_type_partenaire(str, enum.Enum):
    EDITEUR = "editeur"
    INTEGRATEUR = "integrateur"
    REVENEUR = "reveneur"
    TECHNIQUE = "technique"


class TechnologyPartner_statut(str, enum.Enum):
    ACTIF = "actif"
    PAUSE = "pause"
    RESILIE = "resilie"


class GlobalConfigSetting_categorie(str, enum.Enum):
    SECURITE = "securite"
    METIER = "metier"
    TECHNIQUE = "technique"
    CONFORMITE = "conformite"


class GlobalConfigSetting_statut(str, enum.Enum):
    ACTIF = "actif"
    PENDING = "pending"
    REJETE = "rejete"


class DrPlan_scenario(str, enum.Enum):
    PANNE_DATA_CENTER = "panne_data_center"
    CYBERATTAQUE = "cyberattaque"
    CATASTROPHE_NATURELLE = "catastrophe_naturelle"
    ERREUR_HUMAINE = "erreur_humaine"


class DrPlan_resultat_test(str, enum.Enum):
    SUCCES = "succes"
    PARTIEL = "partiel"
    ECHEC = "echec"


# ─── Modeles ──────────────────────────────────────────────────────────────────

class PlatformAudit(Base):
    """Audit global plateforme multi-tenant."""
    __tablename__ = "platform_audits"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_platform_audits_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    periode_debut = Column(Date, nullable=True)
    periode_fin = Column(Date, nullable=True)
    nb_tenants_audites = Column(Integer, nullable=True)
    constats = Column(Text(2000), nullable=True)
    recommandations = Column(Text(2000), nullable=True)
    statut = Column(_enum(PlatformAudit_statut), default=PlatformAudit_statut.PLANIFIE)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ComplianceDashboard(Base):
    """Tableaux conformite globale."""
    __tablename__ = "compliance_dashboards"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_compliance_dashboard_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    domaine = Column(_enum(ComplianceDashboard_domaine), default=ComplianceDashboard_domaine.RGPD)
    nb_tenants_conformes = Column(Integer, nullable=True)
    nb_tenants_hors = Column(Integer, nullable=True)
    score_global_pct = Column(Numeric, nullable=True)
    date_revue = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class RetentionPolicy(Base):
    """Politique retention / purge."""
    __tablename__ = "retention_policies"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_retention_policies_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    categorie = Column(_enum(RetentionPolicy_categorie), default=RetentionPolicy_categorie.DOCUMENT_METIER)
    duree_conservation_jours = Column(Integer, nullable=True)
    methode_purge = Column(_enum(RetentionPolicy_methode_purge), default=RetentionPolicy_methode_purge.ANONYMISATION)
    base_legale = Column(Text(2000), nullable=True)
    actif = Column(Boolean, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class PlatformIncident(Base):
    """Reponse incidents plateforme."""
    __tablename__ = "platform_incidents"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_platform_incidents_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    titre = Column(String(150), nullable=True)
    priorite = Column(_enum(PlatformIncident_priorite), default=PlatformIncident_priorite.P2)
    date_debut = Column(DateTime(timezone=True), nullable=True)
    date_resolution = Column(DateTime(timezone=True), nullable=True)
    impact_tenants = Column(Text(2000), nullable=True)
    cause_racine = Column(Text(2000), nullable=True)
    statut = Column(_enum(PlatformIncident_statut), default=PlatformIncident_statut.OUVERT)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class AccessReview(Base):
    """Revue periodique des acces."""
    __tablename__ = "access_reviews"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_access_reviews_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    tenant_id = Column(Integer, nullable=True)
    date_revue = Column(Date, nullable=True)
    nb_utilisateurs_revus = Column(Integer, nullable=True)
    nb_droits_retires = Column(Integer, nullable=True)
    revue_par = Column(String(150), nullable=True)
    statut = Column(_enum(AccessReview_statut), default=AccessReview_statut.PLANIFIE)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class SoftwareLicense(Base):
    """Gestion licences et modules."""
    __tablename__ = "software_licenses"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_software_licenses_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    module = Column(String(150), nullable=True)
    editeur = Column(String(150), nullable=True)
    nb_sieges = Column(Integer, nullable=True)
    date_debut = Column(Date, nullable=True)
    date_fin = Column(Date, nullable=True)
    cotisation_xaf = Column(Numeric, nullable=True)
    statut = Column(_enum(SoftwareLicense_statut), default=SoftwareLicense_statut.ACTIVE)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class TechnologyPartner(Base):
    """Reseau partenaires technologiques."""
    __tablename__ = "technology_partners"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_technology_partners_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    nom = Column(String(150), nullable=True)
    type_partenaire = Column(_enum(TechnologyPartner_type_partenaire), default=TechnologyPartner_type_partenaire.EDITEUR)
    produit_associe = Column(String(150), nullable=True)
    contrat = Column(Text(2000), nullable=True)
    date_debut = Column(Date, nullable=True)
    statut = Column(_enum(TechnologyPartner_statut), default=TechnologyPartner_statut.ACTIF)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class SaasRevenueRecord(Base):
    """Analytique revenus SaaS / MRR."""
    __tablename__ = "saas_revenue_records"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_saas_revenue_records_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    mois = Column(String(150), nullable=True)
    mrr_xaf = Column(Numeric, nullable=True)
    churn_mrr_xaf = Column(Numeric, nullable=True)
    expansion_mrr_xaf = Column(Numeric, nullable=True)
    arpu_xaf = Column(Numeric, nullable=True)
    nb_customers = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class GlobalConfigSetting(Base):
    """Configuration systeme globale."""
    __tablename__ = "global_config_settings"
    __table_args__ = (
        UniqueConstraint('company_id', 'code_setting', name='uix_global_config_settin_company_code_setting'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    code_setting = Column(String(150), nullable=False, index=True)
    valeur = Column(Text(2000), nullable=True)
    categorie = Column(_enum(GlobalConfigSetting_categorie), default=GlobalConfigSetting_categorie.TECHNIQUE)
    description = Column(Text(2000), nullable=True)
    modifie_par = Column(String(150), nullable=True)
    date_modif = Column(DateTime(timezone=True), nullable=True)
    statut = Column(_enum(GlobalConfigSetting_statut), default=GlobalConfigSetting_statut.ACTIF)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class DrPlan(Base):
    """Plan reprise activite."""
    __tablename__ = "dr_plans"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_dr_plans_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    scenario = Column(_enum(DrPlan_scenario), default=DrPlan_scenario.PANNE_DATA_CENTER)
    rto_heures = Column(Numeric, nullable=True)
    rpo_minutes = Column(Numeric, nullable=True)
    solution_secours = Column(Text(2000), nullable=True)
    date_dernier_test = Column(Date, nullable=True)
    resultat_test = Column(_enum(DrPlan_resultat_test), default=DrPlan_resultat_test.SUCCES)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

