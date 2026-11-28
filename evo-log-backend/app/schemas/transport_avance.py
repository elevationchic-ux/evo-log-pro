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
    coordonnees_livraison: Optional[str] = None


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
    satisfaction_client: Optional[float] = None
    note_performance: float
    nombre_missions: int = 0
    nombre_km_parcourus: float = 0


class AlertPerformanceResponse(BaseModel):
    type: str
    gravite: str
    valeur: float
# ============ TOURNÉES & LIVRAISONS ============
# Schémas alignés sur app/models/transport_avance.py (Tournée, Livraison)

class TourneeCreate(BaseModel):
    conducteur_id: int
    camion_id: int
    date_tournee: date
    type_tournee: Optional[str] = None
    notes: Optional[str] = None


class TourneeUpdate(BaseModel):
    statut: Optional[str] = None
    type_tournee: Optional[str] = None
    notes: Optional[str] = None


class TourneeResponse(BaseModel):
    id: int
    numero_tournee: Optional[str] = None
    conducteur_id: Optional[int] = None
    camion_id: Optional[int] = None
    date_tournee: Optional[date] = None
    statut: Optional[str] = None
    nombre_livraisons: Optional[int] = None
    nombre_livraisons_effectuees: Optional[int] = None
    type_tournee: Optional[str] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class LivraisonCreate(BaseModel):
    client_id: int
    point_dechargement: str
    heure_debut_prevue: Optional[str] = None
    heure_fin_prevue: Optional[str] = None
    nombre_colis: Optional[int] = None
    poids_total: Optional[float] = None
    commentaire: Optional[str] = None


class LivraisonUpdate(BaseModel):
    statut: Optional[str] = None
    heure_debut_reelle: Optional[str] = None
    heure_fin_reelle: Optional[str] = None
    nombre_colis: Optional[int] = None
    poids_total: Optional[float] = None
    preuve_livraison: Optional[str] = None
    commentaire: Optional[str] = None


class LivraisonResponse(BaseModel):
    id: int
    numero_livraison: Optional[str] = None
    tournee_id: Optional[int] = None
    client_id: Optional[int] = None
    point_dechargement: Optional[str] = None
    heure_debut_prevue: Optional[str] = None
    heure_fin_prevue: Optional[str] = None
    heure_debut_reelle: Optional[str] = None
    heure_fin_reelle: Optional[str] = None
    statut: Optional[str] = None
    nombre_colis: Optional[int] = None
    poids_total: Optional[float] = None
    commentaire: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============ FRAIS & TEMPS DE CONDUITE ============
# Alignés sur FraisKilometrique / TempsConduite (colonnes réelles)

class FraisKilometriqueCreate(BaseModel):
    employe_id: int
    mission_id: Optional[int] = None
    kilometrage_parcouru: float
    kilometrage_theorique: Optional[float] = None
    taux_indemnite: Optional[float] = None
    commentaires: Optional[str] = None


class FraisKilometriqueResponse(BaseModel):
    id: int
    employe_id: Optional[int] = None
    mission_id: Optional[int] = None
    date_frais: Optional[date] = None
    kilometrage_parcouru: Optional[float] = None
    kilometrage_theorique: Optional[float] = None
    taux_indemnite: Optional[float] = None
    montant_indemnite: Optional[float] = None
    surconsommation: Optional[float] = None
    statut: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TempsConduiteCreate(BaseModel):
    conducteur_id: int
    mission_id: Optional[int] = None
    date: date
    heure_debut_conduite: str
    heure_fin_conduite: Optional[str] = None
    temps_conduite: int  # minutes
    temps_repos: Optional[int] = None
    commentaires: Optional[str] = None


class TempsConduiteResponse(BaseModel):
    id: int
    conducteur_id: Optional[int] = None
    mission_id: Optional[int] = None
    date: Optional[date] = None
    heure_debut_conduite: Optional[str] = None
    heure_fin_conduite: Optional[str] = None
    temps_conduite: Optional[int] = None
    temps_repos: Optional[int] = None
    temps_service: Optional[int] = None
    conformite_legale: Optional[bool] = None
    statut: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ConformiteTempsResponse(BaseModel):
    conducteur_id: int
    date: date
    total_minutes_conduite: int
    limite_journaliere_minutes: int = 540
    infractions: int = 0
    conforme: bool
    alerte: Optional[str] = None


# ============ SOUS-TRAITANCE ============
# Alignés sur SousTraitant / ContratSousTraitant / MissionSousTraitant

class SousTraitantCreate(BaseModel):
    nom: str
    code: Optional[str] = None
    type_service: Optional[str] = None
    specialite: Optional[str] = None
    numero_licence: Optional[str] = None
    adresse: Optional[str] = None
    ville: Optional[str] = None
    telephone: Optional[str] = None
    email: Optional[str] = None


