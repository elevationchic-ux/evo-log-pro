"""Schemas Pydantic pour transport-ferroviaire (genere)."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date


class RailWagonCreate(BaseModel):
    numeration_wagon: str
    type_wagon: Optional[str] = None
    capacite_tonnes: Optional[int] = None
    livree: Optional[str] = None
    date_mise_circulation: Optional[date] = None
    prochaine_revision: Optional[date] = None
    statut: Optional[str] = None


class RailWagonUpdate(BaseModel):
    numeration_wagon: Optional[str] = None
    type_wagon: Optional[str] = None
    capacite_tonnes: Optional[int] = None
    livree: Optional[str] = None
    date_mise_circulation: Optional[date] = None
    prochaine_revision: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class RailWagonOut(BaseModel):
    id: int
    company_id: int
    numeration_wagon: str
    type_wagon: Optional[str] = None
    capacite_tonnes: Optional[int] = None
    livree: Optional[str] = None
    date_mise_circulation: Optional[date] = None
    prochaine_revision: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class RailLocomotiveCreate(BaseModel):
    numero_series: str
    modele: Optional[str] = None
    type_energie: Optional[str] = None
    puissance_kw: Optional[int] = None
    vitesse_max_kmh: Optional[int] = None
    kilometrage_actuel: Optional[int] = None
    prochaine_revision_km: Optional[int] = None
    statut: Optional[str] = None


class RailLocomotiveUpdate(BaseModel):
    numero_series: Optional[str] = None
    modele: Optional[str] = None
    type_energie: Optional[str] = None
    puissance_kw: Optional[int] = None
    vitesse_max_kmh: Optional[int] = None
    kilometrage_actuel: Optional[int] = None
    prochaine_revision_km: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class RailLocomotiveOut(BaseModel):
    id: int
    company_id: int
    numero_series: str
    modele: Optional[str] = None
    type_energie: Optional[str] = None
    puissance_kw: Optional[int] = None
    vitesse_max_kmh: Optional[int] = None
    kilometrage_actuel: Optional[int] = None
    prochaine_revision_km: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class RailTrainPathCreate(BaseModel):
    code_sillon: str
    gare_origine: Optional[str] = None
    gare_destination: Optional[str] = None
    date_circulation: Optional[date] = None
    heure_depart: Optional[str] = None
    heure_arrivee: Optional[str] = None
    numero_train: Optional[str] = None
    statut: Optional[str] = None


class RailTrainPathUpdate(BaseModel):
    code_sillon: Optional[str] = None
    gare_origine: Optional[str] = None
    gare_destination: Optional[str] = None
    date_circulation: Optional[date] = None
    heure_depart: Optional[str] = None
    heure_arrivee: Optional[str] = None
    numero_train: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class RailTrainPathOut(BaseModel):
    id: int
    company_id: int
    code_sillon: str
    gare_origine: Optional[str] = None
    gare_destination: Optional[str] = None
    date_circulation: Optional[date] = None
    heure_depart: Optional[str] = None
    heure_arrivee: Optional[str] = None
    numero_train: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class RailShuntingYardCreate(BaseModel):
    code_triage: str
    nom: Optional[str] = None
    localisation: Optional[str] = None
    nb_voies_tri: Optional[int] = None
    nb_voies_parc: Optional[int] = None
    capacite_journee_wagons: Optional[int] = None
    taux_occupation_pct: Optional[int] = None
    statut: Optional[str] = None


class RailShuntingYardUpdate(BaseModel):
    code_triage: Optional[str] = None
    nom: Optional[str] = None
    localisation: Optional[str] = None
    nb_voies_tri: Optional[int] = None
    nb_voies_parc: Optional[int] = None
    capacite_journee_wagons: Optional[int] = None
    taux_occupation_pct: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class RailShuntingYardOut(BaseModel):
    id: int
    company_id: int
    code_triage: str
    nom: Optional[str] = None
    localisation: Optional[str] = None
    nb_voies_tri: Optional[int] = None
    nb_voies_parc: Optional[int] = None
    capacite_journee_wagons: Optional[int] = None
    taux_occupation_pct: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class RailTerminalCreate(BaseModel):
    code_terminal: str
    port_associe: Optional[str] = None
    nb_voies_fond: Optional[int] = None
    longueur_quai_m: Optional[int] = None
    equipement_manutention: Optional[str] = None
    debit_conteneur_h: Optional[int] = None
    statut: Optional[str] = None


class RailTerminalUpdate(BaseModel):
    code_terminal: Optional[str] = None
    port_associe: Optional[str] = None
    nb_voies_fond: Optional[int] = None
    longueur_quai_m: Optional[int] = None
    equipement_manutention: Optional[str] = None
    debit_conteneur_h: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class RailTerminalOut(BaseModel):
    id: int
    company_id: int
    code_terminal: str
    port_associe: Optional[str] = None
    nb_voies_fond: Optional[int] = None
    longueur_quai_m: Optional[int] = None
    equipement_manutention: Optional[str] = None
    debit_conteneur_h: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class RailConsistencyPlanCreate(BaseModel):
    reference: str
    code_sillon: Optional[str] = None
    type_train: Optional[str] = None
    nb_wagons: Optional[int] = None
    masse_totale_tonnes: Optional[int] = None
    longueur_totale_m: Optional[int] = None
    locomotive_atteltee: Optional[str] = None
    statut: Optional[str] = None


class RailConsistencyPlanUpdate(BaseModel):
    reference: Optional[str] = None
    code_sillon: Optional[str] = None
    type_train: Optional[str] = None
    nb_wagons: Optional[int] = None
    masse_totale_tonnes: Optional[int] = None
    longueur_totale_m: Optional[int] = None
    locomotive_atteltee: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class RailConsistencyPlanOut(BaseModel):
    id: int
    company_id: int
    reference: str
    code_sillon: Optional[str] = None
    type_train: Optional[str] = None
    nb_wagons: Optional[int] = None
    masse_totale_tonnes: Optional[int] = None
    longueur_totale_m: Optional[int] = None
    locomotive_atteltee: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class RailWaybillCreate(BaseModel):
    numero_lcv: str
    expediteur: Optional[str] = None
    destinataire: Optional[str] = None
    gare_depart: Optional[str] = None
    gare_arrivee: Optional[str] = None
    date_emission: Optional[date] = None
    valeur_marchandise_xaf: Optional[int] = None
    statut: Optional[str] = None


class RailWaybillUpdate(BaseModel):
    numero_lcv: Optional[str] = None
    expediteur: Optional[str] = None
    destinataire: Optional[str] = None
    gare_depart: Optional[str] = None
    gare_arrivee: Optional[str] = None
    date_emission: Optional[date] = None
    valeur_marchandise_xaf: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class RailWaybillOut(BaseModel):
    id: int
    company_id: int
    numero_lcv: str
    expediteur: Optional[str] = None
    destinataire: Optional[str] = None
    gare_depart: Optional[str] = None
    gare_arrivee: Optional[str] = None
    date_emission: Optional[date] = None
    valeur_marchandise_xaf: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class RailTariffCreate(BaseModel):
    code_tarif: str
    relation: Optional[str] = None
    type_marchandise: Optional[str] = None
    prix_par_tonne_km_xaf: Optional[int] = None
    remise_volume_pct: Optional[int] = None
    date_debut_validite: Optional[date] = None
    date_fin_validite: Optional[date] = None
    statut: Optional[str] = None


class RailTariffUpdate(BaseModel):
    code_tarif: Optional[str] = None
    relation: Optional[str] = None
    type_marchandise: Optional[str] = None
    prix_par_tonne_km_xaf: Optional[int] = None
    remise_volume_pct: Optional[int] = None
    date_debut_validite: Optional[date] = None
    date_fin_validite: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class RailTariffOut(BaseModel):
    id: int
    company_id: int
    code_tarif: str
    relation: Optional[str] = None
    type_marchandise: Optional[str] = None
    prix_par_tonne_km_xaf: Optional[int] = None
    remise_volume_pct: Optional[int] = None
    date_debut_validite: Optional[date] = None
    date_fin_validite: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class RailWagonTrackingCreate(BaseModel):
    reference: str
    numeration_wagon: Optional[str] = None
    code_lcv: Optional[str] = None
    gare_actuelle: Optional[str] = None
    date_position: Optional[datetime] = None
    evenement: Optional[str] = None
    geolocalisation_gps: Optional[str] = None
    statut: Optional[str] = None


class RailWagonTrackingUpdate(BaseModel):
    reference: Optional[str] = None
    numeration_wagon: Optional[str] = None
    code_lcv: Optional[str] = None
    gare_actuelle: Optional[str] = None
    date_position: Optional[datetime] = None
    evenement: Optional[str] = None
    geolocalisation_gps: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class RailWagonTrackingOut(BaseModel):
    id: int
    company_id: int
    reference: str
    numeration_wagon: Optional[str] = None
    code_lcv: Optional[str] = None
    gare_actuelle: Optional[str] = None
    date_position: Optional[datetime] = None
    evenement: Optional[str] = None
    geolocalisation_gps: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class RailWagonMaintenanceCreate(BaseModel):
    reference: str
    numeration_wagon: Optional[str] = None
    atelier: Optional[str] = None
    type_intervention: Optional[str] = None
    date_debut: Optional[date] = None
    date_fin_prevue: Optional[date] = None
    date_retour_service: Optional[date] = None
    cout_xaf: Optional[int] = None
    statut: Optional[str] = None


class RailWagonMaintenanceUpdate(BaseModel):
    reference: Optional[str] = None
    numeration_wagon: Optional[str] = None
    atelier: Optional[str] = None
    type_intervention: Optional[str] = None
    date_debut: Optional[date] = None
    date_fin_prevue: Optional[date] = None
    date_retour_service: Optional[date] = None
    cout_xaf: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class RailWagonMaintenanceOut(BaseModel):
    id: int
    company_id: int
    reference: str
    numeration_wagon: Optional[str] = None
    atelier: Optional[str] = None
    type_intervention: Optional[str] = None
    date_debut: Optional[date] = None
    date_fin_prevue: Optional[date] = None
    date_retour_service: Optional[date] = None
    cout_xaf: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class RailSafetyRecordCreate(BaseModel):
    reference: str
    date_evenement: Optional[datetime] = None
    type_incident: Optional[str] = None
    gravite: Optional[str] = None
    lgn_concernee: Optional[str] = None
    wagon_train_implique: Optional[str] = None
    description: Optional[str] = None
    mesure_correctrice: Optional[str] = None
    statut: Optional[str] = None


class RailSafetyRecordUpdate(BaseModel):
    reference: Optional[str] = None
    date_evenement: Optional[datetime] = None
    type_incident: Optional[str] = None
    gravite: Optional[str] = None
    lgn_concernee: Optional[str] = None
    wagon_train_implique: Optional[str] = None
    description: Optional[str] = None
    mesure_correctrice: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class RailSafetyRecordOut(BaseModel):
    id: int
    company_id: int
    reference: str
    date_evenement: Optional[datetime] = None
    type_incident: Optional[str] = None
    gravite: Optional[str] = None
    lgn_concernee: Optional[str] = None
    wagon_train_implique: Optional[str] = None
    description: Optional[str] = None
    mesure_correctrice: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class RailCorridorCreate(BaseModel):
    code_corridor: str
    nom: Optional[str] = None
    pays_traverses: Optional[str] = None
    longueur_km: Optional[int] = None
    gares_focales: Optional[str] = None
    operateurs: Optional[str] = None
    debit_annuel_teu: Optional[int] = None
    statut: Optional[str] = None


class RailCorridorUpdate(BaseModel):
    code_corridor: Optional[str] = None
    nom: Optional[str] = None
    pays_traverses: Optional[str] = None
    longueur_km: Optional[int] = None
    gares_focales: Optional[str] = None
    operateurs: Optional[str] = None
    debit_annuel_teu: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class RailCorridorOut(BaseModel):
    id: int
    company_id: int
    code_corridor: str
    nom: Optional[str] = None
    pays_traverses: Optional[str] = None
    longueur_km: Optional[int] = None
    gares_focales: Optional[str] = None
    operateurs: Optional[str] = None
    debit_annuel_teu: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}

