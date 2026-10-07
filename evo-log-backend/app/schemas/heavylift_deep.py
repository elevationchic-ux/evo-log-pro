"""Schemas Pydantic auto- genere (expansion wave 5)."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date


class HeavyLiftProjectCreate(BaseModel):
    code_projet: str
    nom: Optional[str] = None
    client: Optional[str] = None
    categorie: Optional[str] = None
    poids_max_t: Optional[int] = None
    volume_m3: Optional[int] = None
    distance_km: Optional[int] = None
    date_debut: Optional[date] = None
    date_fin_prevue: Optional[date] = None
    budget_xaf: Optional[int] = None
    statut: Optional[str] = None


class HeavyLiftProjectUpdate(BaseModel):
    code_projet: Optional[str] = None
    nom: Optional[str] = None
    client: Optional[str] = None
    categorie: Optional[str] = None
    poids_max_t: Optional[int] = None
    volume_m3: Optional[int] = None
    distance_km: Optional[int] = None
    date_debut: Optional[date] = None
    date_fin_prevue: Optional[date] = None
    budget_xaf: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class HeavyLiftProjectOut(BaseModel):
    id: int
    company_id: int
    code_projet: str
    nom: Optional[str] = None
    client: Optional[str] = None
    categorie: Optional[str] = None
    poids_max_t: Optional[int] = None
    volume_m3: Optional[int] = None
    distance_km: Optional[int] = None
    date_debut: Optional[date] = None
    date_fin_prevue: Optional[date] = None
    budget_xaf: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class HeavyLiftCraneCreate(BaseModel):
    numero_grue: str
    type_grue: Optional[str] = None
    capacite_max_t: Optional[int] = None
    portee_max_m: Optional[int] = None
    hauteur_max_m: Optional[int] = None
    mise_en_service: Optional[date] = None
    prochaine_visite: Optional[date] = None
    cout_location_jour_xaf: Optional[int] = None
    statut: Optional[str] = None


class HeavyLiftCraneUpdate(BaseModel):
    numero_grue: Optional[str] = None
    type_grue: Optional[str] = None
    capacite_max_t: Optional[int] = None
    portee_max_m: Optional[int] = None
    hauteur_max_m: Optional[int] = None
    mise_en_service: Optional[date] = None
    prochaine_visite: Optional[date] = None
    cout_location_jour_xaf: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class HeavyLiftCraneOut(BaseModel):
    id: int
    company_id: int
    numero_grue: str
    type_grue: Optional[str] = None
    capacite_max_t: Optional[int] = None
    portee_max_m: Optional[int] = None
    hauteur_max_m: Optional[int] = None
    mise_en_service: Optional[date] = None
    prochaine_visite: Optional[date] = None
    cout_location_jour_xaf: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class HeavyLiftModularTrailerCreate(BaseModel):
    plaque: str
    type_remorque: Optional[str] = None
    nb_essieux: Optional[int] = None
    charge_utile_t: Optional[int] = None
    longueur_m: Optional[int] = None
    largeur_m: Optional[int] = None
    hauteur_min_m: Optional[int] = None
    angle_orientation_deg: Optional[int] = None
    statut: Optional[str] = None


class HeavyLiftModularTrailerUpdate(BaseModel):
    plaque: Optional[str] = None
    type_remorque: Optional[str] = None
    nb_essieux: Optional[int] = None
    charge_utile_t: Optional[int] = None
    longueur_m: Optional[int] = None
    largeur_m: Optional[int] = None
    hauteur_min_m: Optional[int] = None
    angle_orientation_deg: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class HeavyLiftModularTrailerOut(BaseModel):
    id: int
    company_id: int
    plaque: str
    type_remorque: Optional[str] = None
    nb_essieux: Optional[int] = None
    charge_utile_t: Optional[int] = None
    longueur_m: Optional[int] = None
    largeur_m: Optional[int] = None
    hauteur_min_m: Optional[int] = None
    angle_orientation_deg: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class HeavyLiftRouteSurveyCreate(BaseModel):
    reference: str
    projet_associe: Optional[str] = None
    origine: Optional[str] = None
    destination: Optional[str] = None
    distance_km: Optional[int] = None
    nb_obstacles: Optional[int] = None
    ouvrages_franchis: Optional[str] = None
    cout_amenagement_xaf: Optional[int] = None
    date_etude: Optional[date] = None
    resultat: Optional[str] = None
    statut: Optional[str] = None


class HeavyLiftRouteSurveyUpdate(BaseModel):
    reference: Optional[str] = None
    projet_associe: Optional[str] = None
    origine: Optional[str] = None
    destination: Optional[str] = None
    distance_km: Optional[int] = None
    nb_obstacles: Optional[int] = None
    ouvrages_franchis: Optional[str] = None
    cout_amenagement_xaf: Optional[int] = None
    date_etude: Optional[date] = None
    resultat: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class HeavyLiftRouteSurveyOut(BaseModel):
    id: int
    company_id: int
    reference: str
    projet_associe: Optional[str] = None
    origine: Optional[str] = None
    destination: Optional[str] = None
    distance_km: Optional[int] = None
    nb_obstacles: Optional[int] = None
    ouvrages_franchis: Optional[str] = None
    cout_amenagement_xaf: Optional[int] = None
    date_etude: Optional[date] = None
    resultat: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class HeavyLiftLiftPlanCreate(BaseModel):
    reference: str
    projet_associe: Optional[str] = None
    type_operation: Optional[str] = None
    charge_t: Optional[int] = None
    hauteur_m: Optional[int] = None
    centre_gravite_haut: Optional[bool] = None
    coefficient_securite_pct: Optional[int] = None
    grue_prevue: Optional[str] = None
    date_prevue: Optional[date] = None
    criticite: Optional[str] = None
    statut: Optional[str] = None


class HeavyLiftLiftPlanUpdate(BaseModel):
    reference: Optional[str] = None
    projet_associe: Optional[str] = None
    type_operation: Optional[str] = None
    charge_t: Optional[int] = None
    hauteur_m: Optional[int] = None
    centre_gravite_haut: Optional[bool] = None
    coefficient_securite_pct: Optional[int] = None
    grue_prevue: Optional[str] = None
    date_prevue: Optional[date] = None
    criticite: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class HeavyLiftLiftPlanOut(BaseModel):
    id: int
    company_id: int
    reference: str
    projet_associe: Optional[str] = None
    type_operation: Optional[str] = None
    charge_t: Optional[int] = None
    hauteur_m: Optional[int] = None
    centre_gravite_haut: Optional[bool] = None
    coefficient_securite_pct: Optional[int] = None
    grue_prevue: Optional[str] = None
    date_prevue: Optional[date] = None
    criticite: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class HeavyLiftPermitCreate(BaseModel):
    numero_permis: str
    type_permis: Optional[str] = None
    autorite: Optional[str] = None
    charge_concernee: Optional[str] = None
    itineraire_depot: Optional[str] = None
    date_depot_demande: Optional[date] = None
    date_delivrance: Optional[date] = None
    date_validite_fin: Optional[date] = None
    cout_redevance_xaf: Optional[int] = None
    statut: Optional[str] = None


class HeavyLiftPermitUpdate(BaseModel):
    numero_permis: Optional[str] = None
    type_permis: Optional[str] = None
    autorite: Optional[str] = None
    charge_concernee: Optional[str] = None
    itineraire_depot: Optional[str] = None
    date_depot_demande: Optional[date] = None
    date_delivrance: Optional[date] = None
    date_validite_fin: Optional[date] = None
    cout_redevance_xaf: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class HeavyLiftPermitOut(BaseModel):
    id: int
    company_id: int
    numero_permis: str
    type_permis: Optional[str] = None
    autorite: Optional[str] = None
    charge_concernee: Optional[str] = None
    itineraire_depot: Optional[str] = None
    date_depot_demande: Optional[date] = None
    date_delivrance: Optional[date] = None
    date_validite_fin: Optional[date] = None
    cout_redevance_xaf: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class HeavyLiftEscortCreate(BaseModel):
    reference: str
    convoi_associe: Optional[str] = None
    type_escorte: Optional[str] = None
    nb_vehicules_escorte: Optional[int] = None
    date_debut: Optional[datetime] = None
    date_fin: Optional[datetime] = None
    zone_administrative: Optional[str] = None
    agent_responsable: Optional[str] = None
    cout_xaf: Optional[int] = None
    statut: Optional[str] = None


class HeavyLiftEscortUpdate(BaseModel):
    reference: Optional[str] = None
    convoi_associe: Optional[str] = None
    type_escorte: Optional[str] = None
    nb_vehicules_escorte: Optional[int] = None
    date_debut: Optional[datetime] = None
    date_fin: Optional[datetime] = None
    zone_administrative: Optional[str] = None
    agent_responsable: Optional[str] = None
    cout_xaf: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class HeavyLiftEscortOut(BaseModel):
    id: int
    company_id: int
    reference: str
    convoi_associe: Optional[str] = None
    type_escorte: Optional[str] = None
    nb_vehicules_escorte: Optional[int] = None
    date_debut: Optional[datetime] = None
    date_fin: Optional[datetime] = None
    zone_administrative: Optional[str] = None
    agent_responsable: Optional[str] = None
    cout_xaf: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class HeavyLiftLashingCreate(BaseModel):
    reference: str
    methode: Optional[str] = None
    charge_amarree: Optional[str] = None
    nb_points: Optional[int] = None
    effort_admissible_t: Optional[int] = None
    coefficient_secu_pct: Optional[int] = None
    operateur: Optional[str] = None
    date_controle: Optional[date] = None
    resultat: Optional[str] = None


class HeavyLiftLashingUpdate(BaseModel):
    reference: Optional[str] = None
    methode: Optional[str] = None
    charge_amarree: Optional[str] = None
    nb_points: Optional[int] = None
    effort_admissible_t: Optional[int] = None
    coefficient_secu_pct: Optional[int] = None
    operateur: Optional[str] = None
    date_controle: Optional[date] = None
    resultat: Optional[str] = None
    is_active: Optional[bool] = None


class HeavyLiftLashingOut(BaseModel):
    id: int
    company_id: int
    reference: str
    methode: Optional[str] = None
    charge_amarree: Optional[str] = None
    nb_points: Optional[int] = None
    effort_admissible_t: Optional[int] = None
    coefficient_secu_pct: Optional[int] = None
    operateur: Optional[str] = None
    date_controle: Optional[date] = None
    resultat: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class HeavyLiftBallastCreate(BaseModel):
    code_ballast: str
    type_ballast: Optional[str] = None
    masse_unitaire_t: Optional[int] = None
    nb_unites: Optional[int] = None
    masse_totale_t: Optional[int] = None
    cout_location_jour_xaf: Optional[int] = None
    lieu_stockage: Optional[str] = None
    statut: Optional[str] = None


class HeavyLiftBallastUpdate(BaseModel):
    code_ballast: Optional[str] = None
    type_ballast: Optional[str] = None
    masse_unitaire_t: Optional[int] = None
    nb_unites: Optional[int] = None
    masse_totale_t: Optional[int] = None
    cout_location_jour_xaf: Optional[int] = None
    lieu_stockage: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class HeavyLiftBallastOut(BaseModel):
    id: int
    company_id: int
    code_ballast: str
    type_ballast: Optional[str] = None
    masse_unitaire_t: Optional[int] = None
    nb_unites: Optional[int] = None
    masse_totale_t: Optional[int] = None
    cout_location_jour_xaf: Optional[int] = None
    lieu_stockage: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class HeavyLiftRiggingMethodCreate(BaseModel):
    code_methode: str
    categorie: Optional[str] = None
    description: Optional[str] = None
    capacite_max_t: Optional[int] = None
    temps_mise_en_oeuvre_h: Optional[int] = None
    nb_techniciens: Optional[int] = None
    cout_moyen_xaf: Optional[int] = None


class HeavyLiftRiggingMethodUpdate(BaseModel):
    code_methode: Optional[str] = None
    categorie: Optional[str] = None
    description: Optional[str] = None
    capacite_max_t: Optional[int] = None
    temps_mise_en_oeuvre_h: Optional[int] = None
    nb_techniciens: Optional[int] = None
    cout_moyen_xaf: Optional[int] = None
    is_active: Optional[bool] = None


class HeavyLiftRiggingMethodOut(BaseModel):
    id: int
    company_id: int
    code_methode: str
    categorie: Optional[str] = None
    description: Optional[str] = None
    capacite_max_t: Optional[int] = None
    temps_mise_en_oeuvre_h: Optional[int] = None
    nb_techniciens: Optional[int] = None
    cout_moyen_xaf: Optional[int] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}

