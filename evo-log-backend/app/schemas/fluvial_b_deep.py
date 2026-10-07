"""Schemas Pydantic pour transport-fluvial (genere)."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date


class FluvialCanalSectionCreate(BaseModel):
    code_section: str
    nom_bief: Optional[str] = None
    longueur_km: Optional[int] = None
    nb_ecluses: Optional[int] = None
    gabarit_max_t: Optional[int] = None
    profondeur_cote_cm: Optional[int] = None
    statut: Optional[str] = None


class FluvialCanalSectionUpdate(BaseModel):
    code_section: Optional[str] = None
    nom_bief: Optional[str] = None
    longueur_km: Optional[int] = None
    nb_ecluses: Optional[int] = None
    gabarit_max_t: Optional[int] = None
    profondeur_cote_cm: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class FluvialCanalSectionOut(BaseModel):
    id: int
    company_id: int
    code_section: str
    nom_bief: Optional[str] = None
    longueur_km: Optional[int] = None
    nb_ecluses: Optional[int] = None
    gabarit_max_t: Optional[int] = None
    profondeur_cote_cm: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class FluvialConvoyCreate(BaseModel):
    numero_convoi: str
    pousseur: Optional[str] = None
    nb_peniches: Optional[int] = None
    masse_total_t: Optional[int] = None
    longueur_total_m: Optional[int] = None
    itineraire: Optional[str] = None
    date_depart: Optional[datetime] = None
    statut: Optional[str] = None


class FluvialConvoyUpdate(BaseModel):
    numero_convoi: Optional[str] = None
    pousseur: Optional[str] = None
    nb_peniches: Optional[int] = None
    masse_total_t: Optional[int] = None
    longueur_total_m: Optional[int] = None
    itineraire: Optional[str] = None
    date_depart: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class FluvialConvoyOut(BaseModel):
    id: int
    company_id: int
    numero_convoi: str
    pousseur: Optional[str] = None
    nb_peniches: Optional[int] = None
    masse_total_t: Optional[int] = None
    longueur_total_m: Optional[int] = None
    itineraire: Optional[str] = None
    date_depart: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class FluvialBallastOperationCreate(BaseModel):
    reference: str
    numero_flotte: Optional[str] = None
    type_operation: Optional[str] = None
    masse_balle_t: Optional[int] = None
    date_operation: Optional[datetime] = None
    terminal: Optional[str] = None
    statut: Optional[str] = None


class FluvialBallastOperationUpdate(BaseModel):
    reference: Optional[str] = None
    numero_flotte: Optional[str] = None
    type_operation: Optional[str] = None
    masse_balle_t: Optional[int] = None
    date_operation: Optional[datetime] = None
    terminal: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class FluvialBallastOperationOut(BaseModel):
    id: int
    company_id: int
    reference: str
    numero_flotte: Optional[str] = None
    type_operation: Optional[str] = None
    masse_balle_t: Optional[int] = None
    date_operation: Optional[datetime] = None
    terminal: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class FluvialWaterGaugeCreate(BaseModel):
    code_poste: str
    nom_poste: Optional[str] = None
    bief: Optional[str] = None
    cote_cm: Optional[int] = None
    cote_seuil_restr_cm: Optional[int] = None
    date_releve: Optional[datetime] = None
    statut: Optional[str] = None


class FluvialWaterGaugeUpdate(BaseModel):
    code_poste: Optional[str] = None
    nom_poste: Optional[str] = None
    bief: Optional[str] = None
    cote_cm: Optional[int] = None
    cote_seuil_restr_cm: Optional[int] = None
    date_releve: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class FluvialWaterGaugeOut(BaseModel):
    id: int
    company_id: int
    code_poste: str
    nom_poste: Optional[str] = None
    bief: Optional[str] = None
    cote_cm: Optional[int] = None
    cote_seuil_restr_cm: Optional[int] = None
    date_releve: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class FluvialBerthingSlotCreate(BaseModel):
    reference: str
    terminal: Optional[str] = None
    numero_appontement: Optional[str] = None
    numero_flotte: Optional[str] = None
    date_debut: Optional[datetime] = None
    date_fin: Optional[datetime] = None
    statut: Optional[str] = None


class FluvialBerthingSlotUpdate(BaseModel):
    reference: Optional[str] = None
    terminal: Optional[str] = None
    numero_appontement: Optional[str] = None
    numero_flotte: Optional[str] = None
    date_debut: Optional[datetime] = None
    date_fin: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class FluvialBerthingSlotOut(BaseModel):
    id: int
    company_id: int
    reference: str
    terminal: Optional[str] = None
    numero_appontement: Optional[str] = None
    numero_flotte: Optional[str] = None
    date_debut: Optional[datetime] = None
    date_fin: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class FluvialCrewRosterCreate(BaseModel):
    reference: str
    numero_flotte: Optional[str] = None
    chef_bord: Optional[str] = None
    nb_marins: Optional[int] = None
    date_debut: Optional[date] = None
    date_fin: Optional[date] = None
    heures_service: Optional[int] = None
    statut: Optional[str] = None


class FluvialCrewRosterUpdate(BaseModel):
    reference: Optional[str] = None
    numero_flotte: Optional[str] = None
    chef_bord: Optional[str] = None
    nb_marins: Optional[int] = None
    date_debut: Optional[date] = None
    date_fin: Optional[date] = None
    heures_service: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class FluvialCrewRosterOut(BaseModel):
    id: int
    company_id: int
    reference: str
    numero_flotte: Optional[str] = None
    chef_bord: Optional[str] = None
    nb_marins: Optional[int] = None
    date_debut: Optional[date] = None
    date_fin: Optional[date] = None
    heures_service: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class FluvialCargoManifestCreate(BaseModel):
    numero_manifeste: str
    numero_convoi: Optional[str] = None
    terminal_depart: Optional[str] = None
    terminal_arrivee: Optional[str] = None
    nb_colis: Optional[int] = None
    masse_total_t: Optional[int] = None
    date_emission: Optional[date] = None
    statut: Optional[str] = None


class FluvialCargoManifestUpdate(BaseModel):
    numero_manifeste: Optional[str] = None
    numero_convoi: Optional[str] = None
    terminal_depart: Optional[str] = None
    terminal_arrivee: Optional[str] = None
    nb_colis: Optional[int] = None
    masse_total_t: Optional[int] = None
    date_emission: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class FluvialCargoManifestOut(BaseModel):
    id: int
    company_id: int
    numero_manifeste: str
    numero_convoi: Optional[str] = None
    terminal_depart: Optional[str] = None
    terminal_arrivee: Optional[str] = None
    nb_colis: Optional[int] = None
    masse_total_t: Optional[int] = None
    date_emission: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class FluvialPortFeeCreate(BaseModel):
    code_tarif: str
    terminal: Optional[str] = None
    categorie: Optional[str] = None
    assiette: Optional[str] = None
    montant_xaf: Optional[int] = None
    unite: Optional[str] = None
    statut: Optional[str] = None


class FluvialPortFeeUpdate(BaseModel):
    code_tarif: Optional[str] = None
    terminal: Optional[str] = None
    categorie: Optional[str] = None
    assiette: Optional[str] = None
    montant_xaf: Optional[int] = None
    unite: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class FluvialPortFeeOut(BaseModel):
    id: int
    company_id: int
    code_tarif: str
    terminal: Optional[str] = None
    categorie: Optional[str] = None
    assiette: Optional[str] = None
    montant_xaf: Optional[int] = None
    unite: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class FluvialVesselInspectionCreate(BaseModel):
    numero_pv: str
    numero_flotte: Optional[str] = None
    type_visite: Optional[str] = None
    date_visite: Optional[date] = None
    date_echeance: Optional[date] = None
    resultat: Optional[str] = None
    observations: Optional[str] = None
    statut: Optional[str] = None


class FluvialVesselInspectionUpdate(BaseModel):
    numero_pv: Optional[str] = None
    numero_flotte: Optional[str] = None
    type_visite: Optional[str] = None
    date_visite: Optional[date] = None
    date_echeance: Optional[date] = None
    resultat: Optional[str] = None
    observations: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class FluvialVesselInspectionOut(BaseModel):
    id: int
    company_id: int
    numero_pv: str
    numero_flotte: Optional[str] = None
    type_visite: Optional[str] = None
    date_visite: Optional[date] = None
    date_echeance: Optional[date] = None
    resultat: Optional[str] = None
    observations: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}

