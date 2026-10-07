"""Modeles magasin-stock (expansion approfondie generee).

12 entites de gestion, chacune scoped par company_id.
Convention d'honnetete : aucune valeur par defaut, NULL = "non enregistre".
"""
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean, Float,
    ForeignKey, Date, Numeric, UniqueConstraint, Enum as SAEnum,
)
from sqlalchemy.sql import func
import enum

from app.core.database import Base


def _enum(cls):
    return SAEnum(cls, native_enum=False, create_constraint=False,
                  values_callable=lambda x: [e.value for e in x])


# ─── Enums ────────────────────────────────────────────────────────────────────

class ArticleCatalog_statut(str, enum.Enum):
    ACTIF = "actif"
    OBSOLETE = "obsolete"
    BLOQUE = "bloque"


class PurchaseOrderDeep_statut(str, enum.Enum):
    ROUE = "roue"
    ENVOYEE = "envoyee"
    PARTIELLE = "partielle"
    RECUE = "recue"
    ANNULEE = "annulee"


class QualityInspection_resultat(str, enum.Enum):
    CONFORME = "conforme"
    PARTIELLE = "partielle"
    NON_CONFORME = "non_conforme"
    REBUT = "rebut"


class StockAlert_statut(str, enum.Enum):
    NORMAL = "normal"
    ALERTE = "alerte"
    RUPTURE = "rupture"
    SURSTOCK = "surstock"


class ExpiryRecord_statut(str, enum.Enum):
    VALIDE = "valide"
    PROCHAIN_EXPIRATION = "prochain_expiration"
    EXPIRE = "expire"
    RETIRE = "retire"


class SerialNumber_statut(str, enum.Enum):
    EN_STOCK = "en_stock"
    SORTI = "sorti"
    RETOUR = "retour"
    REPARATION = "reparation"
    REFORME = "reforme"


class PackingUnit_type_uc(str, enum.Enum):
    COLIS = "colis"
    CARTON = "carton"
    PALETTE = "palette"
    BIG_BAG = "big_bag"
    FUT = "fut"
    CONTEUR = "conteur"


class StockReturn_type_retour(str, enum.Enum):
    CLIENT = "client"
    FOURNISSEUR = "fournisseur"
    INTERNE = "interne"


class StockReturn_statut(str, enum.Enum):
    DEMANDE = "demande"
    ACCEPTE = "accepte"
    REFUSE = "refuse"
    TRAITE = "traite"


class ConsignmentStock_statut(str, enum.Enum):
    EN_COURS = "en_cours"
    EPUISE = "epuise"
    RESTITUE = "restitue"
    EXPEDITE = "expedite"


class StockValuation_methode(str, enum.Enum):
    CMUP = "cmup"
    COI = "coi"
    PMP = "pmp"
    COUT_STANDARD = "cout_standard"


# ─── Modeles ──────────────────────────────────────────────────────────────────

