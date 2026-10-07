"""Modeles transport-fluvial (expansion approfondie generee).

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

class FluvialCanalSection_statut(str, enum.Enum):
    OUVERT = "ouvert"
    RESTRICTION = "restriction"
    TRAVAUX = "travaux"
    FERME = "ferme"


class FluvialConvoy_statut(str, enum.Enum):
    CONSTITUE = "constitue"
    EN_ROUTE = "en_route"
    ARRIVE = "arrive"
    DISSOCIE = "dissocie"


class FluvialBallastOperation_type_operation(str, enum.Enum):
    LESTAGE = "lestage"
    DELESTAGE = "delestage"


class FluvialBallastOperation_statut(str, enum.Enum):
    PLANIFIE = "planifie"
    EN_COURS = "en_cours"
    TERMINE = "termine"


class FluvialWaterGauge_statut(str, enum.Enum):
    NORMAL = "normal"
    BASE = "base"
    CREUE = "creue"
    CRUE = "crue"


class FluvialBerthingSlot_statut(str, enum.Enum):
    RESERVE = "reserve"
    OCCUPE = "occupe"
    LIBERE = "libere"
    ANNULE = "annule"


class FluvialCrewRoster_statut(str, enum.Enum):
    PLANIFIE = "planifie"
    EN_SERVICE = "en_service"
    REPOS = "repos"
    TERMINE = "termine"


class FluvialCargoManifest_statut(str, enum.Enum):
    EMISE = "emise"
    CHARGEE = "chargee"
    EN_ROUTE = "en_route"
    LIVRE = "livre"
    CLOTURE = "cloture"


class FluvialPortFee_categorie(str, enum.Enum):
    STATIONNEMENT = "stationnement"
    MANUTENTION = "manutention"
    PASSAGE = "passage"
    OUTILLAGE = "outillage"


class FluvialPortFee_statut(str, enum.Enum):
    ACTIF = "actif"
    BROUILLON = "brouillon"
    EXPIRE = "expire"


class FluvialVesselInspection_type_visite(str, enum.Enum):
    INITIALE = "initiale"
    PERIODIQUE = "periodique"
    SUPPLEMENTAIRE = "supplementaire"
    IMPREVUE = "imprevue"


class FluvialVesselInspection_resultat(str, enum.Enum):
    CONFORME = "conforme"
    RESERVE = "reserve"
    NON_CONFORME = "non_conforme"


class FluvialVesselInspection_statut(str, enum.Enum):
    PLANIFIEE = "planifiee"
    EN_COURS = "en_cours"
    VALIDEE = "validee"
    EXPIREE = "expiree"


# ─── Modeles ──────────────────────────────────────────────────────────────────

class FluvialCanalSection(Base):
    """Sections de voie navigable."""
    __tablename__ = "flvb_canal_sections"
    __table_args__ = (
        UniqueConstraint('company_id', 'code_section', name='uix_flvb_canal_sections_company_code_section'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    code_section = Column(String(150), nullable=False, index=True)
    nom_bief = Column(String(150), nullable=True)
    longueur_km = Column(Integer, nullable=True)
    nb_ecluses = Column(Integer, nullable=True)
    gabarit_max_t = Column(Integer, nullable=True)
    profondeur_cote_cm = Column(Integer, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class FluvialConvoy(Base):
    """Convois pousses."""
    __tablename__ = "flvb_convoys"
    __table_args__ = (
        UniqueConstraint('company_id', 'numero_convoi', name='uix_flvb_convoys_company_numero_convoi'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    numero_convoi = Column(String(150), nullable=False, index=True)
    pousseur = Column(String(150), nullable=True)
    nb_peniches = Column(Integer, nullable=True)
    masse_total_t = Column(Integer, nullable=True)
    longueur_total_m = Column(Integer, nullable=True)
    itineraire = Column(String(150), nullable=True)
    date_depart = Column(DateTime(timezone=True), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class FluvialBallastOperation(Base):
    """Lestage / delestage."""
    __tablename__ = "flvb_ballast_ops"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_flvb_ballast_ops_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    numero_flotte = Column(String(150), nullable=True)
    type_operation = Column(String(150), nullable=True)
    masse_balle_t = Column(Integer, nullable=True)
    date_operation = Column(DateTime(timezone=True), nullable=True)
    terminal = Column(String(150), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class FluvialWaterGauge(Base):
    """Echelles d eau / limnimetres."""
    __tablename__ = "flvb_water_gauges"
    __table_args__ = (
        UniqueConstraint('company_id', 'code_poste', name='uix_flvb_water_gauges_company_code_poste'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    code_poste = Column(String(150), nullable=False, index=True)
    nom_poste = Column(String(150), nullable=True)
    bief = Column(String(150), nullable=True)
    cote_cm = Column(Integer, nullable=True)
    cote_seuil_restr_cm = Column(Integer, nullable=True)
    date_releve = Column(DateTime(timezone=True), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class FluvialBerthingSlot(Base):
    """Creneaux d amarrage."""
    __tablename__ = "flvb_berthing_slots"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_flvb_berthing_slots_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    terminal = Column(String(150), nullable=True)
    numero_appontement = Column(String(150), nullable=True)
    numero_flotte = Column(String(150), nullable=True)
    date_debut = Column(DateTime(timezone=True), nullable=True)
    date_fin = Column(DateTime(timezone=True), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class FluvialCrewRoster(Base):
    """Equipages fluviaux."""
    __tablename__ = "flvb_crew_rosters"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_flvb_crew_rosters_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    numero_flotte = Column(String(150), nullable=True)
    chef_bord = Column(String(150), nullable=True)
    nb_marins = Column(Integer, nullable=True)
    date_debut = Column(Date, nullable=True)
    date_fin = Column(Date, nullable=True)
    heures_service = Column(Integer, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class FluvialCargoManifest(Base):
    """Manifestes de chargement fluviaux."""
    __tablename__ = "flvb_cargo_manifests"
    __table_args__ = (
        UniqueConstraint('company_id', 'numero_manifeste', name='uix_flvb_cargo_manifests_company_numero_manifest'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    numero_manifeste = Column(String(150), nullable=False, index=True)
    numero_convoi = Column(String(150), nullable=True)
    terminal_depart = Column(String(150), nullable=True)
    terminal_arrivee = Column(String(150), nullable=True)
    nb_colis = Column(Integer, nullable=True)
    masse_total_t = Column(Integer, nullable=True)
    date_emission = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class FluvialPortFee(Base):
    """Droits de port fluvial."""
    __tablename__ = "flvb_port_fees"
    __table_args__ = (
        UniqueConstraint('company_id', 'code_tarif', name='uix_flvb_port_fees_company_code_tarif'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    code_tarif = Column(String(150), nullable=False, index=True)
    terminal = Column(String(150), nullable=True)
    categorie = Column(String(150), nullable=True)
    assiette = Column(String(150), nullable=True)
    montant_xaf = Column(Integer, nullable=True)
    unite = Column(String(150), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class FluvialVesselInspection(Base):
    """Visites techniques batellerie."""
    __tablename__ = "flvb_vessel_inspections"
    __table_args__ = (
        UniqueConstraint('company_id', 'numero_pv', name='uix_flvb_vessel_inspecti_company_numero_pv'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    numero_pv = Column(String(150), nullable=False, index=True)
    numero_flotte = Column(String(150), nullable=True)
    type_visite = Column(String(150), nullable=True)
    date_visite = Column(Date, nullable=True)
    date_echeance = Column(Date, nullable=True)
    resultat = Column(String(150), nullable=True)
    observations = Column(Text(2000), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

