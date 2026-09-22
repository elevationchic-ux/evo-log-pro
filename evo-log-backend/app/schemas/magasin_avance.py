"""Pydantic schemas for advanced warehouse module"""
from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, Field


# Peremption schemas
class PeremptionBase(BaseModel):
    date_peremption: date
    lot_numero: str
    numero_serie: Optional[str] = None


class PeremptionCreate(PeremptionBase):
    stock_id: int


class PeremptionResponse(PeremptionBase):
    id: int
    stock_id: int
    
    class Config:
        from_attributes = True


# ReservationStock schemas
class ReservationStockBase(BaseModel):
    stock_id: int
    type_reservation: str
    reference_id: int
    quantite: float
    date_expiration: Optional[date] = None


class ReservationStockCreate(ReservationStockBase):
    pass


class ReservationStockResponse(ReservationStockBase):
    id: int
    date_reservation: datetime
    statut: str
    date_liberation: Optional[datetime] = None
    date_consommation: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# KitArticle schemas
class KitArticleBase(BaseModel):
    article_kit_id: int
    nom_kit: str
    description: str


class KitArticleCreate(KitArticleBase):
    pass


class KitArticleResponse(KitArticleBase):
    id: int
    
    class Config:
        from_attributes = True


class ComposantKitBase(BaseModel):
    kit_id: int
    article_composant_id: int
    quantite: float


class ComposantKitCreate(ComposantKitBase):
    pass


class ComposantKitResponse(ComposantKitBase):
    id: int
    
    class Config:
        from_attributes = True


# EmplacementDetail schemas
class EmplacementDetailBase(BaseModel):
    entrepot_id: int
    zone: str
    allee: str
    rack: Optional[str] = None
    casier: Optional[str] = None
    niveau: Optional[str] = None


class EmplacementDetailCreate(EmplacementDetailBase):
    pass


class EmplacementDetailResponse(EmplacementDetailBase):
    id: int
    
    class Config:
        from_attributes = True


# TransfertStock schemas
class TransfertStockBase(BaseModel):
    stock_id: int
    entrepot_source_id: int
    entrepot_destination_id: int
    quantite: float
    motif: str
    date_transfert: Optional[date] = None


class TransfertStockCreate(TransfertStockBase):
    pass


class TransfertStockResponse(TransfertStockBase):
    id: int
    statut: str
    date_execution: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# InventaireTournant schemas
class InventaireTournantBase(BaseModel):
    entrepot_id: int
    date_inventaire: date
    type_inventaire: str = "tournant"


class InventaireTournantCreate(InventaireTournantBase):
    pass


class InventaireTournantResponse(InventaireTournantBase):
    id: int
    statut: str
    validateur_id: Optional[int] = None
    date_validation: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class LigneInventaireBase(BaseModel):
    inventaire_id: int
    stock_id: int
    quantite_comptee: float
    compteur_id: int


class LigneInventaireCreate(LigneInventaireBase):
    pass


class LigneInventaireResponse(LigneInventaireBase):
    id: int
    quantite_theorique: float
    ecart: float
    date_comptage: datetime
    
    class Config:
        from_attributes = True


# FournisseurStock schemas
class FournisseurStockBase(BaseModel):
    fournisseur_id: int
    delai_livraison_jours: int
    qualite: str = "standard"
    fiabilite: float = 100.0


class FournisseurStockCreate(FournisseurStockBase):
    pass


class FournisseurStockResponse(FournisseurStockBase):
    id: int
    
    class Config:
        from_attributes = True


# CommandeFournisseur schemas
class CommandeFournisseurBase(BaseModel):
    fournisseur_id: int
    reference: str
    date_commande: date
    date_prevue: date
    statut: str = "en_attente"


class CommandeFournisseurCreate(CommandeFournisseurBase):
    pass


class CommandeFournisseurResponse(CommandeFournisseurBase):
    id: int
    date_livraison: Optional[date] = None
    
    class Config:
        from_attributes = True


