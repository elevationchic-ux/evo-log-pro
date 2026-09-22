"""Pydantic schemas for Reporting module - Executive dashboard and multi-dimensional reporting for Cameroon/CEMAC"""
from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel


# Dashboard Executif schemas
class DashboardExecutifBase(BaseModel):
    code: str
    nom: str
    layout: dict
    widgets: dict
    filtres: dict


class DashboardExecutifCreate(DashboardExecutifBase):
    description: str = ""
    role_autorise: list = []
    proprietaire_id: int = None


class DashboardExecutifUpdate(BaseModel):
    description: Optional[str] = None
    role_autorise: Optional[list] = None
    actif: Optional[bool] = None


class DashboardExecutifResponse(DashboardExecutifBase):
    id: int
    description: Optional[str] = None
    role_autorise: Optional[list] = None
    proprietaire_id: Optional[int] = None
    actif: bool
    date_creation: datetime
    modifie_par: Optional[str] = None
    date_modification: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# KPI schemas
class KPIBase(BaseModel):
    code: str
    nom: str
    type_rapport: str
    categorie: str
    formule: str
    unite: str
    objectif: float


class KPICreate(KPIBase):
    description: str = ""
    seuil_alerte: float = 0.0
    couleur_alerte: str = "#FF0000"
    source_donnees: str = ""
    frequence_calcul: str = ""


class KPIUpdate(BaseModel):
    description: Optional[str] = None
    seuil_alerte: Optional[float] = None
    couleur_alerte: Optional[str] = None
    source_donnees: Optional[str] = None
    frequence_calcul: Optional[str] = None
    actif: Optional[bool] = None


class KPIResponse(KPIBase):
    id: int
    description: Optional[str] = None
    seuil_alerte: float
    couleur_alerte: str
    source_donnees: Optional[str] = None
    frequence_calcul: Optional[str] = None
    derniere_valeur: Optional[float] = None
    date_derniere_valeur: Optional[datetime] = None
    tendance: Optional[str] = None
    variation_pourcentage: Optional[float] = None
    historique: Optional[dict] = None
    actif: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Rapport schemas
class RapportBase(BaseModel):
    numero_rapport: str
    titre: str
    type_rapport: str
    frequence: str
    requetes: dict
    colonnes: dict


class RapportCreate(RapportBase):
    description: str = ""
    filtres: dict = {}
    parametres: dict = {}
    tri: dict = {}
    graphiques: dict = {}
    tables: dict = {}


class RapportUpdate(BaseModel):
    description: Optional[str] = None
    filtres: Optional[dict] = None
    parametres: Optional[dict] = None
    tri: Optional[dict] = None
    graphiques: Optional[dict] = None
    tables: Optional[dict] = None
    statut: Optional[str] = None
    date_expiration: Optional[datetime] = None


class RapportResponse(RapportBase):
    id: int
    description: Optional[str] = None
    filtres: Optional[dict] = None
    parametres: Optional[dict] = None
    tri: Optional[dict] = None
    graphiques: Optional[dict] = None
    tables: Optional[dict] = None
    statut: str
    cree_par: int
    date_creation: datetime
    date_generation: Optional[datetime] = None
    date_expiration: Optional[datetime] = None
    fichier: Optional[str] = None
    taille_octets: Optional[int] = None
    nombre_lignes: int
    duree_generation: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Export schemas
class ExportBase(BaseModel):
    numero_export: str
    rapport_id: int
    type_rapport: str
    format_export: str
    parametres: dict


class ExportCreate(ExportBase):
    utilisateur_id: int = None


class ExportUpdate(BaseModel):
    statut: Optional[str] = None
    progression: Optional[int] = None
    fichier: Optional[str] = None
    taille_octets: Optional[int] = None
    nombre_enregistrements: Optional[int] = None
    erreur: Optional[str] = None


class ExportResponse(ExportBase):
    id: int
    date_demande: datetime
    date_debut: Optional[datetime] = None
    date_fin: Optional[datetime] = None
    statut: str
    utilisateur_id: int
    progression: int
    fichier: Optional[str] = None
    taille_octets: Optional[int] = None
    nombre_enregistrements: int
    erreur: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Widget schemas
class WidgetBase(BaseModel):
    code: str
    nom: str
    type_widget: str
    type_rapport: str
    requete: str
    configuration: dict


class WidgetCreate(WidgetBase):
    couleurs: dict = {}
    filtres: dict = {}
    refresh_secondes: int = 300
    largeur: int = 6
    hauteur: int = 400
    position_x: int = 0
    position_y: int = 0


class WidgetUpdate(BaseModel):
    couleurs: Optional[dict] = None
    filtres: Optional[dict] = None
    refresh_secondes: Optional[int] = None
    largeur: Optional[int] = None
    hauteur: Optional[int] = None
    position_x: Optional[int] = None
    position_y: Optional[int] = None
    actif: Optional[bool] = None


class WidgetResponse(WidgetBase):
    id: int
    couleurs: Optional[dict] = None
    filtres: Optional[dict] = None
    refresh_secondes: int
    largeur: int
    hauteur: int
    position_x: int
    position_y: int
    actif: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Tableau Bord Operationnel schemas
class TableauBordOperationnelBase(BaseModel):
    code: str
    nom: str
    module: str
    metriques: dict
    graphiques: dict


class TableauBordOperationnelCreate(TableauBordOperationnelBase):
    alertes: dict = {}
    filtres: dict = {}
    responsable: str = ""


class TableauBordOperationnelUpdate(BaseModel):
    alertes: Optional[dict] = None
    filtres: Optional[dict] = None
    responsable: Optional[str] = None
    actif: Optional[bool] = None


class TableauBordOperationnelResponse(TableauBordOperationnelBase):
    id: int
    alertes: Optional[dict] = None
    filtres: Optional[dict] = None
    derniere_actualisation: Optional[datetime] = None
    responsable: Optional[str] = None
    actif: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Indicateur Financier schemas
class IndicateurFinancierBase(BaseModel):
    code: str
    nom: str
    categorie: str
    periode: str
    valeur_actuelle: float
    valeur_precedente: float
    objectif: float


class IndicateurFinancierCreate(IndicateurFinancierBase):
    pass


class IndicateurFinancierUpdate(BaseModel):
    valeur_actuelle: Optional[float] = None
    valeur_precedente: Optional[float] = None
    date_mesure: Optional[date] = None


class IndicateurFinancierResponse(IndicateurFinancierBase):
    id: int
    variation: float
    tendance: str
    unite: str
    devise: str
    date_mesure: date
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Indicateur Douanier schemas
class IndicateurDouanierBase(BaseModel):
    code: str
    nom: str
    categorie: str
    periode: str
    valeur_actuelle: float
    valeur_precedente: float
    objectif: float


class IndicateurDouanierCreate(IndicateurDouanierBase):
    pass


class IndicateurDouanierUpdate(BaseModel):
    valeur_actuelle: Optional[float] = None
    valeur_precedente: Optional[float] = None
    date_mesure: Optional[date] = None


class IndicateurDouanierResponse(IndicateurDouanierBase):
    id: int
    variation: float
    tendance: str
    unite: str
    date_mesure: date
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Rapports consolidés
class RapportExecutifResponse(BaseModel):
    kpis: list
    nombre_kpis: int
    k_par_type: dict


class RapportFinancierResponse(BaseModel):
    periode: str
    indicateurs: list


class RapportDouanierResponse(BaseModel):
    periode: str
    indicateurs: list
