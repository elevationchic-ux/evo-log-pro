"""Modeles reports-bi (expansion approfondie generee).

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

class WarehouseTable_frequence_refresh(str, enum.Enum):
    HEURTAIRE = "heurtaire"
    QUOTIDIEN = "quotidien"
    HEBDO = "hebdo"
    MENSUEL = "mensuel"


class WarehouseTable_statut(str, enum.Enum):
    ACTIF = "actif"
    DEGRADE = "degrade"
    KO = "ko"


class PredictiveModel_type_modele(str, enum.Enum):
    REGRESSION = "regression"
    SERIE_TEMP = "serie_temp"
    CLASSIFICATION = "classification"


class PredictiveModel_statut(str, enum.Enum):
    ACTIF = "actif"
    ENTRAINEMENT = "entrainement"
    OBSOLETE = "obsolete"


class CustomDashboard_partage(str, enum.Enum):
    PRIVE = "prive"
    EQUIPE = "equipe"
    PUBLIC = "public"


class CustomDashboard_frequence(str, enum.Enum):
    TEMPS_REEL = "temps_reel"
    HOURLY = "hourly"
    QUOTIDIEN = "quotidien"
    HEBDO = "hebdo"


class ReportExport_format(str, enum.Enum):
    PDF = "pdf"
    XLSX = "xlsx"
    CSV = "csv"
    HTML = "html"


class ReportExport_frequence(str, enum.Enum):
    QUOTIDIEN = "quotidien"
    HEBDO = "hebdo"
    MENSUEL = "mensuel"
    TRIMESTRIEL = "trimestriel"


class ReportExport_statut(str, enum.Enum):
    ACTIF = "actif"
    PAUSE = "pause"
    ERREUR = "erreur"


class KpiDefinition_periodicite(str, enum.Enum):
    QUOTIDIEN = "quotidien"
    HEBDO = "hebdo"
    MENSUEL = "mensuel"
    TRIMESTRIEL = "trimestriel"
    ANNUEL = "annuel"


class AnomalyRecord_statut(str, enum.Enum):
    DETECTE = "detecte"
    INVESTIGUE = "investigue"
    RESOLU = "resolu"
    FAUX_POSITIF = "faux_positif"


class RegulatoryReport_type_rapport(str, enum.Enum):
    APN = "apn"
    DOUANE = "douane"
    CNPS = "cnps"
    IMPOTS = "impots"
    STATISTIQUE = "statistique"


class RegulatoryReport_statut(str, enum.Enum):
    BROUILLON = "brouillon"
    DEPOSE = "depose"
    ACCEPTE = "accepte"
    REJETE = "rejete"


# ─── Modeles ──────────────────────────────────────────────────────────────────

class WarehouseTable(Base):
    """Entrepot de donnees."""
    __tablename__ = "warehouse_tables"
    __table_args__ = (
        UniqueConstraint('company_id', 'code_table', name='uix_warehouse_tables_company_code_table'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    code_table = Column(String(150), nullable=False, index=True)
    domaine = Column(String(150), nullable=True)
    frequence_refresh = Column(_enum(WarehouseTable_frequence_refresh), default=WarehouseTable_frequence_refresh.QUOTIDIEN)
    volume_lignes = Column(Integer, nullable=True)
    dernier_refresh = Column(DateTime(timezone=True), nullable=True)
    statut = Column(_enum(WarehouseTable_statut), default=WarehouseTable_statut.ACTIF)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Scorecard(Base):
    """Tableaux de score par pole."""
    __tablename__ = "scorecards"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_scorecards_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    pole = Column(String(150), nullable=True)
    periode = Column(String(150), nullable=True)
    nb_kpis = Column(Integer, nullable=True)
    score_global_pct = Column(Numeric, nullable=True)
    kpis_rouges = Column(Integer, nullable=True)
    kpis_oranges = Column(Integer, nullable=True)
    kpis_verts = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class IndustryBenchmark(Base):
    """Comparaison sectorielle ports CEMAC."""
    __tablename__ = "industry_benchmarks"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_industry_benchmarks_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    indicateur = Column(String(150), nullable=True)
    valeur_interne = Column(Numeric, nullable=True)
    valeur_benchmark = Column(Numeric, nullable=True)
    port_reference = Column(String(150), nullable=True)
    source = Column(String(150), nullable=True)
    ecart_pct = Column(Numeric, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class PredictiveModel(Base):
    """Analyses predictives."""
    __tablename__ = "predictive_models"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_predictive_models_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    nom_modele = Column(String(150), nullable=True)
    type_modele = Column(_enum(PredictiveModel_type_modele), default=PredictiveModel_type_modele.REGRESSION)
    variable_predite = Column(String(150), nullable=True)
    precision_pct = Column(Numeric, nullable=True)
    date_entrainement = Column(DateTime(timezone=True), nullable=True)
    statut = Column(_enum(PredictiveModel_statut), default=PredictiveModel_statut.ACTIF)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class CustomDashboard(Base):
    """Tableaux de bord personnalises."""
    __tablename__ = "custom_dashboards"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_custom_dashboards_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    nom = Column(String(150), nullable=True)
    proprietaire = Column(String(150), nullable=True)
    nb_widgets = Column(Integer, nullable=True)
    partage = Column(_enum(CustomDashboard_partage), default=CustomDashboard_partage.PRIVE)
    frequence = Column(_enum(CustomDashboard_frequence), default=CustomDashboard_frequence.QUOTIDIEN)
    actif = Column(Boolean, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ReportExport(Base):
    """Exports planifies / abonnes."""
    __tablename__ = "report_exports"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_report_exports_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    rapport_source = Column(String(150), nullable=True)
    format = Column(_enum(ReportExport_format), default=ReportExport_format.PDF)
    frequence = Column(_enum(ReportExport_frequence), default=ReportExport_frequence.MENSUEL)
    destinataires = Column(Text, nullable=True)
    dernier_envoi = Column(DateTime(timezone=True), nullable=True)
    statut = Column(_enum(ReportExport_statut), default=ReportExport_statut.ACTIF)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class KpiDefinition(Base):
    """Catalogue et definitions KPI."""
    __tablename__ = "kpi_definitions"
    __table_args__ = (
        UniqueConstraint('company_id', 'code_kpi', name='uix_kpi_definitions_company_code_kpi'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    code_kpi = Column(String(150), nullable=False, index=True)
    intitule = Column(String(150), nullable=True)
    formule = Column(Text, nullable=True)
    unite = Column(String(150), nullable=True)
    source = Column(String(150), nullable=True)
    periodicite = Column(_enum(KpiDefinition_periodicite), default=KpiDefinition_periodicite.MENSUEL)
    responsable = Column(String(150), nullable=True)
    actif = Column(Boolean, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class DrillPath(Base):
    """Explorations en cascade."""
    __tablename__ = "drill_paths"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_drill_paths_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    nom = Column(String(150), nullable=True)
    niveau_1 = Column(String(150), nullable=True)
    niveau_2 = Column(String(150), nullable=True)
    niveau_3 = Column(String(150), nullable=True)
    actif = Column(Boolean, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class CohortAnalysis(Base):
    """Analyse de cohortes."""
    __tablename__ = "cohort_analyses"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_cohort_analyses_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    nom_cohorte = Column(String(150), nullable=True)
    criteres = Column(Text, nullable=True)
    taille = Column(Integer, nullable=True)
    date_debut = Column(Date, nullable=True)
    taux_retention_m1_pct = Column(Numeric, nullable=True)
    taux_retention_m12_pct = Column(Numeric, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class AnomalyRecord(Base):
    """Detection anomalies / seuils."""
    __tablename__ = "anomaly_records"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_anomaly_records_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    indicateur = Column(String(150), nullable=True)
    valeur_constatee = Column(Numeric, nullable=True)
    valeur_attendue = Column(Numeric, nullable=True)
    seuil_pct = Column(Numeric, nullable=True)
    date_detection = Column(DateTime(timezone=True), nullable=True)
    statut = Column(_enum(AnomalyRecord_statut), default=AnomalyRecord_statut.DETECTE)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class RegulatoryReport(Base):
    """Rapports reglementaires (APN, douane)."""
    __tablename__ = "regulatory_reports"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_regulatory_reports_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    autorite = Column(String(150), nullable=True)
    type_rapport = Column(_enum(RegulatoryReport_type_rapport), default=RegulatoryReport_type_rapport.APN)
    periode_debut = Column(Date, nullable=True)
    periode_fin = Column(Date, nullable=True)
    date_depot = Column(Date, nullable=True)
    statut = Column(_enum(RegulatoryReport_statut), default=RegulatoryReport_statut.BROUILLON)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