class SousTraitantUpdate(BaseModel):
    nom: Optional[str] = None
    type_service: Optional[str] = None
    specialite: Optional[str] = None
    numero_licence: Optional[str] = None
    adresse: Optional[str] = None
    ville: Optional[str] = None
    telephone: Optional[str] = None
    email: Optional[str] = None
    statut: Optional[str] = None


class SousTraitantResponse(BaseModel):
    id: int
    code: Optional[str] = None
    nom: Optional[str] = None
    type_service: Optional[str] = None
    specialite: Optional[str] = None
    numero_licence: Optional[str] = None
    adresse: Optional[str] = None
    ville: Optional[str] = None
    telephone: Optional[str] = None
    email: Optional[str] = None
    statut: Optional[str] = None
    evaluation_performance: Optional[float] = None
    date_debut_contrat: Optional[date] = None
    date_fin_contrat: Optional[date] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ContratSousTraitantCreate(BaseModel):
    sous_traitant_id: int
    numero_contrat: str
    type_service: Optional[str] = None
    date_debut: date
    date_fin: Optional[date] = None
    tarif_unitaire: Optional[float] = None
    unite_tarif: Optional[str] = None
    volume_minimum: Optional[float] = None
    conditions_paiement: Optional[str] = None
    notes: Optional[str] = None


class ContratSousTraitantUpdate(BaseModel):
    date_fin: Optional[date] = None
    tarif_unitaire: Optional[float] = None
    conditions_paiement: Optional[str] = None
    statut: Optional[str] = None
    notes: Optional[str] = None


class ContratSousTraitantResponse(BaseModel):
    id: int
    sous_traitant_id: Optional[int] = None
    numero_contrat: Optional[str] = None
    type_service: Optional[str] = None
    date_debut: Optional[date] = None
    date_fin: Optional[date] = None
    tarif_unitaire: Optional[float] = None
    unite_tarif: Optional[str] = None
    statut: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class MissionSousTraitantCreate(BaseModel):
    sous_traitant_id: int
    contrat_id: Optional[int] = None
    client_id: int
    date_mission: date
    point_depart: str
    point_arrivee: str
    distance: Optional[float] = None
    type_marchandise: Optional[str] = None
    poids: Optional[float] = None
    cout_estime: Optional[float] = None
    notes: Optional[str] = None


class MissionSousTraitantUpdate(BaseModel):
    statut: Optional[str] = None
    cout_reel: Optional[float] = None
    qualite_service: Optional[float] = None
    ponctualite: Optional[float] = None
    notes: Optional[str] = None


class MissionSousTraitantResponse(BaseModel):
    id: int
    numero_mission: Optional[str] = None
    sous_traitant_id: Optional[int] = None
    contrat_id: Optional[int] = None
    client_id: Optional[int] = None
    date_mission: Optional[date] = None
    point_depart: Optional[str] = None
    point_arrivee: Optional[str] = None
    distance: Optional[float] = None
    type_marchandise: Optional[str] = None
    poids: Optional[float] = None
    statut: Optional[str] = None
    cout_estime: Optional[float] = None
    cout_reel: Optional[float] = None
    qualite_service: Optional[float] = None
    ponctualite: Optional[float] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============ ACCIDENTS & MAINTENANCE PRÉVENTIVE ========
# ============ ACCIDENTS & MAINTENANCE PRÉVENTIVE ============

class AccidentTransportCreate(BaseModel):
    vehicule_id: int
    conducteur_id: int
    mission_id: Optional[int] = None
    date_accident: datetime
    heure_accident: Optional[str] = None
    lieu: str
    type_accident: Optional[str] = None
    gravite: Optional[str] = None
    blesses: int = 0
    deces: int = 0
    degats_materiels: Optional[str] = None
    temoins: Optional[str] = None
    constat: Optional[str] = None
    assureur: Optional[str] = None
    numero_police: Optional[str] = None
    montant_dommages: Optional[float] = None
    notes: Optional[str] = None


class AccidentTransportUpdate(BaseModel):
    statut: Optional[str] = None
    constat: Optional[str] = None
    notes: Optional[str] = None
    montant_rembourse: Optional[float] = None
    date_clos: Optional[date] = None


class AccidentTransportResponse(BaseModel):
    id: int
    numero_accident: Optional[str] = None
    vehicule_id: Optional[int] = None
    conducteur_id: Optional[int] = None
    mission_id: Optional[int] = None
    date_accident: Optional[datetime] = None
    heure_accident: Optional[str] = None
    lieu: Optional[str] = None
    type_accident: Optional[str] = None
    gravite: Optional[str] = None
    blesses: Optional[int] = None
    deces: Optional[int] = None
    statut: Optional[str] = None
    montant_dommages: Optional[float] = None
    montant_rembourse: Optional[float] = None
    date_clos: Optional[date] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class MaintenancePreventiveCreate(BaseModel):
    vehicule_id: int
    type_maintenance: str
    kilometrage_prevu: int
    date_prevue: date
    periodicite: Optional[int] = None
    cout_estime: Optional[float] = None
    notes: Optional[str] = None


