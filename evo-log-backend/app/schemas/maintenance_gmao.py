"""Pydantic schemas for Maintenance GMAO module - CMMS for Cameroon/CEMAC"""
from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel


# Ordre Maintenance schemas
class OrdreMaintenanceBase(BaseModel):
    numero_ordre: str
    equipement_id: int
    type_maintenance: str
    priorite: str
    description: str


class OrdreMaintenanceCreate(OrdreMaintenanceBase):
    date_planifiee: date
    duree_estimee: int = 0
    travaux: str = ""
    technicien_id: int


class OrdreMaintenanceUpdate(BaseModel):
    date_debut: Optional[datetime] = None
    date_fin: Optional[datetime] = None
    duree_reelle: Optional[int] = None
    travaux: Optional[str] = None
    statut: Optional[str] = None
    cout_pieces: Optional[float] = None
    cout_main_oeuvre: Optional[float] = None
    observations: Optional[str] = None
    validation_technicien: Optional[bool] = None
    date_validation: Optional[date] = None
    valide_par: Optional[str] = None


class OrdreMaintenanceResponse(OrdreMaintenanceBase):
    id: int
    date_creation: datetime
    date_planifiee: date
    date_debut: Optional[datetime] = None
    date_fin: Optional[datetime] = None
    duree_estimee: int
    duree_reelle: Optional[int] = None
    travaux: Optional[str] = None
    technicien_id: int
    statut: str
    cout_pieces: float
    cout_main_oeuvre: float
    cout_total: float
    devise: str
    observations: Optional[str] = None
    validation_technicien: bool
    date_validation: Optional[date] = None
    valide_par: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Equipement GMAO schemas
class EquipementGMAOBase(BaseModel):
    numero_serie: str
    designation: str
    type_equipement: str
    marque: str
    modele: str
    localisation: str


class EquipementGMAOCreate(EquipementGMAOBase):
    annee_fabrication: int = None
    date_mise_service: date = None
    departement: str = ""
    responsable: str = ""
    date_achat: date = None
    fournisseur: str = ""
    cout_achat: float = 0.0
    valeur_residuelle: float = 0.0
    duree_vie_estimee: int = 10
    description: str = ""
    caracteristiques: str = ""
    manuel_fabricant: str = ""
    manuel_maintenance: str = ""


class EquipementGMAOUpdate(BaseModel):
    annee_fabrication: Optional[int] = None
    date_mise_service: Optional[date] = None
    departement: Optional[str] = None
    responsable: Optional[str] = None
    statut: Optional[str] = None
    date_achat: Optional[date] = None
    fournisseur: Optional[str] = None
    cout_achat: Optional[float] = None
    valeur_residuelle: Optional[float] = None
    duree_vie_estimee: Optional[int] = None
    description: Optional[str] = None
    caracteristiques: Optional[str] = None
    manuel_fabricant: Optional[str] = None
    manuel_maintenance: Optional[str] = None


class EquipementGMAOResponse(EquipementGMAOBase):
    id: int
    annee_fabrication: Optional[int] = None
    date_mise_service: Optional[date] = None
    departement: Optional[str] = None
    responsable: Optional[str] = None
    statut: str
    date_achat: Optional[date] = None
    fournisseur: Optional[str] = None
    cout_achat: Optional[float] = None
    devise: str
    valeur_residuelle: Optional[float] = None
    duree_vie_estimee: int
    description: Optional[str] = None
    caracteristiques: Optional[str] = None
    manuel_fabricant: Optional[str] = None
    manuel_maintenance: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Plan Maintenance schemas
class PlanMaintenanceBase(BaseModel):
    numero_plan: str
    equipement_id: int
    type_maintenance: str
    frequence: str
    intervalle_jours: int
    date_debut: date


class PlanMaintenanceCreate(PlanMaintenanceBase):
    date_fin: date = None
    description: str = ""
    taches: str = ""
    duree_estimee: int = 0
    technicien_assigne: str = ""
    pieces_requises: str = ""


class PlanMaintenanceUpdate(BaseModel):
    date_fin: Optional[date] = None
    description: Optional[str] = None
    taches: Optional[str] = None
    duree_estimee: Optional[int] = None
    technicien_assigne: Optional[str] = None
    pieces_requises: Optional[str] = None
    statut: Optional[str] = None
    dernier_execution: Optional[date] = None
    prochaine_execution: Optional[date] = None


