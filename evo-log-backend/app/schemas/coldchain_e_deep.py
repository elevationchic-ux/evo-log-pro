"""Schemas Pydantic pour chaine-froid (genere)."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date


class Cold2TemperatureLogCreate(BaseModel):
    reference: str
    unite: Optional[str] = None
    temperature: Optional[float] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None


class Cold2TemperatureLogUpdate(BaseModel):
    reference: Optional[str] = None
    unite: Optional[str] = None
    temperature: Optional[float] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class Cold2TemperatureLogOut(BaseModel):
    id: int
    company_id: int
    reference: str
    unite: Optional[str] = None
    temperature: Optional[float] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class Cold2ColdExcursionCreate(BaseModel):
    reference: str
    cargaison: Optional[str] = None
    temperature_max: Optional[float] = None
    duree_min: Optional[int] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None


class Cold2ColdExcursionUpdate(BaseModel):
    reference: Optional[str] = None
    cargaison: Optional[str] = None
    temperature_max: Optional[float] = None
    duree_min: Optional[int] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class Cold2ColdExcursionOut(BaseModel):
    id: int
    company_id: int
    reference: str
    cargaison: Optional[str] = None
    temperature_max: Optional[float] = None
    duree_min: Optional[int] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class Cold2ProbeCalibrationCreate(BaseModel):
    reference: str
    sonde: Optional[str] = None
    ecart: Optional[float] = None
    date: Optional[date] = None
    statut: Optional[str] = None


class Cold2ProbeCalibrationUpdate(BaseModel):
    reference: Optional[str] = None
    sonde: Optional[str] = None
    ecart: Optional[float] = None
    date: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class Cold2ProbeCalibrationOut(BaseModel):
    id: int
    company_id: int
    reference: str
    sonde: Optional[str] = None
    ecart: Optional[float] = None
    date: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class Cold2BlastFreezeCycleCreate(BaseModel):
    reference: str
    produit: Optional[str] = None
    temp_finale: Optional[float] = None
    duree_min: Optional[int] = None
    statut: Optional[str] = None


class Cold2BlastFreezeCycleUpdate(BaseModel):
    reference: Optional[str] = None
    produit: Optional[str] = None
    temp_finale: Optional[float] = None
    duree_min: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class Cold2BlastFreezeCycleOut(BaseModel):
    id: int
    company_id: int
    reference: str
    produit: Optional[str] = None
    temp_finale: Optional[float] = None
    duree_min: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class Cold2DoorOpenEventCreate(BaseModel):
    reference: str
    chambre: Optional[str] = None
    duree_sec: Optional[int] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None


class Cold2DoorOpenEventUpdate(BaseModel):
    reference: Optional[str] = None
    chambre: Optional[str] = None
    duree_sec: Optional[int] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class Cold2DoorOpenEventOut(BaseModel):
    id: int
    company_id: int
    reference: str
    chambre: Optional[str] = None
    duree_sec: Optional[int] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class Cold2HumidityLogCreate(BaseModel):
    reference: str
    chambre: Optional[str] = None
    humidite_pct: Optional[float] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None


class Cold2HumidityLogUpdate(BaseModel):
    reference: Optional[str] = None
    chambre: Optional[str] = None
    humidite_pct: Optional[float] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class Cold2HumidityLogOut(BaseModel):
    id: int
    company_id: int
    reference: str
    chambre: Optional[str] = None
    humidite_pct: Optional[float] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class Cold2RefrigerantChargeCreate(BaseModel):
    reference: str
    circuit: Optional[str] = None
    fluide: Optional[str] = None
    quantite_kg: Optional[float] = None
    date: Optional[date] = None
    statut: Optional[str] = None


class Cold2RefrigerantChargeUpdate(BaseModel):
    reference: Optional[str] = None
    circuit: Optional[str] = None
    fluide: Optional[str] = None
    quantite_kg: Optional[float] = None
    date: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class Cold2RefrigerantChargeOut(BaseModel):
    id: int
    company_id: int
    reference: str
    circuit: Optional[str] = None
    fluide: Optional[str] = None
    quantite_kg: Optional[float] = None
    date: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class Cold2ShipmentApprovalCreate(BaseModel):
    reference: str
    cargaison: Optional[str] = None
    temp_chargement: Optional[float] = None
    valideur: Optional[str] = None
    statut: Optional[str] = None


class Cold2ShipmentApprovalUpdate(BaseModel):
    reference: Optional[str] = None
    cargaison: Optional[str] = None
    temp_chargement: Optional[float] = None
    valideur: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class Cold2ShipmentApprovalOut(BaseModel):
    id: int
    company_id: int
    reference: str
    cargaison: Optional[str] = None
    temp_chargement: Optional[float] = None
    valideur: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class Cold2IceBatteryChargeCreate(BaseModel):
    reference: str
    caisson: Optional[str] = None
    niveau_gel: Optional[str] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None


class Cold2IceBatteryChargeUpdate(BaseModel):
    reference: Optional[str] = None
    caisson: Optional[str] = None
    niveau_gel: Optional[str] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class Cold2IceBatteryChargeOut(BaseModel):
    id: int
    company_id: int
    reference: str
    caisson: Optional[str] = None
    niveau_gel: Optional[str] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}

