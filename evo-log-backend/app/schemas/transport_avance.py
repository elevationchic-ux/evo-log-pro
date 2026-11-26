"""Schemas pour le transport avancé - Dispatch, E-POD, Analytics"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal


# ============ DISPATCH ============

class DispatchBase(BaseModel):
    mission_id: int
    conducteur_id: int
    camion_id: int
    type_optimisation: str = Field(default="plus_court_chemin")
    priorite: int = Field(default=5, ge=1, le=10)


class DispatchCreate(DispatchBase):
    pass


class DispatchUpdate(BaseModel):
    statut: Optional[str] = None
    date_debut_reelle: Optional[datetime] = None
    date_fin_reelle: Optional[datetime] = None
    distance_reelle: Optional[Decimal] = None
    duree_reelle: Optional[int] = None
    cout_reel: Optional[Decimal] = None
    notes: Optional[str] = None


class DispatchResponse(DispatchBase):
    id: int
    numero_dispatch: str
    statut: str
    date_planification: datetime
    date_debut_prevue: Optional[datetime] = None
    date_fin_prevue: Optional[datetime] = None
    distance_estimee: Optional[Decimal] = None
    duree_estimee: Optional[int] = None
    cout_estime: Optional[Decimal] = None
    score_confiance: Optional[Decimal] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class OptimisationTourneesRequest(BaseModel):
    missions_ids: List[int]
    contraintes: Optional[dict] = None


class EquilibreChargeResponse(BaseModel):
    periode: str
    nombre_conducteurs: int
    moyenne_missions: float
    desequilibres: List[dict]


# ============ ARRETS ============

class ArretBase(BaseModel):
    dispatch_id: int
    type_arret: str
    ordre_sequence: int
    adresse: str
    duree_estimee: int = Field(default=30, ge=0)


class ArretCreate(ArretBase):
    client_id: Optional[int] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None


class ArretResponse(ArretBase):
    id: int
    client_id: Optional[int] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    duree_reelle: Optional[int] = None
    heure_arrivee_prevue: Optional[datetime] = None
    heure_arrivee_reelle: Optional[datetime] = None
    heure_depart_prevue: Optional[datetime] = None
    heure_depart_reelle: Optional[datetime] = None
    statut: str
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ============ E-POD ============

class PODBase(BaseModel):
    livraison_id: int
    signature_client: Optional[str] = None
    photo_marchandise: Optional[str] = None
    coordonnees: Optional[str] = None


class PODCreate(PODBase):
    pass


class PODUpdate(BaseModel):
    statut: Optional[str] = None
    nom_receveur: Optional[str] = None
    fonction_receveur: Optional[str] = None
    commentaire_client: Optional[str] = None
    commentaire_chauffeur: Optional[str] = None


class PODResponse(PODBase):
    id: int
    numero_pod: str
    date_pod: datetime
    statut: str
    photo_signature: Optional[str] = None
    horodatage: Optional[datetime] = None
    nom_receveur: Optional[str] = None
    fonction_receveur: Optional[str] = None
    commentaire_client: Optional[str] = None
    commentaire_chauffeur: Optional[str] = None
    valide_par: Optional[int] = None
    date_validation: Optional[datetime] = None
    hash_preuve: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class DocumentPODBase(BaseModel):
    pod_id: int
    type_document: str
    nom_fichier: str
    url_fichier: str


class DocumentPODCreate(DocumentPODBase):
    taille_fichier: Optional[int] = None
    type_mime: Optional[str] = None


class DocumentPODResponse(DocumentPODBase):
    id: int
    type_preuve: Optional[str] = None
    taille_fichier: Optional[int] = None
    type_mime: Optional[str] = None
    hash_fichier: Optional[str] = None
    upload_par: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============ ANALYTICS ============

class TableauBordTransportResponse(BaseModel):
    date: date
    missions_actives: int
    missions_terminees: int
    vehicules_disponibles: int
    vehicules_en_mission: int
    taux_occupation: float


class KPIResponse(BaseModel):
    periode: str
    taux_reussite: float
    satisfaction_client: float
    note_performance: float


class AlertPerformanceResponse(BaseModel):
    type: str
    gravite: str
    valeur: float

# ============ TOURNÉES & LIVRAISONS ============

class TourneeBase(BaseModel):
    vehicule_id: Optional[int] = None
    conducteur_id: Optional[int] = None
    date_tournee: Optional[date] = None
    origine: Optional[str] = None
    destination: Optional[str] = None
    statut: Optional[str] = "planifie"


class TourneeCreate(TourneeBase):
    pass


class TourneeUpdate(BaseModel):
    vehicule_id: Optional[int] = None
    conducteur_id: Optional[int] = None
    statut: Optional[str] = None
    date_debut_reelle: Optional[datetime] = None
    date_fin_reelle: Optional[datetime] = None


class TourneeResponse(TourneeBase):
    id: int
    numero_tournee: Optional[str] = None
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class LivraisonBase(BaseModel):
    tournee_id: Optional[int] = None
    client_id: Optional[int] = None
    adresse_livraison: Optional[str] = None
    destinataire: Optional[str] = None
    statut: Optional[str] = "en_attente"


class LivraisonCreate(LivraisonBase):
    pass


class LivraisonUpdate(BaseModel):
    statut: Optional[str] = None
    date_livraison: Optional[datetime] = None
    signature: Optional[str] = None


class LivraisonResponse(LivraisonBase):
    id: int
    numero_livraison: Optional[str] = None
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ============ FRAIS & TEMPS DE CONDUITE ============

class FraisKilometriqueCreate(BaseModel):
    mission_id: int
    distance_km: float
    taux_km: float
    montant: Optional[float] = None
    justificatif: Optional[str] = None


class FraisKilometriqueResponse(BaseModel):
    id: int
    mission_id: int
    distance_km: float
    taux_km: float
    montant: float
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TempsConduiteCreate(BaseModel):
    conducteur_id: int
    date_service: date
    duree_conduite_minutes: int
    duree_pause_minutes: int
    duree_repos_minutes: int


class TempsConduiteResponse(BaseModel):
    id: int
    conducteur_id: int
    date_service: date
    duree_conduite_minutes: int
    duree_pause_minutes: int
    duree_repos_minutes: int
    conforme: bool = True

    class Config:
        from_attributes = True


class ConformiteTempsResponse(BaseModel):
    conducteur_id: int
    periode: str
    taux_conformite: float
    infractions_detectees: int
    details: List[str] = []


# ============ SOUS-TRAITANCE ============

class SousTraitantBase(BaseModel):
    raison_sociale: str
    niu: Optional[str] = None
    rccm: Optional[str] = None
    telephone: Optional[str] = None
    email: Optional[str] = None
    adresse: Optional[str] = None
    actif: bool = True


class SousTraitantCreate(SousTraitantBase):
    pass


class SousTraitantUpdate(BaseModel):
    raison_sociale: Optional[str] = None
    telephone: Optional[str] = None
    email: Optional[str] = None
    actif: Optional[bool] = None


class SousTraitantResponse(SousTraitantBase):
    id: int
    code_sous_traitant: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ContratSousTraitantCreate(BaseModel):
    sous_traitant_id: int
    numero_contrat: str
    date_debut: date
    date_fin: Optional[date] = None
    conditions_tarifaires: Optional[str] = None


class ContratSousTraitantUpdate(BaseModel):
    date_fin: Optional[date] = None
    statut: Optional[str] = None


class ContratSousTraitantResponse(BaseModel):
    id: int
    sous_traitant_id: int
    numero_contrat: str
    date_debut: date
    date_fin: Optional[date] = None
    statut: str = "actif"

    class Config:
        from_attributes = True


class MissionSousTraitantCreate(BaseModel):
    mission_id: int
    sous_traitant_id: int
    tarif_convenu: float
    devise: str = "XAF"


class MissionSousTraitantUpdate(BaseModel):
    statut: Optional[str] = None
    tarif_final: Optional[float] = None


class MissionSousTraitantResponse(BaseModel):
    id: int
    mission_id: int
    sous_traitant_id: int
    tarif_convenu: float
    statut: str = "assignee"

    class Config:
        from_attributes = True


# ============ ACCIDENTS & MAINTENANCE PRÉVENTIVE ============

class AccidentTransportCreate(BaseModel):
    vehicule_id: int
    conducteur_id: Optional[int] = None
    date_accident: datetime
    lieu: str
    gravite: str
    description: str


class AccidentTransportUpdate(BaseModel):
    statut: Optional[str] = None
    montant_assurance: Optional[float] = None
    date_resolution: Optional[date] = None


class AccidentTransportResponse(BaseModel):
    id: int
    vehicule_id: int
    date_accident: datetime
    lieu: str
    gravite: str
    statut: str = "signale"

    class Config:
        from_attributes = True


class MaintenancePreventiveCreate(BaseModel):
    vehicule_id: int
    type_maintenance: str
    date_prevue: date
    kilometrage_prevu: Optional[int] = None
    description: Optional[str] = None


class MaintenancePreventiveUpdate(BaseModel):
    statut: Optional[str] = None
    date_realisee: Optional[date] = None
    cout_reel: Optional[float] = None


class MaintenancePreventiveResponse(BaseModel):
    id: int
    vehicule_id: int
    type_maintenance: str
    date_prevue: date
    statut: str = "planifiee"

    class Config:
        from_attributes = True


# ============ GPS & GEOFENCING ============

class PositionGPSCreate(BaseModel):
    vehicule_id: int
    latitude: float
    longitude: float
    vitesse: Optional[float] = None
    cap: Optional[float] = None
    timestamp: Optional[datetime] = None


class PositionGPSResponse(BaseModel):
    id: int
    vehicule_id: int
    latitude: float
    longitude: float
    vitesse: Optional[float] = None
    timestamp: datetime

    class Config:
        from_attributes = True


class ZoneGeofencingCreate(BaseModel):
    nom: str
    type_zone: str = "circulaire"
    centre_latitude: Optional[float] = None
    centre_longitude: Optional[float] = None
    rayon_metres: Optional[float] = None
    polygone_coordonnees: Optional[str] = None


class ZoneGeofencingUpdate(BaseModel):
    nom: Optional[str] = None
    actif: Optional[bool] = None


class ZoneGeofencingResponse(BaseModel):
    id: int
    nom: str
    type_zone: str
    actif: bool = True

    class Config:
        from_attributes = True


class EvenementVehiculeCreate(BaseModel):
    vehicule_id: int
    type_evenement: str
    timestamp: datetime
    description: Optional[str] = None


class EvenementVehiculeResponse(BaseModel):
    id: int
    vehicule_id: int
    type_evenement: str
    timestamp: datetime

    class Config:
        from_attributes = True


# ============ ANALYTICS AVANCÉS ============

class CoutKmResponse(BaseModel):
    vehicule_id: int
    periode: str
    cout_total: float
    distance_km: float
    cout_par_km: float


class AnomalieCarburantResponse(BaseModel):
    vehicule_id: int
    type_anomalie: str
    niveau_gravite: str
    description: str
    date_detection: datetime


class PerformanceSousTraitantResponse(BaseModel):
    sous_traitant_id: int
    missions_totales: int
    taux_ponctualite: float
    note_qualite: float


class StatistiquesAccidentsResponse(BaseModel):
    periode: str
    accidents_totaux: int
    par_gravite: dict
    cout_total: float


class ComportementConducteurResponse(BaseModel):
    conducteur_id: int
    score_ecoconduite: float
    exces_vitesse: int
    freinages_brusques: int


class KPITransportResponse(BaseModel):
    taux_disponibilité_flotte: float
    taux_ponctualite_livraison: float
    consommation_moyenne_100km: float
    cout_moyen_km: float
