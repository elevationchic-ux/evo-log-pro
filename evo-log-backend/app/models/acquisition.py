"""Acquisition models - Procurement and supplier management for Cameroon/CEMAC"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, Enum, Date, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class TypeAppelOffres(str, enum.Enum):
    """Tender type enumeration"""
    OUVERT = "ouvert"
    RESTREINT = "restreint"
    NEGOCIE = "negocie"
    CADO = "cado"  # Consultation à défaut


class StatutAppelOffres(str, enum.Enum):
    """Tender status enumeration"""
    BROUILLON = "brouillon"
    PUBLIE = "publie"
    EN_COURS = "en_cours"
    ANALYSE = "analyse"
    ATTRIBUE = "attribue"
    ANNULE = "annule"
    SANS_SUITE = "sans_suite"


class CritereEvaluation(str, enum.Enum):
    """Evaluation criterion enumeration"""
    PRIX = "prix"
    QUALITE = "qualite"
    DELAI = "delai"
    EXPERIENCE = "experience"
    TECHNIQUE = "technique"
    FINANCIER = "financier"
    ENVIRONNEMENTAL = "environnemental"


class AppelOffres(Base):
    """Tender/Call for bids"""
    __tablename__ = "appels_offres"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_appel = Column(String(50), unique=True, nullable=False, index=True)
    titre = Column(String(200), nullable=False)
    type_appel = Column(Enum(TypeAppelOffres))
    statut = Column(Enum(StatutAppelOffres), default=StatutAppelOffres.BROUILLON)
    date_publication = Column(Date)
    date_limite = Column(Date)
    date_ouverture = Column(Date)
    date_attribution = Column(Date)
    budget_estime = Column(Numeric(15, 2))
    devise = Column(String(3), default="XAF")
    responsable = Column(String(100))
    departement = Column(String(50))
    description = Column(Text)
    conditions_participation = Column(Text)
    documents_requis = Column(Text)  # JSON array
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    cahier_charges = relationship("CahierCharges", back_populates="appel_offres")
    offres = relationship("Offre", back_populates="appel_offres")
    comparatifs = relationship("Comparatif", back_populates="appel_offres")


class CahierCharges(Base):
    """Cahier des charges - Specifications"""
    __tablename__ = "cahiers_charges"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_cdc = Column(String(50), unique=True, nullable=False, index=True)
    appel_offres_id = Column(Integer, ForeignKey('appels_offres.id'))
    version = Column(Integer, default=1)
    date_version = Column(Date)
    objet = Column(String(500), nullable=False)
    description_technique = Column(Text)
    specifications = Column(Text)  # JSON with detailed specs
    normes = Column(Text)  # ISO, CEMAC standards
    conditions_commerciales = Column(Text)
    conditions_paiement = Column(Text)
    delai_livraison = Column(Integer)  # en jours
    penalites_retard = Column(Numeric(15, 2))
    devise = Column(String(3), default="XAF")
    garanties = Column(Text)
    clauses_speciales = Column(Text)
    approuve_par = Column(String(100))
    date_approbation = Column(Date)
    statut = Column(String(20), default="brouillon")  # brouillon, valide, annule
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    appel_offres = relationship("AppelOffres", back_populates="cahier_charges")
    lignes_cdc = relationship("LigneCDC", back_populates="cahier_charges")


class LigneCDC(Base):
    """Cahier des charges line item"""
    __tablename__ = "lignes_cdc"
    
    id = Column(Integer, primary_key=True, index=True)
    cdc_id = Column(Integer, ForeignKey('cahiers_charges.id'))
    article_id = Column(Integer, ForeignKey('stocks.id'))
    designation = Column(String(200), nullable=False)
    description = Column(Text)
    quantite = Column(Numeric)
    unite = Column(String(20))
    specifications_detaillees = Column(Text)
    norme = Column(String(50))
    classe = Column(String(50))
    origine = Column(String(50))  # "local", "import", "cemac"
    budget_unitaire = Column(Numeric(15, 2))
    budget_total = Column(Numeric(15, 2))
    devise = Column(String(3), default="XAF")
    priorite = Column(String(20))  # "haute", "moyenne", "basse"
    statut = Column(String(20), default="actif")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    cahier_charges = relationship("CahierCharges", back_populates="lignes_cdc")


class Offre(Base):
    """Supplier bid/proposal"""
    __tablename__ = "offres"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_offre = Column(String(50), unique=True, nullable=False, index=True)
    appel_offres_id = Column(Integer, ForeignKey('appels_offres.id'))
    fournisseur_id = Column(Integer, ForeignKey('tiers.id'))
    date_reception = Column(Date)
    date_validite = Column(Date)
    montant_total = Column(Numeric(15, 2))
    devise = Column(String(3), default="XAF")
    delai_livraison = Column(Integer)  # en jours
    validite_offre = Column(Integer)  # en jours
    notes = Column(Text)
    statut = Column(String(20), default="recu")  # recu, valide, retenu, rejete, retire
    raison_rejet = Column(Text)
    rang = Column(Integer)  # Rang après évaluation
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    appel_offres = relationship("AppelOffres", back_populates="offres")
    lignes_offre = relationship("LigneOffre", back_populates="offre")
    evaluations = relationship("EvaluationOffre", back_populates="offre")


class LigneOffre(Base):
    """Bid line item"""
    __tablename__ = "lignes_offre"
    
    id = Column(Integer, primary_key=True, index=True)
    offre_id = Column(Integer, ForeignKey('offres.id'))
    ligne_cdc_id = Column(Integer, ForeignKey('lignes_cdc.id'))
    designation = Column(String(200))
    quantite = Column(Numeric)
    unite = Column(String(20))
    prix_unitaire = Column(Numeric(15, 2))
    prix_total = Column(Numeric(15, 2))
    devise = Column(String(3), default="XAF")
    delai = Column(Integer)
    conformite = Column(Boolean, default=True)
    observations = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    offre = relationship("Offre", back_populates="lignes_offre")


class EvaluationOffre(Base):
    """Bid evaluation"""
    __tablename__ = "evaluations_offre"
    
    id = Column(Integer, primary_key=True, index=True)
    offre_id = Column(Integer, ForeignKey('offres.id'))
    critere = Column(Enum(CritereEvaluation))
    note = Column(Numeric)  # sur 20
    poids = Column(Numeric)  # % importance
    note_ponderee = Column(Numeric)
    evaluateur = Column(String(100))
    date_evaluation = Column(Date)
    commentaires = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    offre = relationship("Offre", back_populates="evaluations")


class Comparatif(Base):
    """Supplier comparison matrix"""
    __tablename__ = "comparatifs"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_comparatif = Column(String(50), unique=True, nullable=False, index=True)
    appel_offres_id = Column(Integer, ForeignKey('appels_offres.id'))
    date_creation = Column(Date)
    date_cloture = Column(Date)
    cree_par = Column(String(100))
    valide_par = Column(String(100))
    date_validation = Column(Date)
    statut = Column(String(20), default="brouillon")  # brouillon, valide, annule
    conclusions = Column(Text)
    recommandation = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    appel_offres = relationship("AppelOffres", back_populates="comparatifs")
    lignes_comparatif = relationship("LigneComparatif", back_populates="comparatif")


class LigneComparatif(Base):
    """Comparison line item"""
    __tablename__ = "lignes_comparatif"
    
    id = Column(Integer, primary_key=True, index=True)
    comparatif_id = Column(Integer, ForeignKey('comparatifs.id'))
    fournisseur_id = Column(Integer, ForeignKey('tiers.id'))
    offre_id = Column(Integer, ForeignKey('offres.id'))
    ligne_cdc_id = Column(Integer, ForeignKey('lignes_cdc.id'))
    prix = Column(Numeric(15, 2))
    devise = Column(String(3), default="XAF")
    delai = Column(Integer)
    note_qualite = Column(Numeric)
    note_technique = Column(Numeric)
    note_financiere = Column(Numeric)
    note_globale = Column(Numeric)
    rang = Column(Integer)
    qualite = Column(String(20))  # "excellent", "bon", "moyen", "faible"
    observations = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    comparatif = relationship("Comparatif", back_populates="lignes_comparatif")


class ContratCadre(Base):
    """Framework contract"""
    __tablename__ = "contrats_cadre"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_contrat = Column(String(50), unique=True, nullable=False, index=True)
    fournisseur_id = Column(Integer, ForeignKey('tiers.id'))
    type_contrat = Column(String(50))  # "approvisionnement", "services", "maintenance"
    date_signature = Column(Date)
    date_debut = Column(Date)
    date_fin = Column(Date)
    duree_mois = Column(Integer)
    montant_annuel = Column(Numeric(15, 2))
    devise = Column(String(3), default="XAF")
    conditions_renouvellement = Column(Text)
    conditions_resiliation = Column(Text)
    garanties = Column(Text)
    clauses_speciales = Column(Text)
    signe_par = Column(String(100))
    fonction = Column(String(50))
    statut = Column(String(20), default="actif")  # actif, suspendu, resilie, expire
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    bons_commande = relationship("BonCommande", back_populates="contrat_cadre")


class BonCommande(Base):
    """Purchase order"""
    __tablename__ = "bons_commande"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_bc = Column(String(50), unique=True, nullable=False, index=True)
    contrat_cadre_id = Column(Integer, ForeignKey('contrats_cadre.id'), nullable=True)
    fournisseur_id = Column(Integer, ForeignKey('tiers.id'))
    date_creation = Column(Date)
    date_prevue_livraison = Column(Date)
    date_reelle_livraison = Column(Date)
    destinataire = Column(String(100))
    lieu_livraison = Column(String(200))
    devise = Column(String(3), default="XAF")
    montant_total = Column(Numeric(15, 2))
    statut = Column(String(20), default="brouillon")  # brouillon, valide, annule, livre
    conditions_paiement = Column(String(50))
    notes = Column(Text)
    valide_par = Column(String(100))
    date_validation = Column(Date)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    contrat_cadre = relationship("ContratCadre", back_populates="bons_commande")
    lignes_bc = relationship("LigneBC", back_populates="bon_commande")
    receptions = relationship("Reception", back_populates="bon_commande")


class LigneBC(Base):
    """Purchase order line"""
    __tablename__ = "lignes_bc"
    
    id = Column(Integer, primary_key=True, index=True)
    bc_id = Column(Integer, ForeignKey('bons_commande.id'))
    article_id = Column(Integer, ForeignKey('stocks.id'))
    designation = Column(String(200))
    quantite = Column(Numeric)
    unite = Column(String(20))
    prix_unitaire = Column(Numeric(15, 2))
    prix_total = Column(Numeric(15, 2))
    devise = Column(String(3), default="XAF")
    quantite_recue = Column(Numeric, default=0)
    date_reception = Column(Date)
    statut = Column(String(20), default="en_attente")  # en_attente, partiel, complet
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    bon_commande = relationship("BonCommande", back_populates="lignes_bc")


class Reception(Base):
    """Goods receipt"""
    __tablename__ = "receptions"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_reception = Column(String(50), unique=True, nullable=False, index=True)
    bc_id = Column(Integer, ForeignKey('bons_commande.id'))
    fournisseur_id = Column(Integer, ForeignKey('tiers.id'))
    date_reception = Column(Date)
    date_prevue = Column(Date)
    type_reception = Column(String(50))  # "complete", "partielle", "control_qualite"
    lieu_reception = Column(String(200))
    responsable = Column(String(100))
    transporteur = Column(String(100))
    numero_transport = Column(String(50))
    condition_marchandise = Column(String(50))  # "conforme", "avarie", "manquant"
    nombre_colis = Column(Integer)
    poids_brut = Column(Numeric)
    poids_net = Column(Numeric)
    emballage = Column(String(50))
    notes = Column(Text)
    statut = Column(String(20), default="en_cours")  # en_cours, controle, valide, rejete
    controle_qualite = Column(Boolean, default=False)
    date_controle = Column(Date)
    controle_par = Column(String(100))
    photo = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    bon_commande = relationship("BonCommande", back_populates="receptions")
    lignes_reception = relationship("LigneReception", back_populates="reception")


class LigneReception(Base):
    """Receipt line item"""
    __tablename__ = "lignes_reception"
    
    id = Column(Integer, primary_key=True, index=True)
    reception_id = Column(Integer, ForeignKey('receptions.id'))
    ligne_bc_id = Column(Integer, ForeignKey('lignes_bc.id'))
    article_id = Column(Integer, ForeignKey('stocks.id'))
    designation = Column(String(200))
    quantite_commandee = Column(Numeric)
    quantite_recue = Column(Numeric)
    quantite_acceptee = Column(Numeric)
    quantite_refusee = Column(Numeric)
    unite = Column(String(20))
    prix_unitaire = Column(Numeric(15, 2))
    valeur_recue = Column(Numeric(15, 2))
    devise = Column(String(3), default="XAF")
    conformite = Column(Boolean, default=True)
    motif_refus = Column(String(200))
    etat = Column(String(50))  # "neuf", "bon", "avare", "recupere"
    emplacement = Column(String(50))
    date_peremption = Column(Date)
    numero_lot = Column(String(50))
    statut = Column(String(20), default="reception")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    reception = relationship("Reception", back_populates="lignes_reception")


class LitigeFournisseur(Base):
    """Supplier dispute"""
    __tablename__ = "litiges_fournisseur"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_litige = Column(String(50), unique=True, nullable=False, index=True)
    fournisseur_id = Column(Integer, ForeignKey('tiers.id'))
    bc_id = Column(Integer, ForeignKey('bons_commande.id'), nullable=True)
    reception_id = Column(Integer, ForeignKey('receptions.id'), nullable=True)
    type_litige = Column(String(50))  # "qualite", "quantite", "delai", "prix", "facture"
    date_ouverture = Column(Date)
    description = Column(Text)
    gravite = Column(String(20))  # "mineur", "moyen", "majeur", "critique"
    montant_en_litige = Column(Numeric(15, 2))
    devise = Column(String(3), default="XAF")
    mesure_demandee = Column(Text)
    date_cloture = Column(Date)
    resolution = Column(Text)
    statut = Column(String(20), default="ouvert")  # ouvert, en_cours, resolu, clos
    responsable = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    historique = relationship("HistoriqueLitige", back_populates="litige")


class HistoriqueLitige(Base):
    """Dispute history"""
    __tablename__ = "historique_litige"
    
    id = Column(Integer, primary_key=True, index=True)
    litige_id = Column(Integer, ForeignKey('litiges_fournisseur.id'))
    date_action = Column(DateTime(timezone=True))
    action = Column(String(100))
    description = Column(Text)
    auteur = Column(String(100))
    resultat = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    litige = relationship("LitigeFournisseur", back_populates="historique")


class EvaluationFournisseur(Base):
    """Supplier evaluation"""
    __tablename__ = "evaluations_fournisseur"
    
    id = Column(Integer, primary_key=True, index=True)
    fournisseur_id = Column(Integer, ForeignKey('tiers.id'))
    periode = Column(String(50))  # "Q1-2026", "mensuel-01-2026"
    date_evaluation = Column(Date)
    evaluateur = Column(String(100))
    note_qualite = Column(Numeric)  # sur 20
    note_delai = Column(Numeric)  # sur 20
    note_prix = Column(Numeric)  # sur 20
    note_service = Column(Numeric)  # sur 20
    note_globale = Column(Numeric)  # sur 20
    classement = Column(String(20))  # "A", "B", "C", "D"
    commentaires = Column(Text)
    recommandation = Column(String(50))  # "maintenir", "surveiller", "remplacer"
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
