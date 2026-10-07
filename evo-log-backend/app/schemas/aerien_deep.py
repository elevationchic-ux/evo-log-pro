"""Schemas Pydantic pour transport-aerien (genere)."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date


class AircraftCreate(BaseModel):
    immatriculation: str
    modele: Optional[str] = None
    operateur: Optional[str] = None
    capacite_tonnes: Optional[int] = None
    autonomie_km: Optional[int] = None
    heures_vol_total: Optional[int] = None
    certificat_navigabilite_fin: Optional[date] = None
    statut: Optional[str] = None


class AircraftUpdate(BaseModel):
    immatriculation: Optional[str] = None
    modele: Optional[str] = None
    operateur: Optional[str] = None
    capacite_tonnes: Optional[int] = None
    autonomie_km: Optional[int] = None
    heures_vol_total: Optional[int] = None
    certificat_navigabilite_fin: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class AircraftOut(BaseModel):
    id: int
    company_id: int
    immatriculation: str
    modele: Optional[str] = None
    operateur: Optional[str] = None
    capacite_tonnes: Optional[int] = None
    autonomie_km: Optional[int] = None
    heures_vol_total: Optional[int] = None
    certificat_navigabilite_fin: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class AirWaybillCreate(BaseModel):
    numero_awb: str
    type_awb: Optional[str] = None
    expediteur: Optional[str] = None
    destinataire: Optional[str] = None
    aeroport_depart: Optional[str] = None
    aeroport_arrivee: Optional[str] = None
    nb_pieces: Optional[int] = None
    poids_kg: Optional[int] = None
    valeur_declaree_xaf: Optional[int] = None
    statut: Optional[str] = None


class AirWaybillUpdate(BaseModel):
    numero_awb: Optional[str] = None
    type_awb: Optional[str] = None
    expediteur: Optional[str] = None
    destinataire: Optional[str] = None
    aeroport_depart: Optional[str] = None
    aeroport_arrivee: Optional[str] = None
    nb_pieces: Optional[int] = None
    poids_kg: Optional[int] = None
    valeur_declaree_xaf: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class AirWaybillOut(BaseModel):
    id: int
    company_id: int
    numero_awb: str
    type_awb: Optional[str] = None
    expediteur: Optional[str] = None
    destinataire: Optional[str] = None
    aeroport_depart: Optional[str] = None
    aeroport_arrivee: Optional[str] = None
    nb_pieces: Optional[int] = None
    poids_kg: Optional[int] = None
    valeur_declaree_xaf: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class AirSlotCreate(BaseModel):
    reference: str
    aeroport: Optional[str] = None
    season: Optional[str] = None
    vol_attribue: Optional[str] = None
    journee: Optional[str] = None
    heure_obtc: Optional[str] = None
    slot_historique: Optional[bool] = None
    statut: Optional[str] = None


class AirSlotUpdate(BaseModel):
    reference: Optional[str] = None
    aeroport: Optional[str] = None
    season: Optional[str] = None
    vol_attribue: Optional[str] = None
    journee: Optional[str] = None
    heure_obtc: Optional[str] = None
    slot_historique: Optional[bool] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class AirSlotOut(BaseModel):
    id: int
    company_id: int
    reference: str
    aeroport: Optional[str] = None
    season: Optional[str] = None
    vol_attribue: Optional[str] = None
    journee: Optional[str] = None
    heure_obtc: Optional[str] = None
    slot_historique: Optional[bool] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class GroundHandlingJobCreate(BaseModel):
    reference: str
    vol: Optional[str] = None
    aeroport: Optional[str] = None
    date_traitement: Optional[datetime] = None
    prestataire: Optional[str] = None
    nb_pieces_fret: Optional[int] = None
    poids_fret_kg: Optional[int] = None
    cout_xaf: Optional[int] = None
    statut: Optional[str] = None


class GroundHandlingJobUpdate(BaseModel):
    reference: Optional[str] = None
    vol: Optional[str] = None
    aeroport: Optional[str] = None
    date_traitement: Optional[datetime] = None
    prestataire: Optional[str] = None
    nb_pieces_fret: Optional[int] = None
    poids_fret_kg: Optional[int] = None
    cout_xaf: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class GroundHandlingJobOut(BaseModel):
    id: int
    company_id: int
    reference: str
    vol: Optional[str] = None
    aeroport: Optional[str] = None
    date_traitement: Optional[datetime] = None
    prestataire: Optional[str] = None
    nb_pieces_fret: Optional[int] = None
    poids_fret_kg: Optional[int] = None
    cout_xaf: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class ULDInventoryCreate(BaseModel):
    numero_uld: str
    type_uld: Optional[str] = None
    proprietaire: Optional[str] = None
    position_actuelle: Optional[str] = None
    etat: Optional[str] = None
    date_derniere_inspection: Optional[date] = None
    statut: Optional[str] = None


class ULDInventoryUpdate(BaseModel):
    numero_uld: Optional[str] = None
    type_uld: Optional[str] = None
    proprietaire: Optional[str] = None
    position_actuelle: Optional[str] = None
    etat: Optional[str] = None
    date_derniere_inspection: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class ULDInventoryOut(BaseModel):
    id: int
    company_id: int
    numero_uld: str
    type_uld: Optional[str] = None
    proprietaire: Optional[str] = None
    position_actuelle: Optional[str] = None
    etat: Optional[str] = None
    date_derniere_inspection: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class CargoSecurityScreenCreate(BaseModel):
    reference: str
    numero_awb: Optional[str] = None
    statut_expediteur: Optional[str] = None
    methode_screening: Optional[str] = None
    date_screening: Optional[datetime] = None
    operateur: Optional[str] = None
    resultat: Optional[str] = None
    statut: Optional[str] = None


class CargoSecurityScreenUpdate(BaseModel):
    reference: Optional[str] = None
    numero_awb: Optional[str] = None
    statut_expediteur: Optional[str] = None
    methode_screening: Optional[str] = None
    date_screening: Optional[datetime] = None
    operateur: Optional[str] = None
    resultat: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class CargoSecurityScreenOut(BaseModel):
    id: int
    company_id: int
    reference: str
    numero_awb: Optional[str] = None
    statut_expediteur: Optional[str] = None
    methode_screening: Optional[str] = None
    date_screening: Optional[datetime] = None
    operateur: Optional[str] = None
    resultat: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class AirDangerousGoodsCreate(BaseModel):
    reference: str
    numero_awb: Optional[str] = None
    un_number: Optional[str] = None
    classe: Optional[str] = None
    packaging_group: Optional[str] = None
    quantite: Optional[str] = None
    etiquettes: Optional[str] = None
    statut: Optional[str] = None


class AirDangerousGoodsUpdate(BaseModel):
    reference: Optional[str] = None
    numero_awb: Optional[str] = None
    un_number: Optional[str] = None
    classe: Optional[str] = None
    packaging_group: Optional[str] = None
    quantite: Optional[str] = None
    etiquettes: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class AirDangerousGoodsOut(BaseModel):
    id: int
    company_id: int
    reference: str
    numero_awb: Optional[str] = None
    un_number: Optional[str] = None
    classe: Optional[str] = None
    packaging_group: Optional[str] = None
    quantite: Optional[str] = None
    etiquettes: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class FlightOperationCreate(BaseModel):
    reference: str
    numero_vol: Optional[str] = None
    aeronef: Optional[str] = None
    aeroport_depart: Optional[str] = None
    aeroport_arrivee: Optional[str] = None
    date_std: Optional[datetime] = None
    date_sta: Optional[datetime] = None
    date_ata: Optional[datetime] = None
    statut: Optional[str] = None


class FlightOperationUpdate(BaseModel):
    reference: Optional[str] = None
    numero_vol: Optional[str] = None
    aeronef: Optional[str] = None
    aeroport_depart: Optional[str] = None
    aeroport_arrivee: Optional[str] = None
    date_std: Optional[datetime] = None
    date_sta: Optional[datetime] = None
    date_ata: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class FlightOperationOut(BaseModel):
    id: int
    company_id: int
    reference: str
    numero_vol: Optional[str] = None
    aeronef: Optional[str] = None
    aeroport_depart: Optional[str] = None
    aeroport_arrivee: Optional[str] = None
    date_std: Optional[datetime] = None
    date_sta: Optional[datetime] = None
    date_ata: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class CrewRosterCreate(BaseModel):
    reference: str
    nom_membre: Optional[str] = None
    role: Optional[str] = None
    licence: Optional[str] = None
    qualification: Optional[str] = None
    date_prise_service: Optional[datetime] = None
    date_fin_service: Optional[datetime] = None
    heures_vol_mois: Optional[int] = None
    statut: Optional[str] = None


class CrewRosterUpdate(BaseModel):
    reference: Optional[str] = None
    nom_membre: Optional[str] = None
    role: Optional[str] = None
    licence: Optional[str] = None
    qualification: Optional[str] = None
    date_prise_service: Optional[datetime] = None
    date_fin_service: Optional[datetime] = None
    heures_vol_mois: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class CrewRosterOut(BaseModel):
    id: int
    company_id: int
    reference: str
    nom_membre: Optional[str] = None
    role: Optional[str] = None
    licence: Optional[str] = None
    qualification: Optional[str] = None
    date_prise_service: Optional[datetime] = None
    date_fin_service: Optional[datetime] = None
    heures_vol_mois: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class AircraftCheckCreate(BaseModel):
    reference: str
    immatriculation: Optional[str] = None
    type_check: Optional[str] = None
    atelier: Optional[str] = None
    date_debut: Optional[date] = None
    date_fin_prevue: Optional[date] = None
    date_retour_service: Optional[date] = None
    heures_arret: Optional[int] = None
    statut: Optional[str] = None


class AircraftCheckUpdate(BaseModel):
    reference: Optional[str] = None
    immatriculation: Optional[str] = None
    type_check: Optional[str] = None
    atelier: Optional[str] = None
    date_debut: Optional[date] = None
    date_fin_prevue: Optional[date] = None
    date_retour_service: Optional[date] = None
    heures_arret: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class AircraftCheckOut(BaseModel):
    id: int
    company_id: int
    reference: str
    immatriculation: Optional[str] = None
    type_check: Optional[str] = None
    atelier: Optional[str] = None
    date_debut: Optional[date] = None
    date_fin_prevue: Optional[date] = None
    date_retour_service: Optional[date] = None
    heures_arret: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class AirportCargoWarehouseCreate(BaseModel):
    code_entrepot: str
    aeroport: Optional[str] = None
    superficie_m2: Optional[int] = None
    capacite_palettes: Optional[int] = None
    zones_froides: Optional[bool] = None
    zone_douaniere: Optional[bool] = None
    zone_surete: Optional[bool] = None
    occupation_pct: Optional[int] = None
    statut: Optional[str] = None


class AirportCargoWarehouseUpdate(BaseModel):
    code_entrepot: Optional[str] = None
    aeroport: Optional[str] = None
    superficie_m2: Optional[int] = None
    capacite_palettes: Optional[int] = None
    zones_froides: Optional[bool] = None
    zone_douaniere: Optional[bool] = None
    zone_surete: Optional[bool] = None
    occupation_pct: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class AirportCargoWarehouseOut(BaseModel):
    id: int
    company_id: int
    code_entrepot: str
    aeroport: Optional[str] = None
    superficie_m2: Optional[int] = None
    capacite_palettes: Optional[int] = None
    zones_froides: Optional[bool] = None
    zone_douaniere: Optional[bool] = None
    zone_surete: Optional[bool] = None
    occupation_pct: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class AirTariffCreate(BaseModel):
    code_tarif: str
    origine: Optional[str] = None
    destination: Optional[str] = None
    poids_min_kg: Optional[int] = None
    type_cargo: Optional[str] = None
    prix_par_kg_xaf: Optional[int] = None
    surcharges_xaf: Optional[int] = None
    validite_debut: Optional[date] = None
    validite_fin: Optional[date] = None
    statut: Optional[str] = None


class AirTariffUpdate(BaseModel):
    code_tarif: Optional[str] = None
    origine: Optional[str] = None
    destination: Optional[str] = None
    poids_min_kg: Optional[int] = None
    type_cargo: Optional[str] = None
    prix_par_kg_xaf: Optional[int] = None
    surcharges_xaf: Optional[int] = None
    validite_debut: Optional[date] = None
    validite_fin: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class AirTariffOut(BaseModel):
    id: int
    company_id: int
    code_tarif: str
    origine: Optional[str] = None
    destination: Optional[str] = None
    poids_min_kg: Optional[int] = None
    type_cargo: Optional[str] = None
    prix_par_kg_xaf: Optional[int] = None
    surcharges_xaf: Optional[int] = None
    validite_debut: Optional[date] = None
    validite_fin: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}

