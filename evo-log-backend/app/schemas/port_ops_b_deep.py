"""Schemas Pydantic pour port-operations (genere)."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date


class PortbBerthScheduleCreate(BaseModel):
    reference: str
    navire: Optional[str] = None
    numero_imo: Optional[str] = None
    poste_amarrage: Optional[str] = None
    date_arrivee_prevue: Optional[datetime] = None
    date_depart_prevu: Optional[datetime] = None
    type_cargo: Optional[str] = None
    pilote: Optional[str] = None
    statut: Optional[str] = None


class PortbBerthScheduleUpdate(BaseModel):
    reference: Optional[str] = None
    navire: Optional[str] = None
    numero_imo: Optional[str] = None
    poste_amarrage: Optional[str] = None
    date_arrivee_prevue: Optional[datetime] = None
    date_depart_prevu: Optional[datetime] = None
    type_cargo: Optional[str] = None
    pilote: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class PortbBerthScheduleOut(BaseModel):
    id: int
    company_id: int
    reference: str
    navire: Optional[str] = None
    numero_imo: Optional[str] = None
    poste_amarrage: Optional[str] = None
    date_arrivee_prevue: Optional[datetime] = None
    date_depart_prevu: Optional[datetime] = None
    type_cargo: Optional[str] = None
    pilote: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class PortbVesselTrafficLogCreate(BaseModel):
    reference: str
    nom_navire: Optional[str] = None
    numero_imo: Optional[str] = None
    mouvement: Optional[str] = None
    balise_vts: Optional[str] = None
    horodatage: Optional[datetime] = None
    operateur: Optional[str] = None
    statut: Optional[str] = None


class PortbVesselTrafficLogUpdate(BaseModel):
    reference: Optional[str] = None
    nom_navire: Optional[str] = None
    numero_imo: Optional[str] = None
    mouvement: Optional[str] = None
    balise_vts: Optional[str] = None
    horodatage: Optional[datetime] = None
    operateur: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class PortbVesselTrafficLogOut(BaseModel):
    id: int
    company_id: int
    reference: str
    nom_navire: Optional[str] = None
    numero_imo: Optional[str] = None
    mouvement: Optional[str] = None
    balise_vts: Optional[str] = None
    horodatage: Optional[datetime] = None
    operateur: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}

