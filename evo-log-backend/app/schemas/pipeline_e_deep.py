"""Schemas Pydantic pour pipeline-oleoduc (genere)."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date


class Pipe2CustodyTransferCreate(BaseModel):
    reference: str
    interface: Optional[str] = None
    produit: Optional[str] = None
    volume_livre: Optional[float] = None
    volume_recu: Optional[float] = None
    statut: Optional[str] = None


class Pipe2CustodyTransferUpdate(BaseModel):
    reference: Optional[str] = None
    interface: Optional[str] = None
    produit: Optional[str] = None
    volume_livre: Optional[float] = None
    volume_recu: Optional[float] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class Pipe2CustodyTransferOut(BaseModel):
    id: int
    company_id: int
    reference: str
    interface: Optional[str] = None
    produit: Optional[str] = None
    volume_livre: Optional[float] = None
    volume_recu: Optional[float] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class Pipe2PressureLogCreate(BaseModel):
    reference: str
    station: Optional[str] = None
    pression_bar: Optional[float] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None


class Pipe2PressureLogUpdate(BaseModel):
    reference: Optional[str] = None
    station: Optional[str] = None
    pression_bar: Optional[float] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class Pipe2PressureLogOut(BaseModel):
    id: int
    company_id: int
    reference: str
    station: Optional[str] = None
    pression_bar: Optional[float] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class Pipe2PumpStationReadCreate(BaseModel):
    reference: str
    station: Optional[str] = None
    debit: Optional[float] = None
    vibration: Optional[float] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None


class Pipe2PumpStationReadUpdate(BaseModel):
    reference: Optional[str] = None
    station: Optional[str] = None
    debit: Optional[float] = None
    vibration: Optional[float] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class Pipe2PumpStationReadOut(BaseModel):
    id: int
    company_id: int
    reference: str
    station: Optional[str] = None
    debit: Optional[float] = None
    vibration: Optional[float] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class Pipe2CorrosionReadingCreate(BaseModel):
    reference: str
    troncon: Optional[str] = None
    epaisseur_mm: Optional[float] = None
    date: Optional[date] = None
    statut: Optional[str] = None


class Pipe2CorrosionReadingUpdate(BaseModel):
    reference: Optional[str] = None
    troncon: Optional[str] = None
    epaisseur_mm: Optional[float] = None
    date: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class Pipe2CorrosionReadingOut(BaseModel):
    id: int
    company_id: int
    reference: str
    troncon: Optional[str] = None
    epaisseur_mm: Optional[float] = None
    date: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class Pipe2FlowCalibrationCreate(BaseModel):
    reference: str
    debitmetre: Optional[str] = None
    coefficient: Optional[float] = None
    date: Optional[date] = None
    statut: Optional[str] = None


class Pipe2FlowCalibrationUpdate(BaseModel):
    reference: Optional[str] = None
    debitmetre: Optional[str] = None
    coefficient: Optional[float] = None
    date: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class Pipe2FlowCalibrationOut(BaseModel):
    id: int
    company_id: int
    reference: str
    debitmetre: Optional[str] = None
    coefficient: Optional[float] = None
    date: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class Pipe2BatchQualityTestCreate(BaseModel):
    reference: str
    lot: Optional[str] = None
    produit: Optional[str] = None
    parametre: Optional[str] = None
    date: Optional[date] = None
    statut: Optional[str] = None


class Pipe2BatchQualityTestUpdate(BaseModel):
    reference: Optional[str] = None
    lot: Optional[str] = None
    produit: Optional[str] = None
    parametre: Optional[str] = None
    date: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class Pipe2BatchQualityTestOut(BaseModel):
    id: int
    company_id: int
    reference: str
    lot: Optional[str] = None
    produit: Optional[str] = None
    parametre: Optional[str] = None
    date: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class Pipe2InterfaceDetectionCreate(BaseModel):
    reference: str
    troncon: Optional[str] = None
    volume_interface: Optional[float] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None


class Pipe2InterfaceDetectionUpdate(BaseModel):
    reference: Optional[str] = None
    troncon: Optional[str] = None
    volume_interface: Optional[float] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class Pipe2InterfaceDetectionOut(BaseModel):
    id: int
    company_id: int
    reference: str
    troncon: Optional[str] = None
    volume_interface: Optional[float] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class Pipe2IntegrityAssessmentCreate(BaseModel):
    reference: str
    troncon: Optional[str] = None
    niveau_risque: Optional[str] = None
    pression_max: Optional[float] = None
    date: Optional[date] = None
    statut: Optional[str] = None


class Pipe2IntegrityAssessmentUpdate(BaseModel):
    reference: Optional[str] = None
    troncon: Optional[str] = None
    niveau_risque: Optional[str] = None
    pression_max: Optional[float] = None
    date: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class Pipe2IntegrityAssessmentOut(BaseModel):
    id: int
    company_id: int
    reference: str
    troncon: Optional[str] = None
    niveau_risque: Optional[str] = None
    pression_max: Optional[float] = None
    date: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class Pipe2SpillResponseActionCreate(BaseModel):
    reference: str
    lieu: Optional[str] = None
    volume_rejete: Optional[float] = None
    volume_recupere: Optional[float] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None


class Pipe2SpillResponseActionUpdate(BaseModel):
    reference: Optional[str] = None
    lieu: Optional[str] = None
    volume_rejete: Optional[float] = None
    volume_recupere: Optional[float] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class Pipe2SpillResponseActionOut(BaseModel):
    id: int
    company_id: int
    reference: str
    lieu: Optional[str] = None
    volume_rejete: Optional[float] = None
    volume_recupere: Optional[float] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}

