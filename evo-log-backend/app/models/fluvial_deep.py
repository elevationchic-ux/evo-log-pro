"""Modeles transport-fluvial (expansion approfondie generee).

10 entites de gestion, chacune scoped par company_id.
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

class FluvialBarge_type(str, enum.Enum):
    PENICHE = "peniche"
    CHALAND = "chaland"
    AUTOMOTEUR = "automoteur"
    Pousse_pousse = "pousse_pousse"
    TANKER_FLUV = "tanker_fluv"
    CONTENEURS = "conteneurs"


class FluvialBarge_statut(str, enum.Enum):
    OPERATIONNEL = "operationnel"
    ATELIER = "atelier"
    ARRETE_SAISON = "arrete_saison"
    REFORME = "reforme"


class FluvialTowboat_statut(str, enum.Enum):
    OPERATIONNEL = "operationnel"
    PANNE = "panne"
    MAINTENANCE = "maintenance"


class LockTransit_statut(str, enum.Enum):
    PLANIFIE = "planifie"
    EN_ATTENTE = "en_attente"
    EN_COURS = "en_cours"
    PASSAGE_OK = "passage_ok"
    REFUSE = "refuse"
    REPORTE = "reporte"


class RiverDepthSurvey_statut(str, enum.Enum):
    NORMAL = "normal"
    RESTRITIF = "restritif"
    CRUE = "crue"
    EPROUVE = "eprouve"
    BLOCAGE = "blocage"


class FluvialTerminal_statut(str, enum.Enum):
    ACTIF = "actif"
    TRAVAUX = "travaux"
    FERME = "ferme"
    PROJET = "projet"


class FluvialBulkOperation_categorie(str, enum.Enum):
    SOLIDE = "solide"
    LIQUIDE = "liquide"
    GATEUX = "gateux"


class FluvialBulkOperation_statut(str, enum.Enum):
    PLANIFIE = "planifie"
    EN_COURS = "en_cours"
    TERMINE = "termine"
    INTERROMPU = "interrompu"


class FluvialSafetyRecord_type_evenement(str, enum.Enum):
    ECHELLEMENT = "echellement"
    COLLISION = "collision"
    COULEMENT = "coulement"
    INCENDIE = "incendie"
    PANNE_MOTOR = "panne_motor"
    Balisage = "balisage"
    AUTRE = "autre"


class FluvialSafetyRecord_gravite(str, enum.Enum):
    NEANT = "neant"
    MINEURE = "mineure"
    MAJEURE = "majeure"
    CRITIQUE = "critique"


class FluvialSafetyRecord_statut(str, enum.Enum):
    OUVERT = "ouvert"
    ENQUETE = "enquete"
    CLOTURE = "cloture"
    TRANSFERT_JUSTICE = "transfert_justice"


class FluvialTariff_saisonnalite(str, enum.Enum):
    HAUTE_EAU = "haute_eau"
    BASSE_EAU = "basse_eau"
    NORMALE = "normale"


class FluvialTariff_statut(str, enum.Enum):
    ACTIF = "actif"
    BROUILLON = "brouillon"
    EXPIRE = "expire"
    GELE = "gele"


class FluvialWaybill_statut(str, enum.Enum):
    EMISE = "emise"
    CHARGEE = "chargee"
    TRANSIT = "transit"
    LIVREE = "livree"
    LITIGE = "litige"


class FluvialPosition_statut(str, enum.Enum):
    EN_MOUVEMENT = "en_mouvement"
    AMARRE = "amarre"
    ATTENTE_ECLUSE = "attente_ecluse"
    ARRET_TECHNIQUE = "arret_technique"
    PERDU = "perdu"


# ─── Modeles ──────────────────────────────────────────────────────────────────

class FluvialBarge(Base):
    """Flotte peniches / chalands."""
    __tablename__ = "fluv_barges"
    __table_args__ = (
        UniqueConstraint('company_id', 'numero_flotte', name='uix_fluv_barges_company_numero_flotte'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    numero_flotte = Column(String(150), nullable=False, index=True)
    type = Column(String(150), nullable=True)
    capacite_tonnes = Column(Integer, nullable=True)
    tirant_eau_max_m = Column(String(150), nullable=True)
    longueur_m = Column(Integer, nullable=True)
    largeur_m = Column(Integer, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class FluvialTowboat(Base):
    """Remorqueurs fluviaux."""
    __tablename__ = "fluv_towboats"
    __table_args__ = (
        UniqueConstraint('company_id', 'numero_tug', name='uix_fluv_towboats_company_numero_tug'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    numero_tug = Column(String(150), nullable=False, index=True)
    nom = Column(String(150), nullable=True)
    puissance_kw = Column(Integer, nullable=True)
    bollard_pull_t = Column(Integer, nullable=True)
    zone_operation = Column(String(150), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class LockTransit(Base):
    """Transits d'ecluses."""
    __tablename__ = "fluv_lock_transits"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_fluv_lock_transits_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    nom_ecluse = Column(String(150), nullable=True)
    date_passage = Column(DateTime(timezone=True), nullable=True)
    numero_peniche = Column(String(150), nullable=True)
    masse_tonnes = Column(Integer, nullable=True)
    tirant_eau_m = Column(String(150), nullable=True)
    attente_minutes = Column(Integer, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class RiverDepthSurvey(Base):
    """Sondes bathymetriques."""
    __tablename__ = "fluv_depth_surveys"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_fluv_depth_surveys_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    bief = Column(String(150), nullable=True)
    date_mesure = Column(Date, nullable=True)
    profondeur_min_cm = Column(Integer, nullable=True)
    tirant_eau_pmax_cm = Column(Integer, nullable=True)
    debit_m3s = Column(Integer, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class FluvialTerminal(Base):
    """Terminaux fluviaux."""
    __tablename__ = "fluv_terminals"
    __table_args__ = (
        UniqueConstraint('company_id', 'code_terminal', name='uix_fluv_terminals_company_code_terminal'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    code_terminal = Column(String(150), nullable=False, index=True)
    nom = Column(String(150), nullable=True)
    fleuve = Column(String(150), nullable=True)
    pays = Column(String(150), nullable=True)
    nb_appontements = Column(Integer, nullable=True)
    longueur_quai_m = Column(Integer, nullable=True)
    connecte_port_maritime = Column(Boolean, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class FluvialBulkOperation(Base):
    """Vrac fluvial."""
    __tablename__ = "fluv_bulk_operations"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_fluv_bulk_operations_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    produit = Column(String(150), nullable=True)
    categorie = Column(String(150), nullable=True)
    quantite_tonnes = Column(Integer, nullable=True)
    terminal = Column(String(150), nullable=True)
    date_operation = Column(DateTime(timezone=True), nullable=True)
    duree_heures = Column(Integer, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class FluvialSafetyRecord(Base):
    """Securite navigation."""
    __tablename__ = "fluv_safety_records"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_fluv_safety_records_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    date_evenement = Column(DateTime(timezone=True), nullable=True)
    bief = Column(String(150), nullable=True)
    type_evenement = Column(String(150), nullable=True)
    gravite = Column(String(150), nullable=True)
    batiments_impliques = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class FluvialTariff(Base):
    """Tarification fluviale."""
    __tablename__ = "fluv_tariffs"
    __table_args__ = (
        UniqueConstraint('company_id', 'code_tarif', name='uix_fluv_tariffs_company_code_tarif'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    code_tarif = Column(String(150), nullable=False, index=True)
    bief = Column(String(150), nullable=True)
    produit = Column(String(150), nullable=True)
    prix_par_tonne_xaf = Column(Integer, nullable=True)
    saisonnalite = Column(String(150), nullable=True)
    remise_volume_pct = Column(Integer, nullable=True)
    validite_debut = Column(Date, nullable=True)
    validite_fin = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class FluvialWaybill(Base):
    """Lettres de voiture fluviale CMNI."""
    __tablename__ = "fluv_waybills"
    __table_args__ = (
        UniqueConstraint('company_id', 'numero', name='uix_fluv_waybills_company_numero'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    numero = Column(String(150), nullable=False, index=True)
    expediteur = Column(String(150), nullable=True)
    destinataire = Column(String(150), nullable=True)
    port_depart = Column(String(150), nullable=True)
    port_arrivee = Column(String(150), nullable=True)
    produit = Column(String(150), nullable=True)
    quantite_tonnes = Column(Integer, nullable=True)
    date_emission = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class FluvialPosition(Base):
    """Positionnement flotte fluviale."""
    __tablename__ = "fluv_positions"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_fluv_positions_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    numero_flotte = Column(String(150), nullable=True)
    date_releve = Column(DateTime(timezone=True), nullable=True)
    latitude = Column(String(150), nullable=True)
    longitude = Column(String(150), nullable=True)
    vitesse_nd = Column(String(150), nullable=True)
    cap = Column(String(150), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

