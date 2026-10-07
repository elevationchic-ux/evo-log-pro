"""Schemas Pydantic pour transport-ferroviaire (genere)."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date


class RailWheelSetCreate(BaseModel):
    numero_essieu: str
    type_essieu: Optional[str] = None
    diametre_mm: Optional[int] = None
    km_parcourus: Optional[int] = None
    date_controle: Optional[date] = None
    statut: Optional[str] = None


class RailWheelSetUpdate(BaseModel):
    numero_essieu: Optional[str] = None
    type_essieu: Optional[str] = None
    diametre_mm: Optional[int] = None
    km_parcourus: Optional[int] = None
    date_controle: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class RailWheelSetOut(BaseModel):
    id: int
    company_id: int
    numero_essieu: str
    type_essieu: Optional[str] = None
    diametre_mm: Optional[int] = None
    km_parcourus: Optional[int] = None
    date_controle: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class RailLoadingGaugeCreate(BaseModel):
    code_gabarit: str
    ligne: Optional[str] = None
    largeur_max_mm: Optional[int] = None
    hauteur_max_mm: Optional[int] = None
    masse_max_t: Optional[int] = None
    statut: Optional[str] = None


class RailLoadingGaugeUpdate(BaseModel):
    code_gabarit: Optional[str] = None
    ligne: Optional[str] = None
    largeur_max_mm: Optional[int] = None
    hauteur_max_mm: Optional[int] = None
    masse_max_t: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class RailLoadingGaugeOut(BaseModel):
    id: int
    company_id: int
    code_gabarit: str
    ligne: Optional[str] = None
    largeur_max_mm: Optional[int] = None
    hauteur_max_mm: Optional[int] = None
    masse_max_t: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class RailShuntingPlanCreate(BaseModel):
    reference: str
    yard: Optional[str] = None
    voie_source: Optional[str] = None
    voie_destinataire: Optional[str] = None
    nb_wagons: Optional[int] = None
    operateur: Optional[str] = None
    date_plan: Optional[datetime] = None
    statut: Optional[str] = None


class RailShuntingPlanUpdate(BaseModel):
    reference: Optional[str] = None
    yard: Optional[str] = None
    voie_source: Optional[str] = None
    voie_destinataire: Optional[str] = None
    nb_wagons: Optional[int] = None
    operateur: Optional[str] = None
    date_plan: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class RailShuntingPlanOut(BaseModel):
    id: int
    company_id: int
    reference: str
    yard: Optional[str] = None
    voie_source: Optional[str] = None
    voie_destinataire: Optional[str] = None
    nb_wagons: Optional[int] = None
    operateur: Optional[str] = None
    date_plan: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class RailTrainConsistCreate(BaseModel):
    reference: str
    numero_train: Optional[str] = None
    nb_wagons: Optional[int] = None
    masse_total_t: Optional[int] = None
    longueur_m: Optional[int] = None
    locomotive: Optional[str] = None
    date_composition: Optional[datetime] = None
    statut: Optional[str] = None


class RailTrainConsistUpdate(BaseModel):
    reference: Optional[str] = None
    numero_train: Optional[str] = None
    nb_wagons: Optional[int] = None
    masse_total_t: Optional[int] = None
    longueur_m: Optional[int] = None
    locomotive: Optional[str] = None
    date_composition: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class RailTrainConsistOut(BaseModel):
    id: int
    company_id: int
    reference: str
    numero_train: Optional[str] = None
    nb_wagons: Optional[int] = None
    masse_total_t: Optional[int] = None
    longueur_m: Optional[int] = None
    locomotive: Optional[str] = None
    date_composition: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class RailPathOccupancyCreate(BaseModel):
    reference: str
    numero_train: Optional[str] = None
    section: Optional[str] = None
    date_debut: Optional[datetime] = None
    date_fin: Optional[datetime] = None
    attribue_par: Optional[str] = None
    statut: Optional[str] = None


class RailPathOccupancyUpdate(BaseModel):
    reference: Optional[str] = None
    numero_train: Optional[str] = None
    section: Optional[str] = None
    date_debut: Optional[datetime] = None
    date_fin: Optional[datetime] = None
    attribue_par: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class RailPathOccupancyOut(BaseModel):
    id: int
    company_id: int
    reference: str
    numero_train: Optional[str] = None
    section: Optional[str] = None
    date_debut: Optional[datetime] = None
    date_fin: Optional[datetime] = None
    attribue_par: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class RailWagonDispatchCreate(BaseModel):
    reference: str
    numero_wagon: Optional[str] = None
    client: Optional[str] = None
    destination: Optional[str] = None
    produit: Optional[str] = None
    date_affectation: Optional[date] = None
    statut: Optional[str] = None


class RailWagonDispatchUpdate(BaseModel):
    reference: Optional[str] = None
    numero_wagon: Optional[str] = None
    client: Optional[str] = None
    destination: Optional[str] = None
    produit: Optional[str] = None
    date_affectation: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class RailWagonDispatchOut(BaseModel):
    id: int
    company_id: int
    reference: str
    numero_wagon: Optional[str] = None
    client: Optional[str] = None
    destination: Optional[str] = None
    produit: Optional[str] = None
    date_affectation: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class RailTerminalCraneCreate(BaseModel):
    code_equipment: str
    terminal: Optional[str] = None
    type: Optional[str] = None
    capacite_tonnes: Optional[int] = None
    portee_m: Optional[int] = None
    date_prochaine_visite: Optional[date] = None
    statut: Optional[str] = None


class RailTerminalCraneUpdate(BaseModel):
    code_equipment: Optional[str] = None
    terminal: Optional[str] = None
    type: Optional[str] = None
    capacite_tonnes: Optional[int] = None
    portee_m: Optional[int] = None
    date_prochaine_visite: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class RailTerminalCraneOut(BaseModel):
    id: int
    company_id: int
    code_equipment: str
    terminal: Optional[str] = None
    type: Optional[str] = None
    capacite_tonnes: Optional[int] = None
    portee_m: Optional[int] = None
    date_prochaine_visite: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}

