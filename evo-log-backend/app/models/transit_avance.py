"""Transit avancé models - Complete customs operations for Cameroon/CEMAC"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, Enum, Date, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class TypeTransit(str, enum.Enum):
    """Transit type enumeration"""
    DIRECT = "DIRECT"
    ORDINAIRE = "ORDINAIRE"
    SUSPENDU = "SUSPENDU"


class RegimeDouanier(str, enum.Enum):
    """Customs regime enumeration"""
    MISE_CONSOMMATION = "MISE_A_LA_CONSOMMATION"
    ADMISSION_TEMPORAIRE = "ADMISSION_TEMPORAIRE"
    ENTREPOT_DOUANIER = "ENTREPOT_DOUANIER"
    ENTREPOT_INDUSTRIEL = "ENTREPOT_INDUSTRIEL"
    DRAWBACK = "DRAWBACK"
    EXPORT_TEMPORAIRE = "EXPORT_TEMPORAIRE"
    TIR = "TIR"
    TSD = "TSD"
    TRANSIT_COMMUNAUTAIRE = "TRANSIT_COMMUNAUTAIRE"


class BureauDouane(Base):
    """Customs office entry/exit point"""
    __tablename__ = "bureaux_douane"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, nullable=False)
    nom = Column(String(100), nullable=False)
    type_bureau = Column(String(20))  # "entree", "sortie", "interieur"
    port_id = Column(Integer, ForeignKey('agencies.id'))
    region = Column(String(50))
    adresse = Column(String(200))
    telephone = Column(String(50))
    email = String(100)
    horaires = Column(Text)
    statut = Column(String(20), default="actif")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class DossierTransitAvance(Base):
    """Enhanced transit dossier with Cameroon/CEMAC compliance"""
    __tablename__ = "dossiers_transit_avance"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_dossier = Column(String(50), unique=True, nullable=False, index=True)
    client_id = Column(Integer, ForeignKey('tiers.id'))
    transitaire_id = Column(Integer, ForeignKey('tiers.id'))
    type_transit = Column(Enum(TypeTransit), default=TypeTransit.ORDINAIRE)
    regime_douanier = Column(Enum(RegimeDouanier))
    bureau_entree_id = Column(Integer, ForeignKey('bureaux_douane.id'))
    bureau_sortie_id = Column(Integer, ForeignKey('bureaux_douane.id'))
    statut = Column(String(20), default="ouvert")
    date_ouverture = Column(DateTime(timezone=True), server_default=func.now())
    date_cloture = Column(DateTime(timezone=True))
    marchandise = Column(Text)
    valeur_marchandise = Column(Numeric(15, 2))
    devise = Column(String(3), default="XAF")
    poids_brut = Column(Numeric)
    poids_net = Column(Numeric)
    nombre_colis = Column(Integer)
    origine = Column(String(100))
    pays_origine_code = Column(String(2))  # ISO country code
    destination = Column(String(100))
    pays_destination_code = Column(String(2))
    moyen_transport = Column(String(50))
    numero_connaisse = Column(String(50))
    numero_cmr = Column(String(50))  # Lettre de voiture CMR
    numero_tir = Column(String(50))  # Carnet TIR
    taux_change = Column(Numeric, default=1.0)
    montant_frais = Column(Numeric(15, 2))
    montant_droits = Column(Numeric(15, 2))
    montant_tva = Column(Numeric(15, 2))
    montant_total = Column(Numeric(15, 2))
    correspondant_agree = Column(String(100))
    reference_sygdonia = Column(String(50))  # SYDONIA+ reference
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    bureau_entree = relationship("BureauDouane", foreign_keys=[bureau_entree_id])
    bureau_sortie = relationship("BureauDouane", foreign_keys=[bureau_sortie_id])
    visites_physiques = relationship("VisitePhysique", back_populates="dossier")
    valorisations = relationship("ValorisationDouaniere", back_populates="dossier")
    bons_a_dedouaner = relationship("BonAD", back_populates="dossier")
    amc = relationship("AvisMiseConsommation", back_populates="dossier")
    credits_enlevement = relationship("CreditEnlevement", back_populates="dossier")
    litiges = relationship("LitigeDouanier", back_populates="dossier")


class VisitePhysique(Base):
    """Physical inspection of goods"""
    __tablename__ = "visites_physiques"
    
    id = Column(Integer, primary_key=True, index=True)
    dossier_transit_id = Column(Integer, ForeignKey('dossiers_transit_avance.id'))
    date_visite = Column(DateTime(timezone=True))
    inspecteur_id = Column(Integer, ForeignKey('users.id'))
    type_visite = Column(String(50))  # "controle", "echantillonnage", "analyse"
    rapport = Column(Text)
    prelevement = Column(Boolean, default=False)
    echantillon = Column(String(100))
    resultat = Column(String(50))  # "conforme", "non_conforme", "analyse_en_cours"
    conformite = Column(Boolean, default=False)
    observations = Column(Text)
    photos = Column(Text)  # JSON array of photo paths
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    dossier = relationship("DossierTransitAvance", back_populates="visites_physiques")


class ValorisationDouaniere(Base):
    """Customs valuation method"""
    __tablename__ = "valorisations_douanieres"
    
    id = Column(Integer, primary_key=True, index=True)
    dossier_transit_id = Column(Integer, ForeignKey('dossiers_transit_avance.id'))
    methode_valorisation = Column(String(50))  # "transaction", "deductive", "valeur_retabile"
    valeur_caf = Column(Numeric(15, 2))
    fret = Column(Numeric(15, 2))
    assurance = Column(Numeric(15, 2))
    autres_frais = Column(Numeric(15, 2))
    valeur_fob = Column(Numeric(15, 2))
    taux_change = Column(Numeric)
    devise = Column(String(3), default="XAF")
    date_valorisation = Column(Date)
    valide_par = Column(Integer, ForeignKey('users.id'))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    dossier = relationship("DossierTransitAvance", back_populates="valorisations")


class NomenclatureCEMAC(Base):
    """CEMAC TARIC nomenclature"""
    __tablename__ = "nomenclature_cemac"
    
    id = Column(Integer, primary_key=True, index=True)
    code_hs = Column(String(10), unique=True, nullable=False, index=True)
    description = Column(String(500), nullable=False)
    section = Column(String(2))
    chapitre = Column(String(2))
    position = Column(String(4))
    taux_dd = Column(Numeric)  # Droits de douane standard
    taux_tva = Column(Numeric)  # TVA standard
    unite = Column(String(20))
    pays_origine = Column(String(50))
    restrictions = Column(Text)
    statut = Column(String(20), default="actif")
    date_effet = Column(Date)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class DeclarationDouaniereAvance(Base):
    """Enhanced customs declaration with SYDONIA+ integration"""
    __tablename__ = "declarations_douaniere_avance"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_declaration = Column(String(50), unique=True, nullable=False, index=True)
    dossier_transit_id = Column(Integer, ForeignKey('dossiers_transit_avance.id'))
    regime_douanier = Column(Enum(RegimeDouanier))
    bureau_douane_id = Column(Integer, ForeignKey('bureaux_douane.id'))
    reference_sygdonia = Column(String(50))  # SYDONIA+ reference
    date_enregistrement = Column(DateTime(timezone=True))
    date_validation = Column(DateTime(timezone=True))
    date_acquittement = Column(DateTime(timezone=True))
    valeur_declaree = Column(Numeric(15, 2))
    devise = Column(String(3), default="XAF")
    poids_declare = Column(Numeric)
    code_hs = Column(String(10))  # TARIC code
    taux_dd = Column(Numeric)
    montant_dd = Column(Numeric(15, 2))
    taux_tva = Column(Numeric)
    montant_tva = Column(Numeric(15, 2))
    taux_autres_taxes = Column(Numeric)
    montant_autres_taxes = Column(Numeric(15, 2))
    total_taxes = Column(Numeric(15, 2))
    numero_b7 = Column(String(50))
    numero_quitus = Column(String(50))
    statut = Column(String(20), default="brouillon")  # brouillon, valide, acquitte, rejete
    motifs_rejet = Column(Text)
    date_rejet = Column(DateTime(timezone=True))
    certificat_origine = Column(String(255))
    facture_proforma = Column(String(255))
    facture_commerciale = Column(String(255))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    dossier = relationship("DossierTransitAvance")
    bureau_douane = relationship("BureauDouane")
    lignes_declaration = relationship("LigneDeclaration", back_populates="declaration")


class LigneDeclaration(Base):
    """Declaration line item"""
    __tablename__ = "lignes_declaration"
    
    id = Column(Integer, primary_key=True, index=True)
    declaration_id = Column(Integer, ForeignKey('declarations_douaniere_avance.id'))
    numero_ligne = Column(Integer)
    designation = Column(String(500))
    quantite = Column(Numeric)
    unite = Column(String(20))
    poids_net = Column(Numeric)
    poids_brut = Column(Numeric)
    valeur_unitaire = Column(Numeric(15, 2))
    valeur_totale = Column(Numeric(15, 2))
    code_hs = Column(String(10))
    taux_dd = Column(Numeric)
    montant_dd = Column(Numeric(15, 2))
    taux_tva = Column(Numeric)
    montant_tva = Column(Numeric(15, 2))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    declaration = relationship("DeclarationDouaniereAvance", back_populates="lignes_declaration")


class BonAD(Base):
    """Bon à dédouaner - Customs debit note"""
    __tablename__ = "bons_ad"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_bad = Column(String(50), unique=True, nullable=False, index=True)
    dossier_transit_id = Column(Integer, ForeignKey('dossiers_transit_avance.id'), nullable=False)
    declaration_id = Column(Integer, ForeignKey('declarations_douaniere_avance.id'))
    signataire = Column(String(100))
    qualite = Column(String(50))  # "importateur", "transitaire", "mandataire"
    date_signature = Column(Date)
    statut = Column(String(20), default="emis")  # emis, annule, remplace
    reference_sygdonia = Column(String(50))
    numero_quitus = Column(String(50))
    montant_total = Column(Numeric(15, 2))
    devise = Column(String(3), default="XAF")
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    dossier = relationship("DossierTransitAvance", back_populates="bons_a_dedouaner")


class AvisMiseConsommation(Base):
    """AMC - Release for consumption"""
    __tablename__ = "amc"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_amc = Column(String(50), unique=True, nullable=False, index=True)
    dossier_transit_id = Column(Integer, ForeignKey('dossiers_transit_avance.id'))
    declaration_id = Column(Integer, ForeignKey('declarations_douaniere_avance.id'))
    bureau_douane_id = Column(Integer, ForeignKey('bureaux_douane.id'))
    date_emission = Column(Date)
    valide_par = Column(String(100))
    fonction = Column(String(50))
    date_validite = Column(Date)
    date_limite = Column(Date)
    montant_dd = Column(Numeric(15, 2))
    montant_tva = Column(Numeric(15, 2))
    montant_total = Column(Numeric(15, 2))
    devise = Column(String(3), default="XAF")
    statut = Column(String(20), default="emis")  # emis, annule
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    dossier = relationship("DossierTransitAvance", back_populates="amc")


class CreditEnlevement(Base):
    """Credit d'enlèvement - Release before clearance"""
    __tablename__ = "credits_enlevement"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_credit = Column(String(50), unique=True, nullable=False, index=True)
    dossier_transit_id = Column(Integer, ForeignKey('dossiers_transit_avance.id'))
    type_garantie = Column(String(50))  # "caution", "assurance", "engagement"
    garant = Column(String(100))
    montant_garantie = Column(Numeric(15, 2))
    devise = Column(String(3), default="XAF")
    date_echeance = Column(Date)
    date_delivrance = Column(Date)
    statut = Column(String(20), default="accordé")  # accordé, utilise, annule, libere
    reference_sygdonia = Column(String(50))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    dossier = relationship("DossierTransitAvance", back_populates="credits_enlevement")


