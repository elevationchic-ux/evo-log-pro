schemas_to_append = '''

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
'''

with open('ERP-logistique-/evo-log-backend/app/schemas/transport_avance.py', 'a', encoding='utf-8') as f:
    f.write(schemas_to_append)

print("Appended missing transport_avance schemas successfully!")
