"""Modeles pipeline-oleoduc (expansion approfondie generee).

9 entites de gestion, chacune scoped par company_id.
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

class Pipe2CustodyTransfer_statut(str, enum.Enum):
    OUVERT = "ouvert"
    RECONCILE = "reconcile"
    ECART = "ecart"
    VALIDE = "valide"


class Pipe2PressureLog_statut(str, enum.Enum):
    NOMINAL = "nominal"
    BAS = "bas"
    HAUT = "haut"
    ALERTE = "alerte"


class Pipe2PumpStationRead_statut(str, enum.Enum):
    EN_MARCHE = "en_marche"
    ARRET = "arret"
    DEGRADE = "degrade"
    MAINTENANCE = "maintenance"


class Pipe2CorrosionReading_statut(str, enum.Enum):
    NOMINAL = "nominal"
    SURVEILLE = "surveille"
    CRITIQUE = "critique"
    REPAR = "repar"


class Pipe2FlowCalibration_statut(str, enum.Enum):
    CONFORME = "conforme"
    AJUSTE = "ajuste"
    HORS_TOLERANCE = "hors_tolerance"
    A_REFAIRE = "a_refaire"


class Pipe2BatchQualityTest_statut(str, enum.Enum):
    EN_COURS = "en_cours"
    CONFORME = "conforme"
    HORS_SPEC = "hors_spec"
    REJETE = "rejete"


class Pipe2InterfaceDetection_statut(str, enum.Enum):
    DETECTEE = "detectee"
    SEPARER = "separer"
    RECYCLE = "recycle"
    PERTE = "perte"


class Pipe2IntegrityAssessment_niveau_risque(str, enum.Enum):
    FAIBLE = "faible"
    MODERE = "modere"
    ELEVE = "eleve"
    CRITIQUE = "critique"


class Pipe2IntegrityAssessment_statut(str, enum.Enum):
    EVALUE = "evalue"
    SURVEILLE = "surveille"
    RESTREINT = "restreint"
    COTEE = "cotee"


class Pipe2SpillResponseAction_statut(str, enum.Enum):
    DETECTE = "detecte"
    CONTENU = "contenu"
    DECONTAMINE = "decontamine"
    CLOTURE = "cloture"
    DECLARE_AUTORITE = "declare_autorite"


# ─── Modeles ──────────────────────────────────────────────────────────────────

class Pipe2CustodyTransfer(Base):
    """Transferts de custody."""
    __tablename__ = "pipe2_custody_transfers"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_pipe2_custody_transf_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    interface = Column(String(150), nullable=True)
    produit = Column(String(150), nullable=True)
    volume_livre = Column(Numeric, nullable=True)
    volume_recu = Column(Numeric, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Pipe2PressureLog(Base):
    """Releves de pression."""
    __tablename__ = "pipe2_pressure_logs"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_pipe2_pressure_logs_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    station = Column(String(150), nullable=True)
    pression_bar = Column(Numeric, nullable=True)
    date = Column(DateTime(timezone=True), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Pipe2PumpStationRead(Base):
    """Releves de station de pompage."""
    __tablename__ = "pipe2_pump_reads"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_pipe2_pump_reads_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    station = Column(String(150), nullable=True)
    debit = Column(Numeric, nullable=True)
    vibration = Column(Numeric, nullable=True)
    date = Column(DateTime(timezone=True), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Pipe2CorrosionReading(Base):
    """Releves de corrosion."""
    __tablename__ = "pipe2_corrosion"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_pipe2_corrosion_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    troncon = Column(String(150), nullable=True)
    epaisseur_mm = Column(Numeric, nullable=True)
    date = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Pipe2FlowCalibration(Base):
    """Etalonnages de debitmetre."""
    __tablename__ = "pipe2_flow_calibrations"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_pipe2_flow_calibrati_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    debitmetre = Column(String(150), nullable=True)
    coefficient = Column(Numeric, nullable=True)
    date = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Pipe2BatchQualityTest(Base):
    """Essais qualite de lot."""
    __tablename__ = "pipe2_batch_quality"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_pipe2_batch_quality_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    lot = Column(String(150), nullable=True)
    produit = Column(String(150), nullable=True)
    parametre = Column(String(150), nullable=True)
    date = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Pipe2InterfaceDetection(Base):
    """Detections d' interface."""
    __tablename__ = "pipe2_interface_detections"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_pipe2_interface_dete_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    troncon = Column(String(150), nullable=True)
    volume_interface = Column(Numeric, nullable=True)
    date = Column(DateTime(timezone=True), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Pipe2IntegrityAssessment(Base):
    """Evaluations d' integrite."""
    __tablename__ = "pipe2_integrity"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_pipe2_integrity_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    troncon = Column(String(150), nullable=True)
    niveau_risque = Column(String(150), nullable=True)
    pression_max = Column(Numeric, nullable=True)
    date = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Pipe2SpillResponseAction(Base):
    """Actions de reponse a deversement."""
    __tablename__ = "pipe2_spill_actions"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_pipe2_spill_actions_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    lieu = Column(String(150), nullable=True)
    volume_rejete = Column(Numeric, nullable=True)
    volume_recupere = Column(Numeric, nullable=True)
    date = Column(DateTime(timezone=True), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

