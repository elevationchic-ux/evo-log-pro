"""Schemas Pydantic pour courier-express (genere)."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date


class Cour2RouteScanCreate(BaseModel):
    reference: str
    colis: Optional[str] = None
    etape: Optional[str] = None
    lieu: Optional[str] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None


class Cour2RouteScanUpdate(BaseModel):
    reference: Optional[str] = None
    colis: Optional[str] = None
    etape: Optional[str] = None
    lieu: Optional[str] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class Cour2RouteScanOut(BaseModel):
    id: int
    company_id: int
    reference: str
    colis: Optional[str] = None
    etape: Optional[str] = None
    lieu: Optional[str] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class Cour2LastMileHandoffCreate(BaseModel):
    reference: str
    colis: Optional[str] = None
    livreur: Optional[str] = None
    agencer: Optional[str] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None


class Cour2LastMileHandoffUpdate(BaseModel):
    reference: Optional[str] = None
    colis: Optional[str] = None
    livreur: Optional[str] = None
    agencer: Optional[str] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class Cour2LastMileHandoffOut(BaseModel):
    id: int
    company_id: int
    reference: str
    colis: Optional[str] = None
    livreur: Optional[str] = None
    agencer: Optional[str] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class Cour2DeliveryAttemptCreate(BaseModel):
    reference: str
    colis: Optional[str] = None
    livreur: Optional[str] = None
    date: Optional[datetime] = None
    motif: Optional[str] = None
    statut: Optional[str] = None


class Cour2DeliveryAttemptUpdate(BaseModel):
    reference: Optional[str] = None
    colis: Optional[str] = None
    livreur: Optional[str] = None
    date: Optional[datetime] = None
    motif: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class Cour2DeliveryAttemptOut(BaseModel):
    id: int
    company_id: int
    reference: str
    colis: Optional[str] = None
    livreur: Optional[str] = None
    date: Optional[datetime] = None
    motif: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class Cour2ExceptionParcelCreate(BaseModel):
    reference: str
    colis: Optional[str] = None
    type_exception: Optional[str] = None
    detecte_le: Optional[datetime] = None
    statut: Optional[str] = None


class Cour2ExceptionParcelUpdate(BaseModel):
    reference: Optional[str] = None
    colis: Optional[str] = None
    type_exception: Optional[str] = None
    detecte_le: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class Cour2ExceptionParcelOut(BaseModel):
    id: int
    company_id: int
    reference: str
    colis: Optional[str] = None
    type_exception: Optional[str] = None
    detecte_le: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class Cour2ReturnToSenderCreate(BaseModel):
    reference: str
    colis: Optional[str] = None
    motif: Optional[str] = None
    date_depart: Optional[datetime] = None
    statut: Optional[str] = None


class Cour2ReturnToSenderUpdate(BaseModel):
    reference: Optional[str] = None
    colis: Optional[str] = None
    motif: Optional[str] = None
    date_depart: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class Cour2ReturnToSenderOut(BaseModel):
    id: int
    company_id: int
    reference: str
    colis: Optional[str] = None
    motif: Optional[str] = None
    date_depart: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class Cour2CourierShiftLogCreate(BaseModel):
    reference: str
    livreur: Optional[str] = None
    date: Optional[date] = None
    colis_livres: Optional[int] = None
    km: Optional[int] = None
    statut: Optional[str] = None


class Cour2CourierShiftLogUpdate(BaseModel):
    reference: Optional[str] = None
    livreur: Optional[str] = None
    date: Optional[date] = None
    colis_livres: Optional[int] = None
    km: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class Cour2CourierShiftLogOut(BaseModel):
    id: int
    company_id: int
    reference: str
    livreur: Optional[str] = None
    date: Optional[date] = None
    colis_livres: Optional[int] = None
    km: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class Cour2SlaBreachLogCreate(BaseModel):
    reference: str
    colis: Optional[str] = None
    retard_min: Optional[int] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None


class Cour2SlaBreachLogUpdate(BaseModel):
    reference: Optional[str] = None
    colis: Optional[str] = None
    retard_min: Optional[int] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class Cour2SlaBreachLogOut(BaseModel):
    id: int
    company_id: int
    reference: str
    colis: Optional[str] = None
    retard_min: Optional[int] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}

