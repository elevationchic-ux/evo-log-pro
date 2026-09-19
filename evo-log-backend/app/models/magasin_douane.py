"""Magasin Douane models - Warehouse under customs for Cameroon/CEMAC"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, Enum, Date, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class TypeEntrepotDouane(str, enum.Enum):
    """Warehouse type enumeration"""
    ZST = "zst"  # Zone de Stockage Temporaire
    MAGASIN_SOUS_DOUANE = "magasin_sous_douane"
    ENTREPOT_INDUSTRIL = "entrepot_industriel"
    ENTREPOT_FRANC = "entrepot_franc"


class RegimeEntrepot(str, enum.Enum):
    """Warehouse regime enumeration"""
    SUSPENDU = "suspendu"
    TEMPORAIRE = "temporaire"
    INDUSTRIEL = "industriel"
    FRANC = "franc"


class EntrepotDouane(Base):
    """Customs warehouse"""
    __tablename__ = "entrepots_douane"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False)
    nom = Column(String(100), nullable=False)
    type_entrepot = Column(Enum(TypeEntrepotDouane))
    regime = Column(Enum(RegimeEntrepot))
    adresse = Column(String(200))
    surface_m2 = Column(Numeric)
    capacite_tonnage = Column(Numeric)
    temperature_controlee = Column(Boolean, default=False)
    temperature_min = Column(Numeric)
    temperature_max = Column(Numeric)
    controle_humidite = Column(Boolean, default=False)
    zone_dangereuse = Column(Boolean, default=False)
    equipe_surveillance = Column(String(100))
    garde_agree = Column(String(100))
    numero_agrement = Column(String(50))
    date_agrement = Column(Date)
    date_expiration_agrement = Column(Date)
    statut = Column(String(20), default="actif")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    declarations_entrepot = relationship("DeclarationEntrepot", back_populates="entrepot")
    fiches_magasin = relationship("FicheMagasin", back_populates="entrepot")
    inventaires_douaniers = relationship("InventaireDouanier", back_populates="entrepot")


class DeclarationEntrepot(Base):
    """Warehouse declaration - Mise en entrepôt"""
    __tablename__ = "declarations_entrepot"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_declaration = Column(String(50), unique=True, nullable=False, index=True)
    entrepot_id = Column(Integer, ForeignKey('entrepots_douane.id'))
    dossier_transit_id = Column(Integer, ForeignKey('dossiers_transit.id'))
    regime = Column(Enum(RegimeEntrepot))
    date_declaration = Column(Date)
    date_acceptation = Column(Date)
    date_limite = Column(Date)
    valide_par = Column(String(100))
    fonction = Column(String(50))
    valeur_marchandise = Column(Numeric(15, 2))
    devise = Column(String(3), default="XAF")
    numero_reference_sygdonia = Column(String(50))
    statut = Column(String(20), default="en_attente")  # en_attente, accepte, refuse, cloture
    motifs_refus = Column(Text)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    entrepot = relationship("EntrepotDouane", back_populates="declarations_entrepot")
    lignes_entrepot = relationship("LigneEntrepot", back_populates="declaration")


class LigneEntrepot(Base):
    """Warehouse declaration line"""
    __tablename__ = "lignes_entrepot"
    
    id = Column(Integer, primary_key=True, index=True)
    declaration_id = Column(Integer, ForeignKey('declarations_entrepot.id'))
    article_id = Column(Integer, ForeignKey('stocks.id'))
    designation = Column(String(200))
    quantite = Column(Numeric)
    unite = Column(String(20))
    poids_net = Column(Numeric)
    poids_brut = Column(Numeric)
    valeur_unitaire = Column(Numeric(15, 2))
    valeur_totale = Column(Numeric(15, 2))
    emplacement = Column(String(50))
    numero_lot = Column(String(50))
    date_peremption = Column(Date)
    dangereux = Column(Boolean, default=False)
    classe_imdg = Column(String(10))
    statut = Column(String(20), default="stocke")  # stocke, sorti, reexporte, detruit
    date_sortie = Column(Date)
    motif_sortie = Column(String(100))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    declaration = relationship("DeclarationEntrepot", back_populates="lignes_entrepot")


class FicheMagasin(Base):
    """Warehouse stock card - Movement tracking"""
    __tablename__ = "fiches_magasin"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_fiche = Column(String(50), unique=True, nullable=False, index=True)
    entrepot_id = Column(Integer, ForeignKey('entrepots_douane.id'))
    article_id = Column(Integer, ForeignKey('stocks.id'))
    designation = Column(String(200))
    numero_lot = Column(String(50))
    date_creation = Column(Date)
    stock_initial = Column(Numeric, default=0)
    stock_actuel = Column(Numeric, default=0)
    unite = Column(String(20))
    emplacement = Column(String(50))
    valeur_unitaire = Column(Numeric(15, 2))
    valeur_totale = Column(Numeric(15, 2))
    derniere_mouvement = Column(DateTime(timezone=True))
    statut = Column(String(20), default="actif")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    entrepot = relationship("EntrepotDouane", back_populates="fiches_magasin")
    mouvements = relationship("MouvementFiche", back_populates="fiche")


class MouvementFiche(Base):
    """Stock card movement entry"""
    __tablename__ = "mouvements_fiche"
    
    id = Column(Integer, primary_key=True, index=True)
    fiche_id = Column(Integer, ForeignKey('fiches_magasin.id'))
    type_mouvement = Column(String(20))  # "entree", "sortie", "transfert", "ajustement"
    date_mouvement = Column(DateTime(timezone=True))
    quantite = Column(Numeric)
    stock_apres = Column(Numeric)
    type_operation = Column(String(50))  # "reception", "livraison", "transfert", "inventaire"
    document_reference = Column(String(50))
    numero_declaration = Column(String(50))
    operateur = Column(String(100))
    motif = Column(String(200))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    fiche = relationship("FicheMagasin", back_populates="mouvements")


class InventaireDouanier(Base):
    """Customs inventory - Mandatory periodic control"""
    __tablename__ = "inventaires_douaniers"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_inventaire = Column(String(50), unique=True, nullable=False, index=True)
    entrepot_id = Column(Integer, ForeignKey('entrepots_douane.id'))
    type_inventaire = Column(String(20))  # "periodique", "exceptionnel", "final"
    date_debut = Column(Date)
    date_fin = Column(Date)
    operateur = Column(String(100))
    inspecteur_douane = Column(String(100))
    date_inspection = Column(Date)
    resultat = Column(String(20))  # "conforme", "ecart", "rejet"
    ecart_tonnage = Column(Numeric)
    ecart_valeur = Column(Numeric(15, 2))
    motif_ecart = Column(Text)
    measures_correctives = Column(Text)
    statut = Column(String(20), default="en_cours")  # en_cours, termine, valide
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    entrepot = relationship("EntrepotDouane", back_populates="inventaires_douaniers")
    lignes_inventaire = relationship("LigneInventaireDouanier", back_populates="inventaire")


class LigneInventaireDouanier(Base):
    """Customs inventory line"""
    __tablename__ = "lignes_inventaire_douanier"
    
    id = Column(Integer, primary_key=True, index=True)
    inventaire_id = Column(Integer, ForeignKey('inventaires_douaniers.id'))
    article_id = Column(Integer, ForeignKey('stocks.id'))
    designation = Column(String(200))
    numero_lot = Column(String(50))
    emplacement = Column(String(50))
    stock_theorique = Column(Numeric)
    stock_reel = Column(Numeric)
    ecart = Column(Numeric)
    unite = Column(String(20))
    valeur_unitaire = Column(Numeric(15, 2))
    valeur_ecart = Column(Numeric(15, 2))
    date_peremption = Column(Date)
    conforme = Column(Boolean, default=True)
    motif_ecart = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    inventaire = relationship("InventaireDouanier", back_populates="lignes_inventaire")


class SurveillanceMagazin(Base):
    """Warehouse surveillance records"""
    __tablename__ = "surveillance_magazin"
    
    id = Column(Integer, primary_key=True, index=True)
    entrepot_id = Column(Integer, ForeignKey('entrepots_douane.id'))
    date_patrouille = Column(DateTime(timezone=True))
    gardien = Column(String(100))
    type_controle = Column(String(50))  # "routine", "exceptionnel", "incident"
    zones_controlees = Column(Text)  # JSON array of zones
    incidents = Column(Text)
    anomalies = Column(Text)
    mesure_prise = Column(Text)
    statut = Column(String(20), default="normal")  # normal, alerte, incident
    photos = Column(Text)  # JSON array of photo paths
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    entrepot = relationship("EntrepotDouane")


class MiseConsommation(Base):
    """Release to consumption - Passage du régime suspensif"""
    __tablename__ = "mises_consommation"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_mise = Column(String(50), unique=True, nullable=False, index=True)
    declaration_entrepot_id = Column(Integer, ForeignKey('declarations_entrepot.id'))
    date_mise = Column(Date)
    valide_par = Column(String(100))
    fonction = Column(String(50))
    reference_sygdonia = Column(String(50))
    montant_dd = Column(Numeric(15, 2))
    montant_tva = Column(Numeric(15, 2))
    montant_total = Column(Numeric(15, 2))
    devise = Column(String(3), default="XAF")
    statut = Column(String(20), default="en_attente")  # en_attente, valide, rejete
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Reexportation(Base):
    """Re-export from warehouse"""
    __tablename__ = "reexportations"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_reexport = Column(String(50), unique=True, nullable=False, index=True)
    declaration_entrepot_id = Column(Integer, ForeignKey('declarations_entrepot.id'))
    pays_destination = Column(String(50))
    code_pays_destination = Column(String(2))
    date_reexport = Column(Date)
    motif = Column(String(200))
    moyen_transport = Column(String(50))
    reference_sygdonia = Column(String(50))
    statut = Column(String(20), default="en_attente")  # en_attente, autorise, refuse
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Destruction(Base):
    """Destruction of goods under customs supervision"""
    __tablename__ = "destructions"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_destruction = Column(String(50), unique=True, nullable=False, index=True)
    declaration_entrepot_id = Column(Integer, ForeignKey('declarations_entrepot.id'))
    date_demande = Column(Date)
    date_autorisation = Column(Date)
    date_destruction = Column(Date)
    motif = Column(Text)
    type_destruction = Column(String(50))  # "incineration", "broyage", "autre"
    autorise_par = Column(String(100))
    fonction = Column(String(50))
    temoin = Column(String(100))
    poids_destruct = Column(Numeric)
    valeur_destruct = Column(Numeric(15, 2))
    devise = Column(String(3), default="XAF")
    rapport_destruction = Column(String(255))
    photos = Column(Text)  # JSON array
    statut = Column(String(20), default="en_attente")  # en_attente, autorise, refuse, effectue
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class EntretienStock(Base):
    """Stock maintenance (repackaging, labeling)"""
    __tablename__ = "entretiens_stock"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_entretien = Column(String(50), unique=True, nullable=False, index=True)
    declaration_entrepot_id = Column(Integer, ForeignKey('declarations_entrepot.id'))
    date_entretien = Column(Date)
    type_entretien = Column(String(50))  # "reconditionnement", "etiquetage", "reemballage"
    article_id = Column(Integer, ForeignKey('stocks.id'))
    quantite = Column(Numeric)
    unite = Column(String(20))
    operateur = Column(String(100))
    description = Column(Text)
    autorise_par = Column(String(100))
    statut = Column(String(20), default="en_attente")  # en_attente, autorise, effectue
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class AssuranceStock(Base):
    """Stock insurance coverage"""
    __tablename__ = "assurances_stock"
    
    id = Column(Integer, primary_key=True, index=True)
    entrepot_id = Column(Integer, ForeignKey('entrepots_douane.id'))
    numero_police = Column(String(50), unique=True, nullable=False)
    assureur = Column(String(100))
    type_couverture = Column(String(50))  # "tous_risques", "feu", "vol", "degradation"
    valeur_assuree = Column(Numeric(15, 2))
    devise = Column(String(3), default="XAF")
    prime_annuelle = Column(Numeric(15, 2))
    date_debut = Column(Date)
    date_fin = Column(Date)
    franchise = Column(Numeric(15, 2))
    exclusions = Column(Text)
    statut = Column(String(20), default="actif")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    entrepot = relationship("EntrepotDouane")


class CompteRenduManutention(Base):
    """Handling operations report"""
    __tablename__ = "comptes_rendus_manutention"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_cr = Column(String(50), unique=True, nullable=False, index=True)
    entrepot_id = Column(Integer, ForeignKey('entrepots_douane.id'))
    date_operation = Column(Date)
    type_operation = Column(String(50))  # "reception", "expedition", "transfert"
    equipe = Column(String(100))
    equipement = Column(String(100))
    duree_heures = Column(Numeric)
    nombre_mouvements = Column(Integer)
    tonnage_total = Column(Numeric)
    observations = Column(Text)
    controle_par = Column(Integer, ForeignKey('users.id'))
    date_controle = Column(DateTime(timezone=True))
    conforme = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    entrepot = relationship("EntrepotDouane")
