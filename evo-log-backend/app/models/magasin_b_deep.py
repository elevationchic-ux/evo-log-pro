"""Modeles magasin-stock (expansion approfondie generee).

2 entites de gestion, chacune scoped par company_id.
Convention d'honnetete : aucune valeur par defaut, NULL = "non enregistre".
"""
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean, Float,
    ForeignKey, Date, Numeric, UniqueConstraint, Enum as SAEnum,
)
from sqlalchemy.sql import func
import enum

from app.core.database import Base


def _enum(cls):
    return SAEnum(cls, native_enum=False, create_constraint=False,
                  values_callable=lambda x: [e.value for e in x])


# ─── Enums ────────────────────────────────────────────────────────────────────

class MagasinbStockCount_statut(str, enum.Enum):
    PLANIFIE = "planifie"
    EN_COURS = "en_cours"
    VALIDE = "valide"
    ECART_CONSTATE = "ecart_constate"


class MagasinbGoodsReceipt_statut(str, enum.Enum):
    EN_ATTENTE = "en_attente"
    PARTIEL = "partiel"
    COMPLETE = "complete"
    REFUSEE = "refusee"


# ─── Modeles ──────────────────────────────────────────────────────────────────

class MagasinbStockCount(Base):
    """Comptages d'inventaire."""
    __tablename__ = "magasinb_stock_counts"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_magasinb_stock_count_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    article = Column(String(150), nullable=True)
    emplacement = Column(String(150), nullable=True)
    quantite_theorique = Column(Integer, nullable=True)
    quantite_physique = Column(Integer, nullable=True)
    ecart = Column(Integer, nullable=True)
    date_inventaire = Column(Date, nullable=True)
    agent = Column(String(150), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class MagasinbGoodsReceipt(Base):
    """Receptions marchandise."""
    __tablename__ = "magasinb_goods_receipts"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_magasinb_goods_recei_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    bon_commande = Column(String(150), nullable=True)
    fournisseur = Column(String(150), nullable=True)
    date_reception = Column(DateTime(timezone=True), nullable=True)
    nb_articles = Column(Integer, nullable=True)
    quantite_recue = Column(Integer, nullable=True)
    controles_fait = Column(Boolean, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

