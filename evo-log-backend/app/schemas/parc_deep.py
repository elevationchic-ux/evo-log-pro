"""Schemas Pydantic pour parc-vehicules (genere)."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date


class VehicleInventoryCreate(BaseModel):
    numero_serie: str
    marque: Optional[str] = None
    modele: Optional[str] = None
    annee: Optional[int] = None
    carrosserie: Optional[str] = None
    energie: Optional[str] = None
    kilometrage: Optional[float] = None
    cout_acquisition_xaf: Optional[float] = None
    valeur_argent_xaf: Optional[float] = None


class VehicleInventoryUpdate(BaseModel):
    numero_serie: Optional[str] = None
    marque: Optional[str] = None
    modele: Optional[str] = None
    annee: Optional[int] = None
    carrosserie: Optional[str] = None
    energie: Optional[str] = None
    kilometrage: Optional[float] = None
    cout_acquisition_xaf: Optional[float] = None
    valeur_argent_xaf: Optional[float] = None
    is_active: Optional[bool] = None


class VehicleInventoryOut(BaseModel):
    id: int
    company_id: int
    numero_serie: str
    marque: Optional[str] = None
    modele: Optional[str] = None
    annee: Optional[int] = None
    carrosserie: Optional[str] = None
    energie: Optional[str] = None
    kilometrage: Optional[float] = None
    cout_acquisition_xaf: Optional[float] = None
    valeur_argent_xaf: Optional[float] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class TyreRecordCreate(BaseModel):
    numero_gomme: str
    vehicule_id: Optional[int] = None
    dimension: Optional[str] = None
    marque: Optional[str] = None
    position: Optional[str] = None
    km_parcourus: Optional[float] = None
    profondeur_couronne_mm: Optional[float] = None
    date_montage: Optional[date] = None
    statut: Optional[str] = None


class TyreRecordUpdate(BaseModel):
    numero_gomme: Optional[str] = None
    vehicule_id: Optional[int] = None
    dimension: Optional[str] = None
    marque: Optional[str] = None
    position: Optional[str] = None
    km_parcourus: Optional[float] = None
    profondeur_couronne_mm: Optional[float] = None
    date_montage: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class TyreRecordOut(BaseModel):
    id: int
    company_id: int
    numero_gomme: str
    vehicule_id: Optional[int] = None
    dimension: Optional[str] = None
    marque: Optional[str] = None
    position: Optional[str] = None
    km_parcourus: Optional[float] = None
    profondeur_couronne_mm: Optional[float] = None
    date_montage: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class SparePartCreate(BaseModel):
    code_piece: str
    designation: Optional[str] = None
    referencence_constructeur: Optional[str] = None
    famille: Optional[str] = None
    stock_actuel: Optional[float] = None
    seuil_mini: Optional[float] = None
    prix_unitaire_xaf: Optional[float] = None
    fournisseur_principal: Optional[str] = None
    compatibilites: Optional[str] = None


class SparePartUpdate(BaseModel):
    code_piece: Optional[str] = None
    designation: Optional[str] = None
    referencence_constructeur: Optional[str] = None
    famille: Optional[str] = None
    stock_actuel: Optional[float] = None
    seuil_mini: Optional[float] = None
    prix_unitaire_xaf: Optional[float] = None
    fournisseur_principal: Optional[str] = None
    compatibilites: Optional[str] = None
    is_active: Optional[bool] = None


class SparePartOut(BaseModel):
    id: int
    company_id: int
    code_piece: str
    designation: Optional[str] = None
    referencence_constructeur: Optional[str] = None
    famille: Optional[str] = None
    stock_actuel: Optional[float] = None
    seuil_mini: Optional[float] = None
    prix_unitaire_xaf: Optional[float] = None
    fournisseur_principal: Optional[str] = None
    compatibilites: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class WorkshopAppointmentCreate(BaseModel):
    reference: str
    vehicule_id: Optional[int] = None
    date_horaire: Optional[datetime] = None
    type_intervention: Optional[str] = None
    mecanicien: Optional[str] = None
    duree_estimee_h: Optional[float] = None
    cout_estime_xaf: Optional[float] = None
    statut: Optional[str] = None
    notes: Optional[str] = None


class WorkshopAppointmentUpdate(BaseModel):
    reference: Optional[str] = None
    vehicule_id: Optional[int] = None
    date_horaire: Optional[datetime] = None
    type_intervention: Optional[str] = None
    mecanicien: Optional[str] = None
    duree_estimee_h: Optional[float] = None
    cout_estime_xaf: Optional[float] = None
    statut: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class WorkshopAppointmentOut(BaseModel):
    id: int
    company_id: int
    reference: str
    vehicule_id: Optional[int] = None
    date_horaire: Optional[datetime] = None
    type_intervention: Optional[str] = None
    mecanicien: Optional[str] = None
    duree_estimee_h: Optional[float] = None
    cout_estime_xaf: Optional[float] = None
    statut: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class InsuranceClaimCreate(BaseModel):
    numero_sinistre: str
    vehicule_id: Optional[int] = None
    date_sinistre: Optional[date] = None
    type_sinistre: Optional[str] = None
    description: Optional[str] = None
    montant_estime_xaf: Optional[float] = None
    montant_indemnise_xaf: Optional[float] = None
    assureur: Optional[str] = None
    statut: Optional[str] = None


class InsuranceClaimUpdate(BaseModel):
    numero_sinistre: Optional[str] = None
    vehicule_id: Optional[int] = None
    date_sinistre: Optional[date] = None
    type_sinistre: Optional[str] = None
    description: Optional[str] = None
    montant_estime_xaf: Optional[float] = None
    montant_indemnise_xaf: Optional[float] = None
    assureur: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class InsuranceClaimOut(BaseModel):
    id: int
    company_id: int
    numero_sinistre: str
    vehicule_id: Optional[int] = None
    date_sinistre: Optional[date] = None
    type_sinistre: Optional[str] = None
    description: Optional[str] = None
    montant_estime_xaf: Optional[float] = None
    montant_indemnise_xaf: Optional[float] = None
    assureur: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class RegistrationRecordCreate(BaseModel):
    numero_immatriculation: str
    vehicule_id: Optional[int] = None
    proprietaire: Optional[str] = None
    date_emission: Optional[date] = None
    date_expiration: Optional[date] = None
    autorite: Optional[str] = None
    statut: Optional[str] = None


class RegistrationRecordUpdate(BaseModel):
    numero_immatriculation: Optional[str] = None
    vehicule_id: Optional[int] = None
    proprietaire: Optional[str] = None
    date_emission: Optional[date] = None
    date_expiration: Optional[date] = None
    autorite: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class RegistrationRecordOut(BaseModel):
    id: int
    company_id: int
    numero_immatriculation: str
    vehicule_id: Optional[int] = None
    proprietaire: Optional[str] = None
    date_emission: Optional[date] = None
    date_expiration: Optional[date] = None
    autorite: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class TechnicalVisitCreate(BaseModel):
    numero_pv: str
    vehicule_id: Optional[int] = None
    date_visite: Optional[date] = None
    centre_controle: Optional[str] = None
    resultat: Optional[str] = None
    observations: Optional[str] = None
    contre_visite_possible: Optional[bool] = None
    statut: Optional[str] = None


class TechnicalVisitUpdate(BaseModel):
    numero_pv: Optional[str] = None
    vehicule_id: Optional[int] = None
    date_visite: Optional[date] = None
    centre_controle: Optional[str] = None
    resultat: Optional[str] = None
    observations: Optional[str] = None
    contre_visite_possible: Optional[bool] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class TechnicalVisitOut(BaseModel):
    id: int
    company_id: int
    numero_pv: str
    vehicule_id: Optional[int] = None
    date_visite: Optional[date] = None
    centre_controle: Optional[str] = None
    resultat: Optional[str] = None
    observations: Optional[str] = None
    contre_visite_possible: Optional[bool] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class FuelConsumptionCreate(BaseModel):
    reference: str
    vehicule_id: Optional[int] = None
    date: Optional[date] = None
    litres: Optional[float] = None
    prix_total_xaf: Optional[float] = None
    km_etape: Optional[float] = None
    conso_l100km: Optional[float] = None
    station: Optional[str] = None
    carburant: Optional[str] = None


class FuelConsumptionUpdate(BaseModel):
    reference: Optional[str] = None
    vehicule_id: Optional[int] = None
    date: Optional[date] = None
    litres: Optional[float] = None
    prix_total_xaf: Optional[float] = None
    km_etape: Optional[float] = None
    conso_l100km: Optional[float] = None
    station: Optional[str] = None
    carburant: Optional[str] = None
    is_active: Optional[bool] = None


class FuelConsumptionOut(BaseModel):
    id: int
    company_id: int
    reference: str
    vehicule_id: Optional[int] = None
    date: Optional[date] = None
    litres: Optional[float] = None
    prix_total_xaf: Optional[float] = None
    km_etape: Optional[float] = None
    conso_l100km: Optional[float] = None
    station: Optional[str] = None
    carburant: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class VehicleLifecycleCreate(BaseModel):
    reference: str
    vehicule_id: Optional[int] = None
    date_acquisition: Optional[date] = None
    date_reforme: Optional[date] = None
    duree_detention_an: Optional[int] = None
    km_final: Optional[float] = None
    mode_reforme: Optional[str] = None
    valeur_recuperation_xaf: Optional[float] = None


class VehicleLifecycleUpdate(BaseModel):
    reference: Optional[str] = None
    vehicule_id: Optional[int] = None
    date_acquisition: Optional[date] = None
    date_reforme: Optional[date] = None
    duree_detention_an: Optional[int] = None
    km_final: Optional[float] = None
    mode_reforme: Optional[str] = None
    valeur_recuperation_xaf: Optional[float] = None
    is_active: Optional[bool] = None


class VehicleLifecycleOut(BaseModel):
    id: int
    company_id: int
    reference: str
    vehicule_id: Optional[int] = None
    date_acquisition: Optional[date] = None
    date_reforme: Optional[date] = None
    duree_detention_an: Optional[int] = None
    km_final: Optional[float] = None
    mode_reforme: Optional[str] = None
    valeur_recuperation_xaf: Optional[float] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class CostAnalysisCreate(BaseModel):
    reference: str
    vehicule_id: Optional[int] = None
    periode: Optional[str] = None
    cout_carburant_xaf: Optional[float] = None
    cout_maintenance_xaf: Optional[float] = None
    cout_assurance_xaf: Optional[float] = None
    cout_amortissement_xaf: Optional[float] = None
    cout_total_xaf: Optional[float] = None


class CostAnalysisUpdate(BaseModel):
    reference: Optional[str] = None
    vehicule_id: Optional[int] = None
    periode: Optional[str] = None
    cout_carburant_xaf: Optional[float] = None
    cout_maintenance_xaf: Optional[float] = None
    cout_assurance_xaf: Optional[float] = None
    cout_amortissement_xaf: Optional[float] = None
    cout_total_xaf: Optional[float] = None
    is_active: Optional[bool] = None


class CostAnalysisOut(BaseModel):
    id: int
    company_id: int
    reference: str
    vehicule_id: Optional[int] = None
    periode: Optional[str] = None
    cout_carburant_xaf: Optional[float] = None
    cout_maintenance_xaf: Optional[float] = None
    cout_assurance_xaf: Optional[float] = None
    cout_amortissement_xaf: Optional[float] = None
    cout_total_xaf: Optional[float] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}

