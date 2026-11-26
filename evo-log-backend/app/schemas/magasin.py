"""
Magasin schemas for warehouse and inventory management
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class MouvementType(str, Enum):
    """Enumeration for stock movement types"""
    ENTREE = "entree"
    SORTIE = "sortie"
    TRANSFERT = "transfert"
    INVENTAIRE = "inventaire"
    AJUSTEMENT = "ajustement"


class StockBase(BaseModel):
    """Base stock schema"""
    code_article: str = Field(..., min_length=2, max_length=50)
    designation: str = Field(..., min_length=2, max_length=200)
    description: Optional[str] = None
    categorie: Optional[str] = None
    unite_mesure: Optional[str] = None
    quantite_disponible: float = 0
    quantite_reservee: float = 0
    quantite_minimum: Optional[float] = None
    quantite_maximum: Optional[float] = None
    prix_unitaire: Optional[float] = None
    emplacement: Optional[str] = None
    entrepot_id: Optional[int] = None
    fournisseur_id: Optional[int] = None
    is_active: bool = True


class StockCreate(StockBase):
    """Schema for stock creation"""
    pass


class StockUpdate(BaseModel):
    """Schema for stock update"""
    designation: Optional[str] = None
    description: Optional[str] = None
    categorie: Optional[str] = None
    unite_mesure: Optional[str] = None
    quantite_minimum: Optional[float] = None
    quantite_maximum: Optional[float] = None
    prix_unitaire: Optional[float] = None
    emplacement: Optional[str] = None
    entrepot_id: Optional[int] = None
    fournisseur_id: Optional[int] = None
    is_active: Optional[bool] = None


class StockResponse(StockBase):
    """Schema for stock response"""
    id: int
    date_derniere_entree: Optional[datetime] = None
    date_derniere_sortie: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class MouvementStockBase(BaseModel):
    """Base stock movement schema"""
    stock_id: Optional[int] = None
    type_mouvement: MouvementType
    quantite: float = Field(..., gt=0)
    quantite_avant: Optional[float] = None
    quantite_apres: Optional[float] = None
    prix_unitaire: Optional[float] = None
    valeur_totale: Optional[float] = None
    raison: Optional[str] = None
    document_reference: Optional[str] = None
    destination: Optional[str] = None
    operateur_id: Optional[int] = None
    notes: Optional[str] = None


class MouvementStockCreate(MouvementStockBase):
    """Schema for stock movement creation"""
    pass


class MouvementStockResponse(MouvementStockBase):
    """Schema for stock movement response"""
    id: int
    reference: str
    date_mouvement: datetime
    
    class Config:
        from_attributes = True


class EntrepotBase(BaseModel):
    """Base warehouse schema"""
    code: str = Field(..., min_length=2, max_length=20)
    nom: str = Field(..., min_length=2, max_length=100)
    adresse: Optional[str] = None
    ville: Optional[str] = None
    telephone: Optional[str] = None
    responsable: Optional[str] = None
    capacite: Optional[float] = None
    superficie: Optional[float] = None
    is_active: bool = True


class EntrepotCreate(EntrepotBase):
    """Schema for warehouse creation"""
    pass


class EntrepotResponse(EntrepotBase):
    """Schema for warehouse response"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True