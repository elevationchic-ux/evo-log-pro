"""Modeles reports-bi (expansion approfondie generee).

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

class RptcScheduledReport_frequence(str, enum.Enum):
    QUOTIDIEN = "quotidien"
    HEBDOMADAIRE = "hebdomadaire"
    MENSUEL = "mensuel"
    TRIMESTRIEL = "trimestriel"


class RptcScheduledReport_format(str, enum.Enum):
    PDF = "pdf"
    XLSX = "xlsx"
    CSV = "csv"


class RptcScheduledReport_statut(str, enum.Enum):
    ACTIF = "actif"
    SUSPENDU = "suspendu"
    EN_ERREUR = "en_erreur"


class RptcReportTemplate_categorie(str, enum.Enum):
    OPERATIONNEL = "operationnel"
    FINANCIER = "financier"
    RH = "rh"
    QUALITE = "qualite"


class RptcReportTemplate_statut(str, enum.Enum):
    BROUILLON = "brouillon"
    PUBLIE = "publie"
    ARCHIVE = "archive"


class RptcDataExport_format(str, enum.Enum):
    CSV = "csv"
    XLSX = "xlsx"
    JSON = "json"
    PDF = "pdf"


class RptcDataExport_statut(str, enum.Enum):
    EN_ATTENTE = "en_attente"
    EN_COURS = "en_cours"
    TERMINE = "termine"
    ECHEC = "echec"


class RptcAdHocQuery_statut(str, enum.Enum):
    BROUILLON = "brouillon"
    ENREGISTREE = "enregistree"
    PUBLIEE = "publiee"
    ARCHIVEE = "archivee"


class RptcOlapCube_statut(str, enum.Enum):
    EN_CONSTRUCTION = "en_construction"
    PRET = "pret"
    OBSOLETE = "obsolete"
    ERREUR = "erreur"


# ─── Modeles ──────────────────────────────────────────────────────────────────

class RptcScheduledReport(Base):
    """Rapports planifies."""
    __tablename__ = "rptc_scheduled_reports"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_rptc_scheduled_repor_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    nom = Column(String(150), nullable=True)
    frequence = Column(String(150), nullable=True)
    format = Column(String(150), nullable=True)
    destinataires = Column(String(150), nullable=True)
    prochaine_execution = Column(DateTime(timezone=True), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class RptcReportTemplate(Base):
    """Modeles de rapport."""
    __tablename__ = "rptc_templates"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_rptc_templates_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    nom = Column(String(150), nullable=True)
    categorie = Column(String(150), nullable=True)
    source_donnees = Column(String(150), nullable=True)
    version = Column(String(150), nullable=True)
    nb_blocs = Column(Integer, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class RptcDataExport(Base):
    """Extractions de donnees."""
    __tablename__ = "rptc_data_exports"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_rptc_data_exports_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    libelle = Column(String(150), nullable=True)
    module_source = Column(String(150), nullable=True)
    format = Column(String(150), nullable=True)
    filtres = Column(Text(2000), nullable=True)
    lignes_exportees = Column(Integer, nullable=True)
    demandeur = Column(String(150), nullable=True)
    date_export = Column(DateTime(timezone=True), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class RptcAdHocQuery(Base):
    """Requetes ad hoc."""
    __tablename__ = "rptc_ad_hoc_queries"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_rptc_ad_hoc_queries_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    titre = Column(String(150), nullable=True)
    source_donnees = Column(String(150), nullable=True)
    dimensions = Column(Text(2000), nullable=True)
    auteur = Column(String(150), nullable=True)
    derniere_execution = Column(DateTime(timezone=True), nullable=True)
    partage = Column(Boolean, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class RptcOlapCube(Base):
    """Cubes analytiques."""
    __tablename__ = "rptc_olap_cubes"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_rptc_olap_cubes_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    nom = Column(String(150), nullable=True)
    source = Column(String(150), nullable=True)
    dimensions = Column(Text(2000), nullable=True)
    mesures = Column(Text(2000), nullable=True)
    nb_lignes = Column(Integer, nullable=True)
    date_dernier_refresh = Column(DateTime(timezone=True), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

