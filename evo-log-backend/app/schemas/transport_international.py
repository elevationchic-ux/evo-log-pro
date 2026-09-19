"""Pydantic schemas for Transport International module - Road transport Cameroon/CEMAC"""
from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel


# Ordre Transport schemas
class OrdreTransportBase(BaseModel):
    numero_ot: str
    client_id: int
    transporteur_id: int
    camion_id: int
    conducteur_id: int
    type_transit: str
    lieu_chargement: str
    lieu_livraison: str
    pays_destination: str
    code_pays_destination: str
    marchandise: str
    poids_net: float
    poids_brut: float
    nombre_colis: int
    valeur_marchandise: float
    montant_freight: float


class OrdreTransportCreate(OrdreTransportBase):
    date_chargement_prevue: Optional[date] = None
    date_livraison_prevue: Optional[date] = None
    volume_m3: Optional[float] = None
    devis: Optional[str] = None
    observations: Optional[str] = None


class OrdreTransportUpdate(BaseModel):
    statut: Optional[str] = None
    date_chargement_reelle: Optional[date] = None
    date_livraison_reelle: Optional[date] = None
    observations: Optional[str] = None


class OrdreTransportResponse(OrdreTransportBase):
    id: int
    statut: str
    date_creation: date
    date_chargement_prevue: Optional[date] = None
    date_chargement_reelle: Optional[date] = None
    date_livraison_prevue: Optional[date] = None
    date_livraison_reelle: Optional[date] = None
    volume_m3: Optional[float] = None
    devise: str
    devis: Optional[str] = None
    observations: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Carnet TIR schemas
class CarnetTIRBase(BaseModel):
    numero_carnet: str
    ordre_transport_id: int
    pays_emission: str
    code_pays_emission: str
    bureau_depart: str
    bureau_arrivee: str
    montant_garantie: float


class CarnetTIRCreate(CarnetTIRBase):
    bureau_transit: Optional[str] = None
    observations: Optional[str] = None


class CarnetTIRUpdate(BaseModel):
    nombre_virements: Optional[int] = None
    statut: Optional[str] = None
    observations: Optional[str] = None


class CarnetTIRResponse(CarnetTIRBase):
    id: int
    date_emission: date
    date_validite: date
    nombre_virements: int
    bureau_transit: Optional[str] = None
    devise: str
    statut: str
    observations: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# CMR schemas
class CMRBase(BaseModel):
    numero_cmr: str
    ordre_transport_id: int
    expediteur: str
    destinataire: str
    transporteur: str
    lieu_chargement: str
    lieu_livraison: str
    marchandise: str
    poids_net: float
    poids_brut: float
    nombre_colis: int
    type_emballage: str
    valeur_marchandise: float


class CMRCreate(CMRBase):
    date_chargement: Optional[date] = None
    date_livraison: Optional[date] = None
    instructions_speciales: Optional[str] = None
    reserve: Optional[str] = None


class CMRUpdate(BaseModel):
    date_chargement: Optional[date] = None
    date_livraison: Optional[date] = None
    instructions_speciales: Optional[str] = None
    reserve: Optional[str] = None
    signature_expediteur: Optional[bool] = None
    signature_transporteur: Optional[bool] = None
    signature_destinataire: Optional[bool] = None
    statut: Optional[str] = None


class CMRResponse(CMRBase):
    id: int
    date_emission: date
    date_chargement: Optional[date] = None
    date_livraison: Optional[date] = None
    devise: str
    instructions_speciales: Optional[str] = None
    reserve: Optional[str] = None
    signature_expediteur: bool
    signature_transporteur: bool
    signature_destinataire: bool
    statut: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Scelle Routier schemas
class ScelleRoutierBase(BaseModel):
    numero_scelle: str
    ordre_transport_id: int
    type_scelle: str
    emplacement: str


class ScelleRoutierCreate(ScelleRoutierBase):
    pass


class ScelleRoutierUpdate(BaseModel):
    date_verification: Optional[datetime] = None
    verifie_par: Optional[str] = None
    intact: Optional[bool] = None
    motif_bris: Optional[str] = None
    photo: Optional[str] = None
    statut: Optional[str] = None


class ScelleRoutierResponse(ScelleRoutierBase):
    id: int
    date_pose: datetime
    pose_par: str
    date_verification: Optional[datetime] = None
    verifie_par: Optional[str] = None
    intact: bool
    motif_bris: Optional[str] = None
    photo: Optional[str] = None
    statut: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Position Transport schemas
class PositionTransportBase(BaseModel):
    ordre_transport_id: int
    latitude: float
    longitude: float
    vitesse_kmh: float
    direction: float


class PositionTransportCreate(PositionTransportBase):
    adresse: Optional[str] = None
    ville: Optional[str] = None
    pays: Optional[str] = None
    altitude: Optional[float] = None
    precision: Optional[float] = None
    statut: str = "en_mouvement"


class PositionTransportResponse(PositionTransportBase):
    id: int
    adresse: Optional[str] = None
    ville: Optional[str] = None
    pays: Optional[str] = None
    date_position: datetime
    altitude: Optional[float] = None
    precision: Optional[float] = None
    statut: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# CET Suivi schemas
class CETSuiviBase(BaseModel):
    ordre_transport_id: int
    numero_cet: str
    bureau_douane: str
    type_controle: str
    resultat: str
    agent: str
    fonction: str


class CETSuiviCreate(CETSuiviBase):
    observations: Optional[str] = None


class CETSuiviResponse(CETSuiviBase):
    id: int
    date_controle: datetime
    observations: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# Assurance FAP schemas
