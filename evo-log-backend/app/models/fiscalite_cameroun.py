"""Cameroon Taxation Models - IRPP, IS, TCF, TDR, Local Taxes"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, Enum, Date, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class TypeImpot(str, enum.Enum):
    """Tax type enumeration Cameroon"""
    IRPP = "irpp"  # Impôt Revenu Personnes Physiques
    IS = "is"  # Impôt Sociétés
    TCF = "tcf"  # Taxe Communale
    TDR = "tdr"  # Taxe Développement Régional
    PATENTE = "patente"
    ICA = "ica"  # Impôt sur le Chiffre d'Affaires


class Periodicite(str, enum.Enum):
    """Payment periodicity"""
    MENSUEL = "mensuel"
    TRIMESTRIEL = "trimestriel"
    ANNUEL = "annuel"
    UNIQUE = "unique"


class ImpotCameroun(Base):
    """Impôt Cameroun"""
    __tablename__ = "impots_cameroun"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, nullable=False, index=True)  # IRPP, IS, TCF, TDR
    designation = Column(String(200), nullable=False)
    description = Column(Text)
    type_impot = Column(Enum(TypeImpot), nullable=False)
    taux = Column(Numeric)  # Pourcentage ou taux fixe
    base_calcul = Column(String(50), nullable=False)  # CA, BENEFICE, SALAIRE, TONNAGE
    periodicite = Column(Enum(Periodicite), nullable=False)
    date_limite = Column(Integer)  # 15, 30, etc. (jour du mois)
    reference_legale = Column(String(100))  # Article de loi
    taux_minimum = Column(Numeric)  # Pour impôts avec minimum
    est_actif = Column(Boolean, default=True)
    date_maj = Column(Date)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class DeclarationFiscale(Base):
    """Déclaration fiscale"""
    __tablename__ = "declarations_fiscales"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    type_impot = Column(Enum(TypeImpot), nullable=False)
    periode_debut = Column(Date, nullable=False)
    periode_fin = Column(Date, nullable=False)
    chiffre_affaires = Column(Numeric(15, 2))
    benefice = Column(Numeric(15, 2))
    salaire_total = Column(Numeric(15, 2))
    tonnage = Column(Numeric)
    montant_du = Column(Numeric(15, 2), nullable=False)
    montant_paye = Column(Numeric(15, 2), default=0)
    reste_a_payer = Column(Numeric(15, 2))
    statut = Column(String(20), default="en_attente")  # en_attente, soumis, valide, rejete, paye
    date_soumission = Column(Date)
    date_validation = Column(Date)
    date_paiement = Column(Date)
    reference_declaration = Column(String(50), unique=True)
    agent_fiscal = Column(String(100))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class PaiementLocal(Base):
    """Paiement local Cameroun"""
    __tablename__ = "paiements_locaux"
    
    id = Column(Integer, primary_key=True, index=True)
    type_paiement = Column(String(20), nullable=False)  # CHEQUE, VIREMENT, MOBILE_MONEY, ESPECE
    reference = Column(String(50), unique=True, nullable=False)
    montant = Column(Numeric(15, 2), nullable=False)
    devise = Column(String(3), default="XAF")
    beneficiaire = Column(String(100), nullable=False)
    banque = Column(String(100))
    compte = Column(String(30))
    date_paiement = Column(Date, nullable=False)
    preuve = Column(String(255))  # URL scan reçu
    declarant_id = Column(Integer, ForeignKey('users.id'))
    description = Column(Text)
    statut = Column(String(20), default="valide")  # valide, annule, conteste
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ContratFiscal(Base):
    """Contrat fiscal avec administration"""
    __tablename__ = "contrats_fiscaux"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    type_contrat = Column(String(50), nullable=False)  # ACCORD, CONVENTION, PLAN
    date_debut = Column(Date, nullable=False)
    date_fin = Column(Date, nullable=False)
    montant_minimum = Column(Numeric(15, 2))
    devise = Column(String(3), default="XAF")
    periodicite = Column(String(20), nullable=False)
    conditions = Column(Text)  # JSON
    reference_contrat = Column(String(50), unique=True)
    signataire = Column(String(100))
    date_signature = Column(Date)
    statut = Column(String(20), default="actif")  # actif, expire, resilie
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class RetenueSourceCameroun(Base):
    """Retenue à la source - Cameroon (fiscalité locale, utilise la même table que RetenueSource OHADA)"""
    __tablename__ = "retenues_source"
    __table_args__ = {'extend_existing': True}
    # PAS index=True ici: la table est deja declaree par RetenueSource
    # (finance_ohada) et redeclarer l'index creerait un doublon
    # 'ix_retenues_source_id' qui fait echouer create_all (Postgres et
    # SQLite partagent les noms d'index au niveau du schema).
    id = Column(Integer, primary_key=True)

    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    type_retenue = Column(String(50), nullable=False)  # SALAIRE, HONORAIRE, DIVIDENDE, LOYER
    montant_brut = Column(Numeric(15, 2), nullable=False)
    taux_retenue = Column(Numeric, nullable=False)  # 15%, 20%, etc.
    montant_retenue = Column(Numeric(15, 2), nullable=False)
    montant_net = Column(Numeric(15, 2), nullable=False)
    beneficiaire = Column(String(200), nullable=False)
    numero_contribuable = Column(String(50))
    date_operation = Column(Date, nullable=False)
    reference_paiement = Column(String(50))
    statut = Column(String(20), default="declare")  # declare, verse, conteste
    date_declaration = Column(Date)
    date_versement = Column(Date)
    admin_fiscale = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

