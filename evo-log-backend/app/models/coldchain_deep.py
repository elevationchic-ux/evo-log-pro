"""Modeles chaine-froid (expansion wave 5).

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

class ColdChainChamber_type_chambre(str, enum.Enum):
    CONGELATEUR = "congelateur"
    FRIGO = "frigo"
    CELLULE_REFROIDISSEMENT = "cellule_refroidissement"
    CHAMBRE_FROIDE = "chambre_froide"
    CHAMBRE_CHEMINEMENT = "chambre_cheminement"
    ANTI_CHAMBRE = "anti_chambre"


class ColdChainChamber_plage(str, enum.Enum):
    ULTRA_BASSE = "ultra_basse"
    CONGELEE = "congelee"
    REFRIGEREE = "refrigeree"
    FRAICHE = "fraiche"
    AMBIANTE_CONTROLEE = "ambiante_controlee"


class ColdChainChamber_statut(str, enum.Enum):
    NOMINAL = "nominal"
    ALERTE = "alerte"
    DEFRICHAGE = "defrichage"
    NETTOYAGE = "nettoyage"
    HORS_SERVICE = "hors_service"


class ColdChainReefer_type_reefer(str, enum.Enum):
    ROUTIER = "routier"
    CONTENEUR = "conteneur"
    AERIEN = "aerien"
    FERROVIAIRE = "ferroviaire"
    PETIT_VRAC = "petit_vrac"


class ColdChainReefer_mode(str, enum.Enum):
    TRACTION = "traction"
    GROUPE_AUTONOME = "groupe_autonome"
    EUTECTIQUE = "eutectique"
    AZOTE_LIQUIDE = "azote_liquide"
    SEC = "sec"


class ColdChainReefer_statut(str, enum.Enum):
    EN_MARCHE = "en_marche"
    PREREFROIDI = "prerefroidi"
    ARRET = "arret"
    PANNE = "panne"
    MAINTENANCE = "maintenance"


class ColdChainLogger_technologie(str, enum.Enum):
    BLUETOOTH = "bluetooth"
    LORA = "lora"
    GSM = "gsm"
    RFID_PASSIF = "rfid_passif"
    USB_OFFLINE = "usb_offline"
    IOT_4G = "iot_4g"


class ColdChainLogger_statut(str, enum.Enum):
    ACTIF = "actif"
    BATTERIE_FAIBLE = "batterie_faible"
    HORS_LIGNE = "hors_ligne"
    SATURE = "sature"
    REFORME = "reforme"


class ColdChainProduct_categorie(str, enum.Enum):
    PHARMA_VACCIN = "pharma_vaccin"
    PHARMA_BIO = "pharma_bio"
    AGRO_FRAIS = "agro_frais"
    AGRO_CONGELE = "agro_congele"
    FLORAUX = "floraux"
    CHIMIE = "chimie"
    COSMETIQUE = "cosmetique"


class ColdChainProduct_classe(str, enum.Enum):
    GDP_A = "gdp_a"
    GDP_B = "gdp_b"
    GDP_C = "gdp_c"
    HACCP_1 = "haccp_1"
    HACCP_2 = "haccp_2"
    HACCP_3 = "haccp_3"


class ColdChainExcursion_type(str, enum.Enum):
    HORS_PLAGE_HAUTE = "hors_plage_haute"
    HORS_PLAGE_BASSE = "hors_plage_basse"
    CONGELATION_INVOULONNAIRE = "congelation_involontaire"
    DECONGELATION = "decongelation"
    RUPTURE_ALIMENTATION = "rupture_alimentation"


class ColdChainExcursion_impact(str, enum.Enum):
    AUCUN = "aucun"
    MINEUR = "mineur"
    MODERE = "modere"
    MAJEUR = "majeur"
    TOTAL_PERTE = "total_perte"


class ColdChainExcursion_statut(str, enum.Enum):
    DETECTEE = "detectee"
    ANALYSEE = "analysee"
    PRODUIT_BLOQUE = "produit_bloque"
    PRODUIT_LIBERE = "produit_libere"
    PRODUIT_DETRUIT = "produit_detruit"


class ColdChainVaccinBatch_type_vaccin(str, enum.Enum):
    EPI_EXTENDU = "epi_etendu"
    POLIO = "polio"
    rougeole = "rougeole"
    PENTA = "penta"
    BCG = "bcg"
    COVID_MRNA = "covid_mrna"
    VARICELLE = "varicelle"


class ColdChainVaccinBatch_statut(str, enum.Enum):
    RECU = "recu"
    EN_STOCK = "en_stock"
    DISTRIBUE = "distribue"
    PERIME = "perime"
    RETIRE = "retire"


class ColdChainHaccpRecord_pratique(str, enum.Enum):
    CCP1_CUISSON = "ccp1_cuisson"
    CCP2_REFROIDISSEMENT = "ccp2_refroidissement"
    CCP3_STOCKAGE = "ccp3_stockage"
    CCP4_TRANSPORT = "ccp4_transport"
    CCP5_DISTRIBUTION = "ccp5_distribution"
    PRP_BONNES_PRATIQUES = "prp_bonnes_pratiques"


class ColdChainHaccpRecord_resultat(str, enum.Enum):
    CONFORME = "conforme"
    NON_CONFORME = "non_conforme"
    A_CORRIGER = "a_corriger"
    CLOTURE = "cloture"


class ColdChainDefrostCycle_frequence(str, enum.Enum):
    QUOTIDIENNE = "quotidienne"
    HEBDOMADAIRE = "hebdomadaire"
    MENSUELLE = "mensuelle"
    TRIMESTRIELLE = "trimestrielle"
    A_LA_DEMANDE = "a_la_demande"


class ColdChainDefrostCycle_type(str, enum.Enum):
    AIR_NATUREL = "air_naturel"
    EAU_CHAUDE = "eau_chaude"
    VAPEUR = "vapeur"
    ELECTRIQUE = "electrique"
    CHIMIQUE = "chimique"


class ColdChainDefrostCycle_statut(str, enum.Enum):
    PLANIFIE = "planifie"
    EN_COURS = "en_cours"
    TERMINE = "termine"
    SURSEAN = "surseen"


class ColdChainEnergyMeter_type_energie(str, enum.Enum):
    ELECTRICITE = "electricite"
    GAZ = "gaz"
    DIESEL = "diesel"
    FREON = "freon"
    AMMONIAC = "ammoniac"


class ColdChainTransportLeg_mode(str, enum.Enum):
    ROUTIER = "routier"
    FER = "fer"
    AIR = "air"
    FLUVIAL = "fluvial"
    MARITIME = "maritime"
    MULTIMODAL = "multimodal"


class ColdChainTransportLeg_statut(str, enum.Enum):
    CHARGE = "charge"
    EN_ROUTE = "en_route"
    ARRIVE = "arrive"
    LIVRE = "livre"
    RETARD = "retard"


# ─── Modeles ──────────────────────────────────────────────────────────────────

class ColdChainChamber(Base):
    """Chambres froides fixes (frigo, congelateur)."""
    __tablename__ = "coldchain_chambers"
    __table_args__ = (
        UniqueConstraint('company_id', 'code_chambre', name='uix_coldchain_chambers_company_code_chambre'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    code_chambre = Column(String(150), nullable=False, index=True)
    type_chambre = Column(String(150), nullable=True)
    plage = Column(String(150), nullable=True)
    temperature_consigne_c = Column(Integer, nullable=True)
    temperature_actuelle_c = Column(Integer, nullable=True)
    capacite_m3 = Column(Integer, nullable=True)
    puissance_kw = Column(Integer, nullable=True)
    date_mise_service = Column(Date, nullable=True)
    prochaine_maintenance = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ColdChainReefer(Base):
    """Conteneurs et caissons refrigerants mobiles."""
    __tablename__ = "coldchain_reefers"
    __table_args__ = (
        UniqueConstraint('company_id', 'numero_reefer', name='uix_coldchain_reefers_company_numero_reefer'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    numero_reefer = Column(String(150), nullable=False, index=True)
    type_reefer = Column(String(150), nullable=True)
    mode = Column(String(150), nullable=True)
    plage_temperature_c = Column(String(150), nullable=True)
    capacite_m3 = Column(Integer, nullable=True)
    date_last_check = Column(Date, nullable=True)
    prochaine_pt = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ColdChainLogger(Base):
    """Enregistreurs de temperature (data loggers)."""
    __tablename__ = "coldchain_loggers"
    __table_args__ = (
        UniqueConstraint('company_id', 'numero_logger', name='uix_coldchain_loggers_company_numero_logger'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    numero_logger = Column(String(150), nullable=False, index=True)
    technologie = Column(String(150), nullable=True)
    frequence_lecture_s = Column(Integer, nullable=True)
    autonomie_jours = Column(Integer, nullable=True)
    precision_c = Column(Integer, nullable=True)
    date_achat = Column(Date, nullable=True)
    date_calibration = Column(Date, nullable=True)
    prochaine_calibration = Column(Date, nullable=True)
    assigned_to = Column("assigned_to", String(150), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ColdChainProduct(Base):
    """Produits sous temperature dirigee."""
    __tablename__ = "coldchain_products"
    __table_args__ = (
        UniqueConstraint('company_id', 'code_sku', name='uix_coldchain_products_company_code_sku'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    code_sku = Column(String(150), nullable=False, index=True)
    nom = Column(String(150), nullable=True)
    categorie = Column(String(150), nullable=True)
    classe = Column(String(150), nullable=True)
    temp_min_c = Column(Integer, nullable=True)
    temp_max_c = Column(Integer, nullable=True)
    duree_vie_jours = Column(Integer, nullable=True)
    seuil_excursion_h = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ColdChainExcursion(Base):
    """Excursions de temperature hors plage."""
    __tablename__ = "coldchain_excursions"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_coldchain_excursions_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    type = Column(String(150), nullable=True)
    produit_concerne = Column(String(150), nullable=True)
    actif_associe = Column(String(150), nullable=True)
    date_debut = Column(DateTime(timezone=True), nullable=True)
    date_fin = Column(DateTime(timezone=True), nullable=True)
    temp_extreme_c = Column(Integer, nullable=True)
    duree_h = Column(Integer, nullable=True)
    impact = Column(String(150), nullable=True)
    valeur_perdue_xaf = Column(Integer, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ColdChainVaccinBatch(Base):
    """Lots de vaccins EPI/PEV tracking."""
    __tablename__ = "coldchain_vaccin_batches"
    __table_args__ = (
        UniqueConstraint('company_id', 'numero_lot', name='uix_coldchain_vaccin_batches_company_numero_lot'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    numero_lot = Column(String(150), nullable=False, index=True)
    fabricant = Column(String(150), nullable=True)
    type_vaccin = Column(String(150), nullable=True)
    nb_doses = Column(Integer, nullable=True)
    date_fabrication = Column(Date, nullable=True)
    date_peremption = Column(Date, nullable=True)
    temp_stockage_c = Column(Integer, nullable=True)
    vvm_statut = Column(String(150), nullable=True)
    lieu_stockage = Column(String(150), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ColdChainHaccpRecord(Base):
    """Enregistrements HACCP / CCP critiques."""
    __tablename__ = "coldchain_haccp_records"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_coldchain_haccp_records_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    pratique = Column(String(150), nullable=True)
    date_lecture = Column(DateTime(timezone=True), nullable=True)
    valeur_lue = Column(String(150), nullable=True)
    seuil_mini = Column(String(150), nullable=True)
    seuil_maxi = Column(String(150), nullable=True)
    operateur = Column(String(150), nullable=True)
    action_corrective = Column(Text, nullable=True)
    resultat = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ColdChainDefrostCycle(Base):
    """Cycles de degivrage et nettoyage."""
    __tablename__ = "coldchain_defrost_cycles"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_coldchain_defrost_cycles_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    chambre_associee = Column(String(150), nullable=True)
    frequence = Column(String(150), nullable=True)
    type = Column(String(150), nullable=True)
    date_prevue = Column(Date, nullable=True)
    date_reelle_debut = Column(DateTime(timezone=True), nullable=True)
    date_reelle_fin = Column(DateTime(timezone=True), nullable=True)
    duree_h = Column(Integer, nullable=True)
    energie_kwh = Column(Integer, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ColdChainEnergyMeter(Base):
    """Compteurs energie des actifs froid."""
    __tablename__ = "coldchain_energy_meters"
    __table_args__ = (
        UniqueConstraint('company_id', 'code_compteur', name='uix_coldchain_energy_meters_company_code_compteur'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    code_compteur = Column(String(150), nullable=False, index=True)
    type_energie = Column(String(150), nullable=True)
    actif_alimente = Column(String(150), nullable=True)
    consommation_kwh = Column(Integer, nullable=True)
    cout_mensuel_xaf = Column(Integer, nullable=True)
    co2_eq_kg = Column(Integer, nullable=True)
    date_releve = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ColdChainTransportLeg(Base):
    """Trajet refrigerie (leg)."""
    __tablename__ = "coldchain_transport_legs"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_coldchain_transport_legs_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    mode = Column(String(150), nullable=True)
    reefer_utilise = Column(String(150), nullable=True)
    produit_transporte = Column(String(150), nullable=True)
    poids_kg = Column(Integer, nullable=True)
    origine = Column(String(150), nullable=True)
    destination = Column(String(150), nullable=True)
    date_depart = Column(DateTime(timezone=True), nullable=True)
    date_arrivee = Column(DateTime(timezone=True), nullable=True)
    temp_moyenne_c = Column(Integer, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
