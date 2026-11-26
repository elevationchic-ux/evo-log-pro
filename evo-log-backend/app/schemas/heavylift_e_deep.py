"""Schemas Pydantic pour convoi-exceptionnel (genere)."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date


class Heavy2LiftPlanCreate(BaseModel):
    reference: str
    charge: Optional[str] = None
    poids_tonnes: Optional[float] = None
    portee_m: Optional[float] = None
    date: Optional[date] = None
    statut: Optional[str] = None


class Heavy2LiftPlanUpdate(BaseModel):
    reference: Optional[str] = None
    charge: Optional[str] = None
    poids_tonnes: Optional[float] = None
    portee_m: Optional[float] = None
    date: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class Heavy2LiftPlanOut(BaseModel):
    id: int
    company_id: int
    reference: str
    charge: Optional[str] = None
    poids_tonnes: Optional[float] = None
    portee_m: Optional[float] = None
    date: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class Heavy2RouteSurveyCreate(BaseModel):
    reference: str
    itineraire: Optional[str] = None
    largeur_m: Optional[float] = None
    hauteur_m: Optional[float] = None
    statut: Optional[str] = None


class Heavy2RouteSurveyUpdate(BaseModel):
    reference: Optional[str] = None
    itineraire: Optional[str] = None
    largeur_m: Optional[float] = None
    hauteur_m: Optional[float] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class Heavy2RouteSurveyOut(BaseModel):
    id: int
    company_id: int
    reference: str
    itineraire: Optional[str] = None
    largeur_m: Optional[float] = None
    hauteur_m: Optional[float] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class Heavy2EscortScheduleCreate(BaseModel):
    reference: str
    convoi: Optional[str] = None
    nb_vehicules: Optional[int] = None
    debut: Optional[datetime] = None
    statut: Optional[str] = None


class Heavy2EscortScheduleUpdate(BaseModel):
    reference: Optional[str] = None
    convoi: Optional[str] = None
    nb_vehicules: Optional[int] = None
    debut: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class Heavy2EscortScheduleOut(BaseModel):
    id: int
    company_id: int
    reference: str
    convoi: Optional[str] = None
    nb_vehicules: Optional[int] = None
    debut: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class Heavy2LoadMomentCalcCreate(BaseModel):
    reference: str
    configuration: Optional[str] = None
    moment_applique: Optional[float] = None
    capacite: Optional[float] = None
    statut: Optional[str] = None


class Heavy2LoadMomentCalcUpdate(BaseModel):
    reference: Optional[str] = None
    configuration: Optional[str] = None
    moment_applique: Optional[float] = None
    capacite: Optional[float] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class Heavy2LoadMomentCalcOut(BaseModel):
    id: int
    company_id: int
    reference: str
    configuration: Optional[str] = None
    moment_applique: Optional[float] = None
    capacite: Optional[float] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class Heavy2CraneSetupRecordCreate(BaseModel):
    reference: str
    grue: Optional[str] = None
    portance_sol: Optional[str] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None


class Heavy2CraneSetupRecordUpdate(BaseModel):
    reference: Optional[str] = None
    grue: Optional[str] = None
    portance_sol: Optional[str] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class Heavy2CraneSetupRecordOut(BaseModel):
    id: int
    company_id: int
    reference: str
    grue: Optional[str] = None
    portance_sol: Optional[str] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class Heavy2PermitObtentionCreate(BaseModel):
    reference: str
    convoi: Optional[str] = None
    autorite: Optional[str] = None
    validite: Optional[date] = None
    statut: Optional[str] = None


class Heavy2PermitObtentionUpdate(BaseModel):
    reference: Optional[str] = None
    convoi: Optional[str] = None
    autorite: Optional[str] = None
    validite: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class Heavy2PermitObtentionOut(BaseModel):
    id: int
    company_id: int
    reference: str
    convoi: Optional[str] = None
    autorite: Optional[str] = None
    validite: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class Heavy2LashingRigCreate(BaseModel):
    reference: str
    charge: Optional[str] = None
    nb_sangles: Optional[int] = None
    angle_deg: Optional[int] = None
    statut: Optional[str] = None


class Heavy2LashingRigUpdate(BaseModel):
    reference: Optional[str] = None
    charge: Optional[str] = None
    nb_sangles: Optional[int] = None
    angle_deg: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class Heavy2LashingRigOut(BaseModel):
    id: int
    company_id: int
    reference: str
    charge: Optional[str] = None
    nb_sangles: Optional[int] = None
    angle_deg: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class Heavy2AxleLoadReadingCreate(BaseModel):
    reference: str
    vehicule: Optional[str] = None
    essieu: Optional[int] = None
    charge_t: Optional[float] = None
    statut: Optional[str] = None


class Heavy2AxleLoadReadingUpdate(BaseModel):
    reference: Optional[str] = None
    vehicule: Optional[str] = None
    essieu: Optional[int] = None
    charge_t: Optional[float] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class Heavy2AxleLoadReadingOut(BaseModel):
    id: int
    company_id: int
    reference: str
    vehicule: Optional[str] = None
    essieu: Optional[int] = None
    charge_t: Optional[float] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class Heavy2ConvoyStagingReportCreate(BaseModel):
    reference: str
    convoi: Optional[str] = None
    lieu_rassemblement: Optional[str] = None
    depart: Optional[datetime] = None
    statut: Optional[str] = None


class Heavy2ConvoyStagingReportUpdate(BaseModel):
    reference: Optional[str] = None
    convoi: Optional[str] = None
    lieu_rassemblement: Optional[str] = None
    depart: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class Heavy2ConvoyStagingReportOut(BaseModel):
    id: int
    company_id: int
    reference: str
    convoi: Optional[str] = None
    lieu_rassemblement: Optional[str] = None
    depart: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}