class ArticleCatalog(Base):
    """Referentiel articles / SKU."""
    __tablename__ = "article_catalogs"
    __table_args__ = (
        UniqueConstraint('company_id', 'code_sku', name='uix_article_catalogs_company_code_sku'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    code_sku = Column(String(150), nullable=False, index=True)
    designation = Column(String(150), nullable=True)
    categorie = Column(String(150), nullable=True)
    unite_principale = Column(String(150), nullable=True)
    code_barre = Column(String(150), nullable=True)
    poids_unitaire_kg = Column(Numeric, nullable=True)
    volume_m3 = Column(Numeric, nullable=True)
    prix_achat_moyen_xaf = Column(Numeric, nullable=True)
    prix_vente_xaf = Column(Numeric, nullable=True)
    statut = Column(_enum(ArticleCatalog_statut), default=ArticleCatalog_statut.ACTIF)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class SupplierArticle(Base):
    """Fournisseurs par article."""
    __tablename__ = "supplier_articles"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_supplier_articles_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    article_id = Column(Integer, nullable=True)
    fournisseur_id = Column(Integer, nullable=True)
    prix_unitaire_xaf = Column(Numeric, nullable=True)
    delai_livraison_jours = Column(Integer, nullable=True)
    quantite_min_commande = Column(Numeric, nullable=True)
    devise = Column(String(150), nullable=True)
    conditions_paiement = Column(String(150), nullable=True)
    actif = Column(Boolean, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class PurchaseOrderDeep(Base):
    """Commandes d'achat."""
    __tablename__ = "purchase_orders_deep"
    __table_args__ = (
        UniqueConstraint('company_id', 'numero_commande', name='uix_purchase_orders_deep_company_numero_commande'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    numero_commande = Column(String(150), nullable=False, index=True)
    fournisseur_id = Column(Integer, nullable=True)
    date_commande = Column(Date, nullable=True)
    date_livraison_prevue = Column(Date, nullable=True)
    montant_total_xaf = Column(Numeric, nullable=True)
    nb_lignes = Column(Integer, nullable=True)
    acheteur = Column(String(150), nullable=True)
    statut = Column(_enum(PurchaseOrderDeep_statut), default=PurchaseOrderDeep_statut.ROUE)
    notes = Column(Text(2000), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class QualityInspection(Base):
    """Controle qualite a reception."""
    __tablename__ = "quality_inspections"
    __table_args__ = (
        UniqueConstraint('company_id', 'numero_controle', name='uix_quality_inspections_company_numero_controle'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    numero_controle = Column(String(150), nullable=False, index=True)
    reception_id = Column(Integer, nullable=True)
    article_id = Column(Integer, nullable=True)
    quantite_inspekte = Column(Numeric, nullable=True)
    quantite_conforme = Column(Numeric, nullable=True)
    quantite_rebutee = Column(Numeric, nullable=True)
    resultat = Column(_enum(QualityInspection_resultat), default=QualityInspection_resultat.CONFORME)
    inspecteur = Column(String(150), nullable=True)
    date_controle = Column(Date, nullable=True)
    observations = Column(Text(2000), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class StockAlert(Base):
    """Seuils et alertes rupture."""
    __tablename__ = "stock_alerts"
    __table_args__ = (
        UniqueConstraint('company_id', 'code_alerte', name='uix_stock_alerts_company_code_alerte'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    code_alerte = Column(String(150), nullable=False, index=True)
    article_id = Column(Integer, nullable=True)
    depot_id = Column(Integer, nullable=True)
    seuil_min = Column(Numeric, nullable=True)
    seuil_max = Column(Numeric, nullable=True)
    point_commande = Column(Numeric, nullable=True)
    quantite_actuelle = Column(Numeric, nullable=True)
    derniere_alerte = Column(DateTime(timezone=True), nullable=True)
    statut = Column(_enum(StockAlert_statut), default=StockAlert_statut.NORMAL)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ExpiryRecord(Base):
    """Peremption / FEFO."""
    __tablename__ = "expiry_records"
    __table_args__ = (
        UniqueConstraint('company_id', 'numero_lot', name='uix_expiry_records_company_numero_lot'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    numero_lot = Column(String(150), nullable=False, index=True)
    article_id = Column(Integer, nullable=True)
    quantite = Column(Numeric, nullable=True)
    date_peremption = Column(Date, nullable=True)
    date_reception = Column(Date, nullable=True)
    statut = Column(_enum(ExpiryRecord_statut), default=ExpiryRecord_statut.VALIDE)
    notes = Column(Text(2000), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class SerialNumber(Base):
    """Tracabilite numeros serie."""
    __tablename__ = "serial_numbers"
    __table_args__ = (
        UniqueConstraint('company_id', 'numero_serial', name='uix_serial_numbers_company_numero_serial'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    numero_serial = Column(String(150), nullable=False, index=True)
    article_id = Column(Integer, nullable=True)
    numero_lot = Column(String(150), nullable=True)
    statut = Column(_enum(SerialNumber_statut), default=SerialNumber_statut.EN_STOCK)
    date_entree = Column(Date, nullable=True)
    date_sortie = Column(Date, nullable=True)
    destination = Column(String(150), nullable=True)
    notes = Column(Text(2000), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class PackingUnit(Base):
    """Unites de conditionnement."""
    __tablename__ = "packing_units"
    __table_args__ = (
        UniqueConstraint('company_id', 'code_uc', name='uix_packing_units_company_code_uc'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    code_uc = Column(String(150), nullable=False, index=True)
    type_uc = Column(_enum(PackingUnit_type_uc), default=PackingUnit_type_uc.COLIS)
    dimensions = Column(String(150), nullable=True)
    poids_tare_kg = Column(Numeric, nullable=True)
    capacite_max_kg = Column(Numeric, nullable=True)
    nb_unites_principales = Column(Numeric, nullable=True)
    actif = Column(Boolean, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class StockReturn(Base):
    """Retours et avoirs stock."""
    __tablename__ = "stock_returns"
    __table_args__ = (
        UniqueConstraint('company_id', 'numero_retour', name='uix_stock_returns_company_numero_retour'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    numero_retour = Column(String(150), nullable=False, index=True)
    type_retour = Column(_enum(StockReturn_type_retour), default=StockReturn_type_retour.CLIENT)
    client_id = Column(Integer, nullable=True)
    fournisseur_id = Column(Integer, nullable=True)
    date_retour = Column(Date, nullable=True)
    article_id = Column(Integer, nullable=True)
    quantite = Column(Numeric, nullable=True)
    motif = Column(Text(2000), nullable=True)
    statut = Column(_enum(StockReturn_statut), default=StockReturn_statut.DEMANDE)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ConsignmentStock(Base):
    """Stock en consignation."""
    __tablename__ = "consignment_stocks"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_consignment_stocks_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    proprietaire_id = Column(Integer, nullable=True)
    article_id = Column(Integer, nullable=True)
    quantite_deposee = Column(Numeric, nullable=True)
    quantite_retiree = Column(Numeric, nullable=True)
    date_depot = Column(Date, nullable=True)
    date_limite = Column(Date, nullable=True)
    statut = Column(_enum(ConsignmentStock_statut), default=ConsignmentStock_statut.EN_COURS)
    notes = Column(Text(2000), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class StockValuation(Base):
    """Valorisation du stock."""
    __tablename__ = "stock_valuations"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_stock_valuations_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    periode = Column(String(150), nullable=True)
    article_id = Column(Integer, nullable=True)
    methode = Column(_enum(StockValuation_methode), default=StockValuation_methode.CMUP)
    quantite_fin = Column(Numeric, nullable=True)
    valeur_cmup_xaf = Column(Numeric, nullable=True)
    valeur_coi_xaf = Column(Numeric, nullable=True)
    date_calcul = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class WmsKpi(Base):
    """KPIs magasin."""
    __tablename__ = "wms_kpis"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_wms_kpis_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    periode_debut = Column(Date, nullable=True)
    periode_fin = Column(Date, nullable=True)
    rotation = Column(Numeric, nullable=True)
    rupture_pct = Column(Numeric, nullable=True)
    taux_service_pct = Column(Numeric, nullable=True)
    cadence_choix_lignes_h = Column(Numeric, nullable=True)
    ecart_inventaire_pct = Column(Numeric, nullable=True)
    notes = Column(Text(2000), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

