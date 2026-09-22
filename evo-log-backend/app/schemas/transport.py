"""
Transport schemas for vehicles, drivers, and missions
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class CamionStatus(str, Enum):
    """Enumeration for truck status"""
    ACTIVE = "active"
    IN_MAINTENANCE = "in_maintenance"
    OUT_OF_SERVICE = "out_of_service"
    RESERVED = "reserved"


class CamionBase(BaseModel):
    """Base truck schema"""
    immatriculation: str = Field(..., min_length=5, max_length=20)
    marque: Optional[str] = None
    modele: Optional[str] = None
    annee: Optional[int] = None
    capacite_tonnage: Optional[float] = None
    status: CamionStatus = CamionStatus.ACTIVE
    kilometrage: int = 0


class CamionCreate(CamionBase):
    """Schema for truck creation"""
    date_mise_service: Optional[datetime] = None


class CamionUpdate(BaseModel):
    """Schema for truck update"""
    marque: Optional[str] = None
    modele: Optional[str] = None
    annee: Optional[int] = None
    capacite_tonnage: Optional[float] = None
    status: Optional[CamionStatus] = None
    kilometrage: Optional[int] = None
    derniere_maintenance: Optional[datetime] = None
    prochaine_maintenance: Optional[datetime] = None
    is_active: Optional[bool] = None


class CamionResponse(CamionBase):
    """Schema for truck response"""
    id: int
    date_mise_service: Optional[datetime] = None
    derniere_maintenance: Optional[datetime] = None
    prochaine_maintenance: Optional[datetime] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ConducteurBase(BaseModel):
    """Base driver schema"""
    nom: str = Field(..., min_length=2, max_length=100)
    prenom: str = Field(..., min_length=2, max_length=100)
    numero_permis: str = Field(..., min_length=5, max_length=50)
    date_expiration_permis: Optional[datetime] = None
    telephone: str = Field(..., min_length=10, max_length=20)
    email: Optional[str] = None
    adresse: Optional[str] = None
    is_active: bool = True


class ConducteurCreate(ConducteurBase):
    """Schema for driver creation"""
    date_embauche: Optional[datetime] = None


class ConducteurUpdate(BaseModel):
    """Schema for driver update"""
    nom: Optional[str] = None
    prenom: Optional[str] = None
    telephone: Optional[str] = None
    email: Optional[str] = None
    adresse: Optional[str] = None
    date_expiration_permis: Optional[datetime] = None
    is_active: Optional[bool] = None


class ConducteurResponse(ConducteurBase):
    """Schema for driver response"""
    id: int
    date_embauche: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class MissionStatus(str, Enum):
    """Enumeration for mission status"""
    PLANIFIEE = "planifiee"
    EN_COURS = "en_cours"
    TERMINEE = "terminee"
    ANNULEE = "annulee"
    EN_RETARD = "en_retard"


class MissionBase(BaseModel):
    """Base mission schema"""
    reference: str = Field(..., min_length=3, max_length=50)
    camion_id: Optional[int] = None
    conducteur_id: Optional[int] = None
    client_id: Optional[int] = None
    type_mission: Optional[str] = None
    statut: MissionStatus = MissionStatus.PLANIFIEE
    point_depart: Optional[str] = None
    point_arrivee: Optional[str] = None
    distance_km: Optional[float] = None
    cout_estime: Optional[float] = None
    cout_reel: Optional[float] = None
    notes: Optional[str] = None


class MissionCreate(MissionBase):
    """Schema for mission creation"""
    date_debut_prevue: Optional[datetime] = None
    date_fin_prevue: Optional[datetime] = None


class MissionUpdate(BaseModel):
    """Schema for mission update"""
    camion_id: Optional[int] = None
    conducteur_id: Optional[int] = None
    statut: Optional[MissionStatus] = None
    date_debut_prevue: Optional[datetime] = None
    date_fin_prevue: Optional[datetime] = None
    date_debut_reelle: Optional[datetime] = None
    date_fin_reelle: Optional[datetime] = None
    point_depart: Optional[str] = None
    point_arrivee: Optional[str] = None
    distance_km: Optional[float] = None
    cout_estime: Optional[float] = None
    cout_reel: Optional[float] = None
    notes: Optional[str] = None


class MissionResponse(MissionBase):
    """Schema for mission response"""
    id: int
    date_debut_prevue: Optional[datetime] = None
    date_fin_prevue: Optional[datetime] = None
    date_debut_reelle: Optional[datetime] = None
    date_fin_reelle: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True