"""Modeles amenagement-portuaire (expansion approfondie generee).

8 entites de gestion, chacune scoped par company_id.
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

class InfrastructureMaintenance_type_intervention(str, enum.Enum):
    PEINTURE = "peinture"
    ETANCHEITE = "etancheite"
    CHARPENTE = "charpente"
    ELECTRIQUE = "electrique"
    HYDRAULIQUE = "hydraulique"


class InfrastructureMaintenance_statut(str, enum.Enum):
    PLANIFIE = "planifie"
    EN_COURS = "en_cours"
    FAITE = "faite"
    RETARDE = "retarde"


class IspsRecord_niveau_isps(str, enum.Enum):
    1 = "1"
    2 = "2"
    3 = "3"


class PortPerception_type_perception(str, enum.Enum):
    TONNAGE = "tonnage"
    OCCUPATION_QUAI = "occupation_quai"
    MANUTENTION = "manutention"
    PILOTAGE = "pilotage"
    SALETE = "salete"


class AnnualActivityReport_statut(str, enum.Enum):
    BROUILLON = "brouillon"
    SOUMIS = "soumis"
    APPROUVE = "approuve"
    PUBLIE = "publie"


class SigLayer_type_couche(str, enum.Enum):
    FONCIER = "foncier"
    BATI = "bati"
    HYDRO = "hydro"
    VOIRIE = "voirie"
    RESEAU = "reseau"


class DomainArchive_type_piece(str, enum.Enum):
    TITRE_PROPRIETE = "titre_propriete"
    ARRETE = "arrete"
    CONVENTION = "convention"
    PLAN = "plan"
    RAPPORT = "rapport"


class DomainArchive_statut(str, enum.Enum):
    ACTIF = "actif"
    ARCHIVE_INTERMEDIAIRE = "archive_intermediaire"
    DEFINITIF = "definitif"


class AmenagementKpi_statut(str, enum.Enum):
    EN_DESSOUS = "en_dessous"
    CONFORME = "conforme"
    EN_AVANCE = "en_avance"


# ─── Modeles ──────────────────────────────────────────────────────────────────

class ConstructionProgress(Base):
    """Suivi avancement physique travaux."""
    __tablename__ = "construction_progress"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_construction_progres_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    marche_id = Column(Integer, nullable=True)
    lot = Column(String(150), nullable=True)
    avancement_pct = Column(Numeric, nullable=True)
    date_releve = Column(Date, nullable=True)
    surface_m2 = Column(Numeric, nullable=True)
    observateur = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class InfrastructureMaintenance(Base):
    """Maintenance preventive ouvrages."""
    __tablename__ = "infrastructure_maintenances"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_infrastructure_maint_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    ouvrage_id = Column(Integer, nullable=True)
    type_intervention = Column(_enum(InfrastructureMaintenance_type_intervention), default=InfrastructureMaintenance_type_intervention.PEINTURE)
    frequence_mois = Column(Integer, nullable=True)
    date_prochaine = Column(Date, nullable=True)
    cout_estime_xaf = Column(Numeric, nullable=True)
    statut = Column(_enum(InfrastructureMaintenance_statut), default=InfrastructureMaintenance_statut.PLANIFIE)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class IspsRecord(Base):
    """Surete ISPS (distinct QHSE)."""
    __tablename__ = "isps_records"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_isps_records_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    niveau_isps = Column(_enum(IspsRecord_niveau_isps), default=IspsRecord_niveau_isps.1)
    date_application = Column(DateTime(timezone=True), nullable=True)
    motif = Column(Text(2000), nullable=True)
    authorite_emetteuse = Column(String(150), nullable=True)
    date_levee = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class PortPerception(Base):
    """Redevances et perceptions portuaires."""
    __tablename__ = "port_perceptions"
    __table_args__ = (
        UniqueConstraint('company_id', 'code_perception', name='uix_port_perceptions_company_code_perception'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    code_perception = Column(String(150), nullable=False, index=True)
    intitule = Column(String(150), nullable=True)
    type_perception = Column(_enum(PortPerception_type_perception), default=PortPerception_type_perception.TONNAGE)
    base_calcul = Column(String(150), nullable=True)
    tarif_xaf = Column(Numeric, nullable=True)
    unite = Column(String(150), nullable=True)
    arrete_reference = Column(String(150), nullable=True)
    date_application = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class AnnualActivityReport(Base):
    """Rapport d'activite annuel."""
    __tablename__ = "annual_activity_reports"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_annual_activity_repo_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    annee = Column(Integer, nullable=True)
    tonnage_traite_t = Column(Numeric, nullable=True)
    nb_escales = Column(Integer, nullable=True)
    nb_conteneurs_evp = Column(Integer, nullable=True)
    recettes_xaf = Column(Numeric, nullable=True)
    statut = Column(_enum(AnnualActivityReport_statut), default=AnnualActivityReport_statut.BROUILLON)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class SigLayer(Base):
    """SIG / cartographie domaine."""
    __tablename__ = "sig_layers"
    __table_args__ = (
        UniqueConstraint('company_id', 'code_couche', name='uix_sig_layers_company_code_couche'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    code_couche = Column(String(150), nullable=False, index=True)
    nom = Column(String(150), nullable=True)
    type_couche = Column(_enum(SigLayer_type_couche), default=SigLayer_type_couche.FONCIER)
    projection = Column(String(150), nullable=True)
    date_maj = Column(Date, nullable=True)
    superficie_ha = Column(Numeric, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class DomainArchive(Base):
    """Archivage pieces domaniales."""
    __tablename__ = "domain_archives"
    __table_args__ = (
        UniqueConstraint('company_id', 'cote_archive', name='uix_domain_archives_company_cote_archive'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    cote_archive = Column(String(150), nullable=False, index=True)
    titre = Column(String(150), nullable=True)
    type_piece = Column(_enum(DomainArchive_type_piece), default=DomainArchive_type_piece.ARRETE)
    periode_couverte = Column(String(150), nullable=True)
    localisation = Column(String(150), nullable=True)
    duree_conservation_an = Column(Integer, nullable=True)
    statut = Column(_enum(DomainArchive_statut), default=DomainArchive_statut.ACTIF)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class AmenagementKpi(Base):
    """Tableau bord indicateurs amenagement."""
    __tablename__ = "amenagement_kpis"
    __table_args__ = (
        UniqueConstraint('company_id', 'code_kpi', name='uix_amenagement_kpis_company_code_kpi'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    code_kpi = Column(String(150), nullable=False, index=True)
    intitule = Column(String(150), nullable=True)
    periode = Column(String(150), nullable=True)
    valeur = Column(Numeric, nullable=True)
    objectif = Column(Numeric, nullable=True)
    ecart_pct = Column(Numeric, nullable=True)
    statut = Column(_enum(AmenagementKpi_statut), default=AmenagementKpi_statut.CONFORME)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

