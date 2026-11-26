"""Modeles transport-ferroviaire (expansion approfondie generee).

7 entites de gestion, chacune scoped par company_id.
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

class RailWheelSet_statut(str, enum.Enum):
    EN_SERVICE = "en_service"
    ATELIER = "atelier"
    REBUT = "rebut"


class RailLoadingGauge_statut(str, enum.Enum):
    ACTIF = "actif"
    RESTRICTION = "restriction"
    SUSPENDU = "suspendu"


class RailShuntingPlan_statut(str, enum.Enum):
    PLANIFIE = "planifie"
    EN_COURS = "en_cours"
    TERMINE = "termine"
    INTERROMPU = "interrompu"


class RailTrainConsist_statut(str, enum.Enum):
    EN_COURS = "en_cours"
    VALIDE = "valide"
    PARTI = "parti"
    MODIFIE = "modifie"


class RailPathOccupancy_statut(str, enum.Enum):
    RESERVE = "reserve"
    OCCUPE = "occupe"
    LIBERE = "libere"
    CONFLIT = "conflit"
    ANNULE = "annule"


class RailWagonDispatch_statut(str, enum.Enum):
    AFFECTE = "affecte"
    CHARGE = "charge"
    EN_ROUTE = "en_route"
    LIVRE = "livre"
    RESTITUE = "restitue"


class RailTerminalCrane_type(str, enum.Enum):
    PORTIQUE = "portique"
    REACH_STACKER = "reach_stacker"
    RMG = "rmg"
    RTG = "rtg"


class RailTerminalCrane_statut(str, enum.Enum):
    DISPONIBLE = "disponible"
    EN_COURS = "en_cours"
    PANNE = "panne"
    MAINTENANCE = "maintenance"


# ─── Modeles ──────────────────────────────────────────────────────────────────

class RailWheelSet(Base):
    """Essieux et roulements."""
    __tablename__ = "railb_wheel_sets"
    __table_args__ = (
        UniqueConstraint('company_id', 'numero_essieu', name='uix_railb_wheel_sets_company_numero_essieu'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    numero_essieu = Column(String(150), nullable=False, index=True)
    type_essieu = Column(String(150), nullable=True)
    diametre_mm = Column(Integer, nullable=True)
    km_parcourus = Column(Integer, nullable=True)
    date_controle = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class RailLoadingGauge(Base):
    """Gabarit de chargement."""
    __tablename__ = "railb_loading_gauges"
    __table_args__ = (
        UniqueConstraint('company_id', 'code_gabarit', name='uix_railb_loading_gauges_company_code_gabarit'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    code_gabarit = Column(String(150), nullable=False, index=True)
    ligne = Column(String(150), nullable=True)
    largeur_max_mm = Column(Integer, nullable=True)
    hauteur_max_mm = Column(Integer, nullable=True)
    masse_max_t = Column(Integer, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class RailShuntingPlan(Base):
    """Plans de manoeuvre."""
    __tablename__ = "railb_shunting_plans"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_railb_shunting_plans_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    yard = Column(String(150), nullable=True)
    voie_source = Column(String(150), nullable=True)
    voie_destinataire = Column(String(150), nullable=True)
    nb_wagons = Column(Integer, nullable=True)
    operateur = Column(String(150), nullable=True)
    date_plan = Column(DateTime(timezone=True), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class RailTrainConsist(Base):
    """Composition de train."""
    __tablename__ = "railb_train_consists"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_railb_train_consists_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    numero_train = Column(String(150), nullable=True)
    nb_wagons = Column(Integer, nullable=True)
    masse_total_t = Column(Integer, nullable=True)
    longueur_m = Column(Integer, nullable=True)
    locomotive = Column(String(150), nullable=True)
    date_composition = Column(DateTime(timezone=True), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class RailPathOccupancy(Base):
    """Occupation de sillons."""
    __tablename__ = "railb_path_occupancy"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_railb_path_occupancy_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    numero_train = Column(String(150), nullable=True)
    section = Column(String(150), nullable=True)
    date_debut = Column(DateTime(timezone=True), nullable=True)
    date_fin = Column(DateTime(timezone=True), nullable=True)
    attribue_par = Column(String(150), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class RailWagonDispatch(Base):
    """Affectation wagons."""
    __tablename__ = "railb_wagon_dispatch"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_railb_wagon_dispatch_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    numero_wagon = Column(String(150), nullable=True)
    client = Column(String(150), nullable=True)
    destination = Column(String(150), nullable=True)
    produit = Column(String(150), nullable=True)
    date_affectation = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class RailTerminalCrane(Base):
    """Portiques terminaux fer."""
    __tablename__ = "railb_terminal_cranes"
    __table_args__ = (
        UniqueConstraint('company_id', 'code_equipment', name='uix_railb_terminal_crane_company_code_equipment'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    code_equipment = Column(String(150), nullable=False, index=True)
    terminal = Column(String(150), nullable=True)
    type = Column(String(150), nullable=True)
    capacite_tonnes = Column(Integer, nullable=True)
    portee_m = Column(Integer, nullable=True)
    date_prochaine_visite = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

