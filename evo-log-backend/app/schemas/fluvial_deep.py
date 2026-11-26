"""Schemas Pydantic pour transport-fluvial (genere)."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date


class FluvialBargeCreate(BaseModel):
    numero_flotte: str
    type: Optional[str] = None
    capacite_tonnes: Optional[int] = None
    tirant_eau_max_m: Optional[str] = None
    longueur_m: Optional[int] = None
    largeur_m: Optional[int] = None
    statut: Optional[str] = None


class FluvialBargeUpdate(BaseModel):
    numero_flotte: Optional[str] = None
    type: Optional[str] = None
    capacite_tonnes: Optional[int] = None
    tirant_eau_max_m: Optional[str] = None
    longueur_m: Optional[int] = None
    largeur_m: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class FluvialBargeOut(BaseModel):
    id: int
    company_id: int
    numero_flotte: str
    type: Optional[str] = None
    capacite_tonnes: Optional[int] = None
    tirant_eau_max_m: Optional[str] = None
    longueur_m: Optional[int] = None
    largeur_m: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class FluvialTowboatCreate(BaseModel):
    numero_tug: str
    nom: Optional[str] = None
    puissance_kw: Optional[int] = None
    bollard_pull_t: Optional[int] = None
    zone_operation: Optional[str] = None
    statut: Optional[str] = None


class FluvialTowboatUpdate(BaseModel):
    numero_tug: Optional[str] = None
    nom: Optional[str] = None
    puissance_kw: Optional[int] = None
    bollard_pull_t: Optional[int] = None
    zone_operation: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class FluvialTowboatOut(BaseModel):
    id: int
    company_id: int
    numero_tug: str
    nom: Optional[str] = None
    puissance_kw: Optional[int] = None
    bollard_pull_t: Optional[int] = None
    zone_operation: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class LockTransitCreate(BaseModel):
    reference: str
    nom_ecluse: Optional[str] = None
    date_passage: Optional[datetime] = None
    numero_peniche: Optional[str] = None
    masse_tonnes: Optional[int] = None
    tirant_eau_m: Optional[str] = None
    attente_minutes: Optional[int] = None
    statut: Optional[str] = None


class LockTransitUpdate(BaseModel):
    reference: Optional[str] = None
    nom_ecluse: Optional[str] = None
    date_passage: Optional[datetime] = None
    numero_peniche: Optional[str] = None
    masse_tonnes: Optional[int] = None
    tirant_eau_m: Optional[str] = None
    attente_minutes: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class LockTransitOut(BaseModel):
    id: int
    company_id: int
    reference: str
    nom_ecluse: Optional[str] = None
    date_passage: Optional[datetime] = None
    numero_peniche: Optional[str] = None
    masse_tonnes: Optional[int] = None
    tirant_eau_m: Optional[str] = None
    attente_minutes: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class RiverDepthSurveyCreate(BaseModel):
    reference: str
    bief: Optional[str] = None
    date_mesure: Optional[date] = None
    profondeur_min_cm: Optional[int] = None
    tirant_eau_pmax_cm: Optional[int] = None
    debit_m3s: Optional[int] = None
    statut: Optional[str] = None


class RiverDepthSurveyUpdate(BaseModel):
    reference: Optional[str] = None
    bief: Optional[str] = None
    date_mesure: Optional[date] = None
    profondeur_min_cm: Optional[int] = None
    tirant_eau_pmax_cm: Optional[int] = None
    debit_m3s: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class RiverDepthSurveyOut(BaseModel):
    id: int
    company_id: int
    reference: str
    bief: Optional[str] = None
    date_mesure: Optional[date] = None
    profondeur_min_cm: Optional[int] = None
    tirant_eau_pmax_cm: Optional[int] = None
    debit_m3s: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class FluvialTerminalCreate(BaseModel):
    code_terminal: str
    nom: Optional[str] = None
    fleuve: Optional[str] = None
    pays: Optional[str] = None
    nb_appontements: Optional[int] = None
    longueur_quai_m: Optional[int] = None
    connecte_port_maritime: Optional[bool] = None
    statut: Optional[str] = None


class FluvialTerminalUpdate(BaseModel):
    code_terminal: Optional[str] = None
    nom: Optional[str] = None
    fleuve: Optional[str] = None
    pays: Optional[str] = None
    nb_appontements: Optional[int] = None
    longueur_quai_m: Optional[int] = None
    connecte_port_maritime: Optional[bool] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class FluvialTerminalOut(BaseModel):
    id: int
    company_id: int
    code_terminal: str
    nom: Optional[str] = None
    fleuve: Optional[str] = None
    pays: Optional[str] = None
    nb_appontements: Optional[int] = None
    longueur_quai_m: Optional[int] = None
    connecte_port_maritime: Optional[bool] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class FluvialBulkOperationCreate(BaseModel):
    reference: str
    produit: Optional[str] = None
    categorie: Optional[str] = None
    quantite_tonnes: Optional[int] = None
    terminal: Optional[str] = None
    date_operation: Optional[datetime] = None
    duree_heures: Optional[int] = None
    statut: Optional[str] = None


class FluvialBulkOperationUpdate(BaseModel):
    reference: Optional[str] = None
    produit: Optional[str] = None
    categorie: Optional[str] = None
    quantite_tonnes: Optional[int] = None
    terminal: Optional[str] = None
    date_operation: Optional[datetime] = None
    duree_heures: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class FluvialBulkOperationOut(BaseModel):
    id: int
    company_id: int
    reference: str
    produit: Optional[str] = None
    categorie: Optional[str] = None
    quantite_tonnes: Optional[int] = None
    terminal: Optional[str] = None
    date_operation: Optional[datetime] = None
    duree_heures: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class FluvialSafetyRecordCreate(BaseModel):
    reference: str
    date_evenement: Optional[datetime] = None
    bief: Optional[str] = None
    type_evenement: Optional[str] = None
    gravite: Optional[str] = None
    batiments_impliques: Optional[str] = None
    description: Optional[str] = None
    statut: Optional[str] = None


class FluvialSafetyRecordUpdate(BaseModel):
    reference: Optional[str] = None
    date_evenement: Optional[datetime] = None
    bief: Optional[str] = None
    type_evenement: Optional[str] = None
    gravite: Optional[str] = None
    batiments_impliques: Optional[str] = None
    description: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class FluvialSafetyRecordOut(BaseModel):
    id: int
    company_id: int
    reference: str
    date_evenement: Optional[datetime] = None
    bief: Optional[str] = None
    type_evenement: Optional[str] = None
    gravite: Optional[str] = None
    batiments_impliques: Optional[str] = None
    description: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class FluvialTariffCreate(BaseModel):
    code_tarif: str
    bief: Optional[str] = None
    produit: Optional[str] = None
    prix_par_tonne_xaf: Optional[int] = None
    saisonnalite: Optional[str] = None
    remise_volume_pct: Optional[int] = None
    validite_debut: Optional[date] = None
    validite_fin: Optional[date] = None
    statut: Optional[str] = None


class FluvialTariffUpdate(BaseModel):
    code_tarif: Optional[str] = None
    bief: Optional[str] = None
    produit: Optional[str] = None
    prix_par_tonne_xaf: Optional[int] = None
    saisonnalite: Optional[str] = None
    remise_volume_pct: Optional[int] = None
    validite_debut: Optional[date] = None
    validite_fin: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class FluvialTariffOut(BaseModel):
    id: int
    company_id: int
    code_tarif: str
    bief: Optional[str] = None
    produit: Optional[str] = None
    prix_par_tonne_xaf: Optional[int] = None
    saisonnalite: Optional[str] = None
    remise_volume_pct: Optional[int] = None
    validite_debut: Optional[date] = None
    validite_fin: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class FluvialWaybillCreate(BaseModel):
    numero: str
    expediteur: Optional[str] = None
    destinataire: Optional[str] = None
    port_depart: Optional[str] = None
    port_arrivee: Optional[str] = None
    produit: Optional[str] = None
    quantite_tonnes: Optional[int] = None
    date_emission: Optional[date] = None
    statut: Optional[str] = None


class FluvialWaybillUpdate(BaseModel):
    numero: Optional[str] = None
    expediteur: Optional[str] = None
    destinataire: Optional[str] = None
    port_depart: Optional[str] = None
    port_arrivee: Optional[str] = None
    produit: Optional[str] = None
    quantite_tonnes: Optional[int] = None
    date_emission: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class FluvialWaybillOut(BaseModel):
    id: int
    company_id: int
    numero: str
    expediteur: Optional[str] = None
    destinataire: Optional[str] = None
    port_depart: Optional[str] = None
    port_arrivee: Optional[str] = None
    produit: Optional[str] = None
    quantite_tonnes: Optional[int] = None
    date_emission: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class FluvialPositionCreate(BaseModel):
    reference: str
    numero_flotte: Optional[str] = None
    date_releve: Optional[datetime] = None
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    vitesse_nd: Optional[str] = None
    cap: Optional[str] = None
    statut: Optional[str] = None


class FluvialPositionUpdate(BaseModel):
    reference: Optional[str] = None
    numero_flotte: Optional[str] = None
    date_releve: Optional[datetime] = None
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    vitesse_nd: Optional[str] = None
    cap: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class FluvialPositionOut(BaseModel):
    id: int
    company_id: int
    reference: str
    numero_flotte: Optional[str] = None
    date_releve: Optional[datetime] = None
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    vitesse_nd: Optional[str] = None
    cap: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}