class DroitPort(Base):
    """Port dues and charges"""
    __tablename__ = "droits_port"
    
    id = Column(Integer, primary_key=True, index=True)
    dossier_transit_id = Column(Integer, ForeignKey('dossiers_transit_avance.id'))
    type_droit = Column(String(50))  # "droit_de_quai", "pilotage", "remorquage", "stationnement"
    description = Column(String(200))
    base_calcul = Column(String(50))  # "tonnage", "nombre_conteneurs", "duree"
    quantite = Column(Numeric)
    taux = Column(Numeric)
    montant = Column(Numeric(15, 2))
    devise = Column(String(3), default="XAF")
    date_facturation = Column(Date)
    reference_facture = Column(String(50))
    statut = Column(String(20), default="facture")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class TimbreUsage(Base):
    """Stamp duty - Timbre d'usage"""
    __tablename__ = "timbres_usage"
    
    id = Column(Integer, primary_key=True, index=True)
    dossier_transit_id = Column(Integer, ForeignKey('dossiers_transit_avance.id'))
    type_timbre = Column(String(50))  # "timbre_douane", "timbre_comptable"
    montant = Column(Numeric(15, 2))
    devise = Column(String(3), default="XAF")
    date_apposition = Column(Date)
    numero_timbre = Column(String(50))
    statut = Column(String(20), default="appose")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class LitigeDouanier(Base):
    """Customs dispute"""
    __tablename__ = "litiges_douaniers"
    
    id = Column(Integer, primary_key=True, index=True)
    dossier_transit_id = Column(Integer, ForeignKey('dossiers_transit_avance.id'))
    type_litige = Column(String(50))  # "classement", "valeur", "origine", "regime"
    description = Column(Text)
    date_litige = Column(DateTime(timezone=True))
    statut = Column(String(20), default="ouvert")  # ouvert, en_cours, resolu, rejet
    montant_en_litige = Column(Numeric(15, 2))
    devise = Column(String(3), default="XAF")
    decision = Column(Text)
    date_decision = Column(DateTime(timezone=True))
    recours = Column(String(50))  # "appel", "contentieux"
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    dossier = relationship("DossierTransitAvance", back_populates="litiges")


