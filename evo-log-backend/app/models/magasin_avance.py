"""
Advanced warehouse models - Complete logistics management for Cameroon/CEMAC
Includes all missing warehouse functionality for professional logistics
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, Enum, Date, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class MethodeEvaluationStock(str, enum.Enum):
    """Stock evaluation methods"""
    FIFO = "fifo"  # First In, First Out
    FEFO = "fefo"  # First Expired, First Out
    LIFO = "lifo"  # Last In, First Out
    CUMP = "cump"  # Weighted Average


class Peremption(Base):
    """Peremption/Expiration date management model"""
    __tablename__ = "peremptions"
    
    id = Column(Integer, primary_key=True, index=True)
    stock_id = Column(Integer, ForeignKey('stocks.id'), nullable=False)
    lot_numero = Column(String(50), nullable=False)
    date_fabrication = Column(Date)
    date_peremption = Column(Date, nullable=False)
    date_alerte = Column(Date)  # Alert date before expiration
    quantite = Column(Numeric, nullable=False)
    methode_evaluation = Column(Enum(MethodeEvaluationStock), default=MethodeEvaluationStock.FIFO)
    statut = Column(String(20), default="actif")  # actif, expire, vendu, consomme
    fournisseur_lot = Column(String(100))
    cout_acquisition = Column(Numeric)
    emplacement = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    stock = relationship("Stock")


class ReservationStock(Base):
    """Stock reservation model for future orders"""
    __tablename__ = "reservations_stock"
    
    id = Column(Integer, primary_key=True, index=True)
    stock_id = Column(Integer, ForeignKey('stocks.id'), nullable=False)
    numero_reservation = Column(String(50), unique=True, nullable=False)
    client_id = Column(Integer, ForeignKey('clients.id'), nullable=False)
    quantite_reservee = Column(Numeric, nullable=False)
    date_reservation = Column(Date, server_default=func.current_date())
    date_validite = Column(Date, nullable=False)
    statut = Column(String(20), default="en_attente")  # en_attente, confirme, annule, livre
    priorite = Column(String(20), default="normale")  # basse, normale, haute, critique
    commande_reference = Column(String(100))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    stock = relationship("Stock")


class KitArticle(Base):
    """Kit/Assembly model for grouped articles"""
    __tablename__ = "kits_articles"
    
    id = Column(Integer, primary_key=True, index=True)
    code_kit = Column(String(50), unique=True, nullable=False)
    nom_kit = Column(String(200), nullable=False)
    description = Column(Text)
    categorie = Column(String(50))
    est_actif = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    composants = relationship("ComposantKit", back_populates="kit")


class ComposantKit(Base):
    """Kit component model"""
    __tablename__ = "composants_kits"
    
    id = Column(Integer, primary_key=True, index=True)
    kit_id = Column(Integer, ForeignKey('kits_articles.id'), nullable=False)
    stock_id = Column(Integer, ForeignKey('stocks.id'), nullable=False)
    quantite = Column(Numeric, nullable=False)
    optionnel = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    kit = relationship("KitArticle", back_populates="composants")
    stock = relationship("Stock")


class EmplacementDetail(Base):
    """Detailed location model - Zones, aisles, shelves, bins"""
    __tablename__ = "emplacements_detail"
    
    id = Column(Integer, primary_key=True, index=True)
    code_emplacement = Column(String(50), unique=True, nullable=False)
    entrepot_id = Column(Integer, ForeignKey('entrepots.id'), nullable=False)
    zone = Column(String(50))  # Zone A, Zone B, etc.
    allee = Column(String(50))  # Allée 1, Allée 2, etc.
    rayon = Column(String(50))  # Rayon A, Rayon B, etc.
    niveau = Column(String(20))  # Niveau 1, Niveau 2, etc.
    casier = Column(String(20))  # Casier 1, Casier 2, etc.
    capacite = Column(Numeric)
    capacite_unite = Column(String(20))  # unite, palette, carton
    type_stockage = Column(String(50))  # standard, climatise, dangereux
    statut = Column(String(20), default="disponible")  # disponible, occupe, maintenance
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    entrepot = relationship("Entrepot")


class TransfertStock(Base):
    """Inter-warehouse stock transfer model"""
    __tablename__ = "transferts_stock"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_transfert = Column(String(50), unique=True, nullable=False)
    stock_id = Column(Integer, ForeignKey('stocks.id'), nullable=False)
    entrepot_source_id = Column(Integer, ForeignKey('entrepots.id'), nullable=False)
    entrepot_destination_id = Column(Integer, ForeignKey('entrepots.id'), nullable=False)
    quantite = Column(Numeric, nullable=False)
    date_transfert = Column(Date, server_default=func.current_date())
    date_reception = Column(Date)
    statut = Column(String(20), default="en_cours")  # en_cours, termine, annule
    motif = Column(Text)
    responsable_source = Column(Integer, ForeignKey('users.id'))
    responsable_destination = Column(Integer, ForeignKey('users.id'))
    cout_transport = Column(Numeric)
    numero_camion = Column(String(50))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    stock = relationship("Stock")
    entrepot_source = relationship("Entrepot", foreign_keys=[entrepot_source_id])
    entrepot_destination = relationship("Entrepot", foreign_keys=[entrepot_destination_id])


class InventaireTournant(Base):
    """Cyclic inventory model"""
    __tablename__ = "inventaires_tournants"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_inventaire = Column(String(50), unique=True, nullable=False)
    entrepot_id = Column(Integer, ForeignKey('entrepots.id'), nullable=False)
    date_debut = Column(Date, nullable=False)
    date_fin = Column(Date)
    type_inventaire = Column(String(50))  # partiel, complet, cyclique
    statut = Column(String(20), default="planifie")  # planifie, en_cours, termine, annule
    responsable = Column(Integer, ForeignKey('users.id'))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    entrepot = relationship("Entrepot")
    lignes_inventaire = relationship("LigneInventaire", back_populates="inventaire")


class LigneInventaire(Base):
    """Inventory line item model"""
    __tablename__ = "lignes_inventaire"
    
    id = Column(Integer, primary_key=True, index=True)
    inventaire_id = Column(Integer, ForeignKey('inventaires_tournants.id'), nullable=False)
    stock_id = Column(Integer, ForeignKey('stocks.id'), nullable=False)
    quantite_theorique = Column(Numeric, nullable=False)
    quantite_comptee = Column(Numeric)
    ecart = Column(Numeric)
    statut = Column(String(20), default="en_attente")  # en_attente, compte, ecart_corrige
    operateur = Column(Integer, ForeignKey('users.id'))
    date_comptage = Column(Date)
    commentaires = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    inventaire = relationship("InventaireTournant", back_populates="lignes_inventaire")
    stock = relationship("Stock")


class FournisseurStock(Base):
    """Supplier performance evaluation model"""
    __tablename__ = "fournisseurs_stock"
    
    id = Column(Integer, primary_key=True, index=True)
    fournisseur_id = Column(Integer, ForeignKey('fournisseurs.id'), nullable=False)
    delai_moyen_livraison = Column(Integer)  # En jours
    taux_livraison_ponctuelle = Column(Numeric)  # Pourcentage
    qualite_produit = Column(Numeric)  # Note 1-10
    prix_competitif = Column(Numeric)  # Note 1-10
    service_client = Column(Numeric)  # Note 1-10
    note_globale = Column(Numeric)
    date_evaluation = Column(Date, server_default=func.current_date())
    evaluateur = Column(Integer, ForeignKey('users.id'))
    commentaires = Column(Text)
    statut = Column(String(20), default="actif")  # actif, inactif
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    fournisseur = relationship("Fournisseur")


class CommandeFournisseur(Base):
    """Supplier order model - Automated replenishment"""
    __tablename__ = "commandes_fournisseur"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_commande = Column(String(50), unique=True, nullable=False)
    fournisseur_id = Column(Integer, ForeignKey('fournisseurs.id'), nullable=False)
    date_commande = Column(Date, server_default=func.current_date())
    date_livraison_prevue = Column(Date)
    date_livraison_reelle = Column(Date)
    statut = Column(String(20), default="en_cours")  # en_cours, livree, annule, partielle
    montant_total = Column(Numeric)
    devise = Column(String(10), default="XAF")
    mode_paiement = Column(String(50))
    conditions_paiement = Column(String(100))
    notes = Column(Text)
    createur = Column(Integer, ForeignKey('users.id'))
    approbateur = Column(Integer, ForeignKey('users.id'))
    date_approbation = Column(Date)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    fournisseur = relationship("Fournisseur")
    lignes_commande = relationship("LigneCommandeFournisseur", back_populates="commande")


class LigneCommandeFournisseur(Base):
    """Supplier order line item model"""
    __tablename__ = "lignes_commande_fournisseur"
    
    id = Column(Integer, primary_key=True, index=True)
    commande_id = Column(Integer, ForeignKey('commandes_fournisseur.id'), nullable=False)
    stock_id = Column(Integer, ForeignKey('stocks.id'), nullable=False)
    quantite_commandee = Column(Numeric, nullable=False)
    prix_unitaire = Column(Numeric, nullable=False)
    quantite_recue = Column(Numeric, default=0)
    prix_total = Column(Numeric)
    statut = Column(String(20), default="en_attente")  # en_attente, recu, annule
    date_reception = Column(Date)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    commande = relationship("CommandeFournisseur", back_populates="lignes_commande")
    stock = relationship("Stock")


class BonReception(Base):
    """Receipt document model"""
    __tablename__ = "bons_reception"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_bon = Column(String(50), unique=True, nullable=False)
    commande_fournisseur_id = Column(Integer, ForeignKey('commandes_fournisseur.id'))
    fournisseur_id = Column(Integer, ForeignKey('fournisseurs.id'), nullable=False)
    entrepot_id = Column(Integer, ForeignKey('entrepots.id'), nullable=False)
    date_reception = Column(Date, server_default=func.current_date())
    operateur = Column(Integer, ForeignKey('users.id'))
    validateur = Column(Integer, ForeignKey('users.id'))
    date_validation = Column(Date)
    statut = Column(String(20), default="en_attente")  # en_attente, valide, refuse
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    commande = relationship("CommandeFournisseur")
    fournisseur = relationship("Fournisseur")
    entrepot = relationship("Entrepot")
    lignes_bon = relationship("LigneBonReception", back_populates="bon")


class LigneBonReception(Base):
    """Receipt line item model"""
    __tablename__ = "lignes_bon_reception"
    
    id = Column(Integer, primary_key=True, index=True)
    bon_reception_id = Column(Integer, ForeignKey('bons_reception.id'), nullable=False)
    stock_id = Column(Integer, ForeignKey('stocks.id'), nullable=False)
    quantite_recue = Column(Numeric, nullable=False)
    quantite_commandee = Column(Numeric)
    prix_unitaire = Column(Numeric)
    emplacement = Column(String(100))
    numero_lot = Column(String(50))
    date_peremption = Column(Date)
    statut = Column(String(20), default="conforme")  # conforme, ecart, refuse
    commentaires = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    bon = relationship("BonReception", back_populates="lignes_bon")
    stock = relationship("Stock")


class BonSortie(Base):
    """Delivery document model"""
    __tablename__ = "bons_sortie"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_bon = Column(String(50), unique=True, nullable=False)
    client_id = Column(Integer, ForeignKey('clients.id'), nullable=False)
    entrepot_id = Column(Integer, ForeignKey('entrepots.id'), nullable=False)
    date_sortie = Column(Date, server_default=func.current_date())
    operateur = Column(Integer, ForeignKey('users.id'))
    validateur = Column(Integer, ForeignKey('users.id'))
    date_validation = Column(Date)
    statut = Column(String(20), default="en_attente")  # en_attente, valide, refuse
    type_sortie = Column(String(50))  # vente, consommation, transfert, perte
    commande_reference = Column(String(100))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    client = relationship("Client")
    entrepot = relationship("Entrepot")
    lignes_bon = relationship("LigneBonSortie", back_populates="bon")


class LigneBonSortie(Base):
    """Delivery line item model"""
    __tablename__ = "lignes_bons_sortie"
    
    id = Column(Integer, primary_key=True, index=True)
    bon_sortie_id = Column(Integer, ForeignKey('bons_sortie.id'), nullable=False)
    stock_id = Column(Integer, ForeignKey('stocks.id'), nullable=False)
    quantite_sortie = Column(Numeric, nullable=False)
    prix_unitaire = Column(Numeric)
    methode_evaluation = Column(Enum(MethodeEvaluationStock), default=MethodeEvaluationStock.FIFO)
    numero_lot = Column(String(50))
    date_peremption = Column(Date)
    statut = Column(String(20), default="conforme")  # conforme, ecart, refuse
    commentaires = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    bon = relationship("BonSortie", back_populates="lignes_bon")
    stock = relationship("Stock")


class RetourClient(Base):
    """Customer return model"""
    __tablename__ = "retours_client"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_retour = Column(String(50), unique=True, nullable=False)
    client_id = Column(Integer, ForeignKey('clients.id'), nullable=False)
    bon_sortie_id = Column(Integer, ForeignKey('bons_sortie.id'))
    date_retour = Column(Date, server_default=func.current_date())
    type_retour = Column(String(50))  # defectif, mauvais_quantite, refus, erreur_livraison
    motif = Column(Text)
    quantite = Column(Numeric)
    statut = Column(String(20), default="en_attente")  # en_attente, accepte, refuse, en_cours_traitement
    action = Column(String(50))  # remplacement, remboursement, destruction
    cout_traitement = Column(Numeric)
    notes = Column(Text)
    operateur = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    client = relationship("Client")
    bon_sortie = relationship("BonSortie")


class LitigeTransporteur(Base):
    """Carrier dispute model"""
    __tablename__ = "litiges_transporteur"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_litige = Column(String(50), unique=True, nullable=False)
    transporteur_id = Column(Integer, ForeignKey('fournisseurs.id'), nullable=False)
    mission_id = Column(Integer, ForeignKey('missions.id'))
    date_incident = Column(Date, server_default=func.current_date())
    type_litige = Column(String(50))  # retard, avarie, perte, erreur_livraison
    description = Column(Text, nullable=False)
    montant_reclame = Column(Numeric)
    statut = Column(String(20), default="en_cours")  # en_cours, resolu, refuse, justice
    resolution = Column(Text)
    date_resolution = Column(Date)
    assureur = Column(String(100))
    numero_police = Column(String(50))
    pieces_jointes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    transporteur = relationship("Fournisseur")
    mission = relationship("Mission")


class Colis(Base):
    """Package management model"""
    __tablename__ = "colis"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_colis = Column(String(50), unique=True, nullable=False)
    bon_sortie_id = Column(Integer, ForeignKey('bons_sortie.id'))
    type_colis = Column(String(50))  # carton, palette, caisse, sac
    poids = Column(Numeric)
    dimensions = Column(String(50))  # LxHxW format
    volume = Column(Numeric)
    contenu = Column(Text)
    fragile = Column(Boolean, default=False)
    empilable = Column(Boolean, default=False)
    emplacement = Column(String(100))
    date_etiquetage = Column(Date)
    operateur = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    bon_sortie = relationship("BonSortie")