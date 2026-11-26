"""Cameroon Customs models - Code des Douanes, Taux BEAC, BSC, CSC, APE"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, Enum, Date, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class ArticleCodeDouanes(Base):
    """Article du Code des Douanes Cameroun (Loi n°98/012 du 14 juillet 1998)"""
    __tablename__ = "articles_code_douanes"
    
    id = Column(Integer, primary_key=True, index=True)
    article = Column(String(20), unique=True, nullable=False, index=True)  # Article 150, 151, etc.
    chapitre = Column(String(20))  # Chapitre du code
    designation = Column(String(500), nullable=False)
    description_regime = Column(Text)
    taux_droit = Column(Numeric)  # 5%, 10%, 20%, 30%
    notes_applicatives = Column(Text)
    reference_legale = Column(String(100))
    date_modification = Column(Date)
    est_actif = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class TauxReferenceBEAC(Base):
    """Taux de référence BEAC (Banque des États de l'Afrique Centrale)"""
    __tablename__ = "taux_reference_beac"
    
    id = Column(Integer, primary_key=True, index=True)
    devise = Column(String(3), nullable=False, index=True)  # USD, EUR, GBP, CNY
    taux_achat = Column(Numeric, nullable=False)
    taux_vente = Column(Numeric, nullable=False)
    taux_moyen = Column(Numeric)
    date_application = Column(Date, nullable=False, index=True)
    source = Column(String(50), default="BEAC")  # BEAC, Douanes
    est_taux_officiel = Column(Boolean, default=True)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class BSC(Base):
    """Bulletin de Soumission Connaissement (Obligatoire pour import)"""
    __tablename__ = "bsc"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_bsc = Column(String(50), unique=True, nullable=False, index=True)
    numero_connaisse = Column(String(50), nullable=False)
    navire = Column(String(200), nullable=False)
    voyage = Column(String(50))
    port_chargement = Column(String(100), nullable=False)
    port_dechargement = Column(String(100), nullable=False)
    date_emission = Column(Date, nullable=False)
    date_validite = Column(Date)
    agent = Column(String(100), nullable=False)  # Transitaire agréé
    importateur = Column(String(200), nullable=False)
    poids_brut_tonnes = Column(Numeric)
    valeur_fob = Column(Numeric(15, 2))
    valeur_caf = Column(Numeric(15, 2))
    devise = Column(String(3), default="USD")
    montant_frais_bsc = Column(Numeric(15, 2))
    devise_frais = Column(String(3), default="XAF")
    statut = Column(String(20), default="en_attente")  # en_attente, valide, expire, annule
    reference_cncc = Column(String(50))
    date_validation = Column(Date)
    date_paiement = Column(Date)
    preuve_paiement = Column(String(255))  # URL scan reçu
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class CSC(Base):
    """Certificat de Sécurité Connaissement (INS - Inspection Nationale)"""
    __tablename__ = "csc"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_csc = Column(String(50), unique=True, nullable=False, index=True)
    numero_connaisse = Column(String(50), nullable=False)
    navire = Column(String(200), nullable=False)
    port_origine = Column(String(100), nullable=False)
    port_destination = Column(String(100), nullable=False)
    date_demande = Column(Date, nullable=False)
    date_emission = Column(Date)
    date_validite = Column(Date)
    inspecteur = Column(String(100))
    compagnie_inspection = Column(String(100))  # INS, BIVAC, etc.
    resultat_inspection = Column(String(50))  # CONFORME, NON_CONFORME, RESERVE
    details_inspection = Column(Text)  # JSON
    poids_brut_tonnes = Column(Numeric)
    nombre_colis = Column(Integer)
    type_marchandise = Column(String(100))
    valeur_fob = Column(Numeric(15, 2))
    statut = Column(String(20), default="en_attente")  # en_attente, emis, rejete
    frais_inspection = Column(Numeric(15, 2))
    date_paiement = Column(Date)
    preuve_paiement = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class APE(Base):
    """Arrêté de Paiement des Étrangers (BEAC - Contrôle devises)"""
    __tablename__ = "ape"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_ape = Column(String(50), unique=True, nullable=False, index=True)
    dossier_import_id = Column(Integer, ForeignKey('dossiers_transit_avance.id'))
    importateur = Column(String(200), nullable=False)
    montant_xaf = Column(Numeric(15, 2), nullable=False)
    montant_devise = Column(Numeric(15, 2))
    devise = Column(String(3), nullable=False)  # USD, EUR
    taux_change = Column(Numeric)
    banque = Column(String(100), nullable=False)
    compte_bancaire = Column(String(30))
    beneficiaire_etranger = Column(String(200))
    pays_beneficiaire = Column(String(50))
    objet_transfert = Column(String(200))
    date_demande = Column(Date, nullable=False)
    date_autorisation = Column(Date)
    date_execution = Column(Date)
    reference_beac = Column(String(50))
    statut = Column(String(20), default="en_attente")  # en_attente, autorise, refuse, execute
    agent_beac = Column(String(100))
    motif_refus = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class DUM(Base):
    """Déclaration Unique de Marchandises (Système douanier moderne)"""
    __tablename__ = "dum"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_dum = Column(String(50), unique=True, nullable=False, index=True)
    dossier_transit_id = Column(Integer, ForeignKey('dossiers_transit_avance.id'))
    type_operation = Column(String(20), nullable=False)  # import, export, transit
    regime_douanier = Column(String(50), nullable=False)
    bureau_douane = Column(String(100), nullable=False)
    date_depot = Column(Date, nullable=False)
    declarant = Column(String(200), nullable=False)
    numero_agrement = Column(String(50))
    importateur = Column(String(200), nullable=False)
    numero_contribuable = Column(String(50))
    marchandise = Column(Text, nullable=False)
    nomenclature = Column(String(20))  # Code SH
    poids_brut = Column(Numeric)
    poids_net = Column(Numeric)
    nombre_colis = Column(Integer)
    valeur_fob = Column(Numeric(15, 2))
    valeur_caf = Column(Numeric(15, 2))
    devise = Column(String(3), default="USD")
    taux_change = Column(Numeric)
    valeur_douane_xaf = Column(Numeric(15, 2))
    droits_douane = Column(Numeric(15, 2))
    tva = Column(Numeric(15, 2))
    centimes_additionnels = Column(Numeric(15, 2))
    timbre_usage = Column(Numeric(15, 2))
    montant_total = Column(Numeric(15, 2))
    statut = Column(String(20), default="en_attente")  # en_attente, valide, rejet, liquidé
    date_validation = Column(Date)
    date_liquidation = Column(Date)
    agent_douane = Column(String(100))
    reference_sydonia = Column(String(50))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class BV(Base):
    """Bureau de Validation (Contrôle qualité déclarations)"""
    __tablename__ = "bv"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_bv = Column(String(50), unique=True, nullable=False, index=True)
    dum_id = Column(Integer, ForeignKey('dum.id'))
    date_validation = Column(Date, nullable=False)
    validateur = Column(String(100), nullable=False)
    grade = Column(String(50))
    resultat = Column(String(20), nullable=False)  # VALIDE, REJET, RESERVE
    motifs_rejet = Column(Text)
    corrections_requises = Column(Text)  # JSON
    date_correction = Column(Date)
    statut_final = Column(String(20))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
