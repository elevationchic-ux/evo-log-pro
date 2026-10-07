"""Modeles pipeline-oleoduc (expansion approfondie generee, wave 5).

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

class PipelineSection_type_produit(str, enum.Enum):
    CRUD_BRUT = "crude_brut"
    PRODUITS_FINIS = "produits_finis"
    GAZ_NATUREL = "gaz_naturel"
    GPL_LPG = "gpl_lpg"
    VRAC_SOLIDE = "vrac_solide"
    EAU_INJECTION = "eau_injection"


class PipelineSection_statut(str, enum.Enum):
    EXPLOITATION = "exploitation"
    MAINTENANCE = "maintenance"
    ARRET_TEMPORAIRE = "arret_temporaire"
    REFORME = "reforme"
    CONSTRUCTION = "construction"


class PipelinePumpStation_type_station(str, enum.Enum):
    BOOSTER = "booster"
    TERMINALE = "terminale"
    INTERMEDIATE = "intermediaire"
    DISTRIBUTION = "distribution"
    MESURAGE = "mesurage"


class PipelinePumpStation_statut(str, enum.Enum):
    ACTIVE = "active"
    STANDBY = "standby"
    MAINTENANCE = "maintenance"
    ARRET = "arret"


class PipelineStorageTank_type_cuve(str, enum.Enum):
    ATMOSPHERIQUE = "atmospherique"
    PRESSURE = "pressure"
    CRYOGENIQUE = "cryogenique"
    DOUBLE_PAROI = "double_paroi"
    FLOTTANTE = "flottante"


class PipelineStorageTank_statut(str, enum.Enum):
    REMPLIE = "remplie"
    VIDE = "vide"
    TRANSFERT = "transfert"
    NETTOYAGE = "nettoyage"
    INSPECTION = "inspection"


class PipelineMeteringPoint_usage(str, enum.Enum):
    CUSTODY_TRANSFER = "custody_transfer"
    FISCAL = "fiscal"
    OPERATIONNEL = "operationnel"
    ALERTE = "alerte"


class PipelineMeteringPoint_technologie(str, enum.Enum):
    TURBINE = "turbine"
    CORIOLIS = "coriolis"
    ULTRASON = "ultrason"
    DP_ORIFICE = "dp_orifice"
    POSITIVE_DISPLACEMENT = "positive_displacement"


class PipelineProductBatch_statut(str, enum.Enum):
    PLANIFIE = "planifie"
    EN_CIRCULATION = "en_circulation"
    LIVRE = "livre"
    REJETE = "rejete"
    LITIGE = "litige"


class PipelinePressureReading_qualite(str, enum.Enum):
    VALIDE = "valide"
    ESTIMEE = "estimee"
    SUSPECTE = "suspecte"
    ANNULEE = "annulee"


class PipelineLeakDetection_technologie(str, enum.Enum):
    SCARBECK = "scarbeck"
    FIBRE_OPTIQUE = "fibre_optique"
    ACOUSTIQUE = "acoustique"
    NEGATIVE_PRESSURE_WAVE = "negative_pressure_wave"
    DRONE_LMDR = "drone_lmrd"


class PipelineLeakDetection_severite(str, enum.Enum):
    AUCUNE = "aucune"
    MICRO = "micro"
    MINEURE = "mineure"
    MAJEURE = "majeure"
    CATASTROPHIQUE = "catastrophique"


class PipelineLeakDetection_statut(str, enum.Enum):
    DETECTE = "detecte"
    CONFIRME = "confirme"
    FAITE_ALARME = "faite_alarme"
    REPARATION = "reparation"
    CLOTURE = "cloture"


class PipelineMaintenanceWork_type_travaux(str, enum.Enum):
    INSPECTION_INTEGRE = "inspection_integre"
    NETTOYAGE_RACLEUR = "nettoyage_racleur"
    REPARATION_REVETEMENT = "reparation_revetement"
    REMPLACEMENT_VANNE = "remplacement_vanne"
    SOUDURE = "soudure"
    PROTECTION_CATHODIQUE = "protection_cathodique"


class PipelineMaintenanceWork_statut(str, enum.Enum):
    PLANIFIE = "planifie"
    EN_COURS = "en_cours"
    TERMINE = "termine"
    SURSEAN = "surseen"
    URGENT = "urgent"


class PipelineInjectionCampaign_type(str, enum.Enum):
    DEBIANTANT = "debiantant"
    INHIBITEUR_CORROSION = "inhibiteur_corrosion"
    BIODEGRADEANT = "biodegradant"
    ANTI_FOAM = "anti_foam"
    DRAG_REDUUCER = "drag_reducer"


class PipelineInjectionCampaign_statut(str, enum.Enum):
    PLANIFIEE = "planifiee"
    EN_COURS = "en_cours"
    TERMINEE = "terminee"
    ANNULEE = "annulee"


class PipelineShipNomination_statut(str, enum.Enum):
    NOMMEE = "nommee"
    CONFIRMEE = "confirmee"
    EN_ROUTE = "en_route"
    ARRIVEE = "arrivee"
    CARGAISON = "cargaison"
    PARTIE = "partie"
    ANNULEE = "annulee"


# ─── Modeles ──────────────────────────────────────────────────────────────────

class PipelineSection(Base):
    """Troncons physiques (pente, revetement, cathodique)."""
    __tablename__ = "pipeline_sections"
    __table_args__ = (
        UniqueConstraint('company_id', 'code_section', name='uix_pipeline_sections_company_code_section'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    code_section = Column(String(150), nullable=False, index=True)
    nom = Column(String(150), nullable=True)
    type_produit = Column(String(150), nullable=True)
    diametre_mm = Column(Integer, nullable=True)
    epaisseur_paroi_mm = Column(Integer, nullable=True)
    longueur_km = Column(Integer, nullable=True)
    origine = Column(String(150), nullable=True)
    destination = Column(String(150), nullable=True)
    date_mise_service = Column(Date, nullable=True)
    pression_max_bar = Column(Integer, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class PipelinePumpStation(Base):
    """Stations de pompage et de compression."""
    __tablename__ = "pipeline_pump_stations"
    __table_args__ = (
        UniqueConstraint('company_id', 'code_station', name='uix_pipeline_pump_stations_company_code_station'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    code_station = Column(String(150), nullable=False, index=True)
    nom = Column(String(150), nullable=True)
    type_station = Column(String(150), nullable=True)
    section_associee = Column(String(150), nullable=True)
    nb_pompes = Column(Integer, nullable=True)
    puissance_totale_kw = Column(Integer, nullable=True)
    debit_nominal_m3h = Column(Integer, nullable=True)
    pression_refoulement_bar = Column(Integer, nullable=True)
    energie_annuelle_kwh = Column(Integer, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class PipelineStorageTank(Base):
    """Cuves de stockage et balls d'interface."""
    __tablename__ = "pipeline_storage_tanks"
    __table_args__ = (
        UniqueConstraint('company_id', 'code_cuve', name='uix_pipeline_storage_tanks_company_code_cuve'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    code_cuve = Column(String(150), nullable=False, index=True)
    type_cuve = Column(String(150), nullable=True)
    capacite_m3 = Column(Integer, nullable=True)
    niveau_actuel_pct = Column(Integer, nullable=True)
    temperature_stockage_c = Column(Integer, nullable=True)
    produit_stocke = Column(String(150), nullable=True)
    date_dernier_nettoyage = Column(Date, nullable=True)
    prochaine_inspection = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class PipelineMeteringPoint(Base):
    """Points de comptage fiscal et custody transfer."""
    __tablename__ = "pipeline_metering_points"
    __table_args__ = (
        UniqueConstraint('company_id', 'code_point', name='uix_pipeline_metering_points_company_code_point'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    code_point = Column(String(150), nullable=False, index=True)
    usage = Column(String(150), nullable=True)
    technologie = Column(String(150), nullable=True)
    section_associee = Column(String(150), nullable=True)
    precision_pct = Column(Integer, nullable=True)
    debit_max_m3h = Column(Integer, nullable=True)
    date_etalonnage = Column(Date, nullable=True)
    prochain_etalonnage = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class PipelineProductBatch(Base):
    """Lots de produit transportes (batch tracking)."""
    __tablename__ = "pipeline_product_batches"
    __table_args__ = (
        UniqueConstraint('company_id', 'numero_lot', name='uix_pipeline_product_batches_company_numero_lot'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    numero_lot = Column(String(150), nullable=False, index=True)
    produit = Column(String(150), nullable=True)
    volume_m3 = Column(Integer, nullable=True)
    densite_api = Column(Integer, nullable=True)
    teneur_soufre_pct = Column(Integer, nullable=True)
    injection_debut = Column(DateTime(timezone=True), nullable=True)
    arrivee_prevue = Column(DateTime(timezone=True), nullable=True)
    destinataire = Column(String(150), nullable=True)
    section_utilisee = Column(String(150), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class PipelinePressureReading(Base):
    """Releves SCADA pression / debit / temperature."""
    __tablename__ = "pipeline_pressure_readings"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_pipeline_pressure_readings_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    section_associee = Column(String(150), nullable=True)
    date_releve = Column(DateTime(timezone=True), nullable=True)
    pression_entree_bar = Column(Integer, nullable=True)
    pression_sortie_bar = Column(Integer, nullable=True)
    debit_m3h = Column(Integer, nullable=True)
    temperature_c = Column(Integer, nullable=True)
    qualite = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class PipelineLeakDetection(Base):
    """Campagnes et alertes de detection de fuite."""
    __tablename__ = "pipeline_leak_detections"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_pipeline_leak_detections_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    date_detection = Column(DateTime(timezone=True), nullable=True)
    section_associee = Column(String(150), nullable=True)
    technologie = Column(String(150), nullable=True)
    perte_estimee_m3 = Column(Integer, nullable=True)
    severite = Column(String(150), nullable=True)
    lat_localisation = Column(String(150), nullable=True)
    lon_localisation = Column(String(150), nullable=True)
    delai_reparation_h = Column(Integer, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class PipelineMaintenanceWork(Base):
    """Travaux d'inspection et de maintenance."""
    __tablename__ = "pipeline_maintenance_works"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_pipeline_maintenance_works_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    section_associee = Column(String(150), nullable=True)
    type_travaux = Column(String(150), nullable=True)
    date_debut = Column(Date, nullable=True)
    date_fin_prevue = Column(Date, nullable=True)
    date_fin_reelle = Column(Date, nullable=True)
    cout_xaf = Column(Integer, nullable=True)
    prestataire = Column(String(150), nullable=True)
    arret_production_h = Column(Integer, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class PipelineInjectionCampaign(Base):
    """Campagnes d'injection chimique (debiantant, corrosion)."""
    __tablename__ = "pipeline_injection_campaigns"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_pipeline_injection_campaigns_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    type = Column(String(150), nullable=True)
    section_associee = Column(String(150), nullable=True)
    produit_chimique = Column(String(150), nullable=True)
    debit_injection_lh = Column(Integer, nullable=True)
    date_debut = Column(Date, nullable=True)
    date_fin = Column(Date, nullable=True)
    volume_total_l = Column(Integer, nullable=True)
    cout_xaf = Column(Integer, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class PipelineShipNomination(Base):
    """Nominations navires aux terminaux pipeline."""
    __tablename__ = "pipeline_ship_nominations"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_pipeline_ship_nominations_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    nom_navire = Column(String(150), nullable=True)
    imo = Column(String(150), nullable=True)
    terminal = Column(String(150), nullable=True)
    produit_charge = Column(String(150), nullable=True)
    volume_m3 = Column(Integer, nullable=True)
    eta = Column(Date, nullable=True)
    etb = Column(Date, nullable=True)
    etc = Column(Date, nullable=True)
    vacis = Column(String(150), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