class LigneCommandeFournisseurBase(BaseModel):
    commande_id: int
    article_id: int
    quantite_commandee: float
    prix_unitaire: float


class LigneCommandeFournisseurCreate(LigneCommandeFournisseurBase):
    pass


class LigneCommandeFournisseurResponse(LigneCommandeFournisseurBase):
    id: int
    quantite_recue: Optional[float] = None
    
    class Config:
        from_attributes = True


# BonReception schemas
class BonReceptionBase(BaseModel):
    commande_id: int
    fournisseur_id: int
    date_reception: date
    statut: str = "en_cours"


class BonReceptionCreate(BonReceptionBase):
    pass


class BonReceptionResponse(BonReceptionBase):
    id: int
    date_validation: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class LigneBonReceptionBase(BaseModel):
    bon_id: int
    article_id: int
    quantite_recue: float
    quantite_commandee: float
    emplacement_id: Optional[int] = None


class LigneBonReceptionCreate(LigneBonReceptionBase):
    pass


class LigneBonReceptionResponse(LigneBonReceptionBase):
    id: int
    
    class Config:
        from_attributes = True


# BonSortie schemas
class BonSortieBase(BaseModel):
    destinataire_id: int
    type_sortie: str
    date_sortie: date
    statut: str = "en_cours"


class BonSortieCreate(BonSortieBase):
    pass


class BonSortieResponse(BonSortieBase):
    id: int
    date_validation: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class LigneBonSortieBase(BaseModel):
    bon_id: int
    stock_id: int
    quantite: float


class LigneBonSortieCreate(LigneBonSortieBase):
    pass


class LigneBonSortieResponse(LigneBonSortieBase):
    id: int
    
    class Config:
        from_attributes = True


# RetourClient schemas
class RetourClientBase(BaseModel):
    client_id: int
    article_id: int
    quantite: float
    motif: str
    etat: str = "a_reparer"


class RetourClientCreate(RetourClientBase):
    pass


class RetourClientUpdate(BaseModel):
    action_effectuee: Optional[str] = None
    statut: Optional[str] = None


class RetourClientResponse(RetourClientBase):
    id: int
    date_retour: datetime
    action_effectuee: Optional[str] = None
    date_traitement: Optional[datetime] = None
    statut: str
    
    class Config:
        from_attributes = True


# LitigeTransporteur schemas
class LitigeTransporteurBase(BaseModel):
    transporteur_id: int
    type_litige: str
    description: str
    montant_reclame: Optional[float] = None


class LitigeTransporteurCreate(LitigeTransporteurBase):
    pass


class LitigeTransporteurUpdate(BaseModel):
    resolution: Optional[str] = None
    statut: Optional[str] = None


class LitigeTransporteurResponse(LitigeTransporteurBase):
    id: int
    date_litige: datetime
    resolution: Optional[str] = None
    date_resolution: Optional[datetime] = None
    statut: str
    
    class Config:
        from_attributes = True


# Colis schemas
class ColisBase(BaseModel):
    reference_colis: str
    poids: float
    dimensions: str
    contenu: str


class ColisCreate(ColisBase):
    pass


class ColisUpdate(BaseModel):
    code_barres: Optional[str] = None
    palette_id: Optional[str] = None


class ColisResponse(ColisBase):
    id: int
    code_barres: Optional[str] = None
    palette_id: Optional[str] = None
    date_creation: datetime
    date_etiquetage: Optional[datetime] = None
    date_palettisation: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# KPI Response schemas
class RotationStockResponse(BaseModel):
    article_id: int
    rotation: float


class PrecisionInventaireResponse(BaseModel):
    inventaire_id: int
    precision: float


class PerformanceFournisseurResponse(BaseModel):
    fournisseur_id: int
    note: float
    commandes: int
    taux_livraison: float
    delai_moyen_jours: float
