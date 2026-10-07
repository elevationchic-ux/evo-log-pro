"""Modeles qhse-securite (expansion approfondie generee).

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

class QhseNearMiss_gravite_potentielle(str, enum.Enum):
    NEGLIGEABLE = "negligeable"
    MINEURE = "mineure"
    MAJEURE = "majeure"
    CRITIQUE = "critique"


class QhseNearMiss_statut(str, enum.Enum):
    DECLARE = "declare"
    ANALYSE = "analyse"
    ACTIONS = "actions"
    CLOTURE = "cloture"


class QhseCalibration_statut(str, enum.Enum):
    CONFORME = "conforme"
    AJUSTE = "ajuste"
    HORS_TOLERANCE = "hors_tolerance"
    REFORME = "reforme"


class QhseWasteManifest_dangerosite(str, enum.Enum):
    NON_DANGEREUX = "non_dangereux"
    DANGEREUX = "dangereux"
    SPECIFIQUE = "specifique"


class QhseWasteManifest_statut(str, enum.Enum):
    EMIS = "emis"
    ENLEVEMENT = "enlevement"
    TRAITE = "traite"
    TRACES = "traces"


class QhseTrainingRecord_type_habilitation(str, enum.Enum):
    EPI = "epi"
    INCENDIE = "incendie"
    PREMIERS_SECOURS = "premiers_secours"
    TRAVAUX_HAUT = "travaux_haut"
    CONDUITE = "conduite"
    CHIMIQUE = "chimique"


class QhseTrainingRecord_statut(str, enum.Enum):
    VALIDE = "valide"
    A_RENOUVELER = "a_renouveler"
    EXPIRE = "expire"


class QhseWorkPermit_type_travaux(str, enum.Enum):
    POINT_CHAUD = "point_chaud"
    ELECTRIQUE = "electrique"
    HAUTEUR = "hauteur"
    ESPACE_CONFINE = "espace_confine"
    LEVERNAGE = "levernage"
    TERRASSEMENT = "terrassement"


class QhseWorkPermit_statut(str, enum.Enum):
    SOUMIS = "soumis"
    APPROUVE = "approuve"
    EN_COURS = "en_cours"
    CLOTURE = "cloture"
    REFUSE = "refuse"


# ─── Modeles ──────────────────────────────────────────────────────────────────

class QhseNearMiss(Base):
    """Quasi-accidents (situations dangereuses)."""
    __tablename__ = "qhseb_near_misses"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_qhseb_near_misses_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    site = Column(String(150), nullable=True)
    date_evenement = Column(DateTime(timezone=True), nullable=True)
    zone = Column(String(150), nullable=True)
    description = Column(Text(2000), nullable=True)
    gravite_potentielle = Column(String(150), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class QhseCalibration(Base):
    """Etalonnage instruments de mesure."""
    __tablename__ = "qhseb_calibrations"
    __table_args__ = (
        UniqueConstraint('company_id', 'numero_instrument', name='uix_qhseb_calibrations_company_numero_instrume'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    numero_instrument = Column(String(150), nullable=False, index=True)
    designation = Column(String(150), nullable=True)
    service = Column(String(150), nullable=True)
    date_etallonage = Column(Date, nullable=True)
    date_prochaine = Column(Date, nullable=True)
    ecart_constate = Column(Numeric, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class QhseWasteManifest(Base):
    """Bordereaux de suivi des dechets (BSD)."""
    __tablename__ = "qhseb_waste_manifests"
    __table_args__ = (
        UniqueConstraint('company_id', 'numero_bsd', name='uix_qhseb_waste_manifest_company_numero_bsd'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    numero_bsd = Column(String(150), nullable=False, index=True)
    site = Column(String(150), nullable=True)
    type_dechet = Column(String(150), nullable=True)
    dangerosite = Column(String(150), nullable=True)
    quantite_tonnes = Column(Numeric, nullable=True)
    destination = Column(String(150), nullable=True)
    date_enlevement = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class QhseTrainingRecord(Base):
    """Habilitations et formations securite."""
    __tablename__ = "qhseb_training_records"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_qhseb_training_recor_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    collaborateur = Column(String(150), nullable=True)
    type_habilitation = Column(String(150), nullable=True)
    date_formation = Column(Date, nullable=True)
    date_validite = Column(Date, nullable=True)
    formateur = Column(String(150), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class QhseWorkPermit(Base):
    """Permis de travail (PTW)."""
    __tablename__ = "qhseb_work_permits"
    __table_args__ = (
        UniqueConstraint('company_id', 'numero_ptw', name='uix_qhseb_work_permits_company_numero_ptw'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    numero_ptw = Column(String(150), nullable=False, index=True)
    site = Column(String(150), nullable=True)
    type_travaux = Column(String(150), nullable=True)
    zone_travail = Column(String(150), nullable=True)
    demandeur = Column(String(150), nullable=True)
    date_debut = Column(DateTime(timezone=True), nullable=True)
    date_fin = Column(DateTime(timezone=True), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

