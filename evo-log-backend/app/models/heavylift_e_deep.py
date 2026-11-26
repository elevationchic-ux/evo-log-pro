"""Modeles convoi-exceptionnel (expansion approfondie generee).

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

class Heavy2LiftPlan_statut(str, enum.Enum):
    ETUDIE = "etudie"
    VALIDE = "valide"
    EN_COURS = "en_cours"
    CLOTURE = "cloture"


class Heavy2RouteSurvey_statut(str, enum.Enum):
    PLANIFIEE = "planifiee"
    FAITE = "faite"
    Faisable = "faisable"
    BLOQUANTE = "bloquante"


class Heavy2EscortSchedule_statut(str, enum.Enum):
    PLANIFIEE = "planifiee"
    AFFECTEE = "affectee"
    EN_COURS = "en_cours"
    TERMINEE = "terminee"


class Heavy2LoadMomentCalc_statut(str, enum.Enum):
    CALCULE = "calcule"
    CONFORME = "conforme"
    LIMITE = "limite"
    DEPASSE = "depasse"


class Heavy2CraneSetupRecord_statut(str, enum.Enum):
    MONTEE = "montee"
    TESTEE = "testee"
    EXPLOITATION = "exploitation"
    DEMONTEE = "demontee"


class Heavy2PermitObtention_statut(str, enum.Enum):
    DEMANDE = "demande"
    INSTRUIT = "instruit"
    OCTROYE = "octroye"
    REFUSE = "refuse"
    EXPIRE = "expire"


class Heavy2LashingRig_statut(str, enum.Enum):
    CONCU = "concu"
    POSE = "pose"
    CONTROLE = "controle"
    REFAIRE = "refaire"


class Heavy2AxleLoadReading_statut(str, enum.Enum):
    CONFORME = "conforme"
    LIMITE = "limite"
    DEPASSEE = "depassee"
    REPARTIR = "repartir"


class Heavy2ConvoyStagingReport_statut(str, enum.Enum):
    PLANIFIE = "planifie"
    RASSEMBLE = "rassemble"
    PARTI = "parti"
    RETARDE = "retarde"
    ANNULE = "annule"


# ─── Modeles ──────────────────────────────────────────────────────────────────

class Heavy2LiftPlan(Base):
    """Plans de levage."""
    __tablename__ = "heavy2_lift_plans"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_heavy2_lift_plans_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    charge = Column(String(150), nullable=True)
    poids_tonnes = Column(Numeric, nullable=True)
    portee_m = Column(Numeric, nullable=True)
    date = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Heavy2RouteSurvey(Base):
    """Reconnaissances d' itineraire."""
    __tablename__ = "heavy2_route_surveys"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_heavy2_route_surveys_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    itineraire = Column(String(150), nullable=True)
    largeur_m = Column(Numeric, nullable=True)
    hauteur_m = Column(Numeric, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Heavy2EscortSchedule(Base):
    """Planning d' escortes."""
    __tablename__ = "heavy2_escorts"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_heavy2_escorts_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    convoi = Column(String(150), nullable=True)
    nb_vehicules = Column(Integer, nullable=True)
    debut = Column(DateTime(timezone=True), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Heavy2LoadMomentCalc(Base):
    """Calculs de moment de charge."""
    __tablename__ = "heavy2_load_moment"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_heavy2_load_moment_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    configuration = Column(String(150), nullable=True)
    moment_applique = Column(Numeric, nullable=True)
    capacite = Column(Numeric, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Heavy2CraneSetupRecord(Base):
    """Montages de grue."""
    __tablename__ = "heavy2_crane_setup"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_heavy2_crane_setup_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    grue = Column(String(150), nullable=True)
    portance_sol = Column(String(150), nullable=True)
    date = Column(DateTime(timezone=True), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Heavy2PermitObtention(Base):
    """Obtentions d' autorisation."""
    __tablename__ = "heavy2_permits"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_heavy2_permits_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    convoi = Column(String(150), nullable=True)
    autorite = Column(String(150), nullable=True)
    validite = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Heavy2LashingRig(Base):
    """Dispositifs d' arrimage."""
    __tablename__ = "heavy2_lashing"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_heavy2_lashing_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    charge = Column(String(150), nullable=True)
    nb_sangles = Column(Integer, nullable=True)
    angle_deg = Column(Integer, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Heavy2AxleLoadReading(Base):
    """Releves de charge par essieu."""
    __tablename__ = "heavy2_axle_loads"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_heavy2_axle_loads_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    vehicule = Column(String(150), nullable=True)
    essieu = Column(Integer, nullable=True)
    charge_t = Column(Numeric, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Heavy2ConvoyStagingReport(Base):
    """Comptes-rendus de rassemblement."""
    __tablename__ = "heavy2_staging"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_heavy2_staging_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    convoi = Column(String(150), nullable=True)
    lieu_rassemblement = Column(String(150), nullable=True)
    depart = Column(DateTime(timezone=True), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

