"""Schemas Pydantic pour transport-flotte (genere)."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date


class VehicleRegistrationCreate(BaseModel):
    numero_immatriculation: str
    marque: Optional[str] = None
    modele: Optional[str] = None
    annee_mise_circulation: Optional[int] = None
    type_vehicule: Optional[str] = None
    ptt_tonnes: Optional[float] = None
    puissance_cv: Optional[int] = None
    kilometrage_actuel: Optional[float] = None
    couleur: Optional[str] = None
    carrosserie: Optional[str] = None
    statut: Optional[str] = None
    notes: Optional[str] = None


class VehicleRegistrationUpdate(BaseModel):
    numero_immatriculation: Optional[str] = None
    marque: Optional[str] = None
    modele: Optional[str] = None
    annee_mise_circulation: Optional[int] = None
    type_vehicule: Optional[str] = None
    ptt_tonnes: Optional[float] = None
    puissance_cv: Optional[int] = None
    kilometrage_actuel: Optional[float] = None
    couleur: Optional[str] = None
    carrosserie: Optional[str] = None
    statut: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class VehicleRegistrationOut(BaseModel):
    id: int
    company_id: int
    numero_immatriculation: str
    marque: Optional[str] = None
    modele: Optional[str] = None
    annee_mise_circulation: Optional[int] = None
    type_vehicule: Optional[str] = None
    ptt_tonnes: Optional[float] = None
    puissance_cv: Optional[int] = None
    kilometrage_actuel: Optional[float] = None
    couleur: Optional[str] = None
    carrosserie: Optional[str] = None
    statut: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class RoutePlanCreate(BaseModel):
    code_tournee: str
    date_tournee: Optional[date] = None
    chauffeur_id: Optional[int] = None
    vehicule_id: Optional[int] = None
    nb_points: Optional[int] = None
    distance_km: Optional[float] = None
    duree_estimee_h: Optional[float] = None
    zonale: Optional[str] = None
    statut: Optional[str] = None
    notes: Optional[str] = None


class RoutePlanUpdate(BaseModel):
    code_tournee: Optional[str] = None
    date_tournee: Optional[date] = None
    chauffeur_id: Optional[int] = None
    vehicule_id: Optional[int] = None
    nb_points: Optional[int] = None
    distance_km: Optional[float] = None
    duree_estimee_h: Optional[float] = None
    zonale: Optional[str] = None
    statut: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class RoutePlanOut(BaseModel):
    id: int
    company_id: int
    code_tournee: str
    date_tournee: Optional[date] = None
    chauffeur_id: Optional[int] = None
    vehicule_id: Optional[int] = None
    nb_points: Optional[int] = None
    distance_km: Optional[float] = None
    duree_estimee_h: Optional[float] = None
    zonale: Optional[str] = None
    statut: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class CheckpointControlCreate(BaseModel):
    numero_pv: str
    date_controle: Optional[datetime] = None
    lieu: Optional[str] = None
    vehicule_id: Optional[int] = None
    poids_reel_t: Optional[float] = None
    poids_autorise_t: Optional[float] = None
    type_controle: Optional[str] = None
    agent: Optional[str] = None
    sanction_appliquee: Optional[str] = None
    statut: Optional[str] = None


class CheckpointControlUpdate(BaseModel):
    numero_pv: Optional[str] = None
    date_controle: Optional[datetime] = None
    lieu: Optional[str] = None
    vehicule_id: Optional[int] = None
    poids_reel_t: Optional[float] = None
    poids_autorise_t: Optional[float] = None
    type_controle: Optional[str] = None
    agent: Optional[str] = None
    sanction_appliquee: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class CheckpointControlOut(BaseModel):
    id: int
    company_id: int
    numero_pv: str
    date_controle: Optional[datetime] = None
    lieu: Optional[str] = None
    vehicule_id: Optional[int] = None
    poids_reel_t: Optional[float] = None
    poids_autorise_t: Optional[float] = None
    type_controle: Optional[str] = None
    agent: Optional[str] = None
    sanction_appliquee: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class CargoInsuranceCreate(BaseModel):
    numero_police: str
    assureur: Optional[str] = None
    type_garantie: Optional[str] = None
    plafond_xaf: Optional[float] = None
    franchise_xaf: Optional[float] = None
    prime_xaf: Optional[float] = None
    date_effet: Optional[date] = None
    date_fin: Optional[date] = None
    statut: Optional[str] = None
    notes: Optional[str] = None


class CargoInsuranceUpdate(BaseModel):
    numero_police: Optional[str] = None
    assureur: Optional[str] = None
    type_garantie: Optional[str] = None
    plafond_xaf: Optional[float] = None
    franchise_xaf: Optional[float] = None
    prime_xaf: Optional[float] = None
    date_effet: Optional[date] = None
    date_fin: Optional[date] = None
    statut: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class CargoInsuranceOut(BaseModel):
    id: int
    company_id: int
    numero_police: str
    assureur: Optional[str] = None
    type_garantie: Optional[str] = None
    plafond_xaf: Optional[float] = None
    franchise_xaf: Optional[float] = None
    prime_xaf: Optional[float] = None
    date_effet: Optional[date] = None
    date_fin: Optional[date] = None
    statut: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class FreightBillCreate(BaseModel):
    numero_facture: str
    client_id: Optional[int] = None
    mission_id: Optional[int] = None
    montant_ht_xaf: Optional[float] = None
    tva_xaf: Optional[float] = None
    total_ttc_xaf: Optional[float] = None
    date_emission: Optional[date] = None
    date_echeance: Optional[date] = None
    statut: Optional[str] = None
    notes: Optional[str] = None


class FreightBillUpdate(BaseModel):
    numero_facture: Optional[str] = None
    client_id: Optional[int] = None
    mission_id: Optional[int] = None
    montant_ht_xaf: Optional[float] = None
    tva_xaf: Optional[float] = None
    total_ttc_xaf: Optional[float] = None
    date_emission: Optional[date] = None
    date_echeance: Optional[date] = None
    statut: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class FreightBillOut(BaseModel):
    id: int
    company_id: int
    numero_facture: str
    client_id: Optional[int] = None
    mission_id: Optional[int] = None
    montant_ht_xaf: Optional[float] = None
    tva_xaf: Optional[float] = None
    total_ttc_xaf: Optional[float] = None
    date_emission: Optional[date] = None
    date_echeance: Optional[date] = None
    statut: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class SubcontractorCreate(BaseModel):
    code_sous_traitant: str
    raison_sociale: Optional[str] = None
    niu: Optional[str] = None
    contact: Optional[str] = None
    telephone: Optional[str] = None
    nb_camions: Optional[int] = None
    zones_couvertes: Optional[str] = None
    agreement_numero: Optional[str] = None
    date_expiration_agreement: Optional[date] = None
    statut: Optional[str] = None


class SubcontractorUpdate(BaseModel):
    code_sous_traitant: Optional[str] = None
    raison_sociale: Optional[str] = None
    niu: Optional[str] = None
    contact: Optional[str] = None
    telephone: Optional[str] = None
    nb_camions: Optional[int] = None
    zones_couvertes: Optional[str] = None
    agreement_numero: Optional[str] = None
    date_expiration_agreement: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class SubcontractorOut(BaseModel):
    id: int
    company_id: int
    code_sous_traitant: str
    raison_sociale: Optional[str] = None
    niu: Optional[str] = None
    contact: Optional[str] = None
    telephone: Optional[str] = None
    nb_camions: Optional[int] = None
    zones_couvertes: Optional[str] = None
    agreement_numero: Optional[str] = None
    date_expiration_agreement: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class DangerousGoodsLoadCreate(BaseModel):
    reference: str
    mission_id: Optional[int] = None
    onu_number: Optional[str] = None
    classe_adr: Optional[str] = None
    designation_officielle: Optional[str] = None
    groupe_emballage: Optional[str] = None
    quantite_kg: Optional[float] = None
    etiquettes: Optional[str] = None
    formation_chauffeur: Optional[bool] = None
    statut: Optional[str] = None


class DangerousGoodsLoadUpdate(BaseModel):
    reference: Optional[str] = None
    mission_id: Optional[int] = None
    onu_number: Optional[str] = None
    classe_adr: Optional[str] = None
    designation_officielle: Optional[str] = None
    groupe_emballage: Optional[str] = None
    quantite_kg: Optional[float] = None
    etiquettes: Optional[str] = None
    formation_chauffeur: Optional[bool] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class DangerousGoodsLoadOut(BaseModel):
    id: int
    company_id: int
    reference: str
    mission_id: Optional[int] = None
    onu_number: Optional[str] = None
    classe_adr: Optional[str] = None
    designation_officielle: Optional[str] = None
    groupe_emballage: Optional[str] = None
    quantite_kg: Optional[float] = None
    etiquettes: Optional[str] = None
    formation_chauffeur: Optional[bool] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class VehicleDocumentCreate(BaseModel):
    numero_document: str
    vehicule_id: Optional[int] = None
    type_document: Optional[str] = None
    autorite_emission: Optional[str] = None
    date_emission: Optional[date] = None
    date_expiration: Optional[date] = None
    numero_police_associe: Optional[str] = None
    statut: Optional[str] = None
    notes: Optional[str] = None


class VehicleDocumentUpdate(BaseModel):
    numero_document: Optional[str] = None
    vehicule_id: Optional[int] = None
    type_document: Optional[str] = None
    autorite_emission: Optional[str] = None
    date_emission: Optional[date] = None
    date_expiration: Optional[date] = None
    numero_police_associe: Optional[str] = None
    statut: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class VehicleDocumentOut(BaseModel):
    id: int
    company_id: int
    numero_document: str
    vehicule_id: Optional[int] = None
    type_document: Optional[str] = None
    autorite_emission: Optional[str] = None
    date_emission: Optional[date] = None
    date_expiration: Optional[date] = None
    numero_police_associe: Optional[str] = None
    statut: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class GpsDeviceCreate(BaseModel):
    numero_serial_gps: str
    vehicule_id: Optional[int] = None
    fournisseur: Optional[str] = None
    modele: Optional[str] = None
    numero_sim: Optional[str] = None
    date_installation: Optional[date] = None
    date_derniere_communication: Optional[datetime] = None
    statut: Optional[str] = None
    notes: Optional[str] = None


class GpsDeviceUpdate(BaseModel):
    numero_serial_gps: Optional[str] = None
    vehicule_id: Optional[int] = None
    fournisseur: Optional[str] = None
    modele: Optional[str] = None
    numero_sim: Optional[str] = None
    date_installation: Optional[date] = None
    date_derniere_communication: Optional[datetime] = None
    statut: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class GpsDeviceOut(BaseModel):
    id: int
    company_id: int
    numero_serial_gps: str
    vehicule_id: Optional[int] = None
    fournisseur: Optional[str] = None
    modele: Optional[str] = None
    numero_sim: Optional[str] = None
    date_installation: Optional[date] = None
    date_derniere_communication: Optional[datetime] = None
    statut: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class TrafficPenaltyCreate(BaseModel):
    numero_pv: str
    vehicule_id: Optional[int] = None
    date_infraction: Optional[date] = None
    lieu: Optional[str] = None
    type_infraction: Optional[str] = None
    montant_amende_xaf: Optional[float] = None
    points_retires: Optional[int] = None
    chauffeur_id: Optional[int] = None
    statut: Optional[str] = None
    notes: Optional[str] = None


class TrafficPenaltyUpdate(BaseModel):
    numero_pv: Optional[str] = None
    vehicule_id: Optional[int] = None
    date_infraction: Optional[date] = None
    lieu: Optional[str] = None
    type_infraction: Optional[str] = None
    montant_amende_xaf: Optional[float] = None
    points_retires: Optional[int] = None
    chauffeur_id: Optional[int] = None
    statut: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class TrafficPenaltyOut(BaseModel):
    id: int
    company_id: int
    numero_pv: str
    vehicule_id: Optional[int] = None
    date_infraction: Optional[date] = None
    lieu: Optional[str] = None
    type_infraction: Optional[str] = None
    montant_amende_xaf: Optional[float] = None
    points_retires: Optional[int] = None
    chauffeur_id: Optional[int] = None
    statut: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class ConvoyCreate(BaseModel):
    code_convoi: str
    date_depart: Optional[datetime] = None
    date_arrivee: Optional[datetime] = None
    nb_vehicules: Optional[int] = None
    type_escorte: Optional[str] = None
    chef_convoi: Optional[str] = None
    itineraire: Optional[str] = None
    statut: Optional[str] = None


class ConvoyUpdate(BaseModel):
    code_convoi: Optional[str] = None
    date_depart: Optional[datetime] = None
    date_arrivee: Optional[datetime] = None
    nb_vehicules: Optional[int] = None
    type_escorte: Optional[str] = None
    chef_convoi: Optional[str] = None
    itineraire: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class ConvoyOut(BaseModel):
    id: int
    company_id: int
    code_convoi: str
    date_depart: Optional[datetime] = None
    date_arrivee: Optional[datetime] = None
    nb_vehicules: Optional[int] = None
    type_escorte: Optional[str] = None
    chef_convoi: Optional[str] = None
    itineraire: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class FleetKpiCreate(BaseModel):
    reference: str
    periode_debut: Optional[date] = None
    periode_fin: Optional[date] = None
    cout_total_xaf: Optional[float] = None
    km_parcourus: Optional[float] = None
    cout_par_km: Optional[float] = None
    taux_dispo_pct: Optional[float] = None
    taux_service_pct: Optional[float] = None
    nb_accidents: Optional[int] = None
    notes: Optional[str] = None


class FleetKpiUpdate(BaseModel):
    reference: Optional[str] = None
    periode_debut: Optional[date] = None
    periode_fin: Optional[date] = None
    cout_total_xaf: Optional[float] = None
    km_parcourus: Optional[float] = None
    cout_par_km: Optional[float] = None
    taux_dispo_pct: Optional[float] = None
    taux_service_pct: Optional[float] = None
    nb_accidents: Optional[int] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class FleetKpiOut(BaseModel):
    id: int
    company_id: int
    reference: str
    periode_debut: Optional[date] = None
    periode_fin: Optional[date] = None
    cout_total_xaf: Optional[float] = None
    km_parcourus: Optional[float] = None
    cout_par_km: Optional[float] = None
    taux_dispo_pct: Optional[float] = None
    taux_service_pct: Optional[float] = None
    nb_accidents: Optional[int] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}