class MaintenancePreventiveUpdate(BaseModel):
    statut: Optional[str] = None
    date_effective: Optional[date] = None
    cout_reel: Optional[float] = None
    realise_par: Optional[str] = None
    notes: Optional[str] = None


class MaintenancePreventiveResponse(BaseModel):
    id: int
    vehicule_id: Optional[int] = None
    type_maintenance: Optional[str] = None
    kilometrage_prevu: Optional[int] = None
    date_prevue: Optional[date] = None
    date_effective: Optional[date] = None
    periodicite: Optional[int] = None
    statut: Optional[str] = None
    cout_estime: Optional[float] = None
    cout_reel: Optional[float] = None
    realise_par: Optional[str] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============ GPS & GEOFENCING ============

class PositionGPSCreate(BaseModel):
    vehicule_id: int
    conducteur_id: Optional[int] = None
    latitude: float
    longitude: float
    altitude: Optional[float] = None
    vitesse: Optional[float] = None
    direction: Optional[float] = None
    statut_moteur: Optional[str] = None
    statut_vehicule: Optional[str] = None
    kilmetrage_actuel: Optional[int] = None  # nom historique du modèle (coquille conservée)
    niveau_carburant: Optional[int] = None
    alerte: Optional[str] = None
    horodatage: Optional[datetime] = None


class PositionGPSResponse(BaseModel):
    id: int
    vehicule_id: Optional[int] = None
    conducteur_id: Optional[int] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    altitude: Optional[float] = None
    vitesse: Optional[float] = None
    direction: Optional[float] = None
    horodatage: Optional[datetime] = None
    statut_moteur: Optional[str] = None
    statut_vehicule: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ZoneGeofencingCreate(BaseModel):
    nom_zone: str
    type_zone: Optional[str] = None
    description: Optional[str] = None
    latitude_centre: float
    longitude_centre: float
    rayon_metres: float
    ville: Optional[str] = None
    limite_vitesse: Optional[int] = None
    alerte_entree: Optional[bool] = True
    alerte_sortie: Optional[bool] = True


class ZoneGeofencingUpdate(BaseModel):
    nom_zone: Optional[str] = None
    type_zone: Optional[str] = None
    description: Optional[str] = None
    statut: Optional[str] = None
    limite_vitesse: Optional[int] = None


class ZoneGeofencingResponse(BaseModel):
    id: int
    nom_zone: Optional[str] = None
    type_zone: Optional[str] = None
    description: Optional[str] = None
    latitude_centre: Optional[float] = None
    longitude_centre: Optional[float] = None
    rayon: Optional[float] = None
    ville: Optional[str] = None
    limite_vitesse: Optional[int] = None
    alerte_entree: Optional[bool] = None
    alerte_sortie: Optional[bool] = None
    statut: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class EvenementVehiculeCreate(BaseModel):
    vehicule_id: int
    type_evenement: str
    description: Optional[str] = None
    localisation: Optional[str] = None
    operateur: Optional[str] = None
    date_evenement: Optional[datetime] = None


class EvenementVehiculeResponse(BaseModel):
    id: int
    vehicule_id: Optional[int] = None
    type_evenement: Optional[str] = None
    date_evenement: Optional[datetime] = None
    localisation: Optional[str] = None
    operateur: Optional[str] = None
    description: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============ ANALYTICS AVANCÉS ============
# Réponses alignées sur ce que les endpoints calculent réellement

class CoutKmResponse(BaseModel):
    camion_id: int
    mois: int
    annee: int
    kilometres: float
    cout_total: float
    cout_par_km: float


class AnomalieCarburantResponse(BaseModel):
    vehicule_id: int
    consommation_actuelle: float
    consommation_theorique: float
    difference: float
    pourcentage_difference: float
    anomalie_detectee: bool
    niveau_alerte: str


class PerformanceSousTraitantResponse(BaseModel):
    sous_traitant_id: int
    missions_totales: int
    missions_terminees: int
    taux_completion: float
    ponctualite_moyenne: Optional[float] = None
    qualite_moyenne: Optional[float] = None
    note: float


class StatistiquesAccidentsResponse(BaseModel):
    debut_periode: date
    fin_periode: date
    accidents_totaux: int
    avec_blesses: int
    avec_deces: int
    montant_total_dommages: float
    montant_total_rembourse: float


class ComportementConducteurResponse(BaseModel):
    conducteur_id: int
    debut_periode: date
    fin_periode: date
    heures_conduite: float
    accidents: int
    missions: int
    score_comportement: float
    niveau: str
