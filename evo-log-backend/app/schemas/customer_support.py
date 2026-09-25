"""
Schemas Tranche C : fleet (vehicules proxy Vehicule + tickets carburant),
customers CRM (+ contrats) et support (tickets, incidents).

Schemas permissifs cf. parc_purchase (pages frontend issuees de mocks,
formes variables).
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# ─── Fleet : vehicules (proxy modele Vehicule existant) ──────────────────────
class FleetVehicleCreate(BaseModel):
    immatriculation: str = Field(..., min_length=1, max_length=20)
    marque: Optional[str] = None
    modele: Optional[str] = None
    annee: Optional[int] = None
    type_vehicule: Optional[str] = None
    carburant: Optional[str] = None
    capacite_reservoir: Optional[float] = None
    kilometrage: Optional[int] = 0
    localisation: Optional[str] = None
    status: Optional[str] = None  # par defaut disponible


class FleetVehicleUpdate(BaseModel):
    marque: Optional[str] = None
    modele: Optional[str] = None
    annee: Optional[int] = None
    type_vehicule: Optional[str] = None
    carburant: Optional[str] = None
    status: Optional[str] = None
    kilometrage: Optional[int] = None
    localisation: Optional[str] = None
    is_active: Optional[bool] = None


class FleetVehicleResponse(BaseModel):
    id: int
    company_id: Optional[int] = None
    immatriculation: str
    marque: Optional[str] = None
    modele: Optional[str] = None
    annee: Optional[int] = None
    type_vehicule: Optional[str] = None
    carburant: Optional[str] = None
    status: Optional[str] = None
    kilometrage: Optional[int] = 0
    localisation: Optional[str] = None
    is_active: Optional[bool] = True
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ─── Fleet : carburant ────────────────────────────────────────────────────────
class FuelRecordCreate(BaseModel):
    vehicule_id: Optional[int] = None
    immatriculation: Optional[str] = None
    litres: Optional[float] = None
    cout: Optional[float] = None
    station: Optional[str] = None
    mode_paiement: Optional[str] = None
    kilometrage: Optional[int] = None
    date_plein: Optional[datetime] = None
    notes: Optional[str] = None


class FuelRecordResponse(FuelRecordCreate):
    id: int
    company_id: Optional[int] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ─── Customers (CRM) ──────────────────────────────────────────────────────────
class CustomerCreate(BaseModel):
    code: Optional[str] = None
    name: str = Field(..., min_length=1, max_length=150)
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = "Cameroun"
    segment: Optional[str] = None
    source: Optional[str] = None
    encadrant: Optional[str] = None


class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    segment: Optional[str] = None
    source: Optional[str] = None
    encadrant: Optional[str] = None
    is_active: Optional[bool] = None


class CustomerResponse(CustomerCreate):
    id: int
    company_id: Optional[int] = None
    is_active: Optional[bool] = True
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ContractCreate(BaseModel):
    reference: Optional[str] = None
    customer_id: Optional[int] = None
    objet: Optional[str] = None
    type_contrat: Optional[str] = None
    date_debut: Optional[datetime] = None
    date_fin: Optional[datetime] = None
    montant: Optional[float] = None
    devise: Optional[str] = "XAF"
    statut: Optional[str] = "actif"
    notes: Optional[str] = None


class ContractResponse(ContractCreate):
    id: int
    company_id: Optional[int] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ─── Support : tickets & incidents ────────────────────────────────────────────
class TicketCreate(BaseModel):
    sujet: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    categorie: Optional[str] = None
    priorite: Optional[str] = "normale"
    demandeur: Optional[str] = None
    module_concerne: Optional[str] = None


class TicketResponse(TicketCreate):
    id: int
    company_id: Optional[int] = None
    reference: str
    statut: Optional[str] = "ouvert"
    assigne_a: Optional[str] = None
    resolved_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class IncidentCreate(BaseModel):
    titre: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    type: Optional[str] = None
    priorite: Optional[str] = "normale"
    signale_par: Optional[str] = None
    localisation: Optional[str] = None


class IncidentUpdate(BaseModel):
    titre: Optional[str] = None
    description: Optional[str] = None
    priorite: Optional[str] = None
    statut: Optional[str] = None
    localisation: Optional[str] = None


class IncidentResponse(IncidentCreate):
    id: int
    company_id: Optional[int] = None
    reference: str
    statut: Optional[str] = "ouvert"
    resolved_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ─── Fleet : documents administratifs ────────────────────────────────────────
class FleetDocumentResponse(BaseModel):
    id: int
    company_id: Optional[int] = None
    vehicule_id: Optional[int] = None
    type_document: Optional[str] = None
    nom_fichier: Optional[str] = None
    url: Optional[str] = None
    date_expiration: Optional[datetime] = None
    statut: Optional[str] = "valide"
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
