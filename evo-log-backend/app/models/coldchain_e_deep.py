"""Modeles chaine-froid (expansion approfondie generee).

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

class Cold2TemperatureLog_statut(str, enum.Enum):
    CONFORME = "conforme"
    HAUTE = "haute"
    BASSE = "basse"
    ALERTE = "alerte"


class Cold2ColdExcursion_statut(str, enum.Enum):
    DETECTEE = "detectee"
    EVALUEE = "evaluee"
    PRODUIT_OK = "produit_ok"
    PRODUIT_PERDU = "produit_perdu"


class Cold2ProbeCalibration_statut(str, enum.Enum):
    CONFORME = "conforme"
    AJUSTEE = "ajustee"
    HORS_TOLERANCE = "hors_tolerance"
    REMPLACER = "remplacer"


class Cold2BlastFreezeCycle_statut(str, enum.Enum):
    EN_COURS = "en_cours"
    REUSSI = "reussi"
    INCOMPLET = "incomplet"
    REPETE = "repete"


class Cold2DoorOpenEvent_statut(str, enum.Enum):
    NOMINAL = "nominal"
    LONG = "long"
    FORCE = "force"
    DEFECTUEUX = "defectueux"


class Cold2HumidityLog_statut(str, enum.Enum):
    CONFORME = "conforme"
    SEC = "sec"
    HUMIDE = "humide"
    ALERTE = "alerte"


class Cold2RefrigerantCharge_statut(str, enum.Enum):
    PLEIN = "plein"
    BAS = "bas"
    FUITE = "fuite"
    RECHARGE = "recharge"


class Cold2ShipmentApproval_statut(str, enum.Enum):
    EN_ATTENTE = "en_attente"
    APPROUVE = "approuve"
    REFUSE = "refuse"
    REPORTE = "reporte"


class Cold2IceBatteryCharge_niveau_gel(str, enum.Enum):
    TOTAL = "total"
    PARTIEL = "partiel"
    IMPACT = "impact"


class Cold2IceBatteryCharge_statut(str, enum.Enum):
    EN_GEL = "en_gel"
    PRET = "pret"
    UTILISE = "utilise"
    A_REGELER = "a_regeler"


# ─── Modeles ──────────────────────────────────────────────────────────────────

class Cold2TemperatureLog(Base):
    """Releves de temperature."""
    __tablename__ = "cold2_temperature_logs"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_cold2_temperature_lo_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    unite = Column(String(150), nullable=True)
    temperature = Column(Numeric, nullable=True)
    date = Column(DateTime(timezone=True), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Cold2ColdExcursion(Base):
    """Excursions de temperature."""
    __tablename__ = "cold2_excursions"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_cold2_excursions_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    cargaison = Column(String(150), nullable=True)
    temperature_max = Column(Numeric, nullable=True)
    duree_min = Column(Integer, nullable=True)
    date = Column(DateTime(timezone=True), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Cold2ProbeCalibration(Base):
    """Etalonnages de sonde."""
    __tablename__ = "cold2_probe_calibrations"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_cold2_probe_calibrat_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    sonde = Column(String(150), nullable=True)
    ecart = Column(Numeric, nullable=True)
    date = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Cold2BlastFreezeCycle(Base):
    """Cycles de surgelation."""
    __tablename__ = "cold2_blast_cycles"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_cold2_blast_cycles_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    produit = Column(String(150), nullable=True)
    temp_finale = Column(Numeric, nullable=True)
    duree_min = Column(Integer, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Cold2DoorOpenEvent(Base):
    """Evenements d' ouverture de porte."""
    __tablename__ = "cold2_door_events"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_cold2_door_events_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    chambre = Column(String(150), nullable=True)
    duree_sec = Column(Integer, nullable=True)
    date = Column(DateTime(timezone=True), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Cold2HumidityLog(Base):
    """Releves d' hygrometrie."""
    __tablename__ = "cold2_humidity_logs"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_cold2_humidity_logs_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    chambre = Column(String(150), nullable=True)
    humidite_pct = Column(Numeric, nullable=True)
    date = Column(DateTime(timezone=True), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Cold2RefrigerantCharge(Base):
    """Recharges de fluide frigorigene."""
    __tablename__ = "cold2_refrigerant"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_cold2_refrigerant_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    circuit = Column(String(150), nullable=True)
    fluide = Column(String(150), nullable=True)
    quantite_kg = Column(Numeric, nullable=True)
    date = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Cold2ShipmentApproval(Base):
    """Validations d' expedition froide."""
    __tablename__ = "cold2_ship_approvals"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_cold2_ship_approvals_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    cargaison = Column(String(150), nullable=True)
    temp_chargement = Column(Numeric, nullable=True)
    valideur = Column(String(150), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Cold2IceBatteryCharge(Base):
    """Recharges de batteries de glace."""
    __tablename__ = "cold2_ice_batteries"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_cold2_ice_batteries_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    caisson = Column(String(150), nullable=True)
    niveau_gel = Column(String(150), nullable=True)
    date = Column(DateTime(timezone=True), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

