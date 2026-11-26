"""Schemas Pydantic pour reports-bi (genere)."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date


class RptcScheduledReportCreate(BaseModel):
    reference: str
    nom: Optional[str] = None
    frequence: Optional[str] = None
    format: Optional[str] = None
    destinataires: Optional[str] = None
    prochaine_execution: Optional[datetime] = None
    statut: Optional[str] = None


class RptcScheduledReportUpdate(BaseModel):
    reference: Optional[str] = None
    nom: Optional[str] = None
    frequence: Optional[str] = None
    format: Optional[str] = None
    destinataires: Optional[str] = None
    prochaine_execution: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class RptcScheduledReportOut(BaseModel):
    id: int
    company_id: int
    reference: str
    nom: Optional[str] = None
    frequence: Optional[str] = None
    format: Optional[str] = None
    destinataires: Optional[str] = None
    prochaine_execution: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class RptcReportTemplateCreate(BaseModel):
    reference: str
    nom: Optional[str] = None
    categorie: Optional[str] = None
    source_donnees: Optional[str] = None
    version: Optional[str] = None
    nb_blocs: Optional[int] = None
    statut: Optional[str] = None


class RptcReportTemplateUpdate(BaseModel):
    reference: Optional[str] = None
    nom: Optional[str] = None
    categorie: Optional[str] = None
    source_donnees: Optional[str] = None
    version: Optional[str] = None
    nb_blocs: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class RptcReportTemplateOut(BaseModel):
    id: int
    company_id: int
    reference: str
    nom: Optional[str] = None
    categorie: Optional[str] = None
    source_donnees: Optional[str] = None
    version: Optional[str] = None
    nb_blocs: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class RptcDataExportCreate(BaseModel):
    reference: str
    libelle: Optional[str] = None
    module_source: Optional[str] = None
    format: Optional[str] = None
    filtres: Optional[str] = None
    lignes_exportees: Optional[int] = None
    demandeur: Optional[str] = None
    date_export: Optional[datetime] = None
    statut: Optional[str] = None


class RptcDataExportUpdate(BaseModel):
    reference: Optional[str] = None
    libelle: Optional[str] = None
    module_source: Optional[str] = None
    format: Optional[str] = None
    filtres: Optional[str] = None
    lignes_exportees: Optional[int] = None
    demandeur: Optional[str] = None
    date_export: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class RptcDataExportOut(BaseModel):
    id: int
    company_id: int
    reference: str
    libelle: Optional[str] = None
    module_source: Optional[str] = None
    format: Optional[str] = None
    filtres: Optional[str] = None
    lignes_exportees: Optional[int] = None
    demandeur: Optional[str] = None
    date_export: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class RptcAdHocQueryCreate(BaseModel):
    reference: str
    titre: Optional[str] = None
    source_donnees: Optional[str] = None
    dimensions: Optional[str] = None
    auteur: Optional[str] = None
    derniere_execution: Optional[datetime] = None
    partage: Optional[bool] = None
    statut: Optional[str] = None


class RptcAdHocQueryUpdate(BaseModel):
    reference: Optional[str] = None
    titre: Optional[str] = None
    source_donnees: Optional[str] = None
    dimensions: Optional[str] = None
    auteur: Optional[str] = None
    derniere_execution: Optional[datetime] = None
    partage: Optional[bool] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class RptcAdHocQueryOut(BaseModel):
    id: int
    company_id: int
    reference: str
    titre: Optional[str] = None
    source_donnees: Optional[str] = None
    dimensions: Optional[str] = None
    auteur: Optional[str] = None
    derniere_execution: Optional[datetime] = None
    partage: Optional[bool] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class RptcOlapCubeCreate(BaseModel):
    reference: str
    nom: Optional[str] = None
    source: Optional[str] = None
    dimensions: Optional[str] = None
    mesures: Optional[str] = None
    nb_lignes: Optional[int] = None
    date_dernier_refresh: Optional[datetime] = None
    statut: Optional[str] = None


class RptcOlapCubeUpdate(BaseModel):
    reference: Optional[str] = None
    nom: Optional[str] = None
    source: Optional[str] = None
    dimensions: Optional[str] = None
    mesures: Optional[str] = None
    nb_lignes: Optional[int] = None
    date_dernier_refresh: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class RptcOlapCubeOut(BaseModel):
    id: int
    company_id: int
    reference: str
    nom: Optional[str] = None
    source: Optional[str] = None
    dimensions: Optional[str] = None
    mesures: Optional[str] = None
    nb_lignes: Optional[int] = None
    date_dernier_refresh: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}

