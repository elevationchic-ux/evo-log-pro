"""Modeles transport-aerien (expansion approfondie generee).

12 entites de gestion, chacune scoped par company_id.
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

class Aircraft_statut(str, enum.Enum):
    OPERATIONNEL = "operationnel"
    MAINTENANCE = "maintenance"
    STORE = "store"
    MISE_A_L_ECHANGE = "mise_a_l_echange"
    REFORME = "reforme"


class AirWaybill_type_awb(str, enum.Enum):
    MAWB = "mawb"
    HAWB = "hawb"


class AirWaybill_statut(str, enum.Enum):
    EMISE = "emise"
    EN_VOL = "en_vol"
    ARRIVEE = "arrivee"
    LIVREE = "livree"
    BLOQUEE = "bloquee"
    LITIGE = "litige"


class AirSlot_statut(str, enum.Enum):
    ATTRIBUE = "attribue"
    RETOURNE = "retourne"
    CONTESTE = "conteste"
    PERTE_HISTORIQUE = "perte_historique"
    TEMPORAIRE = "temporaire"


class GroundHandlingJob_statut(str, enum.Enum):
    PLANIFIE = "planifie"
    EN_COURS = "en_cours"
    TERMINE = "termine"
    RETARDE = "retarde"
    ANNULE = "annule"


class ULDInventory_type_uld(str, enum.Enum):
    AKE = "ake"
    AKH = "akh"
    ALA = "ala"
    PMC = "pmc"
    PAG = "pag"
    PLA = "pla"
    DKE = "dke"
    OTHER = "other"


class ULDInventory_etat(str, enum.Enum):
    BON = "bon"
    MOYEN = "moyen"
    REPARER = "reparer"
    REFORME = "reforme"


class ULDInventory_statut(str, enum.Enum):
    DISPONIBLE = "disponible"
    EN_SERVICE = "en_service"
    EN_TRANSIT = "en_transit"
    PERDU = "perdu"
    ENDOMMAGE = "endommage"


class CargoSecurityScreen_statut_expediteur(str, enum.Enum):
    RA = "ra"
    KC = "kc"
    AC = "ac"
    UNKNOWN = "unknown"


class CargoSecurityScreen_methode_screening(str, enum.Enum):
    RX = "rx"
    EXP = "exp"
    ETD = "etd"
    CHIMIQUE = "chimique"
    VISUEL = "visuel"
    BIEN_DETECTEUR = "bien_detecteur"


class CargoSecurityScreen_resultat(str, enum.Enum):
    CLAIR = "clair"
    SUSPECT = "suspect"
    SAISISSEMENT = "saisissement"


class CargoSecurityScreen_statut(str, enum.Enum):
    EN_ATTENTE = "en_attente"
    VALIDE = "valide"
    REJETE = "rejete"
    ESCALADE = "escalade"


class AirDangerousGoods_classe(str, enum.Enum):
    C1 = "c1"
    C2 = "c2"
    C3 = "c3"
    C4 = "c4"
    C5 = "c5"
    C6 = "c6"
    C7 = "c7"
    C8 = "c8"
    C9 = "c9"


class AirDangerousGoods_packaging_group(str, enum.Enum):
    I = "i"
    II = "ii"
    III = "iii"
    NA = "na"


class AirDangerousGoods_statut(str, enum.Enum):
    DECLARER = "declarer"
    ACCEPTE = "accepte"
    REFUSE = "refuse"
    TRANSFERT = "transfert"


class FlightOperation_statut(str, enum.Enum):
    PLANIFIE = "planifie"
    BARREE = "barree"
    DECOLLE = "decolle"
    EN_VOL = "en_vol"
    POSE = "pose"
    ANNULE = "annule"
    DEROUTE = "deroute"
    RETOUR_BASE = "retour_base"


class CrewRoster_role(str, enum.Enum):
    COMMANDANT = "commandant"
    COPILOT = "copilot"
    PNC_CHEF = "pnc_chef"
    PNC = "pnc"
    MéDECIN = "médecin"


class CrewRoster_statut(str, enum.Enum):
    PLANIFIE = "planifie"
    EN_SERVICE = "en_service"
    REPOS = "repos"
    MALADIE = "maladie"
    FORMATE = "formate"
    SUSPENDU = "suspendu"


class AircraftCheck_type_check(str, enum.Enum):
    A = "a"
    C = "c"
    D = "d"
    LOURDE = "lourde"
    ADR = "adr"
    SB = "sb"
    TROUVE = "trouve"


class AircraftCheck_statut(str, enum.Enum):
    PLANIFIE = "planifie"
    EN_COURS = "en_cours"
    TERMINE = "termine"
    SURSEAN = "sursean"
    ANNULE = "annule"


class AirportCargoWarehouse_statut(str, enum.Enum):
    ACTIF = "actif"
    SATURATION = "saturation"
    TRAVAUX = "travaux"
    FERME = "ferme"


class AirTariff_type_cargo(str, enum.Enum):
    GENERAL = "general"
    PERISSABLE = "perissable"
    DG = "dg"
    VIVANT = "vivant"
    DIPLO = "diplo"
    ECOM = "ecom"
    OTHER = "other"


class AirTariff_statut(str, enum.Enum):
    ACTIF = "actif"
    BROUILLON = "brouillon"
    EXPIRE = "expire"
    GELE = "gele"


# ─── Modeles ──────────────────────────────────────────────────────────────────

class Aircraft(Base):
    """Flotte aeronefs."""
    __tablename__ = "air_aircraft"
    __table_args__ = (
        UniqueConstraint('company_id', 'immatriculation', name='uix_air_aircraft_company_immatriculation'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    immatriculation = Column(String(150), nullable=False, index=True)
    modele = Column(String(150), nullable=True)
    operateur = Column(String(150), nullable=True)
    capacite_tonnes = Column(Integer, nullable=True)
    autonomie_km = Column(Integer, nullable=True)
    heures_vol_total = Column(Integer, nullable=True)
    certificat_navigabilite_fin = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class AirWaybill(Base):
    """Lia / lettres de transport aerien."""
    __tablename__ = "air_waybills"
    __table_args__ = (
        UniqueConstraint('company_id', 'numero_awb', name='uix_air_waybills_company_numero_awb'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    numero_awb = Column(String(150), nullable=False, index=True)
    type_awb = Column(String(150), nullable=True)
    expediteur = Column(String(150), nullable=True)
    destinataire = Column(String(150), nullable=True)
    aeroport_depart = Column(String(150), nullable=True)
    aeroport_arrivee = Column(String(150), nullable=True)
    nb_pieces = Column(Integer, nullable=True)
    poids_kg = Column(Integer, nullable=True)
    valeur_declaree_xaf = Column(Integer, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class AirSlot(Base):
    """Creneaux aeroportuaires."""
    __tablename__ = "air_slots"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_air_slots_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    aeroport = Column(String(150), nullable=True)
    season = Column(String(150), nullable=True)
    vol_attribue = Column(String(150), nullable=True)
    journee = Column(String(150), nullable=True)
    heure_obtc = Column(String(150), nullable=True)
    slot_historique = Column(Boolean, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class GroundHandlingJob(Base):
    """Traitement au sol."""
    __tablename__ = "air_handling_jobs"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_air_handling_jobs_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    vol = Column(String(150), nullable=True)
    aeroport = Column(String(150), nullable=True)
    date_traitement = Column(DateTime(timezone=True), nullable=True)
    prestataire = Column(String(150), nullable=True)
    nb_pieces_fret = Column(Integer, nullable=True)
    poids_fret_kg = Column(Integer, nullable=True)
    cout_xaf = Column(Integer, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ULDInventory(Base):
    """Parc ULD."""
    __tablename__ = "air_uld"
    __table_args__ = (
        UniqueConstraint('company_id', 'numero_uld', name='uix_air_uld_company_numero_uld'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    numero_uld = Column(String(150), nullable=False, index=True)
    type_uld = Column(String(150), nullable=True)
    proprietaire = Column(String(150), nullable=True)
    position_actuelle = Column(String(150), nullable=True)
    etat = Column(String(150), nullable=True)
    date_derniere_inspection = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class CargoSecurityScreen(Base):
    """Sûreté fret arien."""
    __tablename__ = "air_cargo_security"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_air_cargo_security_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    numero_awb = Column(String(150), nullable=True)
    statut_expediteur = Column(String(150), nullable=True)
    methode_screening = Column(String(150), nullable=True)
    date_screening = Column(DateTime(timezone=True), nullable=True)
    operateur = Column(String(150), nullable=True)
    resultat = Column(String(150), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class AirDangerousGoods(Base):
    """Marchandises dangereuses IATA."""
    __tablename__ = "air_dg_shipments"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_air_dg_shipments_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    numero_awb = Column(String(150), nullable=True)
    un_number = Column(String(150), nullable=True)
    classe = Column(String(150), nullable=True)
    packaging_group = Column(String(150), nullable=True)
    quantite = Column(String(150), nullable=True)
    etiquettes = Column(String(150), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class FlightOperation(Base):
    """Operations vol."""
    __tablename__ = "air_flight_operations"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_air_flight_operation_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    numero_vol = Column(String(150), nullable=True)
    aeronef = Column(String(150), nullable=True)
    aeroport_depart = Column(String(150), nullable=True)
    aeroport_arrivee = Column(String(150), nullable=True)
    date_std = Column(DateTime(timezone=True), nullable=True)
    date_sta = Column(DateTime(timezone=True), nullable=True)
    date_ata = Column(DateTime(timezone=True), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class CrewRoster(Base):
    """Navigation planning."""
    __tablename__ = "air_crew_rosters"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_air_crew_rosters_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    nom_membre = Column(String(150), nullable=True)
    role = Column(String(150), nullable=True)
    licence = Column(String(150), nullable=True)
    qualification = Column(String(150), nullable=True)
    date_prise_service = Column(DateTime(timezone=True), nullable=True)
    date_fin_service = Column(DateTime(timezone=True), nullable=True)
    heures_vol_mois = Column(Integer, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class AircraftCheck(Base):
    """Maintenance aeronefs (MRO)."""
    __tablename__ = "air_mro_checks"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_air_mro_checks_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    immatriculation = Column(String(150), nullable=True)
    type_check = Column(String(150), nullable=True)
    atelier = Column(String(150), nullable=True)
    date_debut = Column(Date, nullable=True)
    date_fin_prevue = Column(Date, nullable=True)
    date_retour_service = Column(Date, nullable=True)
    heures_arret = Column(Integer, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class AirportCargoWarehouse(Base):
    """Terminal fret aerien."""
    __tablename__ = "air_cargo_warehouses"
    __table_args__ = (
        UniqueConstraint('company_id', 'code_entrepot', name='uix_air_cargo_warehouses_company_code_entrepot'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    code_entrepot = Column(String(150), nullable=False, index=True)
    aeroport = Column(String(150), nullable=True)
    superficie_m2 = Column(Integer, nullable=True)
    capacite_palettes = Column(Integer, nullable=True)
    zones_froides = Column(Boolean, nullable=True)
    zone_douaniere = Column(Boolean, nullable=True)
    zone_surete = Column(Boolean, nullable=True)
    occupation_pct = Column(Integer, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class AirTariff(Base):
    """Tarification aerienne."""
    __tablename__ = "air_tariffs"
    __table_args__ = (
        UniqueConstraint('company_id', 'code_tarif', name='uix_air_tariffs_company_code_tarif'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    code_tarif = Column(String(150), nullable=False, index=True)
    origine = Column(String(150), nullable=True)
    destination = Column(String(150), nullable=True)
    poids_min_kg = Column(Integer, nullable=True)
    type_cargo = Column(String(150), nullable=True)
    prix_par_kg_xaf = Column(Integer, nullable=True)
    surcharges_xaf = Column(Integer, nullable=True)
    validite_debut = Column(Date, nullable=True)
    validite_fin = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

