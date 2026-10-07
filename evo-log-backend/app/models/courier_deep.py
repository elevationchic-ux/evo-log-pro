"""Modeles courier-express (expansion wave 5).

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

class CourierParcel_type_colis(str, enum.Enum):
    ENVELOPPE = "enveloppe"
    COLIS = "colis"
    PALETTE = "palette"
    BIGBAG = "bigbag"
    DOCUMENT = "document"
    VALEUR = "valeur"


class CourierParcel_format(str, enum.Enum):
    S = "s"
    M = "m"
    L = "l"
    XL = "xl"
    OVERSIZE = "oversize"


class CourierParcel_statut(str, enum.Enum):
    PRIS_EN_CHARGE = "pris_en_charge"
    EN_TRANSIT = "en_transit"
    EN_DOUANE = "en_douane"
    DERNIER_MILE = "dernier_mile"
    LIVRE = "livre"
    REFUSE = "refuse"
    RETOUR = "retour"
    PERDU = "perdu"


class CourierWaybill_type_service(str, enum.Enum):
    MEME_VILLE = "meme_ville"
    NATIONAL = "national"
    REGIONAL_CEMAC = "regional_cemac"
    INTERNATIONAL = "international"
    EXPRESS_24H = "express_24h"
    ECONOMIQUE = "economique"


class CourierWaybill_statut(str, enum.Enum):
    CREE = "cree"
    EMIS = "emis"
    COLLECTE = "collecte"
    LIVRE = "livre"
    ANNULE = "annule"


class CourierHub_capacite(str, enum.Enum):
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    ALPHA = "alpha"


class CourierHub_statut(str, enum.Enum):
    ACTIF = "actif"
    SATURATION = "saturation"
    FERMETURE = "fermeture"
    TRAVAUX = "travaux"


class CourierDeliveryZone_type_zone(str, enum.Enum):
    URBAINE = "urbaine"
    PERI_URBAINE = "peri_urbaine"
    RURALE = "rurale"
    DIFFICILE_ACCES = "difficile_acces"
    INDUSTRIELLE = "industrielle"


class CourierRoute_type_route(str, enum.Enum):
    COLLECTE = "collecte"
    LIVRAISON = "livraison"
    MIXTE = "mixte"
    NAVETTE = "navette"
    LONGUE_DISTANCE = "longue_distance"


class CourierRoute_statut(str, enum.Enum):
    PLANIFIEE = "planifiee"
    EN_COURS = "en_cours"
    TERMINEE = "terminee"
    ANNULEE = "annulee"


class CourierCourier_type_contrat(str, enum.Enum):
    SALARIE = "salarie"
    INDEPENDANT = "independant"
    SOUS_TRAITANT = "sous_traitant"
    TEMPORAIRE = "temporaire"


class CourierCourier_disponibilite(str, enum.Enum):
    DISPONIBLE = "disponible"
    EN_TOURNEE = "en_tournee"
    CONGE = "conge"
    INJOIGNABLE = "injoignable"


class CourierPod_resultat(str, enum.Enum):
    LIVRE_DESTINATAIRE = "livre_destinataire"
    LIVRE_TIERS = "livre_tiers"
    REFUS = "refus"
    ABSENT = "absent"
    ADRESSE_INCORRECTE = "adresse_incorrecte"


class CourierSla_categorie(str, enum.Enum):
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"
    PRIORITAIRE = "prioritaire"


class CourierSla_statut(str, enum.Enum):
    ACTIF = "actif"
    BRECHE = "breche"
    RESILIE = "resilie"


class CourierLocker_type_acces(str, enum.Enum):
    PIN = "pin"
    QR = "qr"
    RFID = "rfid"
    MOBILE = "mobile"


class CourierLocker_statut(str, enum.Enum):
    DISPONIBLE = "disponible"
    OCCUPE = "occupe"
    HORS_SERVICE = "hors_service"
    PLEIN = "plein"


class CourierVehicule_type_vehicule(str, enum.Enum):
    MOTO = "moto"
    SCOOTER = "scooter"
    VOITURE = "voiture"
    FOURGON = "fourgon"
    TRACTORETTE = "tractorette"
    CAMION_LEGER = "camion_ger"


class CourierVehicule_statut(str, enum.Enum):
    ACTIF = "actif"
    MAINTENANCE = "maintenance"
    IMMOBILISE = "immobilise"
    REFORME = "reforme"


class CourierTarif_zone_tarifaire(str, enum.Enum):
    ZONE_1 = "zone_1"
    ZONE_2 = "zone_2"
    ZONE_3 = "zone_3"
    ZONE_4 = "zone_4"
    HORS_ZONE = "hors_zone"


class CourierTarif_statut(str, enum.Enum):
    ACTIF = "actif"
    BROUILLON = "brouillon"
    EXPIRE = "expire"
    GELE = "gele"


class CourierException_type_exception(str, enum.Enum):
    ADRESSE_INCORRECTE = "adresse_incorrecte"
    DESTINATAIRE_ABSENT = "destinataire_absent"
    COLIS_ENDOMMAGE = "colis_endommage"
    COLIS_PERDU = "colis_perdu"
    RETARD_DOUANE = "retard_douane"
    REFUS_DESTINATAIRE = "refus_destinataire"
    FORCE_MAJEURE = "force_majeure"


class CourierException_statut(str, enum.Enum):
    OUVERTE = "ouverte"
    EN_COURS = "en_cours"
    RESOLUE = "resolue"
    ESCALADEE = "escaladee"
    CLOTUREE = "cloturee"


# ─── Modeles ──────────────────────────────────────────────────────────────────

class CourierParcel(Base):
    """Colis et pli elementaires."""
    __tablename__ = "courier_parcels"
    __table_args__ = (
        UniqueConstraint('company_id', 'numero_colis', name='uix_courier_parcels_company_numero_colis'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    numero_colis = Column(String(150), nullable=False, index=True)
    type_colis = Column(String(150), nullable=True)
    format = Column(String(150), nullable=True)
    poids_kg = Column(Integer, nullable=True)
    dimensions_cm = Column(String(150), nullable=True)
    valeur_declaree_xaf = Column(Integer, nullable=True)
    expediteur = Column(String(150), nullable=True)
    destinataire = Column(String(150), nullable=True)
    date_prise_en_charge = Column(Date, nullable=True)
    date_livraison = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class CourierWaybill(Base):
    """Lettre de voiture express (LSE)."""
    __tablename__ = "courier_waybills"
    __table_args__ = (
        UniqueConstraint('company_id', 'numero_lse', name='uix_courier_waybills_company_numero_lse'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    numero_lse = Column(String(150), nullable=False, index=True)
    type_service = Column(String(150), nullable=True)
    client = Column(String(150), nullable=True)
    nb_colis = Column(Integer, nullable=True)
    poids_total_kg = Column(Integer, nullable=True)
    montant_facture_xaf = Column(Integer, nullable=True)
    date_emission = Column(Date, nullable=True)
    date_livraison_prevue = Column(Date, nullable=True)
    date_livraison_reelle = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class CourierHub(Base):
    """Hubs et plateformes de tri."""
    __tablename__ = "courier_hubs"
    __table_args__ = (
        UniqueConstraint('company_id', 'code_hub', name='uix_courier_hubs_company_code_hub'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    code_hub = Column(String(150), nullable=False, index=True)
    nom = Column(String(150), nullable=True)
    ville = Column(String(150), nullable=True)
    pays = Column(String(150), nullable=True)
    capacite = Column(String(150), nullable=True)
    nb_tri_jour = Column(Integer, nullable=True)
    surface_m2 = Column(Integer, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class CourierDeliveryZone(Base):
    """Zones de livraison."""
    __tablename__ = "courier_delivery_zones"
    __table_args__ = (
        UniqueConstraint('company_id', 'code_zone', name='uix_courier_delivery_zones_company_code_zone'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    code_zone = Column(String(150), nullable=False, index=True)
    nom = Column(String(150), nullable=True)
    type_zone = Column(String(150), nullable=True)
    ville = Column(String(150), nullable=True)
    nb_habitants = Column(Integer, nullable=True)
    nb_colis_jour = Column(Integer, nullable=True)
    hub_rattachement = Column(String(150), nullable=True)
    surcost_xaf = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class CourierRoute(Base):
    """Tournees de collecte et livraison."""
    __tablename__ = "courier_routes"
    __table_args__ = (
        UniqueConstraint('company_id', 'code_tournee', name='uix_courier_routes_company_code_tournee'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    code_tournee = Column(String(150), nullable=False, index=True)
    type_route = Column(String(150), nullable=True)
    zone_associee = Column(String(150), nullable=True)
    chauffeur = Column(String(150), nullable=True)
    vehicule = Column(String(150), nullable=True)
    date_tournee = Column(Date, nullable=True)
    nb_arrets = Column(Integer, nullable=True)
    distance_km = Column(Integer, nullable=True)
    duree_h = Column(Integer, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class CourierCourier(Base):
    """Coursiers et livreurs."""
    __tablename__ = "courier_couriers"
    __table_args__ = (
        UniqueConstraint('company_id', 'code_coursier', name='uix_courier_couriers_company_code_coursier'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    code_coursier = Column(String(150), nullable=False, index=True)
    nom = Column(String(150), nullable=True)
    telephone = Column(String(150), nullable=True)
    email = Column(String(150), nullable=True)
    type_contrat = Column(String(150), nullable=True)
    permis_conduire = Column(String(150), nullable=True)
    date_embauche = Column(Date, nullable=True)
    nb_livraisons_jour = Column(Integer, nullable=True)
    taux_ponctualite_pct = Column(Integer, nullable=True)
    disponibilite = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class CourierPod(Base):
    """Preuves de livraison (POD)."""
    __tablename__ = "courier_pods"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference_pod', name='uix_courier_pods_company_reference_pod'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference_pod = Column(String(150), nullable=False, index=True)
    numero_colis = Column(String(150), nullable=True)
    date_livraison = Column(DateTime(timezone=True), nullable=True)
    destination_finale = Column(String(150), nullable=True)
    agent_livreur = Column(String(150), nullable=True)
    resultat = Column(String(150), nullable=True)
    signature_recu = Column(Boolean, nullable=True)
    photo_url = Column(String(150), nullable=True)
    geo_lat = Column(String(150), nullable=True)
    geo_lon = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class CourierSla(Base):
    """Accords de niveau de service."""
    __tablename__ = "courier_slas"
    __table_args__ = (
        UniqueConstraint('company_id', 'code_sla', name='uix_courier_slas_company_code_sla'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    code_sla = Column(String(150), nullable=False, index=True)
    client = Column(String(150), nullable=True)
    categorie = Column(String(150), nullable=True)
    engagement_pct = Column(Integer, nullable=True)
    delai_h = Column(Integer, nullable=True)
    penalite_xaf = Column(Integer, nullable=True)
    mesure_pct = Column(Integer, nullable=True)
    date_debut = Column(Date, nullable=True)
    date_fin = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class CourierLocker(Base):
    """Consignes automatiques."""
    __tablename__ = "courier_lockers"
    __table_args__ = (
        UniqueConstraint('company_id', 'code_locker', name='uix_courier_lockers_company_code_locker'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    code_locker = Column(String(150), nullable=False, index=True)
    adresse = Column(String(150), nullable=True)
    ville = Column(String(150), nullable=True)
    nb_cases = Column(Integer, nullable=True)
    nb_cases_libres = Column(Integer, nullable=True)
    type_acces = Column(String(150), nullable=True)
    horaires_ouverture = Column(String(150), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class CourierVehicule(Base):
    """Parc vehicules de livraison."""
    __tablename__ = "courier_vehicules"
    __table_args__ = (
        UniqueConstraint('company_id', 'plaque', name='uix_courier_vehicules_company_plaque'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    plaque = Column(String(150), nullable=False, index=True)
    type_vehicule = Column(String(150), nullable=True)
    marque = Column(String(150), nullable=True)
    modele = Column(String(150), nullable=True)
    capacite_m3 = Column(Integer, nullable=True)
    date_mise_circulation = Column(Date, nullable=True)
    kilometrage_actuel = Column(Integer, nullable=True)
    prochaine_revision_km = Column(Integer, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class CourierTarif(Base):
    """Grille tarifaire par zone et poids."""
    __tablename__ = "courier_tarifs"
    __table_args__ = (
        UniqueConstraint('company_id', 'code_tarif', name='uix_courier_tarifs_company_code_tarif'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    code_tarif = Column(String(150), nullable=False, index=True)
    zone_tarifaire = Column(String(150), nullable=True)
    tranche_poids_kg = Column(String(150), nullable=True)
    prix_base_xaf = Column(Integer, nullable=True)
    prix_par_kg_supp_xaf = Column(Integer, nullable=True)
    options_payantes = Column(Text, nullable=True)
    date_debut_validite = Column(Date, nullable=True)
    date_fin_validite = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class CourierException(Base):
    """Anomalies et litiges de livraison."""
    __tablename__ = "courier_exceptions"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_courier_exceptions_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    numero_colis = Column(String(150), nullable=True)
    type_exception = Column(String(150), nullable=True)
    date_signalement = Column(DateTime(timezone=True), nullable=True)
    description = Column(Text, nullable=True)
    montant_litige_xaf = Column(Integer, nullable=True)
    agent = Column(String(150), nullable=True)
    date_resolution = Column(DateTime(timezone=True), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
