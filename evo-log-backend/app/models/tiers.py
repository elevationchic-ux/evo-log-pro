"""
Tiers model for managing clients, suppliers, and partners
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class TiersType(str, enum.Enum):
    """Enumeration for different types of tiers"""
    CLIENT = "client"
    FOURNISSEUR = "fournisseur"
    PARTENAIRE = "partenaire"


class Tiers(Base):
    """Base Tiers model for all business partners"""
    __tablename__ = "tiers"
    __mapper_args__ = {
        "polymorphic_on": "type",
        "polymorphic_identity": "tiers"
    }
    
    id = Column(Integer, primary_key=True, index=True)
    # Isolation multi-tenant : porte toutes les lignes clients/fournisseurs/partenaires.
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=True, index=True)
    code = Column(String(20), unique=True, nullable=False, index=True)
    type = Column(Enum(TiersType), nullable=False)
    name = Column(String(100), nullable=False)
    legal_form = Column(String(50))
    tax_id = Column(String(50))  # Numéro contribuable
    contact_person = Column(String(100))
    email = Column(String(100))
    phone = Column(String(20))
    address = Column(Text)
    city = Column(String(50))
    country = Column(String(50), default="Cameroun")
    is_active = Column(Boolean, default=True)
    credit_limit = Column(Integer, default=0)
    balance = Column(Integer, default=0)
    payment_terms = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Self-referential relationship for parent/child companies
    parent_id = Column(Integer, ForeignKey('tiers.id'))
    parent = relationship("Tiers", remote_side=[id])


class Client(Tiers):
    """Client specific model"""
    __tablename__ = "clients"
    __mapper_args__ = {
        "polymorphic_identity": TiersType.CLIENT,
    }
    
    id = Column(Integer, ForeignKey('tiers.id'), primary_key=True)
    industry = Column(String(50))
    customer_since = Column(DateTime(timezone=True))
    rating = Column(String(10))  # A, B, C, D
    factures = relationship("Facture", back_populates="client")


class Fournisseur(Tiers):
    """Supplier specific model"""
    __tablename__ = "fournisseurs"
    __mapper_args__ = {
        "polymorphic_identity": TiersType.FOURNISSEUR,
    }
    
    id = Column(Integer, ForeignKey('tiers.id'), primary_key=True)
    industry = Column(String(50))
    supplier_since = Column(DateTime(timezone=True))
    rating = Column(String(10))
    approved = Column(Boolean, default=True)


class Partenaire(Tiers):
    """Partner specific model"""
    __tablename__ = "partenaires"
    __mapper_args__ = {
        "polymorphic_identity": TiersType.PARTENAIRE,
    }
    
    id = Column(Integer, ForeignKey('tiers.id'), primary_key=True)
    partnership_type = Column(String(50))  # e.g., "logistique", "financier", "technique"
    partnership_start = Column(DateTime(timezone=True))
    partnership_end = Column(DateTime(timezone=True))