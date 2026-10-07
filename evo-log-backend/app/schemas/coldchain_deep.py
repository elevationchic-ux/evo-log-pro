"""Schemas Pydantic auto- genere (expansion wave 5)."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date


class ColdChainChamberCreate(BaseModel):
    code_chambre: str
    type_chambre: Optional[str] = None
    plage: Optional[str] = None
    temperature_consigne_c: Optional[int] = None
    temperature_actuelle_c: Optional[int] = None
    capacite_m3: Optional[int] = None
    puissance_kw: Optional[int] = None
    date_mise_service: Optional[date] = None
    prochaine_maintenance: Optional[date] = None
    statut: Optional[str] = None


class ColdChainChamberUpdate(BaseModel):
    code_chambre: Optional[str] = None
    type_chambre: Optional[str] = None
    plage: Optional[str] = None
    temperature_consigne_c: Optional[int] = None
    temperature_actuelle_c: Optional[int] = None
    capacite_m3: Optional[int] = None
    puissance_kw: Optional[int] = None
    date_mise_service: Optional[date] = None
    prochaine_maintenance: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class ColdChainChamberOut(BaseModel):
    id: int
    company_id: int
    code_chambre: str
    type_chambre: Optional[str] = None
    plage: Optional[str] = None
    temperature_consigne_c: Optional[int] = None
    temperature_actuelle_c: Optional[int] = None
    capacite_m3: Optional[int] = None
    puissance_kw: Optional[int] = None
    date_mise_service: Optional[date] = None
    prochaine_maintenance: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class ColdChainReeferCreate(BaseModel):
    numero_reefer: str
    type_reefer: Optional[str] = None
    mode: Optional[str] = None
    plage_temperature_c: Optional[str] = None
    capacite_m3: Optional[int] = None
    date_last_check: Optional[date] = None
    prochaine_pt: Optional[date] = None
    statut: Optional[str] = None


class ColdChainReeferUpdate(BaseModel):
    numero_reefer: Optional[str] = None
    type_reefer: Optional[str] = None
    mode: Optional[str] = None
    plage_temperature_c: Optional[str] = None
    capacite_m3: Optional[int] = None
    date_last_check: Optional[date] = None
    prochaine_pt: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class ColdChainReeferOut(BaseModel):
    id: int
    company_id: int
    numero_reefer: str
    type_reefer: Optional[str] = None
    mode: Optional[str] = None
    plage_temperature_c: Optional[str] = None
    capacite_m3: Optional[int] = None
    date_last_check: Optional[date] = None
    prochaine_pt: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class ColdChainLoggerCreate(BaseModel):
    numero_logger: str
    technologie: Optional[str] = None
    frequence_lecture_s: Optional[int] = None
    autonomie_jours: Optional[int] = None
    precision_c: Optional[int] = None
    date_achat: Optional[date] = None
    date_calibration: Optional[date] = None
    prochaine_calibration: Optional[date] = None
    assigned_to: Optional[str] = None
    statut: Optional[str] = None


class ColdChainLoggerUpdate(BaseModel):
    numero_logger: Optional[str] = None
    technologie: Optional[str] = None
    frequence_lecture_s: Optional[int] = None
    autonomie_jours: Optional[int] = None
    precision_c: Optional[int] = None
    date_achat: Optional[date] = None
    date_calibration: Optional[date] = None
    prochaine_calibration: Optional[date] = None
    assigned_to: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class ColdChainLoggerOut(BaseModel):
    id: int
    company_id: int
    numero_logger: str
    technologie: Optional[str] = None
    frequence_lecture_s: Optional[int] = None
    autonomie_jours: Optional[int] = None
    precision_c: Optional[int] = None
    date_achat: Optional[date] = None
    date_calibration: Optional[date] = None
    prochaine_calibration: Optional[date] = None
    assigned_to: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class ColdChainProductCreate(BaseModel):
    code_sku: str
    nom: Optional[str] = None
    categorie: Optional[str] = None
    classe: Optional[str] = None
    temp_min_c: Optional[int] = None
    temp_max_c: Optional[int] = None
    duree_vie_jours: Optional[int] = None
    seuil_excursion_h: Optional[int] = None


class ColdChainProductUpdate(BaseModel):
    code_sku: Optional[str] = None
    nom: Optional[str] = None
    categorie: Optional[str] = None
    classe: Optional[str] = None
    temp_min_c: Optional[int] = None
    temp_max_c: Optional[int] = None
    duree_vie_jours: Optional[int] = None
    seuil_excursion_h: Optional[int] = None
    is_active: Optional[bool] = None


class ColdChainProductOut(BaseModel):
    id: int
    company_id: int
    code_sku: str
    nom: Optional[str] = None
    categorie: Optional[str] = None
    classe: Optional[str] = None
    temp_min_c: Optional[int] = None
    temp_max_c: Optional[int] = None
    duree_vie_jours: Optional[int] = None
    seuil_excursion_h: Optional[int] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class ColdChainExcursionCreate(BaseModel):
    reference: str
    type: Optional[str] = None
    produit_concerne: Optional[str] = None
    actif_associe: Optional[str] = None
    date_debut: Optional[datetime] = None
    date_fin: Optional[datetime] = None
    temp_extreme_c: Optional[int] = None
    duree_h: Optional[int] = None
    impact: Optional[str] = None
    valeur_perdue_xaf: Optional[int] = None
    statut: Optional[str] = None


class ColdChainExcursionUpdate(BaseModel):
    reference: Optional[str] = None
    type: Optional[str] = None
    produit_concerne: Optional[str] = None
    actif_associe: Optional[str] = None
    date_debut: Optional[datetime] = None
    date_fin: Optional[datetime] = None
    temp_extreme_c: Optional[int] = None
    duree_h: Optional[int] = None
    impact: Optional[str] = None
    valeur_perdue_xaf: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class ColdChainExcursionOut(BaseModel):
    id: int
    company_id: int
    reference: str
    type: Optional[str] = None
    produit_concerne: Optional[str] = None
    actif_associe: Optional[str] = None
    date_debut: Optional[datetime] = None
    date_fin: Optional[datetime] = None
    temp_extreme_c: Optional[int] = None
    duree_h: Optional[int] = None
    impact: Optional[str] = None
    valeur_perdue_xaf: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class ColdChainVaccinBatchCreate(BaseModel):
    numero_lot: str
    fabricant: Optional[str] = None
    type_vaccin: Optional[str] = None
    nb_doses: Optional[int] = None
    date_fabrication: Optional[date] = None
    date_peremption: Optional[date] = None
    temp_stockage_c: Optional[int] = None
    vvm_statut: Optional[str] = None
    lieu_stockage: Optional[str] = None
    statut: Optional[str] = None


class ColdChainVaccinBatchUpdate(BaseModel):
    numero_lot: Optional[str] = None
    fabricant: Optional[str] = None
    type_vaccin: Optional[str] = None
    nb_doses: Optional[int] = None
    date_fabrication: Optional[date] = None
    date_peremption: Optional[date] = None
    temp_stockage_c: Optional[int] = None
    vvm_statut: Optional[str] = None
    lieu_stockage: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class ColdChainVaccinBatchOut(BaseModel):
    id: int
    company_id: int
    numero_lot: str
    fabricant: Optional[str] = None
    type_vaccin: Optional[str] = None
    nb_doses: Optional[int] = None
    date_fabrication: Optional[date] = None
    date_peremption: Optional[date] = None
    temp_stockage_c: Optional[int] = None
    vvm_statut: Optional[str] = None
    lieu_stockage: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class ColdChainHaccpRecordCreate(BaseModel):
    reference: str
    pratique: Optional[str] = None
    date_lecture: Optional[datetime] = None
    valeur_lue: Optional[str] = None
    seuil_mini: Optional[str] = None
    seuil_maxi: Optional[str] = None
    operateur: Optional[str] = None
    action_corrective: Optional[str] = None
    resultat: Optional[str] = None


class ColdChainHaccpRecordUpdate(BaseModel):
    reference: Optional[str] = None
    pratique: Optional[str] = None
    date_lecture: Optional[datetime] = None
    valeur_lue: Optional[str] = None
    seuil_mini: Optional[str] = None
    seuil_maxi: Optional[str] = None
    operateur: Optional[str] = None
    action_corrective: Optional[str] = None
    resultat: Optional[str] = None
    is_active: Optional[bool] = None


class ColdChainHaccpRecordOut(BaseModel):
    id: int
    company_id: int
    reference: str
    pratique: Optional[str] = None
    date_lecture: Optional[datetime] = None
    valeur_lue: Optional[str] = None
    seuil_mini: Optional[str] = None
    seuil_maxi: Optional[str] = None
    operateur: Optional[str] = None
    action_corrective: Optional[str] = None
    resultat: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class ColdChainDefrostCycleCreate(BaseModel):
    reference: str
    chambre_associee: Optional[str] = None
    frequence: Optional[str] = None
    type: Optional[str] = None
    date_prevue: Optional[date] = None
    date_reelle_debut: Optional[datetime] = None
    date_reelle_fin: Optional[datetime] = None
    duree_h: Optional[int] = None
    energie_kwh: Optional[int] = None
    statut: Optional[str] = None


class ColdChainDefrostCycleUpdate(BaseModel):
    reference: Optional[str] = None
    chambre_associee: Optional[str] = None
    frequence: Optional[str] = None
    type: Optional[str] = None
    date_prevue: Optional[date] = None
    date_reelle_debut: Optional[datetime] = None
    date_reelle_fin: Optional[datetime] = None
    duree_h: Optional[int] = None
    energie_kwh: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class ColdChainDefrostCycleOut(BaseModel):
    id: int
    company_id: int
    reference: str
    chambre_associee: Optional[str] = None
    frequence: Optional[str] = None
    type: Optional[str] = None
    date_prevue: Optional[date] = None
    date_reelle_debut: Optional[datetime] = None
    date_reelle_fin: Optional[datetime] = None
    duree_h: Optional[int] = None
    energie_kwh: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class ColdChainEnergyMeterCreate(BaseModel):
    code_compteur: str
    type_energie: Optional[str] = None
    actif_alimente: Optional[str] = None
    consommation_kwh: Optional[int] = None
    cout_mensuel_xaf: Optional[int] = None
    co2_eq_kg: Optional[int] = None
    date_releve: Optional[date] = None


class ColdChainEnergyMeterUpdate(BaseModel):
    code_compteur: Optional[str] = None
    type_energie: Optional[str] = None
    actif_alimente: Optional[str] = None
    consommation_kwh: Optional[int] = None
    cout_mensuel_xaf: Optional[int] = None
    co2_eq_kg: Optional[int] = None
    date_releve: Optional[date] = None
    is_active: Optional[bool] = None


class ColdChainEnergyMeterOut(BaseModel):
    id: int
    company_id: int
    code_compteur: str
    type_energie: Optional[str] = None
    actif_alimente: Optional[str] = None
    consommation_kwh: Optional[int] = None
    cout_mensuel_xaf: Optional[int] = None
    co2_eq_kg: Optional[int] = None
    date_releve: Optional[date] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class ColdChainTransportLegCreate(BaseModel):
    reference: str
    mode: Optional[str] = None
    reefer_utilise: Optional[str] = None
    produit_transporte: Optional[str] = None
    poids_kg: Optional[int] = None
    origine: Optional[str] = None
    destination: Optional[str] = None
    date_depart: Optional[datetime] = None
    date_arrivee: Optional[datetime] = None
    temp_moyenne_c: Optional[int] = None
    statut: Optional[str] = None


class ColdChainTransportLegUpdate(BaseModel):
    reference: Optional[str] = None
    mode: Optional[str] = None
    reefer_utilise: Optional[str] = None
    produit_transporte: Optional[str] = None
    poids_kg: Optional[int] = None
    origine: Optional[str] = None
    destination: Optional[str] = None
    date_depart: Optional[datetime] = None
    date_arrivee: Optional[datetime] = None
    temp_moyenne_c: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class ColdChainTransportLegOut(BaseModel):
    id: int
    company_id: int
    reference: str
    mode: Optional[str] = None
    reefer_utilise: Optional[str] = None
    produit_transporte: Optional[str] = None
    poids_kg: Optional[int] = None
    origine: Optional[str] = None
    destination: Optional[str] = None
    date_depart: Optional[datetime] = None
    date_arrivee: Optional[datetime] = None
    temp_moyenne_c: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}

