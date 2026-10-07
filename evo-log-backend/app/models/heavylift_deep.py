"""Modeles convoi-exceptionnel heavy-lift (expansion wave 5).

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

class HeavyLiftProject_categorie(str, enum.Enum):
    INDUSTRIEL = "industriel"
    ENERGIE = "energie"
    MINIER = "minier"
    BTP = "btp"
    AERO = "aero"
    MILITAIRE = "militaire"
    HUMANITAIRE = "humanitaire"


class HeavyLiftProject_statut(str, enum.Enum):
    ETUDE = "etude"
    OFFRE = "offre"
    ADJUGE = "adjuge"
    MOBILISATION = "mobilisation"
    EXECUTION = "execution"
    CLOTURE = "cloture"
    ANNULE = "annule"


class HeavyLiftCrane_type_grue(str, enum.Enum):
    MOBILE = "mobile"
    CHENILLEE = "chenillee"
    TOUR = "tour"
    GME = "gme"
    FLOATING = "floating"
    TELESCOPIQUE = "telescopique"


class HeavyLiftCrane_statut(str, enum.Enum):
    DISPONIBLE = "disponible"
    LOUEE = "louee"
    CHANTIER = "chantier"
    MAINTENANCE = "maintenance"
    IMMOBILISEE = "immobilisee"


class HeavyLiftModularTrailer_type_remorque(str, enum.Enum):
    SPMT = "spmt"
    SEMI_LOWBO = "semi_lowboy"
    TRIPLE_AXLE = "triple_axle"
    MODULAIRE_EXTENSIBLE = "modulaire_extensible"
    CYNES = "cynes"
    DOLVIN = "dolvin"


class HeavyLiftModularTrailer_statut(str, enum.Enum):
    DISPONIBLE = "disponible"
    AFFECTEE = "affectee"
    MAINTENANCE = "maintenance"
    REFORMEE = "reformee"


class HeavyLiftRouteSurvey_resultat(str, enum.Enum):
    PRATICABLE = "praticable"
    PRATICABLE_AMENAGE = "praticable_amenage"
    TRAVAUX_REQUIS = "travaux_requis"
    ITINERAIRE_BIS = "itineraire_bis"
    IMPRATICABLE = "impraticable"


class HeavyLiftRouteSurvey_statut(str, enum.Enum):
    PLANIFIEE = "planifiee"
    EN_COURS = "en_cours"
    VALIDE = "valide"
    REJETEE = "rejete"


class HeavyLiftLiftPlan_type_operation(str, enum.Enum):
    LEVAGE_SIMPLE = "levage_simple"
    LEVAGE_TANDEM = "levage_tandem"
    PUSHER_METHOD = "pusher_method"
    SKYJACK = "skyjack"
    ROLLER_BEAM = "roller_beam"
    DOLVING = "dolving"


class HeavyLiftLiftPlan_criticite(str, enum.Enum):
    STANDARD = "standard"
    COMPLEXE = "complexe"
    CRITIQUE = "critique"
    NON_STANDARD = "non_standard"


class HeavyLiftLiftPlan_statut(str, enum.Enum):
    BROUILLON = "brouillon"
    APPROUVE = "approuve"
    EN_EXECUTION = "en_execution"
    REALISE = "realise"
    ANNULE = "annule"


class HeavyLiftPermit_type_permis(str, enum.Enum):
    PONCTUEL = "ponctuel"
    ANNUEL = "annuel"
    MULTI_TRAVERS = "multi_travers"
    EXCEPTIONNEL_MASSE = "exceptionnel_masse"
    EXCEPTIONNEL_DIMENSION = "exceptionnel_dimension"
    ADR_SPECIAL = "adr_special"


class HeavyLiftPermit_autorite(str, enum.Enum):
    MINTRANS = "mintrans"
    ONVT = "onvt"
    MINTP = "mintp"
    COMMUNE = "commune"
    DOGAMI = "dogami"
    PREFECTURE = "prefecture"


class HeavyLiftPermit_statut(str, enum.Enum):
    DEMANDE = "demande"
    INSTRUCTION = "instruction"
    ACCORDE = "accorde"
    REFUSE = "refuse"
    EXPIRE = "expire"


class HeavyLiftEscort_type_escorte(str, enum.Enum):
    POLICE = "police"
    PRIVEE = "privee"
    MIXTE = "mixte"
    GENDARMERIE = "gendarmerie"
    CIVILE = "civile"


class HeavyLiftEscort_statut(str, enum.Enum):
    PLANIFIEE = "planifiee"
    EN_COURS = "en_cours"
    TERMINEE = "terminee"
    ANNULEE = "annulee"


class HeavyLiftLashing_methode(str, enum.Enum):
    CHAINTE = "chaines"
    ELINGUE = "elingues"
    CALEUSES = "caleuses"
    VENTOUSES = "ventouses"
    BERCEAU = "berceau"
    CADENAS = "cadenas"


class HeavyLiftLashing_resultat(str, enum.Enum):
    CONFORME = "conforme"
    A_REVOIR = "a_revoir"
    NON_CONFORME = "non_conforme"


class HeavyLiftBallast_type_ballast(str, enum.Enum):
    ACIER = "acier"
    BETON = "beton"
    EAU = "eau"
    SABLE = "sable"
    COMPOSITE = "composite"


class HeavyLiftBallast_statut(str, enum.Enum):
    EN_STOCK = "en_stock"
    AFFECTE = "affecte"
    LIVRE = "livre"
    RETOURNE = "retourne"


class HeavyLiftRiggingMethod_categorie(str, enum.Enum):
    TWO_POINT = "two_point"
    FOUR_POINT = "four_point"
    SPREADER_BEAM = "spreader_beam"
    LIFTING_FRAME = "lifting_frame"
    TRUSS = "truss"
    CUSTOM = "custom"


class HeavyLiftRiggingMethod_statut(str, enum.Enum):
    ETUDE = "etude"
    VALIDE = "valide"
    UTILISE = "utilise"
    ABANDONNE = "abandonne"


# ─── Modeles ──────────────────────────────────────────────────────────────────

class HeavyLiftProject(Base):
    """Projets heavy-lift / project cargo."""
    __tablename__ = "heavylift_projects"
    __table_args__ = (
        UniqueConstraint('company_id', 'code_projet', name='uix_heavylift_projects_company_code_projet'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    code_projet = Column(String(150), nullable=False, index=True)
    nom = Column(String(150), nullable=True)
    client = Column(String(150), nullable=True)
    categorie = Column(String(150), nullable=True)
    poids_max_t = Column(Integer, nullable=True)
    volume_m3 = Column(Integer, nullable=True)
    distance_km = Column(Integer, nullable=True)
    date_debut = Column(Date, nullable=True)
    date_fin_prevue = Column(Date, nullable=True)
    budget_xaf = Column(Integer, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class HeavyLiftCrane(Base):
    """Parc de grues."""
    __tablename__ = "heavylift_cranes"
    __table_args__ = (
        UniqueConstraint('company_id', 'numero_grue', name='uix_heavylift_cranes_company_numero_grue'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    numero_grue = Column(String(150), nullable=False, index=True)
    type_grue = Column(String(150), nullable=True)
    capacite_max_t = Column(Integer, nullable=True)
    portee_max_m = Column(Integer, nullable=True)
    hauteur_max_m = Column(Integer, nullable=True)
    mise_en_service = Column(Date, nullable=True)
    prochaine_visite = Column(Date, nullable=True)
    cout_location_jour_xaf = Column(Integer, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class HeavyLiftModularTrailer(Base):
    """Remorques modulaires et SPMT."""
    __tablename__ = "heavylift_modular_trailers"
    __table_args__ = (
        UniqueConstraint('company_id', 'plaque', name='uix_heavylift_modular_trailers_company_plaque'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    plaque = Column(String(150), nullable=False, index=True)
    type_remorque = Column(String(150), nullable=True)
    nb_essieux = Column(Integer, nullable=True)
    charge_utile_t = Column(Integer, nullable=True)
    longueur_m = Column(Integer, nullable=True)
    largeur_m = Column(Integer, nullable=True)
    hauteur_min_m = Column(Integer, nullable=True)
    angle_orientation_deg = Column(Integer, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class HeavyLiftRouteSurvey(Base):
    """Etudes d'itineraire (route survey)."""
    __tablename__ = "heavylift_route_surveys"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_heavylift_route_surveys_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    projet_associe = Column(String(150), nullable=True)
    origine = Column(String(150), nullable=True)
    destination = Column(String(150), nullable=True)
    distance_km = Column(Integer, nullable=True)
    nb_obstacles = Column(Integer, nullable=True)
    ouvrages_franchis = Column(Text(2000), nullable=True)
    cout_amenagement_xaf = Column(Integer, nullable=True)
    date_etude = Column(Date, nullable=True)
    resultat = Column(String(150), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class HeavyLiftLiftPlan(Base):
    """Plans de levage (lift plan / RAMPS)."""
    __tablename__ = "heavylift_lift_plans"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_heavylift_lift_plans_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    projet_associe = Column(String(150), nullable=True)
    type_operation = Column(String(150), nullable=True)
    charge_t = Column(Integer, nullable=True)
    hauteur_m = Column(Integer, nullable=True)
    centre_gravite_haut = Column(Boolean, nullable=True)
    coefficient_securite_pct = Column(Integer, nullable=True)
    grue_prevue = Column(String(150), nullable=True)
    date_prevue = Column(Date, nullable=True)
    criticite = Column(String(150), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class HeavyLiftPermit(Base):
    """Permis de convoi exceptionnel."""
    __tablename__ = "heavylift_permits"
    __table_args__ = (
        UniqueConstraint('company_id', 'numero_permis', name='uix_heavylift_permits_company_numero_permis'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    numero_permis = Column(String(150), nullable=False, index=True)
    type_permis = Column(String(150), nullable=True)
    autorite = Column(String(150), nullable=True)
    charge_concernee = Column(String(150), nullable=True)
    itineraire_depot = Column(Text(2000), nullable=True)
    date_depot_demande = Column(Date, nullable=True)
    date_delivrance = Column(Date, nullable=True)
    date_validite_fin = Column(Date, nullable=True)
    cout_redevance_xaf = Column(Integer, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class HeavyLiftEscort(Base):
    """Escoltes et pilotes."""
    __tablename__ = "heavylift_escorts"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_heavylift_escorts_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    convoi_associe = Column(String(150), nullable=True)
    type_escorte = Column(String(150), nullable=True)
    nb_vehicules_escorte = Column(Integer, nullable=True)
    date_debut = Column(DateTime(timezone=True), nullable=True)
    date_fin = Column(DateTime(timezone=True), nullable=True)
    zone_administrative = Column(String(150), nullable=True)
    agent_responsable = Column(String(150), nullable=True)
    cout_xaf = Column(Integer, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class HeavyLiftLashing(Base):
    """Registre d'amarrage et saisine."""
    __tablename__ = "heavylift_lashings"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_heavylift_lashings_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    methode = Column(String(150), nullable=True)
    charge_amarree = Column(String(150), nullable=True)
    nb_points = Column(Integer, nullable=True)
    effort_admissible_t = Column(Integer, nullable=True)
    coefficient_secu_pct = Column(Integer, nullable=True)
    operateur = Column(String(150), nullable=True)
    date_controle = Column(Date, nullable=True)
    resultat = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class HeavyLiftBallast(Base):
    """Ballast de lestage."""
    __tablename__ = "heavylift_ballasts"
    __table_args__ = (
        UniqueConstraint('company_id', 'code_ballast', name='uix_heavylift_ballasts_company_code_ballast'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    code_ballast = Column(String(150), nullable=False, index=True)
    type_ballast = Column(String(150), nullable=True)
    masse_unitaire_t = Column(Integer, nullable=True)
    nb_unites = Column(Integer, nullable=True)
    masse_totale_t = Column(Integer, nullable=True)
    cout_location_jour_xaf = Column(Integer, nullable=True)
    lieu_stockage = Column(String(150), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class HeavyLiftRiggingMethod(Base):
    """Methodes de greage (rigging)."""
    __tablename__ = "heavylift_rigging_methods"
    __table_args__ = (
        UniqueConstraint('company_id', 'code_methode', name='uix_heavylift_rigging_methods_company_code_methode'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    code_methode = Column(String(150), nullable=False, index=True)
    categorie = Column(String(150), nullable=True)
    description = Column(Text(2000), nullable=True)
    capacite_max_t = Column(Integer, nullable=True)
    temps_mise_en_oeuvre_h = Column(Integer, nullable=True)
    nb_techniciens = Column(Integer, nullable=True)
    cout_moyen_xaf = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
