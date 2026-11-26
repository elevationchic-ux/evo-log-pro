"""Schemas Pydantic pour magasin-stock (genere)."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date


class MagasinbStockCountCreate(BaseModel):
    reference: str
    article: Optional[str] = None
    emplacement: Optional[str] = None
    quantite_theorique: Optional[int] = None
    quantite_physique: Optional[int] = None
    ecart: Optional[int] = None
    date_inventaire: Optional[date] = None
    agent: Optional[str] = None
    statut: Optional[str] = None


class MagasinbStockCountUpdate(BaseModel):
    reference: Optional[str] = None
    article: Optional[str] = None
    emplacement: Optional[str] = None
    quantite_theorique: Optional[int] = None
    quantite_physique: Optional[int] = None
    ecart: Optional[int] = None
    date_inventaire: Optional[date] = None
    agent: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class MagasinbStockCountOut(BaseModel):
    id: int
    company_id: int
    reference: str
    article: Optional[str] = None
    emplacement: Optional[str] = None
    quantite_theorique: Optional[int] = None
    quantite_physique: Optional[int] = None
    ecart: Optional[int] = None
    date_inventaire: Optional[date] = None
    agent: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class MagasinbGoodsReceiptCreate(BaseModel):
    reference: str
    bon_commande: Optional[str] = None
    fournisseur: Optional[str] = None
    date_reception: Optional[datetime] = None
    nb_articles: Optional[int] = None
    quantite_recue: Optional[int] = None
    controles_fait: Optional[bool] = None
    statut: Optional[str] = None


class MagasinbGoodsReceiptUpdate(BaseModel):
    reference: Optional[str] = None
    bon_commande: Optional[str] = None
    fournisseur: Optional[str] = None
    date_reception: Optional[datetime] = None
    nb_articles: Optional[int] = None
    quantite_recue: Optional[int] = None
    controles_fait: Optional[bool] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class MagasinbGoodsReceiptOut(BaseModel):
    id: int
    company_id: int
    reference: str
    bon_commande: Optional[str] = None
    fournisseur: Optional[str] = None
    date_reception: Optional[datetime] = None
    nb_articles: Optional[int] = None
    quantite_recue: Optional[int] = None
    controles_fait: Optional[bool] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}