class PlanMaintenanceResponse(PlanMaintenanceBase):
    id: int
    date_fin: Optional[date] = None
    description: Optional[str] = None
    taches: Optional[str] = None
    duree_estimee: int
    technicien_assigne: Optional[str] = None
    pieces_requises: Optional[str] = None
    statut: str
    dernier_execution: Optional[date] = None
    prochaine_execution: Optional[date] = None
    nombre_executions: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Piece Rechange GMAO schemas
class PieceRechangeGMAOBase(BaseModel):
    reference: str
    designation: str
    equipement_id: int
    categorie: str
    prix_unitaire: float


class PieceRechangeGMAOCreate(PieceRechangeGMAOBase):
    marque: str = ""
    modele: str = ""
    description: str = ""
    stock_minimum: int = 0
    stock_actuel: int = 0
    stock_maximum: int = 0
    unite: str = ""
    fournisseur: str = ""
    reference_fournisseur: str = ""
    emplacement_stockage: str = ""
    date_achat: date = None
    date_expiration: date = None
    perissable: bool = False


class PieceRechangeGMAOUpdate(BaseModel):
    marque: Optional[str] = None
    modele: Optional[str] = None
    description: Optional[str] = None
    stock_minimum: Optional[int] = None
    stock_actuel: Optional[int] = None
    stock_maximum: Optional[int] = None
    unite: Optional[str] = None
    prix_unitaire: Optional[float] = None
    fournisseur: Optional[str] = None
    reference_fournisseur: Optional[str] = None
    emplacement_stockage: Optional[str] = None
    date_achat: Optional[date] = None
    date_expiration: Optional[date] = None
    perissable: Optional[bool] = None
    statut: Optional[str] = None


class PieceRechangeGMAOResponse(PieceRechangeGMAOBase):
    id: int
    marque: Optional[str] = None
    modele: Optional[str] = None
    description: Optional[str] = None
    stock_minimum: int
    stock_actuel: int
    stock_maximum: Optional[int] = None
    unite: Optional[str] = None
    devise: str
    fournisseur: Optional[str] = None
    reference_fournisseur: Optional[str] = None
    emplacement_stockage: Optional[str] = None
    date_achat: Optional[date] = None
    date_expiration: Optional[date] = None
    perissable: bool
    statut: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Calibration schemas
class CalibrationBase(BaseModel):
    numero_calibration: str
    equipement_id: int
    instrument: str
    date_calibration: date
    intervalle_mois: int


class CalibrationCreate(CalibrationBase):
    laboratoire: str = ""
    technicien: str = ""
    valeurs_avant: str = ""
    valeurs_apres: str = ""
    tolerance: str = ""
    resultat: str = ""
    actions: str = ""
    certificat: str = ""


class CalibrationUpdate(BaseModel):
    laboratoire: Optional[str] = None
    technicien: Optional[str] = None
    valeurs_avant: Optional[str] = None
    valeurs_apres: Optional[str] = None
    tolerance: Optional[str] = None
    resultat: Optional[str] = None
    actions: Optional[str] = None
    certificat: Optional[str] = None
    statut: Optional[str] = None


class CalibrationResponse(CalibrationBase):
    id: int
    date_prochaine: date
    laboratoire: Optional[str] = None
    technicien: Optional[str] = None
    valeurs_avant: Optional[str] = None
    valeurs_apres: Optional[str] = None
    tolerance: Optional[str] = None
    resultat: Optional[str] = None
    actions: Optional[str] = None
    certificat: Optional[str] = None
    statut: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Performance Equipement schemas
class PerformanceEquipementBase(BaseModel):
    equipement_id: int
    periode: str
    temps_fonctionnement: float
    temps_arret: float
    nombre_pannes: int
    temps_maintenance: float


class PerformanceEquipementCreate(PerformanceEquipementBase):
    cout_maintenance: float = 0.0
    observations: str = ""


class PerformanceEquipementResponse(PerformanceEquipementBase):
    id: int
    date_mesure: date
    mtbf: float
    mttr: float
    disponibilite: float
    taux_panne: float
    cout_maintenance: float
    devise: str
    observations: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Rapport Maintenance
class RapportMaintenanceResponse(BaseModel):
    equipement: dict
    maintenance: dict
