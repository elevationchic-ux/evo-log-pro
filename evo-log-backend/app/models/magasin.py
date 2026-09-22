"""
Magasin models for warehouse and inventory management
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, Enum, Numeric, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class MouvementType(str, enum.Enum):
    """Enumeration for stock movement types"""
    ENTREE = "entree"
    SORTIE = "sortie"
    TRANSFERT = "transfert"
    INVENTAIRE = "inventaire"
    AJUSTEMENT = "ajustement"


class Stock(Base):
    """Stock/Inventory item model"""
    __tablename__ = "stocks"
    __table_args__ = (
        UniqueConstraint('company_id', 'code_article', name='uix_stock_company_code'),
    )
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=True, index=True)
    code_article = Column(String(50), nullable=False, index=True)
    designation = Column(String(200), nullable=False)
    description = Column(Text)
    categorie = Column(String(50))
    unite_mesure = Column(String(20))  # e.g., "unite", "kg", "litre", "metre"
    quantite_disponible = Column(Numeric, default=0)
    quantite_reservee = Column(Numeric, default=0)
    quantite_minimum = Column(Numeric)
    quantite_maximum = Column(Numeric)
    prix_unitaire = Column(Numeric)
    emplacement = Column(String(100))
    entrepot_id = Column(Integer, ForeignKey('entrepots.id'))
    fournisseur_id = Column(Integer, ForeignKey('fournisseurs.id'))
    date_derniere_entree = Column(DateTime(timezone=True))
    date_derniere_sortie = Column(DateTime(timezone=True))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    mouvements = relationship("MouvementStock", back_populates="stock")
    entrepot = relationship("Entrepot", back_populates="stocks")


class MouvementStock(Base):
    """Stock movement model for tracking inventory changes"""
    __tablename__ = "mouvements_stocks"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_mouvement_company_ref'),
    )
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=True, index=True)
    reference = Column(String(50), nullable=False, index=True)
    stock_id = Column(Integer, ForeignKey('stocks.id'))
    type_mouvement = Column(Enum(MouvementType), nullable=False)
    quantite = Column(Numeric, nullable=False)
    quantite_avant = Column(Numeric)
    quantite_apres = Column(Numeric)
    prix_unitaire = Column(Numeric)
    valeur_totale = Column(Numeric)
    raison = Column(String(200))
    document_reference = Column(String(50))  # e.g., bon de livraison, bon de sortie
    destination = Column(String(100))
    operateur_id = Column(Integer, ForeignKey('users.id'))
    date_mouvement = Column(DateTime(timezone=True), server_default=func.now())
    notes = Column(Text)
    
    # Relationships
    stock = relationship("Stock", back_populates="mouvements")


class Entrepot(Base):
    """Warehouse model"""
    __tablename__ = "entrepots"
    __table_args__ = (
        UniqueConstraint('company_id', 'code', name='uix_entrepot_company_code'),
    )
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=True, index=True)
    code = Column(String(20), nullable=False, index=True)
    nom = Column(String(100), nullable=False)
    adresse = Column(Text)
    ville = Column(String(50))
    telephone = Column(String(20))
    responsable = Column(String(100))
    capacite = Column(Numeric)
    superficie = Column(Numeric)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    stocks = relationship("Stock", back_populates="entrepot")