class ArchivageDossier(Base):
    """Dossier archiving - 10-year retention"""
    __tablename__ = "archivage_dossiers"
    
    id = Column(Integer, primary_key=True, index=True)
    dossier_transit_id = Column(Integer, ForeignKey('dossiers_transit_avance.id'))
    date_archivage = Column(Date)
    date_destruction = Column(Date)  # 10 years later
    lieu_archivage = Column(String(100))
    numero_archive = Column(String(50))
    contenu = Column(Text)  # JSON with all document paths
    statut = Column(String(20), default="archive")
    accessible = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    dossier = relationship("DossierTransitAvance")


class ProcedureUrgente(Base):
    """Urgent customs procedure"""
    __tablename__ = "procedures_urgent"
    
    id = Column(Integer, primary_key=True, index=True)
    dossier_transit_id = Column(Integer, ForeignKey('dossiers_transit_avance.id'))
    type_urgence = Column(String(50))  # "perissable", "sanitaire", "militaire"
    justification = Column(Text)
    date_demande = Column(DateTime(timezone=True))
    date_autorisation = Column(DateTime(timezone=True))
    autorise_par = Column(String(100))
    fonction = Column(String(50))
    statut = Column(String(20), default="en_attente")  # en_attente, autorise, refuse
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    dossier = relationship("DossierTransitAvance")

# Compatibility exports retained during the EVO-LOG Pro reconciliation.
BAD = BonAD
AMC = AvisMiseConsommation
Valorisation = ValorisationDouaniere
