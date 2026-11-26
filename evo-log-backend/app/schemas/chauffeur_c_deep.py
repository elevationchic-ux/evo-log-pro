"""Schemas Pydantic pour portail-chauffeur (genere)."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date


class ChfTripSheetCreate(BaseModel):
    reference: str
    mission: Optional[str] = None
    debut: Optional[datetime] = None
    fin: Optional[datetime] = None
    km_debut: Optional[int] = None
    km_fin: Optional[int] = None
    statut: Optional[str] = None


class ChfTripSheetUpdate(BaseModel):
    reference: Optional[str] = None
    mission: Optional[str] = None
    debut: Optional[datetime] = None
    fin: Optional[datetime] = None
    km_debut: Optional[int] = None
    km_fin: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class ChfTripSheetOut(BaseModel):
    id: int
    company_id: int
    reference: str
    mission: Optional[str] = None
    debut: Optional[datetime] = None
    fin: Optional[datetime] = None
    km_debut: Optional[int] = None
    km_fin: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class ChfDailyVehicleCheckCreate(BaseModel):
    reference: str
    vehicule: Optional[str] = None
    date_controle: Optional[datetime] = None
    points_controles: Optional[int] = None
    anomalies: Optional[bool] = None
    statut: Optional[str] = None


class ChfDailyVehicleCheckUpdate(BaseModel):
    reference: Optional[str] = None
    vehicule: Optional[str] = None
    date_controle: Optional[datetime] = None
    points_controles: Optional[int] = None
    anomalies: Optional[bool] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class ChfDailyVehicleCheckOut(BaseModel):
    id: int
    company_id: int
    reference: str
    vehicule: Optional[str] = None
    date_controle: Optional[datetime] = None
    points_controles: Optional[int] = None
    anomalies: Optional[bool] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class ChfFuelLogCreate(BaseModel):
    reference: str
    vehicule: Optional[str] = None
    litres: Optional[float] = None
    prix: Optional[float] = None
    station: Optional[str] = None
    date_plein: Optional[datetime] = None
    statut: Optional[str] = None


class ChfFuelLogUpdate(BaseModel):
    reference: Optional[str] = None
    vehicule: Optional[str] = None
    litres: Optional[float] = None
    prix: Optional[float] = None
    station: Optional[str] = None
    date_plein: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class ChfFuelLogOut(BaseModel):
    id: int
    company_id: int
    reference: str
    vehicule: Optional[str] = None
    litres: Optional[float] = None
    prix: Optional[float] = None
    station: Optional[str] = None
    date_plein: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class ChfDrivingTimeRecordCreate(BaseModel):
    reference: str
    chauffeur: Optional[str] = None
    debut: Optional[datetime] = None
    fin: Optional[datetime] = None
    minutes_conduite: Optional[int] = None
    statut: Optional[str] = None


class ChfDrivingTimeRecordUpdate(BaseModel):
    reference: Optional[str] = None
    chauffeur: Optional[str] = None
    debut: Optional[datetime] = None
    fin: Optional[datetime] = None
    minutes_conduite: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class ChfDrivingTimeRecordOut(BaseModel):
    id: int
    company_id: int
    reference: str
    chauffeur: Optional[str] = None
    debut: Optional[datetime] = None
    fin: Optional[datetime] = None
    minutes_conduite: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class ChfRestBreakCreate(BaseModel):
    reference: str
    chauffeur: Optional[str] = None
    debut: Optional[datetime] = None
    duree_min: Optional[int] = None
    lieu: Optional[str] = None
    statut: Optional[str] = None


class ChfRestBreakUpdate(BaseModel):
    reference: Optional[str] = None
    chauffeur: Optional[str] = None
    debut: Optional[datetime] = None
    duree_min: Optional[int] = None
    lieu: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class ChfRestBreakOut(BaseModel):
    id: int
    company_id: int
    reference: str
    chauffeur: Optional[str] = None
    debut: Optional[datetime] = None
    duree_min: Optional[int] = None
    lieu: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class ChfTollReceiptCreate(BaseModel):
    reference: str
    peage: Optional[str] = None
    montant: Optional[float] = None
    date_passage: Optional[datetime] = None
    troncon: Optional[str] = None
    statut: Optional[str] = None


class ChfTollReceiptUpdate(BaseModel):
    reference: Optional[str] = None
    peage: Optional[str] = None
    montant: Optional[float] = None
    date_passage: Optional[datetime] = None
    troncon: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class ChfTollReceiptOut(BaseModel):
    id: int
    company_id: int
    reference: str
    peage: Optional[str] = None
    montant: Optional[float] = None
    date_passage: Optional[datetime] = None
    troncon: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class ChfParkingSessionCreate(BaseModel):
    reference: str
    lieu: Optional[str] = None
    entree: Optional[datetime] = None
    sortie: Optional[datetime] = None
    frais: Optional[float] = None
    statut: Optional[str] = None


class ChfParkingSessionUpdate(BaseModel):
    reference: Optional[str] = None
    lieu: Optional[str] = None
    entree: Optional[datetime] = None
    sortie: Optional[datetime] = None
    frais: Optional[float] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class ChfParkingSessionOut(BaseModel):
    id: int
    company_id: int
    reference: str
    lieu: Optional[str] = None
    entree: Optional[datetime] = None
    sortie: Optional[datetime] = None
    frais: Optional[float] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class ChfCargoSealCreate(BaseModel):
    reference: str
    unite: Optional[str] = None
    numero_plomb: Optional[str] = None
    pose_datetime: Optional[datetime] = None
    retrait_datetime: Optional[datetime] = None
    intact: Optional[bool] = None
    statut: Optional[str] = None


class ChfCargoSealUpdate(BaseModel):
    reference: Optional[str] = None
    unite: Optional[str] = None
    numero_plomb: Optional[str] = None
    pose_datetime: Optional[datetime] = None
    retrait_datetime: Optional[datetime] = None
    intact: Optional[bool] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class ChfCargoSealOut(BaseModel):
    id: int
    company_id: int
    reference: str
    unite: Optional[str] = None
    numero_plomb: Optional[str] = None
    pose_datetime: Optional[datetime] = None
    retrait_datetime: Optional[datetime] = None
    intact: Optional[bool] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class ChfRoadsideIncidentCreate(BaseModel):
    reference: str
    type_incident: Optional[str] = None
    localisation: Optional[str] = None
    date: Optional[datetime] = None
    gravite: Optional[str] = None
    decrit: Optional[str] = None
    statut: Optional[str] = None


class ChfRoadsideIncidentUpdate(BaseModel):
    reference: Optional[str] = None
    type_incident: Optional[str] = None
    localisation: Optional[str] = None
    date: Optional[datetime] = None
    gravite: Optional[str] = None
    decrit: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class ChfRoadsideIncidentOut(BaseModel):
    id: int
    company_id: int
    reference: str
    type_incident: Optional[str] = None
    localisation: Optional[str] = None
    date: Optional[datetime] = None
    gravite: Optional[str] = None
    decrit: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class ChfDeliveryStopCreate(BaseModel):
    reference: str
    tournee: Optional[str] = None
    adresse: Optional[str] = None
    ordre: Optional[int] = None
    arrivee: Optional[datetime] = None
    departure: Optional[datetime] = None
    statut: Optional[str] = None


class ChfDeliveryStopUpdate(BaseModel):
    reference: Optional[str] = None
    tournee: Optional[str] = None
    adresse: Optional[str] = None
    ordre: Optional[int] = None
    arrivee: Optional[datetime] = None
    departure: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class ChfDeliveryStopOut(BaseModel):
    id: int
    company_id: int
    reference: str
    tournee: Optional[str] = None
    adresse: Optional[str] = None
    ordre: Optional[int] = None
    arrivee: Optional[datetime] = None
    departure: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class ChfMileageLogCreate(BaseModel):
    reference: str
    vehicule: Optional[str] = None
    date: Optional[datetime] = None
    km_debut: Optional[int] = None
    km_fin: Optional[int] = None
    statut: Optional[str] = None


class ChfMileageLogUpdate(BaseModel):
    reference: Optional[str] = None
    vehicule: Optional[str] = None
    date: Optional[datetime] = None
    km_debut: Optional[int] = None
    km_fin: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class ChfMileageLogOut(BaseModel):
    id: int
    company_id: int
    reference: str
    vehicule: Optional[str] = None
    date: Optional[datetime] = None
    km_debut: Optional[int] = None
    km_fin: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class ChfLoadSecuringCheckCreate(BaseModel):
    reference: str
    unite: Optional[str] = None
    sangles_ok: Optional[bool] = None
    poids_equilibre: Optional[str] = None
    controle_datetime: Optional[datetime] = None
    statut: Optional[str] = None


class ChfLoadSecuringCheckUpdate(BaseModel):
    reference: Optional[str] = None
    unite: Optional[str] = None
    sangles_ok: Optional[bool] = None
    poids_equilibre: Optional[str] = None
    controle_datetime: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class ChfLoadSecuringCheckOut(BaseModel):
    id: int
    company_id: int
    reference: str
    unite: Optional[str] = None
    sangles_ok: Optional[bool] = None
    poids_equilibre: Optional[str] = None
    controle_datetime: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class ChfBorderCrossingCreate(BaseModel):
    reference: str
    poste: Optional[str] = None
    pays: Optional[str] = None
    entree_sortie: Optional[str] = None
    horodatage: Optional[datetime] = None
    documents_ok: Optional[bool] = None
    statut: Optional[str] = None


class ChfBorderCrossingUpdate(BaseModel):
    reference: Optional[str] = None
    poste: Optional[str] = None
    pays: Optional[str] = None
    entree_sortie: Optional[str] = None
    horodatage: Optional[datetime] = None
    documents_ok: Optional[bool] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class ChfBorderCrossingOut(BaseModel):
    id: int
    company_id: int
    reference: str
    poste: Optional[str] = None
    pays: Optional[str] = None
    entree_sortie: Optional[str] = None
    horodatage: Optional[datetime] = None
    documents_ok: Optional[bool] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class ChfDeliveryAppointmentCreate(BaseModel):
    reference: str
    client: Optional[str] = None
    creneau: Optional[datetime] = None
    site: Optional[str] = None
    contact: Optional[str] = None
    statut: Optional[str] = None


class ChfDeliveryAppointmentUpdate(BaseModel):
    reference: Optional[str] = None
    client: Optional[str] = None
    creneau: Optional[datetime] = None
    site: Optional[str] = None
    contact: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class ChfDeliveryAppointmentOut(BaseModel):
    id: int
    company_id: int
    reference: str
    client: Optional[str] = None
    creneau: Optional[datetime] = None
    site: Optional[str] = None
    contact: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class ChfPpeIssueCreate(BaseModel):
    reference: str
    equipement: Optional[str] = None
    taille: Optional[str] = None
    date_remise: Optional[date] = None
    etat: Optional[str] = None
    statut: Optional[str] = None


class ChfPpeIssueUpdate(BaseModel):
    reference: Optional[str] = None
    equipement: Optional[str] = None
    taille: Optional[str] = None
    date_remise: Optional[date] = None
    etat: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class ChfPpeIssueOut(BaseModel):
    id: int
    company_id: int
    reference: str
    equipement: Optional[str] = None
    taille: Optional[str] = None
    date_remise: Optional[date] = None
    etat: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class ChfShiftHandoverCreate(BaseModel):
    reference: str
    sortant: Optional[str] = None
    entrant: Optional[str] = None
    datetime: Optional[datetime] = None
    consignes: Optional[str] = None
    statut: Optional[str] = None


class ChfShiftHandoverUpdate(BaseModel):
    reference: Optional[str] = None
    sortant: Optional[str] = None
    entrant: Optional[str] = None
    datetime: Optional[datetime] = None
    consignes: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class ChfShiftHandoverOut(BaseModel):
    id: int
    company_id: int
    reference: str
    sortant: Optional[str] = None
    entrant: Optional[str] = None
    datetime: Optional[datetime] = None
    consignes: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class ChfBreakdownReportCreate(BaseModel):
    reference: str
    vehicule: Optional[str] = None
    panne: Optional[str] = None
    lieu: Optional[str] = None
    date_signalement: Optional[datetime] = None
    immobilise: Optional[bool] = None
    statut: Optional[str] = None


class ChfBreakdownReportUpdate(BaseModel):
    reference: Optional[str] = None
    vehicule: Optional[str] = None
    panne: Optional[str] = None
    lieu: Optional[str] = None
    date_signalement: Optional[datetime] = None
    immobilise: Optional[bool] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class ChfBreakdownReportOut(BaseModel):
    id: int
    company_id: int
    reference: str
    vehicule: Optional[str] = None
    panne: Optional[str] = None
    lieu: Optional[str] = None
    date_signalement: Optional[datetime] = None
    immobilise: Optional[bool] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class ChfTyreCheckCreate(BaseModel):
    reference: str
    vehicule: Optional[str] = None
    numero_essieu: Optional[int] = None
    pression_bar: Optional[float] = None
    usure_mm: Optional[float] = None
    date_controle: Optional[datetime] = None
    statut: Optional[str] = None


class ChfTyreCheckUpdate(BaseModel):
    reference: Optional[str] = None
    vehicule: Optional[str] = None
    numero_essieu: Optional[int] = None
    pression_bar: Optional[float] = None
    usure_mm: Optional[float] = None
    date_controle: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class ChfTyreCheckOut(BaseModel):
    id: int
    company_id: int
    reference: str
    vehicule: Optional[str] = None
    numero_essieu: Optional[int] = None
    pression_bar: Optional[float] = None
    usure_mm: Optional[float] = None
    date_controle: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class ChfCargoPhotoCreate(BaseModel):
    reference: str
    mission: Optional[str] = None
    prise: Optional[datetime] = None
    legende: Optional[str] = None
    fichier: Optional[str] = None
    statut: Optional[str] = None


class ChfCargoPhotoUpdate(BaseModel):
    reference: Optional[str] = None
    mission: Optional[str] = None
    prise: Optional[datetime] = None
    legende: Optional[str] = None
    fichier: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class ChfCargoPhotoOut(BaseModel):
    id: int
    company_id: int
    reference: str
    mission: Optional[str] = None
    prise: Optional[datetime] = None
    legende: Optional[str] = None
    fichier: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}

