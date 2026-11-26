"""Schemas Pydantic pour transport-flotte (genere)."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date


class TransportbDispatchCreate(BaseModel):
    reference: str
    chauffeur: Optional[str] = None
    vehicule: Optional[str] = None
    point_depart: Optional[str] = None
    point_arrivee: Optional[str] = None
    date_depart: Optional[datetime] = None
    date_arrivee: Optional[datetime] = None
    km_parcourus: Optional[int] = None
    statut: Optional[str] = None


class TransportbDispatchUpdate(BaseModel):
    reference: Optional[str] = None
    chauffeur: Optional[str] = None
    vehicule: Optional[str] = None
    point_depart: Optional[str] = None
    point_arrivee: Optional[str] = None
    date_depart: Optional[datetime] = None
    date_arrivee: Optional[datetime] = None
    km_parcourus: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class TransportbDispatchOut(BaseModel):
    id: int
    company_id: int
    reference: str
    chauffeur: Optional[str] = None
    vehicule: Optional[str] = None
    point_depart: Optional[str] = None
    point_arrivee: Optional[str] = None
    date_depart: Optional[datetime] = None
    date_arrivee: Optional[datetime] = None
    km_parcourus: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class TransportbPodCreate(BaseModel):
    reference: str
    mission: Optional[str] = None
    destinataire: Optional[str] = None
    date_livraison: Optional[datetime] = None
    nb_colis_livres: Optional[int] = None
    incidents: Optional[str] = None
    signature_recu: Optional[bool] = None
    statut: Optional[str] = None


class TransportbPodUpdate(BaseModel):
    reference: Optional[str] = None
    mission: Optional[str] = None
    destinataire: Optional[str] = None
    date_livraison: Optional[datetime] = None
    nb_colis_livres: Optional[int] = None
    incidents: Optional[str] = None
    signature_recu: Optional[bool] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class TransportbPodOut(BaseModel):
    id: int
    company_id: int
    reference: str
    mission: Optional[str] = None
    destinataire: Optional[str] = None
    date_livraison: Optional[datetime] = None
    nb_colis_livres: Optional[int] = None
    incidents: Optional[str] = None
    signature_recu: Optional[bool] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}

