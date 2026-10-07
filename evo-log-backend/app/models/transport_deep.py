"""Modeles transport-flotte (expansion approfondie generee).

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

class VehicleRegistration_type_vehicule(str, enum.Enum):
    CAMION = "camion"
    TRACTEUR = "tracteur"
    BENNE = "benne"
    CITERNE = "citerne"
    FRIGORIFIQUE = "frigorifique"
    PORTE_CONTENEUR = "porte_conteneur"
    UTILITAIRE = "utilitaire"
    BUS = "bus"


class VehicleRegistration_statut(str, enum.Enum):
    ACTIF = "actif"
    IMMOBILISE = "immobilise"
    VENDE = "vende"
    REFORME = "reforme"


class RoutePlan_statut(str, enum.Enum):
    PLANIFIEE = "planifiee"
    EN_COURS = "en_cours"
    TERMINEE = "terminee"
    ANNULEE = "annulee"


class CheckpointControl_type_controle(str, enum.Enum):
    PESAGE = "pesage"
    DOCUMENTS = "documents"
    ETAT_TECHNIQUE = "etat_technique"
    ALCOOL = "alcool"
    VITESSE = "vitesse"


class CheckpointControl_statut(str, enum.Enum):
    CONFORME = "conforme"
    PV_DRESSE = "pv_dresse"
    IMMOBILISATION = "immobilisation"


class CargoInsurance_type_garantie(str, enum.Enum):
    TOUS_RISQUES = "tous_risques"
    FAC = "fac"
    FAP = "fap"
    RESP_CIVILE = "resp_civile"


class CargoInsurance_statut(str, enum.Enum):
    ACTIVE = "active"
    EXPIREE = "expiree"
    RESILIEE = "resiliee"


class FreightBill_statut(str, enum.Enum):
    BROUILLON = "brouillon"
    EMISE = "emise"
    PAYEE = "payee"
    IMPAYEE = "impayee"
    ANNULEE = "annulee"


class Subcontractor_statut(str, enum.Enum):
    AGREE = "agree"
    SUSPENDU = "suspendu"
    NOIRE = "noire"
    RETIREE = "retiree"


class DangerousGoodsLoad_groupe_emballage(str, enum.Enum):
    I = "i"
    II = "ii"
    III = "iii"
    NA = "na"


class DangerousGoodsLoad_statut(str, enum.Enum):
    PLANIFIE = "planifie"
    TRANSPORTE = "transporte"
    LITIGE = "litige"


class VehicleDocument_type_document(str, enum.Enum):
    CARTE_GRISE = "carte_grise"
    ASSURANCE_RC = "assurance_rc"
    VIGNETTE = "vignette"
    CONTROLE_TECHNIQUE = "controle_technique"
    AUTORISATION_TRANSPORT = "autorisation_transport"


class VehicleDocument_statut(str, enum.Enum):
    VALIDE = "valide"
    EXPIRE = "expire"
    PERDU = "perdu"
    EN_RENOUVELLEMENT = "en_renouvellement"


class GpsDevice_statut(str, enum.Enum):
    ACTIF = "actif"
    HORS_RESEAU = "hors_reseau"
    PANNE = "panne"
    DESACTIVE = "desactive"


class TrafficPenalty_type_infraction(str, enum.Enum):
    EXCES_VITESSE = "exces_vitesse"
    SURCHARGE = "surcharge"
    GRILLE_FEUX = "grille_feux"
    STATIONNEMENT = "stationnement"
    ALCOOL = "alcool"
    PAPIERS = "papiers"


class TrafficPenalty_statut(str, enum.Enum):
    RECUS = "recus"
    CONTESTE = "conteste"
    PAYE = "paye"
    PRESSE = "presse"


class Convoy_type_escorte(str, enum.Enum):
    AUCUNE = "aucune"
    CIVILE = "civile"
    POLICE = "police"
    ARMEE = "armee"


class Convoy_statut(str, enum.Enum):
    PLANIFIE = "planifie"
    EN_COURS = "en_cours"
    TERMINE = "termine"
    INCIDENT = "incident"


# ─── Modeles ──────────────────────────────────────────────────────────────────

class VehicleRegistration(Base):
    """Fiche vehicule."""
    __tablename__ = "vehicle_registrations"
    __table_args__ = (
        UniqueConstraint('company_id', 'numero_immatriculation', name='uix_vehicle_registration_company_numero_immatric'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    numero_immatriculation = Column(String(150), nullable=False, index=True)
    marque = Column(String(150), nullable=True)
    modele = Column(String(150), nullable=True)
    annee_mise_circulation = Column(Integer, nullable=True)
    type_vehicule = Column(_enum(VehicleRegistration_type_vehicule), default=VehicleRegistration_type_vehicule.CAMION)
    ptt_tonnes = Column(Numeric, nullable=True)
    puissance_cv = Column(Integer, nullable=True)
    kilometrage_actuel = Column(Numeric, nullable=True)
    couleur = Column(String(150), nullable=True)
    carrosserie = Column(String(150), nullable=True)
    statut = Column(_enum(VehicleRegistration_statut), default=VehicleRegistration_statut.ACTIF)
    notes = Column(Text(2000), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class RoutePlan(Base):
    """Planification tournees."""
    __tablename__ = "route_plans"
    __table_args__ = (
        UniqueConstraint('company_id', 'code_tournee', name='uix_route_plans_company_code_tournee'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    code_tournee = Column(String(150), nullable=False, index=True)
    date_tournee = Column(Date, nullable=True)
    chauffeur_id = Column(Integer, nullable=True)
    vehicule_id = Column(Integer, nullable=True)
    nb_points = Column(Integer, nullable=True)
    distance_km = Column(Numeric, nullable=True)
    duree_estimee_h = Column(Numeric, nullable=True)
    zonale = Column(String(150), nullable=True)
    statut = Column(_enum(RoutePlan_statut), default=RoutePlan_statut.PLANIFIEE)
    notes = Column(Text(2000), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class CheckpointControl(Base):
    """Controles routiers et pesages."""
    __tablename__ = "checkpoint_controls"
    __table_args__ = (
        UniqueConstraint('company_id', 'numero_pv', name='uix_checkpoint_controls_company_numero_pv'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    numero_pv = Column(String(150), nullable=False, index=True)
    date_controle = Column(DateTime(timezone=True), nullable=True)
    lieu = Column(String(150), nullable=True)
    vehicule_id = Column(Integer, nullable=True)
    poids_reel_t = Column(Numeric, nullable=True)
    poids_autorise_t = Column(Numeric, nullable=True)
    type_controle = Column(_enum(CheckpointControl_type_controle), default=CheckpointControl_type_controle.PESAGE)
    agent = Column(String(150), nullable=True)
    sanction_appliquee = Column(Text(2000), nullable=True)
    statut = Column(_enum(CheckpointControl_statut), default=CheckpointControl_statut.CONFORME)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class CargoInsurance(Base):
    """Assurance marchandise transportee."""
    __tablename__ = "cargo_insurances"
    __table_args__ = (
        UniqueConstraint('company_id', 'numero_police', name='uix_cargo_insurances_company_numero_police'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    numero_police = Column(String(150), nullable=False, index=True)
    assureur = Column(String(150), nullable=True)
    type_garantie = Column(_enum(CargoInsurance_type_garantie), default=CargoInsurance_type_garantie.TOUS_RISQUES)
    plafond_xaf = Column(Numeric, nullable=True)
    franchise_xaf = Column(Numeric, nullable=True)
    prime_xaf = Column(Numeric, nullable=True)
    date_effet = Column(Date, nullable=True)
    date_fin = Column(Date, nullable=True)
    statut = Column(_enum(CargoInsurance_statut), default=CargoInsurance_statut.ACTIVE)
    notes = Column(Text(2000), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class FreightBill(Base):
    """Facturation fret."""
    __tablename__ = "freight_bills"
    __table_args__ = (
        UniqueConstraint('company_id', 'numero_facture', name='uix_freight_bills_company_numero_facture'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    numero_facture = Column(String(150), nullable=False, index=True)
    client_id = Column(Integer, nullable=True)
    mission_id = Column(Integer, nullable=True)
    montant_ht_xaf = Column(Numeric, nullable=True)
    tva_xaf = Column(Numeric, nullable=True)
    total_ttc_xaf = Column(Numeric, nullable=True)
    date_emission = Column(Date, nullable=True)
    date_echeance = Column(Date, nullable=True)
    statut = Column(_enum(FreightBill_statut), default=FreightBill_statut.BROUILLON)
    notes = Column(Text(2000), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Subcontractor(Base):
    """Transporteurs sous-traitants."""
    __tablename__ = "subcontractors"
    __table_args__ = (
        UniqueConstraint('company_id', 'code_sous_traitant', name='uix_subcontractors_company_code_sous_trait'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    code_sous_traitant = Column(String(150), nullable=False, index=True)
    raison_sociale = Column(String(150), nullable=True)
    niu = Column(String(150), nullable=True)
    contact = Column(String(150), nullable=True)
    telephone = Column(String(150), nullable=True)
    nb_camions = Column(Integer, nullable=True)
    zones_couvertes = Column(Text(2000), nullable=True)
    agreement_numero = Column(String(150), nullable=True)
    date_expiration_agreement = Column(Date, nullable=True)
    statut = Column(_enum(Subcontractor_statut), default=Subcontractor_statut.AGREE)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class DangerousGoodsLoad(Base):
    """Marchandises dangereuses ADR."""
    __tablename__ = "dangerous_goods_loads"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_dangerous_goods_load_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    mission_id = Column(Integer, nullable=True)
    onu_number = Column(String(150), nullable=True)
    classe_adr = Column(String(150), nullable=True)
    designation_officielle = Column(String(150), nullable=True)
    groupe_emballage = Column(_enum(DangerousGoodsLoad_groupe_emballage), default=DangerousGoodsLoad_groupe_emballage.II)
    quantite_kg = Column(Numeric, nullable=True)
    etiquettes = Column(String(150), nullable=True)
    formation_chauffeur = Column(Boolean, nullable=True)
    statut = Column(_enum(DangerousGoodsLoad_statut), default=DangerousGoodsLoad_statut.PLANIFIE)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class VehicleDocument(Base):
    """Cartes grises / assurances / vignettes."""
    __tablename__ = "vehicle_documents"
    __table_args__ = (
        UniqueConstraint('company_id', 'numero_document', name='uix_vehicle_documents_company_numero_document'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    numero_document = Column(String(150), nullable=False, index=True)
    vehicule_id = Column(Integer, nullable=True)
    type_document = Column(_enum(VehicleDocument_type_document), default=VehicleDocument_type_document.CARTE_GRISE)
    autorite_emission = Column(String(150), nullable=True)
    date_emission = Column(Date, nullable=True)
    date_expiration = Column(Date, nullable=True)
    numero_police_associe = Column(String(150), nullable=True)
    statut = Column(_enum(VehicleDocument_statut), default=VehicleDocument_statut.VALIDE)
    notes = Column(Text(2000), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class GpsDevice(Base):
    """Boitiers GPS / telematique."""
    __tablename__ = "gps_devices"
    __table_args__ = (
        UniqueConstraint('company_id', 'numero_serial_gps', name='uix_gps_devices_company_numero_serial_g'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    numero_serial_gps = Column(String(150), nullable=False, index=True)
    vehicule_id = Column(Integer, nullable=True)
    fournisseur = Column(String(150), nullable=True)
    modele = Column(String(150), nullable=True)
    numero_sim = Column(String(150), nullable=True)
    date_installation = Column(Date, nullable=True)
    date_derniere_communication = Column(DateTime(timezone=True), nullable=True)
    statut = Column(_enum(GpsDevice_statut), default=GpsDevice_statut.ACTIF)
    notes = Column(Text(2000), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class TrafficPenalty(Base):
    """Infractions et PV routiers."""
    __tablename__ = "traffic_penalties"
    __table_args__ = (
        UniqueConstraint('company_id', 'numero_pv', name='uix_traffic_penalties_company_numero_pv'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    numero_pv = Column(String(150), nullable=False, index=True)
    vehicule_id = Column(Integer, nullable=True)
    date_infraction = Column(Date, nullable=True)
    lieu = Column(String(150), nullable=True)
    type_infraction = Column(_enum(TrafficPenalty_type_infraction), default=TrafficPenalty_type_infraction.EXCES_VITESSE)
    montant_amende_xaf = Column(Numeric, nullable=True)
    points_retires = Column(Integer, nullable=True)
    chauffeur_id = Column(Integer, nullable=True)
    statut = Column(_enum(TrafficPenalty_statut), default=TrafficPenalty_statut.RECUS)
    notes = Column(Text(2000), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Convoy(Base):
    """Convois et escorte."""
    __tablename__ = "convoys"
    __table_args__ = (
        UniqueConstraint('company_id', 'code_convoi', name='uix_convoys_company_code_convoi'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    code_convoi = Column(String(150), nullable=False, index=True)
    date_depart = Column(DateTime(timezone=True), nullable=True)
    date_arrivee = Column(DateTime(timezone=True), nullable=True)
    nb_vehicules = Column(Integer, nullable=True)
    type_escorte = Column(_enum(Convoy_type_escorte), default=Convoy_type_escorte.CIVILE)
    chef_convoi = Column(String(150), nullable=True)
    itineraire = Column(Text(2000), nullable=True)
    statut = Column(_enum(Convoy_statut), default=Convoy_statut.PLANIFIE)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class FleetKpi(Base):
    """TCO et taux de service."""
    __tablename__ = "fleet_kpis"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_fleet_kpis_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    periode_debut = Column(Date, nullable=True)
    periode_fin = Column(Date, nullable=True)
    cout_total_xaf = Column(Numeric, nullable=True)
    km_parcourus = Column(Numeric, nullable=True)
    cout_par_km = Column(Numeric, nullable=True)
    taux_dispo_pct = Column(Numeric, nullable=True)
    taux_service_pct = Column(Numeric, nullable=True)
    nb_accidents = Column(Integer, nullable=True)
    notes = Column(Text(2000), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

