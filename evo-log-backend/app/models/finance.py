"""
Finance models - Facturation, Paiements, Comptabilité
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, Enum, Date, Numeric, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class FactureStatus(str, enum.Enum):
    """Invoice status"""
    BROUILLON = "brouillon"
    EMISE = "emise"
    PAYEE_PARTIELLEMENT = "payee_partiellement"
    PAYEE = "payee"
    ANNULEE = "annulee"
    RETARD = "retard"


class PaiementStatus(str, enum.Enum):
    """Payment status"""
    EN_ATTENTE = "en_attente"
    CONFIRME = "confirme"
    ANNULE = "annule"
    REMBOURSE = "rembourse"


class Facture(Base):
    """Invoice model"""
    __tablename__ = "factures"
    __table_args__ = (
        UniqueConstraint('company_id', 'numero_facture', name='uix_facture_company_numero'),
    )
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=True, index=True)
    numero_facture = Column(String(50), nullable=False, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"))
    date_emission = Column(Date, nullable=False, default=func.now())
    date_echeance = Column(Date)
    montant_ht = Column(Numeric(15, 2), nullable=False)
    montant_tva = Column(Numeric(15, 2), default=0)
    montant_ttc = Column(Numeric(15, 2), nullable=False)
    devise = Column(String(3), default="XAF")
    statut = Column(Enum(FactureStatus), default=FactureStatus.BROUILLON)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    client = relationship("Client", back_populates="factures")
    lignes = relationship("LigneFactureSimple", back_populates="facture")
    paiements = relationship("Paiement", back_populates="facture")
    reglements = relationship("Reglement", back_populates="facture")
    retenues_source = relationship("RetenueSource", back_populates="facture")


class LigneFactureSimple(Base):
    """Invoice line item (simple version)"""
    __tablename__ = "lignes_facture_simple"
    
    id = Column(Integer, primary_key=True, index=True)
    facture_id = Column(Integer, ForeignKey("factures.id"), nullable=False)
    description = Column(String(255), nullable=False)
    quantite = Column(Numeric(10, 2), nullable=False)
    prix_unitaire = Column(Numeric(15, 2), nullable=False)
    montant_ht = Column(Numeric(15, 2), nullable=False)
    tva_taux = Column(Numeric(5, 2), default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    facture = relationship("Facture", back_populates="lignes")


class Paiement(Base):
    """Payment model"""
    __tablename__ = "paiements"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=True, index=True)
    facture_id = Column(Integer, ForeignKey("factures.id"), nullable=False)
    montant = Column(Numeric(15, 2), nullable=False)
    date_paiement = Column(Date, nullable=False, default=func.now())
    mode_paiement = Column(String(50))  # virement, espece, cheque, mobile_money
    reference = Column(String(100))
    statut = Column(Enum(PaiementStatus), default=PaiementStatus.EN_ATTENTE)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    facture = relationship("Facture", back_populates="paiements")


class Compte(Base):
    """Account model for accounting"""
    __tablename__ = "comptes"
    __table_args__ = (
        UniqueConstraint('company_id', 'numero_compte', name='uix_compte_company_numero'),
    )
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=True, index=True)
    numero_compte = Column(String(20), nullable=False, index=True)
    nom_compte = Column(String(100), nullable=False)
    type_compte = Column(String(50))  # actif, passif, recettes, depenses
    solde = Column(Numeric(15, 2), default=0)
    devise = Column(String(3), default="XAF")
    is_actif = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class EcritureComptable(Base):
    """Accounting entry model"""
    __tablename__ = "ecritures_comptables"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=True, index=True)
    date_ecriture = Column(Date, nullable=False, default=func.now())
    reference = Column(String(50))
    libelle = Column(Text, nullable=False)
    compte_debit = Column(Integer, ForeignKey("comptes.id"))
    compte_credit = Column(Integer, ForeignKey("comptes.id"))
    montant_debit = Column(Numeric(15, 2))
    montant_credit = Column(Numeric(15, 2))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    compte_debit_rel = relationship("Compte", foreign_keys=[compte_debit])
    compte_credit_rel = relationship("Compte", foreign_keys=[compte_credit])

# Compatibility exports retained during the EVO-LOG Pro reconciliation.
# Import the OHADA classes lazily so the model metadata is registered only once.
import app.models.finance_ohada as finance_ohada_module

PlanComptableOHADA = finance_ohada_module.PlanComptableOHADA
EcritureComptableNew = finance_ohada_module.EcritureComptableNew
ExerciceComptable = finance_ohada_module.ExerciceComptable
FactureNew = finance_ohada_module.FactureNew
LigneFactureOHADA = finance_ohada_module.LigneFactureOHADA
ISDeclarable = finance_ohada_module.ISDeclarable
TVA = finance_ohada_module.TVADeclarable
RetenueSource = finance_ohada_module.RetenueSource
CentimesAdditionnels = finance_ohada_module.CentimesAdditionnels
Patente = finance_ohada_module.Patente
LigneFacture = LigneFactureSimple
PlanComptable = PlanComptableOHADA
MinimumCorporateTax = ISDeclarable
