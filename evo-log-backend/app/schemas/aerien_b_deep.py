"""Schemas Pydantic pour transport-aerien (genere)."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date


class HouseAirWaybillCreate(BaseModel):
    numero_hawb: str
    numero_mawb: Optional[str] = None
    expediteur: Optional[str] = None
    destinataire: Optional[str] = None
    nb_colis: Optional[int] = None
    poids_kg: Optional[int] = None
    nature_marchandise: Optional[str] = None
    statut: Optional[str] = None


class HouseAirWaybillUpdate(BaseModel):
    numero_hawb: Optional[str] = None
    numero_mawb: Optional[str] = None
    expediteur: Optional[str] = None
    destinataire: Optional[str] = None
    nb_colis: Optional[int] = None
    poids_kg: Optional[int] = None
    nature_marchandise: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class HouseAirWaybillOut(BaseModel):
    id: int
    company_id: int
    numero_hawb: str
    numero_mawb: Optional[str] = None
    expediteur: Optional[str] = None
    destinataire: Optional[str] = None
    nb_colis: Optional[int] = None
    poids_kg: Optional[int] = None
    nature_marchandise: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class PerishableCargoCreate(BaseModel):
    reference: str
    numero_mawb: Optional[str] = None
    produit: Optional[str] = None
    plage_temp_c: Optional[str] = None
    poids_kg: Optional[int] = None
    date_embarquement: Optional[datetime] = None
    statut: Optional[str] = None


class PerishableCargoUpdate(BaseModel):
    reference: Optional[str] = None
    numero_mawb: Optional[str] = None
    produit: Optional[str] = None
    plage_temp_c: Optional[str] = None
    poids_kg: Optional[int] = None
    date_embarquement: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class PerishableCargoOut(BaseModel):
    id: int
    company_id: int
    reference: str
    numero_mawb: Optional[str] = None
    produit: Optional[str] = None
    plage_temp_c: Optional[str] = None
    poids_kg: Optional[int] = None
    date_embarquement: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class LiveAnimalShipmentCreate(BaseModel):
    reference: str
    numero_mawb: Optional[str] = None
    espece: Optional[str] = None
    nb_animaux: Optional[int] = None
    type_conteneur: Optional[str] = None
    date_depart: Optional[datetime] = None
    statut: Optional[str] = None


class LiveAnimalShipmentUpdate(BaseModel):
    reference: Optional[str] = None
    numero_mawb: Optional[str] = None
    espece: Optional[str] = None
    nb_animaux: Optional[int] = None
    type_conteneur: Optional[str] = None
    date_depart: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class LiveAnimalShipmentOut(BaseModel):
    id: int
    company_id: int
    reference: str
    numero_mawb: Optional[str] = None
    espece: Optional[str] = None
    nb_animaux: Optional[int] = None
    type_conteneur: Optional[str] = None
    date_depart: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class CharteredFlightCreate(BaseModel):
    numero_affretement: str
    client: Optional[str] = None
    immatriculation: Optional[str] = None
    depart_aeroport: Optional[str] = None
    arrivee_aeroport: Optional[str] = None
    capacite_tonnes: Optional[int] = None
    date_vol: Optional[datetime] = None
    statut: Optional[str] = None


class CharteredFlightUpdate(BaseModel):
    numero_affretement: Optional[str] = None
    client: Optional[str] = None
    immatriculation: Optional[str] = None
    depart_aeroport: Optional[str] = None
    arrivee_aeroport: Optional[str] = None
    capacite_tonnes: Optional[int] = None
    date_vol: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class CharteredFlightOut(BaseModel):
    id: int
    company_id: int
    numero_affretement: str
    client: Optional[str] = None
    immatriculation: Optional[str] = None
    depart_aeroport: Optional[str] = None
    arrivee_aeroport: Optional[str] = None
    capacite_tonnes: Optional[int] = None
    date_vol: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class AirCustomsClearanceCreate(BaseModel):
    numero_dossier: str
    numero_mawb: Optional[str] = None
    type_operation: Optional[str] = None
    bureau_douane: Optional[str] = None
    droits_xaf: Optional[int] = None
    date_depot: Optional[date] = None
    statut: Optional[str] = None


class AirCustomsClearanceUpdate(BaseModel):
    numero_dossier: Optional[str] = None
    numero_mawb: Optional[str] = None
    type_operation: Optional[str] = None
    bureau_douane: Optional[str] = None
    droits_xaf: Optional[int] = None
    date_depot: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class AirCustomsClearanceOut(BaseModel):
    id: int
    company_id: int
    numero_dossier: str
    numero_mawb: Optional[str] = None
    type_operation: Optional[str] = None
    bureau_douane: Optional[str] = None
    droits_xaf: Optional[int] = None
    date_depot: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class ApronMovementCreate(BaseModel):
    reference: str
    poste_parc: Optional[str] = None
    immatriculation: Optional[str] = None
    type_mouvement: Optional[str] = None
    date_debut: Optional[datetime] = None
    date_fin: Optional[datetime] = None
    statut: Optional[str] = None


class ApronMovementUpdate(BaseModel):
    reference: Optional[str] = None
    poste_parc: Optional[str] = None
    immatriculation: Optional[str] = None
    type_mouvement: Optional[str] = None
    date_debut: Optional[datetime] = None
    date_fin: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class ApronMovementOut(BaseModel):
    id: int
    company_id: int
    reference: str
    poste_parc: Optional[str] = None
    immatriculation: Optional[str] = None
    type_mouvement: Optional[str] = None
    date_debut: Optional[datetime] = None
    date_fin: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class NoiseComplianceRecordCreate(BaseModel):
    reference: str
    immatriculation: Optional[str] = None
    coefficient_bruit_db: Optional[int] = None
    creneau: Optional[str] = None
    date_mesure: Optional[date] = None
    quota_consomme: Optional[int] = None
    statut: Optional[str] = None


class NoiseComplianceRecordUpdate(BaseModel):
    reference: Optional[str] = None
    immatriculation: Optional[str] = None
    coefficient_bruit_db: Optional[int] = None
    creneau: Optional[str] = None
    date_mesure: Optional[date] = None
    quota_consomme: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class NoiseComplianceRecordOut(BaseModel):
    id: int
    company_id: int
    reference: str
    immatriculation: Optional[str] = None
    coefficient_bruit_db: Optional[int] = None
    creneau: Optional[str] = None
    date_mesure: Optional[date] = None
    quota_consomme: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}

