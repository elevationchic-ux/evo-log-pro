"""Schemas Pydantic pour pipeline-oleoduc (genere)."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date


class PipelineSectionCreate(BaseModel):
    code_section: str
    nom: Optional[str] = None
    type_produit: Optional[str] = None
    diametre_mm: Optional[int] = None
    epaisseur_paroi_mm: Optional[int] = None
    longueur_km: Optional[int] = None
    origine: Optional[str] = None
    destination: Optional[str] = None
    date_mise_service: Optional[date] = None
    pression_max_bar: Optional[int] = None
    statut: Optional[str] = None


class PipelineSectionUpdate(BaseModel):
    code_section: Optional[str] = None
    nom: Optional[str] = None
    type_produit: Optional[str] = None
    diametre_mm: Optional[int] = None
    epaisseur_paroi_mm: Optional[int] = None
    longueur_km: Optional[int] = None
    origine: Optional[str] = None
    destination: Optional[str] = None
    date_mise_service: Optional[date] = None
    pression_max_bar: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class PipelineSectionOut(BaseModel):
    id: int
    company_id: int
    code_section: str
    nom: Optional[str] = None
    type_produit: Optional[str] = None
    diametre_mm: Optional[int] = None
    epaisseur_paroi_mm: Optional[int] = None
    longueur_km: Optional[int] = None
    origine: Optional[str] = None
    destination: Optional[str] = None
    date_mise_service: Optional[date] = None
    pression_max_bar: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class PipelinePumpStationCreate(BaseModel):
    code_station: str
    nom: Optional[str] = None
    type_station: Optional[str] = None
    section_associee: Optional[str] = None
    nb_pompes: Optional[int] = None
    puissance_totale_kw: Optional[int] = None
    debit_nominal_m3h: Optional[int] = None
    pression_refoulement_bar: Optional[int] = None
    energie_annuelle_kwh: Optional[int] = None
    statut: Optional[str] = None


class PipelinePumpStationUpdate(BaseModel):
    code_station: Optional[str] = None
    nom: Optional[str] = None
    type_station: Optional[str] = None
    section_associee: Optional[str] = None
    nb_pompes: Optional[int] = None
    puissance_totale_kw: Optional[int] = None
    debit_nominal_m3h: Optional[int] = None
    pression_refoulement_bar: Optional[int] = None
    energie_annuelle_kwh: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class PipelinePumpStationOut(BaseModel):
    id: int
    company_id: int
    code_station: str
    nom: Optional[str] = None
    type_station: Optional[str] = None
    section_associee: Optional[str] = None
    nb_pompes: Optional[int] = None
    puissance_totale_kw: Optional[int] = None
    debit_nominal_m3h: Optional[int] = None
    pression_refoulement_bar: Optional[int] = None
    energie_annuelle_kwh: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class PipelineStorageTankCreate(BaseModel):
    code_cuve: str
    type_cuve: Optional[str] = None
    capacite_m3: Optional[int] = None
    niveau_actuel_pct: Optional[int] = None
    temperature_stockage_c: Optional[int] = None
    produit_stocke: Optional[str] = None
    date_dernier_nettoyage: Optional[date] = None
    prochaine_inspection: Optional[date] = None
    statut: Optional[str] = None


class PipelineStorageTankUpdate(BaseModel):
    code_cuve: Optional[str] = None
    type_cuve: Optional[str] = None
    capacite_m3: Optional[int] = None
    niveau_actuel_pct: Optional[int] = None
    temperature_stockage_c: Optional[int] = None
    produit_stocke: Optional[str] = None
    date_dernier_nettoyage: Optional[date] = None
    prochaine_inspection: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class PipelineStorageTankOut(BaseModel):
    id: int
    company_id: int
    code_cuve: str
    type_cuve: Optional[str] = None
    capacite_m3: Optional[int] = None
    niveau_actuel_pct: Optional[int] = None
    temperature_stockage_c: Optional[int] = None
    produit_stocke: Optional[str] = None
    date_dernier_nettoyage: Optional[date] = None
    prochaine_inspection: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class PipelineMeteringPointCreate(BaseModel):
    code_point: str
    usage: Optional[str] = None
    technologie: Optional[str] = None
    section_associee: Optional[str] = None
    precision_pct: Optional[int] = None
    debit_max_m3h: Optional[int] = None
    date_etalonnage: Optional[date] = None
    prochain_etalonnage: Optional[date] = None
    statut: Optional[str] = None


class PipelineMeteringPointUpdate(BaseModel):
    code_point: Optional[str] = None
    usage: Optional[str] = None
    technologie: Optional[str] = None
    section_associee: Optional[str] = None
    precision_pct: Optional[int] = None
    debit_max_m3h: Optional[int] = None
    date_etalonnage: Optional[date] = None
    prochain_etalonnage: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class PipelineMeteringPointOut(BaseModel):
    id: int
    company_id: int
    code_point: str
    usage: Optional[str] = None
    technologie: Optional[str] = None
    section_associee: Optional[str] = None
    precision_pct: Optional[int] = None
    debit_max_m3h: Optional[int] = None
    date_etalonnage: Optional[date] = None
    prochain_etalonnage: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class PipelineProductBatchCreate(BaseModel):
    numero_lot: str
    produit: Optional[str] = None
    volume_m3: Optional[int] = None
    densite_api: Optional[int] = None
    teneur_soufre_pct: Optional[int] = None
    injection_debut: Optional[datetime] = None
    arrivee_prevue: Optional[datetime] = None
    destinataire: Optional[str] = None
    section_utilisee: Optional[str] = None
    statut: Optional[str] = None


class PipelineProductBatchUpdate(BaseModel):
    numero_lot: Optional[str] = None
    produit: Optional[str] = None
    volume_m3: Optional[int] = None
    densite_api: Optional[int] = None
    teneur_soufre_pct: Optional[int] = None
    injection_debut: Optional[datetime] = None
    arrivee_prevue: Optional[datetime] = None
    destinataire: Optional[str] = None
    section_utilisee: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class PipelineProductBatchOut(BaseModel):
    id: int
    company_id: int
    numero_lot: str
    produit: Optional[str] = None
    volume_m3: Optional[int] = None
    densite_api: Optional[int] = None
    teneur_soufre_pct: Optional[int] = None
    injection_debut: Optional[datetime] = None
    arrivee_prevue: Optional[datetime] = None
    destinataire: Optional[str] = None
    section_utilisee: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class PipelinePressureReadingCreate(BaseModel):
    reference: str
    section_associee: Optional[str] = None
    date_releve: Optional[datetime] = None
    pression_entree_bar: Optional[int] = None
    pression_sortie_bar: Optional[int] = None
    debit_m3h: Optional[int] = None
    temperature_c: Optional[int] = None
    qualite: Optional[str] = None


class PipelinePressureReadingUpdate(BaseModel):
    reference: Optional[str] = None
    section_associee: Optional[str] = None
    date_releve: Optional[datetime] = None
    pression_entree_bar: Optional[int] = None
    pression_sortie_bar: Optional[int] = None
    debit_m3h: Optional[int] = None
    temperature_c: Optional[int] = None
    qualite: Optional[str] = None
    is_active: Optional[bool] = None


class PipelinePressureReadingOut(BaseModel):
    id: int
    company_id: int
    reference: str
    section_associee: Optional[str] = None
    date_releve: Optional[datetime] = None
    pression_entree_bar: Optional[int] = None
    pression_sortie_bar: Optional[int] = None
    debit_m3h: Optional[int] = None
    temperature_c: Optional[int] = None
    qualite: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class PipelineLeakDetectionCreate(BaseModel):
    reference: str
    date_detection: Optional[datetime] = None
    section_associee: Optional[str] = None
    technologie: Optional[str] = None
    perte_estimee_m3: Optional[int] = None
    severite: Optional[str] = None
    lat_localisation: Optional[str] = None
    lon_localisation: Optional[str] = None
    delai_reparation_h: Optional[int] = None
    statut: Optional[str] = None


class PipelineLeakDetectionUpdate(BaseModel):
    reference: Optional[str] = None
    date_detection: Optional[datetime] = None
    section_associee: Optional[str] = None
    technologie: Optional[str] = None
    perte_estimee_m3: Optional[int] = None
    severite: Optional[str] = None
    lat_localisation: Optional[str] = None
    lon_localisation: Optional[str] = None
    delai_reparation_h: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class PipelineLeakDetectionOut(BaseModel):
    id: int
    company_id: int
    reference: str
    date_detection: Optional[datetime] = None
    section_associee: Optional[str] = None
    technologie: Optional[str] = None
    perte_estimee_m3: Optional[int] = None
    severite: Optional[str] = None
    lat_localisation: Optional[str] = None
    lon_localisation: Optional[str] = None
    delai_reparation_h: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class PipelineMaintenanceWorkCreate(BaseModel):
    reference: str
    section_associee: Optional[str] = None
    type_travaux: Optional[str] = None
    date_debut: Optional[date] = None
    date_fin_prevue: Optional[date] = None
    date_fin_reelle: Optional[date] = None
    cout_xaf: Optional[int] = None
    prestataire: Optional[str] = None
    arret_production_h: Optional[int] = None
    statut: Optional[str] = None


class PipelineMaintenanceWorkUpdate(BaseModel):
    reference: Optional[str] = None
    section_associee: Optional[str] = None
    type_travaux: Optional[str] = None
    date_debut: Optional[date] = None
    date_fin_prevue: Optional[date] = None
    date_fin_reelle: Optional[date] = None
    cout_xaf: Optional[int] = None
    prestataire: Optional[str] = None
    arret_production_h: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class PipelineMaintenanceWorkOut(BaseModel):
    id: int
    company_id: int
    reference: str
    section_associee: Optional[str] = None
    type_travaux: Optional[str] = None
    date_debut: Optional[date] = None
    date_fin_prevue: Optional[date] = None
    date_fin_reelle: Optional[date] = None
    cout_xaf: Optional[int] = None
    prestataire: Optional[str] = None
    arret_production_h: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class PipelineInjectionCampaignCreate(BaseModel):
    reference: str
    type: Optional[str] = None
    section_associee: Optional[str] = None
    produit_chimique: Optional[str] = None
    debit_injection_lh: Optional[int] = None
    date_debut: Optional[date] = None
    date_fin: Optional[date] = None
    volume_total_l: Optional[int] = None
    cout_xaf: Optional[int] = None
    statut: Optional[str] = None


class PipelineInjectionCampaignUpdate(BaseModel):
    reference: Optional[str] = None
    type: Optional[str] = None
    section_associee: Optional[str] = None
    produit_chimique: Optional[str] = None
    debit_injection_lh: Optional[int] = None
    date_debut: Optional[date] = None
    date_fin: Optional[date] = None
    volume_total_l: Optional[int] = None
    cout_xaf: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class PipelineInjectionCampaignOut(BaseModel):
    id: int
    company_id: int
    reference: str
    type: Optional[str] = None
    section_associee: Optional[str] = None
    produit_chimique: Optional[str] = None
    debit_injection_lh: Optional[int] = None
    date_debut: Optional[date] = None
    date_fin: Optional[date] = None
    volume_total_l: Optional[int] = None
    cout_xaf: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class PipelineShipNominationCreate(BaseModel):
    reference: str
    nom_navire: Optional[str] = None
    imo: Optional[str] = None
    terminal: Optional[str] = None
    produit_charge: Optional[str] = None
    volume_m3: Optional[int] = None
    eta: Optional[date] = None
    etb: Optional[date] = None
    etc: Optional[date] = None
    vacis: Optional[str] = None
    statut: Optional[str] = None


class PipelineShipNominationUpdate(BaseModel):
    reference: Optional[str] = None
    nom_navire: Optional[str] = None
    imo: Optional[str] = None
    terminal: Optional[str] = None
    produit_charge: Optional[str] = None
    volume_m3: Optional[int] = None
    eta: Optional[date] = None
    etb: Optional[date] = None
    etc: Optional[date] = None
    vacis: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class PipelineShipNominationOut(BaseModel):
    id: int
    company_id: int
    reference: str
    nom_navire: Optional[str] = None
    imo: Optional[str] = None
    terminal: Optional[str] = None
    produit_charge: Optional[str] = None
    volume_m3: Optional[int] = None
    eta: Optional[date] = None
    etb: Optional[date] = None
    etc: Optional[date] = None
    vacis: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}
