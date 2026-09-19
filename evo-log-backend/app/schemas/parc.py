"""
Parc schemas for fleet and equipment management
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class VehiculeStatus(str, Enum):
    """Enumeration for vehicle status"""
    DISPONIBLE = "disponible"
    EN_USAGE = "en_usage"
    EN_MAINTENANCE = "en_maintenance"
    HORS_SERVICE = "hors_service"
    RESERVE = "reserve"


class VehiculeBase(BaseModel):
    """Base vehicle schema"""
    immatriculation: str = Field(..., min_length=5, max_length=20)
    marque: Optional[str] = None
    modele: Optional[str] = None
    annee: Optional[int] = None
    type_vehicule: Optional[str] = None
    carburant: Optional[str] = None
    capacite_reservoir: Optional[float] = None
    consommation_moyenne: Optional[float] = None
    status: VehiculeStatus = VehiculeStatus.DISPONIBLE
    kilometrage: int = 0
    localisation: Optional[str] = None
    assigne_a: Optional[int] = None
    is_active: bool = True


class VehiculeCreate(VehiculeBase):
    """Schema for vehicle creation"""
    date_acquisition: Optional[datetime] = None
    date_mise_service: Optional[datetime] = None
    valeur_acquisition: Optional[float] = None


class VehiculeUpdate(BaseModel):
    """Schema for vehicle update"""
    marque: Optional[str] = None
    modele: Optional[str] = None
    annee: Optional[int] = None
    type_vehicule: Optional[str] = None
    carburant: Optional[str] = None
    capacite_reservoir: Optional[float] = None
    consommation_moyenne: Optional[float] = None
    status: Optional[VehiculeStatus] = None
    kilometrage: Optional[int] = None
    localisation: Optional[str] = None
    assigne_a: Optional[int] = None
    is_active: Optional[bool] = None
    valeur_actuelle: Optional[float] = None


class VehiculeResponse(VehiculeBase):
    """Schema for vehicle response"""
    id: int
    date_acquisition: Optional[datetime] = None
    date_mise_service: Optional[datetime] = None
    valeur_acquisition: Optional[float] = None
    valeur_actuelle: Optional[float] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class EquipementBase(BaseModel):
    """Base equipment schema"""
    code: str = Field(..., min_length=2, max_length=50)
    nom: str = Field(..., min_length=2, max_length=100)
    type_equipement: Optional[str] = None
    marque: Optional[str] = None
    modele: Optional[str] = None
    numero_serie: Optional[str] = None
    capacite: Optional[float] = None
    status: str = "disponible"
    localisation: Optional[str] = None
    valeur: Optional[float] = None
    is_active: bool = True


class EquipementCreate(EquipementBase):
    """Schema for equipment creation"""
    date_acquisition: Optional[datetime] = None


class EquipementResponse(EquipementBase):
    """Schema for equipment response"""
    id: int
    date_acquisition: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class MaintenanceBase(BaseModel):
    """Base maintenance schema"""
    vehicule_id: Optional[int] = None
    type_maintenance: Optional[str] = None
    date_debut: Optional[datetime] = None
    date_fin: Optional[datetime] = None
    kilometrage: Optional[int] = None
    description: Optional[str] = None
    cout: Optional[float] = None
    realisateur: Optional[str] = None
    statut: str = "planifie"
    notes: Optional[str] = None


class MaintenanceCreate(MaintenanceBase):
    """Schema for maintenance creation"""
    created_by: Optional[int] = None


class MaintenanceResponse(MaintenanceBase):
    """Schema for maintenance response"""
    id: int
    created_at: datetime
    created_by: Optional[int] = None
    
    class Config:
        from_attributes = True