"""Modeles transport-aerien (expansion approfondie generee).

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

class HouseAirWaybill_statut(str, enum.Enum):
    EMIS = "emis"
    CONSOLIDE = "consolide"
    CHARGE = "charge"
    LIVRE = "livre"
    LITIGE = "litige"


class PerishableCargo_statut(str, enum.Enum):
    RECU = "recu"
    CHAMBRE_FROIDE = "chambre_froide"
    EMBARQUE = "embarque"
    LIVRE = "livre"
    RUPTURE_CHAINE = "rupture_chaine"


class LiveAnimalShipment_type_conteneur(str, enum.Enum):
    CR1 = "cr1"
    CR2 = "cr2"
    CR3 = "cr3"
    CONTAINER = "container"


class LiveAnimalShipment_statut(str, enum.Enum):
    RESERVE = "reserve"
    ACCEPTE = "accepte"
    EN_VOL = "en_vol"
    ARRIVE = "arrive"
    REFUSE = "refuse"


class CharteredFlight_statut(str, enum.Enum):
    DEVIS = "devis"
    CONFIRME = "confirme"
    EFFECTUE = "effectue"
    ANNULE = "annule"


class AirCustomsClearance_type_operation(str, enum.Enum):
    IMPORT = "import"
    EXPORT = "export"
    TRANSIT = "transit"


class AirCustomsClearance_statut(str, enum.Enum):
    EN_ATTENTE = "en_attente"
    DEPOSE = "depose"
    CONTROLE = "controle"
    DECHARGE = "decharge"
    BLOQUE = "bloque"


class ApronMovement_type_mouvement(str, enum.Enum):
    ARRIVEE = "arrivee"
    DEPART = "depart"
    PUSHBACK = "pushback"
    REPOSITIONNEMENT = "repositionnement"


class ApronMovement_statut(str, enum.Enum):
    PLANIFIE = "planifie"
    EN_COURS = "en_cours"
    TERMINE = "termine"
    RETARDE = "retarde"


class NoiseComplianceRecord_creneau(str, enum.Enum):
    JOUR = "jour"
    SOIREE = "soiree"
    NUIT = "nuit"


class NoiseComplianceRecord_statut(str, enum.Enum):
    CONFORME = "conforme"
    DEPASSEMENT = "depassement"
    SANCTIONNE = "sanctionne"
    EXEMPT = "exempt"


# ─── Modeles ──────────────────────────────────────────────────────────────────

class HouseAirWaybill(Base):
    """Lettres de transport house (HAWB)."""
    __tablename__ = "airb_house_waybills"
    __table_args__ = (
        UniqueConstraint('company_id', 'numero_hawb', name='uix_airb_house_waybills_company_numero_hawb'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    numero_hawb = Column(String(150), nullable=False, index=True)
    numero_mawb = Column(String(150), nullable=True)
    expediteur = Column(String(150), nullable=True)
    destinataire = Column(String(150), nullable=True)
    nb_colis = Column(Integer, nullable=True)
    poids_kg = Column(Integer, nullable=True)
    nature_marchandise = Column(String(150), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class PerishableCargo(Base):
    """Fret perishable (chaine du froid)."""
    __tablename__ = "airb_perishable_cargo"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_airb_perishable_carg_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    numero_mawb = Column(String(150), nullable=True)
    produit = Column(String(150), nullable=True)
    plage_temp_c = Column(String(150), nullable=True)
    poids_kg = Column(Integer, nullable=True)
    date_embarquement = Column(DateTime(timezone=True), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class LiveAnimalShipment(Base):
    """Fret vivant (animaux)."""
    __tablename__ = "airb_live_animals"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_airb_live_animals_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    numero_mawb = Column(String(150), nullable=True)
    espece = Column(String(150), nullable=True)
    nb_animaux = Column(Integer, nullable=True)
    type_conteneur = Column(String(150), nullable=True)
    date_depart = Column(DateTime(timezone=True), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class CharteredFlight(Base):
    """Vols affretes."""
    __tablename__ = "airb_chartered_flights"
    __table_args__ = (
        UniqueConstraint('company_id', 'numero_affretement', name='uix_airb_chartered_fligh_company_numero_affretem'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    numero_affretement = Column(String(150), nullable=False, index=True)
    client = Column(String(150), nullable=True)
    immatriculation = Column(String(150), nullable=True)
    depart_aeroport = Column(String(150), nullable=True)
    arrivee_aeroport = Column(String(150), nullable=True)
    capacite_tonnes = Column(Integer, nullable=True)
    date_vol = Column(DateTime(timezone=True), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class AirCustomsClearance(Base):
    """Dedouanement fret aerien."""
    __tablename__ = "airb_customs_clearance"
    __table_args__ = (
        UniqueConstraint('company_id', 'numero_dossier', name='uix_airb_customs_clearan_company_numero_dossier'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    numero_dossier = Column(String(150), nullable=False, index=True)
    numero_mawb = Column(String(150), nullable=True)
    type_operation = Column(String(150), nullable=True)
    bureau_douane = Column(String(150), nullable=True)
    droits_xaf = Column(Integer, nullable=True)
    date_depot = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ApronMovement(Base):
    """Mouvements piste (apron)."""
    __tablename__ = "airb_apron_movements"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_airb_apron_movements_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    poste_parc = Column(String(150), nullable=True)
    immatriculation = Column(String(150), nullable=True)
    type_mouvement = Column(String(150), nullable=True)
    date_debut = Column(DateTime(timezone=True), nullable=True)
    date_fin = Column(DateTime(timezone=True), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class NoiseComplianceRecord(Base):
    """Conformite nuisances sonores."""
    __tablename__ = "airb_noise_compliance"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_airb_noise_complianc_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    immatriculation = Column(String(150), nullable=True)
    coefficient_bruit_db = Column(Integer, nullable=True)
    creneau = Column(String(150), nullable=True)
    date_mesure = Column(Date, nullable=True)
    quota_consomme = Column(Integer, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

