"""Schemas Pydantic pour amenagement-portuaire (genere)."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date


class ConstructionProgressCreate(BaseModel):
    reference: str
    marche_id: Optional[int] = None
    lot: Optional[str] = None
    avancement_pct: Optional[float] = None
    date_releve: Optional[date] = None
    surface_m2: Optional[float] = None
    observateur: Optional[str] = None


class ConstructionProgressUpdate(BaseModel):
    reference: Optional[str] = None
    marche_id: Optional[int] = None
    lot: Optional[str] = None
    avancement_pct: Optional[float] = None
    date_releve: Optional[date] = None
    surface_m2: Optional[float] = None
    observateur: Optional[str] = None
    is_active: Optional[bool] = None


class ConstructionProgressOut(BaseModel):
    id: int
    company_id: int
    reference: str
    marche_id: Optional[int] = None
    lot: Optional[str] = None
    avancement_pct: Optional[float] = None
    date_releve: Optional[date] = None
    surface_m2: Optional[float] = None
    observateur: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class InfrastructureMaintenanceCreate(BaseModel):
    reference: str
    ouvrage_id: Optional[int] = None
    type_intervention: Optional[str] = None
    frequence_mois: Optional[int] = None
    date_prochaine: Optional[date] = None
    cout_estime_xaf: Optional[float] = None
    statut: Optional[str] = None


class InfrastructureMaintenanceUpdate(BaseModel):
    reference: Optional[str] = None
    ouvrage_id: Optional[int] = None
    type_intervention: Optional[str] = None
    frequence_mois: Optional[int] = None
    date_prochaine: Optional[date] = None
    cout_estime_xaf: Optional[float] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class InfrastructureMaintenanceOut(BaseModel):
    id: int
    company_id: int
    reference: str
    ouvrage_id: Optional[int] = None
    type_intervention: Optional[str] = None
    frequence_mois: Optional[int] = None
    date_prochaine: Optional[date] = None
    cout_estime_xaf: Optional[float] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class IspsRecordCreate(BaseModel):
    reference: str
    niveau_isps: Optional[str] = None
    date_application: Optional[datetime] = None
    motif: Optional[str] = None
    authorite_emetteuse: Optional[str] = None
    date_levee: Optional[datetime] = None


class IspsRecordUpdate(BaseModel):
    reference: Optional[str] = None
    niveau_isps: Optional[str] = None
    date_application: Optional[datetime] = None
    motif: Optional[str] = None
    authorite_emetteuse: Optional[str] = None
    date_levee: Optional[datetime] = None
    is_active: Optional[bool] = None


class IspsRecordOut(BaseModel):
    id: int
    company_id: int
    reference: str
    niveau_isps: Optional[str] = None
    date_application: Optional[datetime] = None
    motif: Optional[str] = None
    authorite_emetteuse: Optional[str] = None
    date_levee: Optional[datetime] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class PortPerceptionCreate(BaseModel):
    code_perception: str
    intitule: Optional[str] = None
    type_perception: Optional[str] = None
    base_calcul: Optional[str] = None
    tarif_xaf: Optional[float] = None
    unite: Optional[str] = None
    arrete_reference: Optional[str] = None
    date_application: Optional[date] = None


class PortPerceptionUpdate(BaseModel):
    code_perception: Optional[str] = None
    intitule: Optional[str] = None
    type_perception: Optional[str] = None
    base_calcul: Optional[str] = None
    tarif_xaf: Optional[float] = None
    unite: Optional[str] = None
    arrete_reference: Optional[str] = None
    date_application: Optional[date] = None
    is_active: Optional[bool] = None


class PortPerceptionOut(BaseModel):
    id: int
    company_id: int
    code_perception: str
    intitule: Optional[str] = None
    type_perception: Optional[str] = None
    base_calcul: Optional[str] = None
    tarif_xaf: Optional[float] = None
    unite: Optional[str] = None
    arrete_reference: Optional[str] = None
    date_application: Optional[date] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class AnnualActivityReportCreate(BaseModel):
    reference: str
    annee: Optional[int] = None
    tonnage_traite_t: Optional[float] = None
    nb_escales: Optional[int] = None
    nb_conteneurs_evp: Optional[int] = None
    recettes_xaf: Optional[float] = None
    statut: Optional[str] = None


class AnnualActivityReportUpdate(BaseModel):
    reference: Optional[str] = None
    annee: Optional[int] = None
    tonnage_traite_t: Optional[float] = None
    nb_escales: Optional[int] = None
    nb_conteneurs_evp: Optional[int] = None
    recettes_xaf: Optional[float] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class AnnualActivityReportOut(BaseModel):
    id: int
    company_id: int
    reference: str
    annee: Optional[int] = None
    tonnage_traite_t: Optional[float] = None
    nb_escales: Optional[int] = None
    nb_conteneurs_evp: Optional[int] = None
    recettes_xaf: Optional[float] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class SigLayerCreate(BaseModel):
    code_couche: str
    nom: Optional[str] = None
    type_couche: Optional[str] = None
    projection: Optional[str] = None
    date_maj: Optional[date] = None
    superficie_ha: Optional[float] = None


class SigLayerUpdate(BaseModel):
    code_couche: Optional[str] = None
    nom: Optional[str] = None
    type_couche: Optional[str] = None
    projection: Optional[str] = None
    date_maj: Optional[date] = None
    superficie_ha: Optional[float] = None
    is_active: Optional[bool] = None


class SigLayerOut(BaseModel):
    id: int
    company_id: int
    code_couche: str
    nom: Optional[str] = None
    type_couche: Optional[str] = None
    projection: Optional[str] = None
    date_maj: Optional[date] = None
    superficie_ha: Optional[float] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class DomainArchiveCreate(BaseModel):
    cote_archive: str
    titre: Optional[str] = None
    type_piece: Optional[str] = None
    periode_couverte: Optional[str] = None
    localisation: Optional[str] = None
    duree_conservation_an: Optional[int] = None
    statut: Optional[str] = None


class DomainArchiveUpdate(BaseModel):
    cote_archive: Optional[str] = None
    titre: Optional[str] = None
    type_piece: Optional[str] = None
    periode_couverte: Optional[str] = None
    localisation: Optional[str] = None
    duree_conservation_an: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class DomainArchiveOut(BaseModel):
    id: int
    company_id: int
    cote_archive: str
    titre: Optional[str] = None
    type_piece: Optional[str] = None
    periode_couverte: Optional[str] = None
    localisation: Optional[str] = None
    duree_conservation_an: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class AmenagementKpiCreate(BaseModel):
    code_kpi: str
    intitule: Optional[str] = None
    periode: Optional[str] = None
    valeur: Optional[float] = None
    objectif: Optional[float] = None
    ecart_pct: Optional[float] = None
    statut: Optional[str] = None


class AmenagementKpiUpdate(BaseModel):
    code_kpi: Optional[str] = None
    intitule: Optional[str] = None
    periode: Optional[str] = None
    valeur: Optional[float] = None
    objectif: Optional[float] = None
    ecart_pct: Optional[float] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class AmenagementKpiOut(BaseModel):
    id: int
    company_id: int
    code_kpi: str
    intitule: Optional[str] = None
    periode: Optional[str] = None
    valeur: Optional[float] = None
    objectif: Optional[float] = None
    ecart_pct: Optional[float] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}

