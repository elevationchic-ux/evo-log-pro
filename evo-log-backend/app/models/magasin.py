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


# ============================================================================
# WMS STORE DOMAIN (Tranche A)  articles, commandes, ordres de transfert,
# bandes de livraison. Ces tables sont newly modeled : elles portent le metier
# magasin/depot que le frontend appelle sous /api/v1/magasin/*.
# ============================================================================

class CommandeStatut(str, enum.Enum):
    """Cycle de vie d'une commande client/entrepot."""
    BROUILLON = "brouillon"
    VALIDEE = "validee"
    EN_PREPARATION = "en_preparation"
    PRETE = "prete"
    LIVREE = "livree"
    ANNULEE = "annulee"


class TransfertStatut(str, enum.Enum):
    """Cycle de vie d'un ordre de transfert inter-magasins."""
    BROUILLON = "brouillon"
    VALIDE = "valide"
    PAYE = "paye"
    EXPEDIE = "expedie"
    RECEPTIONNE = "receptionne"
    ANNULE = "annule"


class Article(Base):
    """Fiche article (master data) distinct de la ligne de stock par emplacement."""
    __tablename__ = "articles"
    __table_args__ = (
        UniqueConstraint('company_id', 'code', name='uix_article_company_code'),
    )

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=True, index=True)
    code = Column(String(50), nullable=False, index=True)
    designation = Column(String(200), nullable=False)
    description = Column(Text)
    categorie = Column(String(50))
    unite_mesure = Column(String(20))
    prix_unitaire = Column(Numeric)
    poids_kg = Column(Numeric)
    volume_m3 = Column(Numeric)
    code_barres = Column(String(100))
    hs_code = Column(String(20))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Commande(Base):
    """Commande d'entreposage / preparation (tete)."""
    __tablename__ = "commandes"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=True, index=True)
    reference = Column(String(50), nullable=False, index=True)
    client_id = Column(Integer, ForeignKey('clients.id'))
    type_commande = Column(String(30), default="sortie")  # entree / sortie / transfert
    statut = Column(Enum(CommandeStatut), default=CommandeStatut.BROUILLON)
    date_commande = Column(DateTime(timezone=True), server_default=func.now())
    date_livraison_prevue = Column(DateTime(timezone=True))
    montant_total = Column(Numeric)
    devise = Column(String(10), default="XAF")
    notes = Column(Text)
    cree_par = Column(Integer, ForeignKey('users.id'))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    lignes = relationship("LigneCommande", back_populates="commande", cascade="all, delete-orphan")


class LigneCommande(Base):
    """Ligne d'une commande."""
    __tablename__ = "lignes_commande"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=True, index=True)
    commande_id = Column(Integer, ForeignKey('commandes.id'), nullable=False, index=True)
    article_id = Column(Integer, ForeignKey('articles.id'))
    designation = Column(String(200))
    quantite = Column(Numeric, default=0)
    prix_unitaire = Column(Numeric)
    montant = Column(Numeric)

    commande = relationship("Commande", back_populates="lignes")


class OrdreTransfert(Base):
    """Ordre de transfert inter-magasins."""
    __tablename__ = "ordres_transfert"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=True, index=True)
    reference = Column(String(50), nullable=False, index=True)
    entrepot_source_id = Column(Integer, ForeignKey('entrepots.id'))
    entrepot_dest_id = Column(Integer, ForeignKey('entrepots.id'))
    article_id = Column(Integer, ForeignKey('articles.id'))
    quantite = Column(Numeric, default=0)
    statut = Column(Enum(TransfertStatut), default=TransfertStatut.BROUILLON)
    motif = Column(String(200))
    montant_paiement = Column(Numeric)
    cree_par = Column(Integer, ForeignKey('users.id'))
    date_transfert = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class BandeLivraison(Base):
    """Bande (fiche) de livraison  preparation physique d'une commande."""
    __tablename__ = "bandes_livraison"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=True, index=True)
    reference = Column(String(50), nullable=False, index=True)
    commande_id = Column(Integer, ForeignKey('commandes.id'))
    ordre_transfert_id = Column(Integer, ForeignKey('ordres_transfert.id'))
    client_id = Column(Integer, ForeignKey('clients.id'))
    statut = Column(String(30), default="en_preparation")  # en_preparation / prete / livre
    prepare_par = Column(String(100))
    poids_total = Column(Numeric)
    nb_colis = Column(Integer, default=0)
    date_preparation = Column(DateTime(timezone=True))
    date_livraison = Column(DateTime(timezone=True))
    notes = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())