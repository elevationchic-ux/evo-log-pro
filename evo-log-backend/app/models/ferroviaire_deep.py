"""Modeles transport-ferroviaire (expansion approfondie generee).

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

class RailWagon_statut(str, enum.Enum):
    CIRCULANT = "circulant"
    ATELIER = "atelier"
    REFORME = "reforme"
    IMMOBILISE = "immobilise"


class RailLocomotive_type_energie(str, enum.Enum):
    ELECTRIQUE = "electrique"
    DIESEL = "diesel"
    BI_MODE = "bi_mode"
    HYBRIDE = "hybride"


class RailLocomotive_statut(str, enum.Enum):
    OPERATIONNELLE = "operationnelle"
    MAINTENANCE = "maintenance"
    PANNE = "panne"
    STOREE = "storee"


class RailTrainPath_statut(str, enum.Enum):
    ATTRIBUE = "attribue"
    CIRCULE = "circule"
    SUPPRIME = "supprime"
    RETARDE = "retarde"


class RailShuntingYard_statut(str, enum.Enum):
    OPERATIONNEL = "operationnel"
    SATURE = "sature"
    MAINTENANCE = "maintenance"
    FERME = "ferme"


class RailTerminal_statut(str, enum.Enum):
    ACTIF = "actif"
    SATURATION = "saturation"
    TRAVAUX = "travaux"
    FERME = "ferme"


class RailConsistencyPlan_type_train(str, enum.Enum):
    FRET_COMPLET = "fret_complet"
    CONTENEURS = "conteneurs"
    VRAC_LIQUIDE = "vrac_liquide"
    INTERMODAL = "intermodal"
    MATERIEL = "materiel"


class RailConsistencyPlan_statut(str, enum.Enum):
    PLANIFIE = "planifie"
    COMPOSE = "compose"
    PARTI = "parti"
    ANNULE = "annule"


class RailWaybill_statut(str, enum.Enum):
    EMISE = "emise"
    CHARGEE = "chargee"
    TRANSIT = "transit"
    LIVREE = "livree"
    LITIGE = "litige"


class RailTariff_statut(str, enum.Enum):
    ACTIF = "actif"
    BROUILLON = "brouillon"
    EXPIRE = "expire"
    GELE = "gele"


class RailWagonTracking_evenement(str, enum.Enum):
    DEPART = "depart"
    ARRIVEE = "arrivee"
    TRANSIT = "transit"
    CHARGEMENT = "chargement"
    DECHARGEMENT = "dechargement"
    IMMO = "immo"


class RailWagonTracking_statut(str, enum.Enum):
    EN_ROUTE = "en_route"
    EN_GARE = "en_gare"
    LIVRE = "livre"
    BLOQUE = "bloque"
    PERDU = "perdu"


class RailWagonMaintenance_type_intervention(str, enum.Enum):
    REVISION_LEGERE = "revision_legere"
    REVISION_LOURDE = "revision_lourde"
    REPARATION = "reparation"
    CONTROLE_TECHNIQUE = "controle_technique"
    PEINTURE = "peinture"


class RailWagonMaintenance_statut(str, enum.Enum):
    PLANIFIE = "planifie"
    EN_COURS = "en_cours"
    TERMINE = "termine"
    SURSEAN = "sursean"
    REFORME = "reforme"


class RailSafetyRecord_type_incident(str, enum.Enum):
    AUCUN = "aucun"
    SIGNALEMENT = "signalement"
    FREIN_dURGENCE = "frein_durgence"
    DERAILLEMENT = "deraillement"
    COLLISION = "collision"
    MARQUAGE_DANGER = "marquage_danger"


class RailSafetyRecord_gravite(str, enum.Enum):
    NEANT = "neant"
    MINEURE = "mineure"
    MAJEURE = "majeure"
    CRITIQUE = "critique"


class RailSafetyRecord_statut(str, enum.Enum):
    OUVERT = "ouvert"
    ENQUETE = "enquete"
    CLOTURE = "cloture"
    TRANSFERT_JUSTICE = "transfert_justice"


class RailCorridor_statut(str, enum.Enum):
    PLANIFIE = "planifie"
    OPERATIONNEL = "operationnel"
    EXTENSION = "extension"
    ABANDONNE = "abandonne"


# ─── Modeles ──────────────────────────────────────────────────────────────────

class RailWagon(Base):
    """Parc wagons."""
    __tablename__ = "rail_wagons"
    __table_args__ = (
        UniqueConstraint('company_id', 'numeration_wagon', name='uix_rail_wagons_company_numeration_wago'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    numeration_wagon = Column(String(150), nullable=False, index=True)
    type_wagon = Column(String(150), nullable=True)
    capacite_tonnes = Column(Integer, nullable=True)
    livree = Column(String(150), nullable=True)
    date_mise_circulation = Column(Date, nullable=True)
    prochaine_revision = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class RailLocomotive(Base):
    """Parc locomotives."""
    __tablename__ = "rail_locomotives"
    __table_args__ = (
        UniqueConstraint('company_id', 'numero_series', name='uix_rail_locomotives_company_numero_series'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    numero_series = Column(String(150), nullable=False, index=True)
    modele = Column(String(150), nullable=True)
    type_energie = Column(String(150), nullable=True)
    puissance_kw = Column(Integer, nullable=True)
    vitesse_max_kmh = Column(Integer, nullable=True)
    kilometrage_actuel = Column(Integer, nullable=True)
    prochaine_revision_km = Column(Integer, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class RailTrainPath(Base):
    """Sillons de circulation."""
    __tablename__ = "rail_train_paths"
    __table_args__ = (
        UniqueConstraint('company_id', 'code_sillon', name='uix_rail_train_paths_company_code_sillon'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    code_sillon = Column(String(150), nullable=False, index=True)
    gare_origine = Column(String(150), nullable=True)
    gare_destination = Column(String(150), nullable=True)
    date_circulation = Column(Date, nullable=True)
    heure_depart = Column(String(150), nullable=True)
    heure_arrivee = Column(String(150), nullable=True)
    numero_train = Column(String(150), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class RailShuntingYard(Base):
    """Gares de triage."""
    __tablename__ = "rail_shunting_yards"
    __table_args__ = (
        UniqueConstraint('company_id', 'code_triage', name='uix_rail_shunting_yards_company_code_triage'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    code_triage = Column(String(150), nullable=False, index=True)
    nom = Column(String(150), nullable=True)
    localisation = Column(String(150), nullable=True)
    nb_voies_tri = Column(Integer, nullable=True)
    nb_voies_parc = Column(Integer, nullable=True)
    capacite_journee_wagons = Column(Integer, nullable=True)
    taux_occupation_pct = Column(Integer, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class RailTerminal(Base):
    """Terminaux fer portuaires."""
    __tablename__ = "rail_terminals"
    __table_args__ = (
        UniqueConstraint('company_id', 'code_terminal', name='uix_rail_terminals_company_code_terminal'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    code_terminal = Column(String(150), nullable=False, index=True)
    port_associe = Column(String(150), nullable=True)
    nb_voies_fond = Column(Integer, nullable=True)
    longueur_quai_m = Column(Integer, nullable=True)
    equipement_manutention = Column(String(150), nullable=True)
    debit_conteneur_h = Column(Integer, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class RailConsistencyPlan(Base):
    """Plans de composition."""
    __tablename__ = "rail_consistency_plans"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_rail_consistency_pla_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    code_sillon = Column(String(150), nullable=True)
    type_train = Column(String(150), nullable=True)
    nb_wagons = Column(Integer, nullable=True)
    masse_totale_tonnes = Column(Integer, nullable=True)
    longueur_totale_m = Column(Integer, nullable=True)
    locomotive_atteltee = Column(String(150), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class RailWaybill(Base):
    """Lettres de voiture CIM/OTIF."""
    __tablename__ = "rail_waybills"
    __table_args__ = (
        UniqueConstraint('company_id', 'numero_lcv', name='uix_rail_waybills_company_numero_lcv'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    numero_lcv = Column(String(150), nullable=False, index=True)
    expediteur = Column(String(150), nullable=True)
    destinataire = Column(String(150), nullable=True)
    gare_depart = Column(String(150), nullable=True)
    gare_arrivee = Column(String(150), nullable=True)
    date_emission = Column(Date, nullable=True)
    valeur_marchandise_xaf = Column(Integer, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class RailTariff(Base):
    """Tarification fret fer."""
    __tablename__ = "rail_tariffs"
    __table_args__ = (
        UniqueConstraint('company_id', 'code_tarif', name='uix_rail_tariffs_company_code_tarif'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    code_tarif = Column(String(150), nullable=False, index=True)
    relation = Column(String(150), nullable=True)
    type_marchandise = Column(String(150), nullable=True)
    prix_par_tonne_km_xaf = Column(Integer, nullable=True)
    remise_volume_pct = Column(Integer, nullable=True)
    date_debut_validite = Column(Date, nullable=True)
    date_fin_validite = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class RailWagonTracking(Base):
    """Suivi wagons / telegrammes RID."""
    __tablename__ = "rail_wagon_tracking"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_rail_wagon_tracking_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    numeration_wagon = Column(String(150), nullable=True)
    code_lcv = Column(String(150), nullable=True)
    gare_actuelle = Column(String(150), nullable=True)
    date_position = Column(DateTime(timezone=True), nullable=True)
    evenement = Column(String(150), nullable=True)
    geolocalisation_gps = Column(String(150), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class RailWagonMaintenance(Base):
    """Maintenance parc wagon."""
    __tablename__ = "rail_wagon_maintenance"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_rail_wagon_maintenan_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    numeration_wagon = Column(String(150), nullable=True)
    atelier = Column(String(150), nullable=True)
    type_intervention = Column(String(150), nullable=True)
    date_debut = Column(Date, nullable=True)
    date_fin_prevue = Column(Date, nullable=True)
    date_retour_service = Column(Date, nullable=True)
    cout_xaf = Column(Integer, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class RailSafetyRecord(Base):
    """Securite circulations."""
    __tablename__ = "rail_safety_records"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_rail_safety_records_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    date_evenement = Column(DateTime(timezone=True), nullable=True)
    type_incident = Column(String(150), nullable=True)
    gravite = Column(String(150), nullable=True)
    lgn_concernee = Column(String(150), nullable=True)
    wagon_train_implique = Column(String(150), nullable=True)
    description = Column(Text, nullable=True)
    mesure_correctrice = Column(Text, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class RailCorridor(Base):
    """Corridors fer-port."""
    __tablename__ = "rail_corridors"
    __table_args__ = (
        UniqueConstraint('company_id', 'code_corridor', name='uix_rail_corridors_company_code_corridor'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    code_corridor = Column(String(150), nullable=False, index=True)
    nom = Column(String(150), nullable=True)
    pays_traverses = Column(String(150), nullable=True)
    longueur_km = Column(Integer, nullable=True)
    gares_focales = Column(Text, nullable=True)
    operateurs = Column(Text, nullable=True)
    debit_annuel_teu = Column(Integer, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

