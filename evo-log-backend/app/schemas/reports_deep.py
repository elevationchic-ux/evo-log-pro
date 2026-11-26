"""Schemas Pydantic pour reports-bi (genere)."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date


class WarehouseTableCreate(BaseModel):
    code_table: str
    domaine: Optional[str] = None
    frequence_refresh: Optional[str] = None
    volume_lignes: Optional[int] = None
    dernier_refresh: Optional[datetime] = None
    statut: Optional[str] = None


class WarehouseTableUpdate(BaseModel):
    code_table: Optional[str] = None
    domaine: Optional[str] = None
    frequence_refresh: Optional[str] = None
    volume_lignes: Optional[int] = None
    dernier_refresh: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class WarehouseTableOut(BaseModel):
    id: int
    company_id: int
    code_table: str
    domaine: Optional[str] = None
    frequence_refresh: Optional[str] = None
    volume_lignes: Optional[int] = None
    dernier_refresh: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class ScorecardCreate(BaseModel):
    reference: str
    pole: Optional[str] = None
    periode: Optional[str] = None
    nb_kpis: Optional[int] = None
    score_global_pct: Optional[float] = None
    kpis_rouges: Optional[int] = None
    kpis_oranges: Optional[int] = None
    kpis_verts: Optional[int] = None


class ScorecardUpdate(BaseModel):
    reference: Optional[str] = None
    pole: Optional[str] = None
    periode: Optional[str] = None
    nb_kpis: Optional[int] = None
    score_global_pct: Optional[float] = None
    kpis_rouges: Optional[int] = None
    kpis_oranges: Optional[int] = None
    kpis_verts: Optional[int] = None
    is_active: Optional[bool] = None


class ScorecardOut(BaseModel):
    id: int
    company_id: int
    reference: str
    pole: Optional[str] = None
    periode: Optional[str] = None
    nb_kpis: Optional[int] = None
    score_global_pct: Optional[float] = None
    kpis_rouges: Optional[int] = None
    kpis_oranges: Optional[int] = None
    kpis_verts: Optional[int] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class IndustryBenchmarkCreate(BaseModel):
    reference: str
    indicateur: Optional[str] = None
    valeur_interne: Optional[float] = None
    valeur_benchmark: Optional[float] = None
    port_reference: Optional[str] = None
    source: Optional[str] = None
    ecart_pct: Optional[float] = None


class IndustryBenchmarkUpdate(BaseModel):
    reference: Optional[str] = None
    indicateur: Optional[str] = None
    valeur_interne: Optional[float] = None
    valeur_benchmark: Optional[float] = None
    port_reference: Optional[str] = None
    source: Optional[str] = None
    ecart_pct: Optional[float] = None
    is_active: Optional[bool] = None


class IndustryBenchmarkOut(BaseModel):
    id: int
    company_id: int
    reference: str
    indicateur: Optional[str] = None
    valeur_interne: Optional[float] = None
    valeur_benchmark: Optional[float] = None
    port_reference: Optional[str] = None
    source: Optional[str] = None
    ecart_pct: Optional[float] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class PredictiveModelCreate(BaseModel):
    reference: str
    nom_modele: Optional[str] = None
    type_modele: Optional[str] = None
    variable_predite: Optional[str] = None
    precision_pct: Optional[float] = None
    date_entrainement: Optional[datetime] = None
    statut: Optional[str] = None


class PredictiveModelUpdate(BaseModel):
    reference: Optional[str] = None
    nom_modele: Optional[str] = None
    type_modele: Optional[str] = None
    variable_predite: Optional[str] = None
    precision_pct: Optional[float] = None
    date_entrainement: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class PredictiveModelOut(BaseModel):
    id: int
    company_id: int
    reference: str
    nom_modele: Optional[str] = None
    type_modele: Optional[str] = None
    variable_predite: Optional[str] = None
    precision_pct: Optional[float] = None
    date_entrainement: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class CustomDashboardCreate(BaseModel):
    reference: str
    nom: Optional[str] = None
    proprietaire: Optional[str] = None
    nb_widgets: Optional[int] = None
    partage: Optional[str] = None
    frequence: Optional[str] = None
    actif: Optional[bool] = None


class CustomDashboardUpdate(BaseModel):
    reference: Optional[str] = None
    nom: Optional[str] = None
    proprietaire: Optional[str] = None
    nb_widgets: Optional[int] = None
    partage: Optional[str] = None
    frequence: Optional[str] = None
    actif: Optional[bool] = None
    is_active: Optional[bool] = None


class CustomDashboardOut(BaseModel):
    id: int
    company_id: int
    reference: str
    nom: Optional[str] = None
    proprietaire: Optional[str] = None
    nb_widgets: Optional[int] = None
    partage: Optional[str] = None
    frequence: Optional[str] = None
    actif: Optional[bool] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class ReportExportCreate(BaseModel):
    reference: str
    rapport_source: Optional[str] = None
    format: Optional[str] = None
    frequence: Optional[str] = None
    destinataires: Optional[str] = None
    dernier_envoi: Optional[datetime] = None
    statut: Optional[str] = None


class ReportExportUpdate(BaseModel):
    reference: Optional[str] = None
    rapport_source: Optional[str] = None
    format: Optional[str] = None
    frequence: Optional[str] = None
    destinataires: Optional[str] = None
    dernier_envoi: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class ReportExportOut(BaseModel):
    id: int
    company_id: int
    reference: str
    rapport_source: Optional[str] = None
    format: Optional[str] = None
    frequence: Optional[str] = None
    destinataires: Optional[str] = None
    dernier_envoi: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class KpiDefinitionCreate(BaseModel):
    code_kpi: str
    intitule: Optional[str] = None
    formule: Optional[str] = None
    unite: Optional[str] = None
    source: Optional[str] = None
    periodicite: Optional[str] = None
    responsable: Optional[str] = None
    actif: Optional[bool] = None


class KpiDefinitionUpdate(BaseModel):
    code_kpi: Optional[str] = None
    intitule: Optional[str] = None
    formule: Optional[str] = None
    unite: Optional[str] = None
    source: Optional[str] = None
    periodicite: Optional[str] = None
    responsable: Optional[str] = None
    actif: Optional[bool] = None
    is_active: Optional[bool] = None


class KpiDefinitionOut(BaseModel):
    id: int
    company_id: int
    code_kpi: str
    intitule: Optional[str] = None
    formule: Optional[str] = None
    unite: Optional[str] = None
    source: Optional[str] = None
    periodicite: Optional[str] = None
    responsable: Optional[str] = None
    actif: Optional[bool] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class DrillPathCreate(BaseModel):
    reference: str
    nom: Optional[str] = None
    niveau_1: Optional[str] = None
    niveau_2: Optional[str] = None
    niveau_3: Optional[str] = None
    actif: Optional[bool] = None


class DrillPathUpdate(BaseModel):
    reference: Optional[str] = None
    nom: Optional[str] = None
    niveau_1: Optional[str] = None
    niveau_2: Optional[str] = None
    niveau_3: Optional[str] = None
    actif: Optional[bool] = None
    is_active: Optional[bool] = None


class DrillPathOut(BaseModel):
    id: int
    company_id: int
    reference: str
    nom: Optional[str] = None
    niveau_1: Optional[str] = None
    niveau_2: Optional[str] = None
    niveau_3: Optional[str] = None
    actif: Optional[bool] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class CohortAnalysisCreate(BaseModel):
    reference: str
    nom_cohorte: Optional[str] = None
    criteres: Optional[str] = None
    taille: Optional[int] = None
    date_debut: Optional[date] = None
    taux_retention_m1_pct: Optional[float] = None
    taux_retention_m12_pct: Optional[float] = None


class CohortAnalysisUpdate(BaseModel):
    reference: Optional[str] = None
    nom_cohorte: Optional[str] = None
    criteres: Optional[str] = None
    taille: Optional[int] = None
    date_debut: Optional[date] = None
    taux_retention_m1_pct: Optional[float] = None
    taux_retention_m12_pct: Optional[float] = None
    is_active: Optional[bool] = None


class CohortAnalysisOut(BaseModel):
    id: int
    company_id: int
    reference: str
    nom_cohorte: Optional[str] = None
    criteres: Optional[str] = None
    taille: Optional[int] = None
    date_debut: Optional[date] = None
    taux_retention_m1_pct: Optional[float] = None
    taux_retention_m12_pct: Optional[float] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class AnomalyRecordCreate(BaseModel):
    reference: str
    indicateur: Optional[str] = None
    valeur_constatee: Optional[float] = None
    valeur_attendue: Optional[float] = None
    seuil_pct: Optional[float] = None
    date_detection: Optional[datetime] = None
    statut: Optional[str] = None


class AnomalyRecordUpdate(BaseModel):
    reference: Optional[str] = None
    indicateur: Optional[str] = None
    valeur_constatee: Optional[float] = None
    valeur_attendue: Optional[float] = None
    seuil_pct: Optional[float] = None
    date_detection: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class AnomalyRecordOut(BaseModel):
    id: int
    company_id: int
    reference: str
    indicateur: Optional[str] = None
    valeur_constatee: Optional[float] = None
    valeur_attendue: Optional[float] = None
    seuil_pct: Optional[float] = None
    date_detection: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class RegulatoryReportCreate(BaseModel):
    reference: str
    autorite: Optional[str] = None
    type_rapport: Optional[str] = None
    periode_debut: Optional[date] = None
    periode_fin: Optional[date] = None
    date_depot: Optional[date] = None
    statut: Optional[str] = None


class RegulatoryReportUpdate(BaseModel):
    reference: Optional[str] = None
    autorite: Optional[str] = None
    type_rapport: Optional[str] = None
    periode_debut: Optional[date] = None
    periode_fin: Optional[date] = None
    date_depot: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class RegulatoryReportOut(BaseModel):
    id: int
    company_id: int
    reference: str
    autorite: Optional[str] = None
    type_rapport: Optional[str] = None
    periode_debut: Optional[date] = None
    periode_fin: Optional[date] = None
    date_depot: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}