class AssuranceFAPBase(BaseModel):
    numero_police: str
    ordre_transport_id: int
    assureur: str
    type_couverture: str
    valeur_assuree: float
    prime: float
    franchise: float


class AssuranceFAPCreate(AssuranceFAPBase):
    exclusions: str = ""


class AssuranceFAPUpdate(BaseModel):
    statut: Optional[str] = None
    exclusions: Optional[str] = None


class AssuranceFAPResponse(AssuranceFAPBase):
    id: int
    devise: str
    date_debut: date
    date_fin: date
    exclusions: Optional[str] = None
    statut: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Planning Livraison schemas
class PlanningLivraisonBase(BaseModel):
    ordre_transport_id: int
    date_livraison: date
    heure_debut: str
    heure_fin: str
    adresse_livraison: str
    contact_client: str
    telephone_client: str


class PlanningLivraisonCreate(PlanningLivraisonBase):
    instructions: Optional[str] = None
    poids_decharge: Optional[float] = None
    volume_decharge: Optional[float] = None
    duree_estimee_heures: Optional[float] = None
    observations: Optional[str] = None


class PlanningLivraisonUpdate(BaseModel):
    statut: Optional[str] = None
    instructions: Optional[str] = None
    poids_decharge: Optional[float] = None
    observations: Optional[str] = None


class PlanningLivraisonResponse(PlanningLivraisonBase):
    id: int
    instructions: Optional[str] = None
    poids_decharge: Optional[float] = None
    volume_decharge: Optional[float] = None
    duree_estimee_heures: Optional[float] = None
    statut: str
    observations: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Preuve Livraison schemas
class PreuveLivraisonBase(BaseModel):
    ordre_transport_id: int
    planning_id: int
    destinataire: str
    fonction: str
    colis_recus: int
    colis_refuses: int
    etat_marchandise: str
    latitude: float
    longitude: float


class PreuveLivraisonCreate(PreuveLivraisonBase):
    signature: Optional[str] = None
    photo: Optional[str] = None
    motifs_refus: Optional[str] = None
    observations: Optional[str] = None


class PreuveLivraisonUpdate(BaseModel):
    signature: Optional[str] = None
    photo: Optional[str] = None
    motifs_refus: Optional[str] = None
    observations: Optional[str] = None
    statut: Optional[str] = None


class PreuveLivraisonResponse(PreuveLivraisonBase):
    id: int
    date_livraison: datetime
    heure_livraison: Optional[str] = None
    signature: Optional[str] = None
    photo: Optional[str] = None
    motifs_refus: Optional[str] = None
    observations: Optional[str] = None
    statut: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# Incident Transport schemas
class IncidentTransportBase(BaseModel):
    ordre_transport_id: int
    type_incident: str
    date_incident: datetime
    lieu: str
    description: str
    gravite: str


class IncidentTransportCreate(IncidentTransportBase):
    avarie_marchandise: bool = False
    valeur_avarie: Optional[float] = None
    blesses: int = 0
    deces: int = 0
    mesure_prise: Optional[str] = None
    police_intervention: bool = False
    numero_police: Optional[str] = None
    photos: str = ""


class IncidentTransportUpdate(BaseModel):
    mesure_prise: Optional[str] = None
    police_intervention: Optional[bool] = None
    numero_police: Optional[str] = None
    photos: Optional[str] = None
    statut: Optional[str] = None


class IncidentTransportResponse(IncidentTransportBase):
    id: int
    avarie_marchandise: bool
    valeur_avarie: Optional[float] = None
    devise: str
    blesses: int
    deces: int
    mesure_prise: Optional[str] = None
    police_intervention: bool
    numero_police: Optional[str] = None
    photos: Optional[str] = None
    statut: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Controle Routier schemas
class ControleRoutierBase(BaseModel):
    ordre_transport_id: int
    type_controle: str
    date_controle: datetime
    lieu: str
    autorite: str
    resultat: str


class ControleRoutierCreate(ControleRoutierBase):
    motif_infraction: Optional[str] = None
    montant_amende: Optional[float] = None
    numero_verbal: Optional[str] = None
    observations: Optional[str] = None


class ControleRoutierResponse(ControleRoutierBase):
    id: int
    motif_infraction: Optional[str] = None
    montant_amende: Optional[float] = None
    devise: str
    numero_verbal: Optional[str] = None
    observations: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# Taxe Routiere schemas
class TaxeRoutiereBase(BaseModel):
    ordre_transport_id: int
    type_taxe: str
    lieu: str
    montant: float
    numero_ticket: str
    kilometrage: float


class TaxeRoutiereCreate(TaxeRoutiereBase):
    pass


class TaxeRoutiereResponse(TaxeRoutiereBase):
    id: int
    devise: str
    date_paiement: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True


# Corridor CEMAC schemas
class CorridorCEMACBase(BaseModel):
    nom: str
    pays_depart: str
    code_pays_depart: str
    pays_arrivee: str
    code_pays_arrivee: str
    distance_km: float
    duree_estimee_heures: float


class CorridorCEMACCreate(CorridorCEMACBase):
    points_controle: str = ""
    dangers: str = ""
    recommandations: str = ""


class CorridorCEMACUpdate(BaseModel):
    points_controle: Optional[str] = None
    dangers: Optional[str] = None
    recommandations: Optional[str] = None
    statut: Optional[str] = None


class CorridorCEMACResponse(CorridorCEMACBase):
    id: int
    points_controle: Optional[str] = None
    dangers: Optional[str] = None
    recommandations: Optional[str] = None
    statut: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Rapport Transport
class RapportTransportResponse(BaseModel):
    ordre_transport: dict
    suivi: dict
