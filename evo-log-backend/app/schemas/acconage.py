"""Pydantic schemas for Acconage module - Complete port operations"""
from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, Field


# Navire schemas
class NavireBase(BaseModel):
    nom: str
    imo: Optional[str] = None
    pavillon: Optional[str] = None
    type_navire: Optional[str] = None
    longueur: Optional[float] = None
    largeur: Optional[float] = None
    tirant_eau: Optional[float] = None
    port_en_lourd: Optional[float] = None
    deadweight: Optional[float] = None
    annee_construction: Optional[int] = None
    proprietaire: Optional[str] = None
    armateur: Optional[str] = None


class NavireCreate(NavireBase):
    pass


class NavireResponse(NavireBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Escale schemas
class EscaleBase(BaseModel):
    navire_id: int
    port_id: int
    poste_quai: Optional[str] = None
    date_arrivee_prevue: Optional[datetime] = None
    date_arrivee_reelle: Optional[datetime] = None
    date_depart_prevue: Optional[datetime] = None
    date_depart_reelle: Optional[datetime] = None
    marchandise: Optional[str] = None
    tonnage: Optional[float] = None
    nombre_conteneurs: Optional[int] = None
    agent: Optional[str] = None
    notes: Optional[str] = None


class EscaleCreate(EscaleBase):
    numero_escale: str


class EscaleUpdate(BaseModel):
    date_arrivee_reelle: Optional[datetime] = None
    date_depart_reelle: Optional[datetime] = None
    statut: Optional[str] = None


class EscaleResponse(EscaleBase):
    id: int
    numero_escale: str
    statut: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Stowage Plan schemas
class StowagePlanBase(BaseModel):
    navire_id: int
    voyage_id: str
    plan_pdf: str


class StowagePlanCreate(StowagePlanBase):
    valide_par: int


class StowagePlanResponse(StowagePlanBase):
    id: int
    valide: bool
    valide_par: Optional[int] = None
    date_creation: datetime
    
    class Config:
        from_attributes = True


class PositionConteneurBase(BaseModel):
    stowage_plan_id: int
    conteneur_id: int
    bay: int
    row: int
    tier: int
    poids: float
    type_marchandise: str
    port_dechargement: str
    dangereux: bool = False
    classe_imdg: Optional[str] = None
    reefer: bool = False
    temperature: Optional[float] = None


class PositionConteneurCreate(PositionConteneurBase):
    pass


class PositionConteneurResponse(PositionConteneurBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Grue schemas
class GrueBase(BaseModel):
    code: str
    type_grue: str
    capacite_tonnes: float
    portee_metres: float
    hauteur_metres: float
    poste_quai: str


class GrueCreate(GrueBase):
    pass


class GrueUpdate(BaseModel):
    statut: Optional[str] = None
    date_maintenance: Optional[date] = None
    prochaine_maintenance: Optional[date] = None
    operator_id: Optional[int] = None


class GrueResponse(GrueBase):
    id: int
    statut: str
    date_maintenance: Optional[date] = None
    prochaine_maintenance: Optional[date] = None
    operator_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ReservationGrueBase(BaseModel):
    grue_id: int
    operation_id: int
    date_debut: datetime
    date_fin: datetime


class ReservationGrueCreate(ReservationGrueBase):
    pass


class ReservationGrueResponse(ReservationGrueBase):
    id: int
    statut: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# Remorqueur schemas
class RemorqueurBase(BaseModel):
    nom: str
    puissance_cv: int
    longueur: float
    port_id: int


class RemorqueurCreate(RemorqueurBase):
    pass


class RemorqueurUpdate(BaseModel):
    statut: Optional[str] = None
    capitaine_id: Optional[int] = None


class RemorqueurResponse(RemorqueurBase):
    id: int
    statut: str
    capitaine_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class AmarageBase(BaseModel):
    escale_id: int
    remorqueur_id: int
    type_amarage: str
    date_debut: datetime
    date_fin: datetime


class AmarageCreate(AmarageBase):
    pass


class AmarageResponse(AmarageBase):
    id: int
    duree_heures: float
    cout: float
    notes: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# Conteneur schemas
class ConteneurBase(BaseModel):
    numero: str
    type_conteneur: str
    statut: str
    tare_weight: float
    gross_weight: float
    navire_id: Optional[int] = None
    scelle: Optional[str] = None


class ConteneurCreate(ConteneurBase):
    pass


class ConteneurUpdate(BaseModel):
    statut: Optional[str] = None
    certificat_origine: Optional[str] = None
    inspection_phasanitaire: Optional[bool] = None


class ConteneurResponse(ConteneurBase):
    id: int
    net_weight: float
    date_scelle: Optional[date] = None
    inspection_phasanitaire: bool
    date_inspection: Optional[date] = None
    certificat_origine: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Connaissement schemas
class ConnaissementBase(BaseModel):
    numero_bl: str
    conteneur_id: int
    type_bl: str
    chargeur: str
    destinataire: str
    port_embarquement: str
    port_dechargement: str
    montant_freight: float


class ConnaissementCreate(ConnaissementBase):
    escale_id: Optional[int] = None


class ConnaissementUpdate(BaseModel):
    statut: Optional[str] = None
    signe_par: Optional[str] = None


class ConnaissementResponse(ConnaissementBase):
    id: int
    date_emission: date
    devise: str
    signe_par: Optional[str] = None
    statut: str
    escale_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Packing List schemas
class PackingListBase(BaseModel):
    numero_pl: str
    conteneur_id: int
    marchandise: str
    description: str
    nombre_colis: int
    type_colis: str
    poids_net: float
    poids_brut: float
    marque: str
    pays_origine: str


class PackingListCreate(PackingListBase):
    connaissement_id: Optional[int] = None


class PackingListResponse(PackingListBase):
    id: int
    volume_m3: float
    numero_serie: Optional[str] = None
    date_emission: date
    connaissement_id: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# Manifeste schemas
class ManifesteBase(BaseModel):
    numero_manifeste: str
    escale_id: int
    type_manifeste: str
    navire: str
    voyage: str
    port_provenance: str
    port_destination: str
    nombre_conteneurs: int
    tonnage_total: float
    valeur_marchandise: float


class ManifesteCreate(ManifesteBase):
    pass


class ManifesteUpdate(BaseModel):
    conforme: Optional[bool] = None
    controle_par: Optional[int] = None
    observations: Optional[str] = None


class ManifesteResponse(ManifesteBase):
    id: int
    devise: str
    signe_par: Optional[str] = None
    date_signature: Optional[date] = None
    conforme: bool
    controle_par: Optional[int] = None
    date_controle: Optional[datetime] = None
    observations: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Marchandise Dangereuse schemas
class MarchandiseDangereuseBase(BaseModel):
    manifeste_id: int
    conteneur_id: int
    classe_imdg: str
    numero_onu: str
    designation: str
    groupe_emballage: str
    etiquette: str
    quantite: float
    emplacement: str


class MarchandiseDangereuseCreate(MarchandiseDangereuseBase):
    unite: str = "kg"
    mesures_speciales: Optional[str] = None


class MarchandiseDangereuseResponse(MarchandiseDangereuseBase):
    id: int
    unite: str
    mesures_speciales: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# Surestarie schemas
class SurestarieBase(BaseModel):
    conteneur_id: int
    date_debut: date
    date_fin: date
    taux_journalier: float = 5000.0


class SurestarieCreate(SurestarieBase):
    connaissement_id: Optional[int] = None


class SurestarieUpdate(BaseModel):
    statut: Optional[str] = None
    reference_facture: Optional[str] = None
    date_paiement: Optional[date] = None


class SurestarieResponse(SurestarieBase):
    id: int
    nombre_jours: int
    montant_total: float
    devise: str
    statut: str
    connaissement_id: Optional[int] = None
    reference_facture: Optional[str] = None
    date_paiement: Optional[date] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# THC schemas
class THCBase(BaseModel):
    conteneur_id: int
    type_operation: str
    type_conteneur: str
    montant: float


class THCCreate(THCBase):
    pass


class THCUpdate(BaseModel):
    statut: Optional[str] = None
    facture_reference: Optional[str] = None


class THCResponse(THCBase):
    id: int
    devise: str
    date_application: date
    facture_reference: Optional[str] = None
    statut: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Nettoyage Cale schemas
class NettoyageCaleBase(BaseModel):
    navire_id: int
    escale_id: int
    cale_numero: str
    type_nettoyage: str
    equipe: str


class NettoyageCaleCreate(NettoyageCaleBase):
    pass


class NettoyageCaleUpdate(BaseModel):
    date_fin: Optional[datetime] = None
    conforme: Optional[bool] = None
    inspecteur_id: Optional[int] = None
    observations: Optional[str] = None


class NettoyageCaleResponse(NettoyageCaleBase):
    id: int
    date_debut: datetime
    date_fin: Optional[datetime] = None
    equipement: Optional[str] = None
    conforme: bool
    inspecteur_id: Optional[int] = None
    date_inspection: Optional[datetime] = None
    observations: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# Rapport Escale
class RapportEscaleResponse(BaseModel):
    escale: dict
    operations: dict
    surestaries: dict


# Operation Acconage schemas
class OperationAcconageCreate(BaseModel):
    numero_operation: str
    navire_id: int
    type_operation: str
    date_debut: datetime
    date_fin_prevue: Optional[datetime] = None
    nombre_conteneurs: int = 0
    statut: str = "en_cours"
    observations: Optional[str] = None


class OperationAcconageResponse(BaseModel):
    id: int
    numero_operation: str
    navire_id: int
    type_operation: str
    date_debut: datetime
    date_fin_prevue: Optional[datetime] = None
    date_fin_effective: Optional[datetime] = None
    nombre_conteneurs: int
    statut: str
    observations: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
