"""Reporting models - Executive dashboard and multi-dimensional reporting for Cameroon/CEMAC"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, Enum, Date, JSON, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class TypeRapport(str, enum.Enum):
    """Report type enumeration"""
    EXECUTIF = "executif"
    OPERATIONNEL = "operationnel"
    FINANCIER = "financier"
    DOUANIER = "douanier"
    QHSE = "qhse"
    PERFORMANCE = "performance"
    AUTRE = "autre"


class FormatExport(str, enum.Enum):
    """Export format enumeration"""
    PDF = "pdf"
    EXCEL = "excel"
    CSV = "csv"
    JSON = "json"
    HTML = "html"


class FrequenceRapport(str, enum.Enum):
    """Report frequency enumeration"""
    QUOTIDIEN = "quotidien"
    HEBDOMADAIRE = "hebdomadaire"
    MENSUEL = "mensuel"
    TRIMESTRIEL = "trimestriel"
    ANNUEL = "annuel"
    A_LA_DEMANDE = "a_la_demande"


class StatutRapport(str, enum.Enum):
    """Report status enumeration"""
    EN_PREPARATION = "en_preparation"
    DISPONIBLE = "disponible"
    EN_COURS = "en_cours"
    ECHOUE = "echoue"
    ANNULE = "annule"


class DashboardExecutif(Base):
    """Executive dashboard"""
    __tablename__ = "dashboards_executifs"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    nom = Column(String(200), nullable=False)
    description = Column(Text)
    layout = Column(JSON)  # Dashboard layout configuration
    widgets = Column(JSON)  # Dashboard widgets configuration
    filtres = Column(JSON)  # Available filters
    role_autorise = Column(JSON)  # Authorized roles
    proprietaire_id = Column(Integer, ForeignKey('users.id'))
    actif = Column(Boolean, default=True)
    date_creation = Column(DateTime(timezone=True), server_default=func.now())
    modifie_par = Column(String(100))
    date_modification = Column(DateTime(timezone=True), onupdate=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class KPI(Base):
    """Key Performance Indicator"""
    __tablename__ = "kpis"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    nom = Column(String(200), nullable=False)
    description = Column(Text)
    type_rapport = Column(String(50))
    categorie = Column(String(50))
    formule = Column(Text)  # Calculation formula
    unite = Column(String(20))
    objectif = Column(Numeric)
    seuil_alerte = Column(Numeric)
    couleur_alerte = Column(String(20))  # hex color
    source_donnees = Column(String(100))  # Data source table
    frequence_calcul = Column(String(50))
    derniere_valeur = Column(Numeric)
    date_derniere_valeur = Column(DateTime(timezone=True))
    tendance = Column(String(20))  # "hausse", "baisse", "stable"
    variation_pourcentage = Column(Numeric)
    historique = Column(JSON)  # Historical values
    actif = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Rapport(Base):
    """Report entity"""
    __tablename__ = "rapports"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_rapport = Column(String(50), unique=True, nullable=False, index=True)
    titre = Column(String(200), nullable=False)
    description = Column(Text)
    type_rapport = Column(String(50))
    frequence = Column(Enum(FrequenceRapport))
    requetes = Column(JSON)  # SQL queries for data
    colonnes = Column(JSON)  # Report columns configuration
    filtres = Column(JSON)  # Available filters
    parametres = Column(JSON)  # Report parameters
    tri = Column(JSON)  # Sort configuration
    graphiques = Column(JSON)  # Charts configuration
    tables = Column(JSON)  # Tables configuration
    statut = Column(Enum(StatutRapport), default=StatutRapport.EN_PREPARATION)
    cree_par = Column(Integer, ForeignKey('users.id'))
    date_creation = Column(DateTime(timezone=True), server_default=func.now())
    date_generation = Column(DateTime(timezone=True))
    date_expiration = Column(DateTime(timezone=True))
    fichier = Column(String(255))
    taille_octets = Column(Integer)
    nombre_lignes = Column(Integer)
    duree_generation = Column(Integer)  # en secondes
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class HistoriqueGeneration(Base):
    """Report generation history"""
    __tablename__ = "historique_generation"
    
    id = Column(Integer, primary_key=True, index=True)
    rapport_id = Column(Integer, ForeignKey('rapports.id'))
    utilisateur_id = Column(Integer, ForeignKey('users.id'))
    parametres = Column(JSON)
    date_generation = Column(DateTime(timezone=True), server_default=func.now())
    statut = Column(String(20))  # "succes", "echoue"
    duree_secondes = Column(Integer)
    nombre_lignes = Column(Integer)
    fichier = Column(String(255))
    taille_octets = Column(Integer)
    erreur = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Export(Base):
    """Export entity"""
    __tablename__ = "exports"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_export = Column(String(50), unique=True, nullable=False, index=True)
    rapport_id = Column(Integer, ForeignKey('rapports.id'))
    type_rapport = Column(String(50))
    format_export = Column(String(50))
    parametres = Column(JSON)
    date_demande = Column(DateTime(timezone=True), server_default=func.now())
    date_debut = Column(DateTime(timezone=True))
    date_fin = Column(DateTime(timezone=True))
    statut = Column(String(20), default="en_attente")  # en_attente, en_cours, termine, echoue
    utilisateur_id = Column(Integer, ForeignKey('users.id'))
    progression = Column(Integer, default=0)
    fichier = Column(String(255))
    taille_octets = Column(Integer)
    nombre_enregistrements = Column(Integer)
    erreur = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Widget(Base):
    """Dashboard widget"""
    __tablename__ = "widgets"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    nom = Column(String(200), nullable=False)
    type_widget = Column(String(50))  # "kpi", "chart", "table", "gauge", "timeline"
    type_rapport = Column(String(50))
    requete = Column(Text)  # SQL query or data source
    configuration = Column(JSON)  # Widget configuration
    couleurs = Column(JSON)  # Color scheme
    filtres = Column(JSON)  # Widget filters
    refresh_secondes = Column(Integer, default=300)
    largeur = Column(Integer)  # 1-12 (grid columns)
    hauteur = Column(Integer)  # in pixels
    position_x = Column(Integer)
    position_y = Column(Integer)
    actif = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class DrillDown(Base):
    """Drill-down configuration"""
    __tablename__ = "drill_downs"
    
    id = Column(Integer, primary_key=True, index=True)
    kpi_id = Column(Integer, ForeignKey('kpis.id'))
    niveau = Column(Integer)  # Drill-down level
    filtre = Column(JSON)  # Filter condition
    detail = Column(Text)  # Detail view configuration
    rapports_lies = Column(JSON)  # Linked reports
    actif = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(Date, onupdate=func.now())


class ScheduleReport(Base):
    """Scheduled report"""
    __tablename__ = "schedule_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    rapport_id = Column(Integer, ForeignKey('rapports.id'))
    nom = Column(String(200), nullable=False)
    frequence = Column(Enum(FrequenceRapport))
    jour_execution = Column(String(20))  # "monday", "tuesday", etc.
    heure_execution = Column(String(5))  # "HH:MM"
    destinataires = Column(JSON)  # Recipients list
    format_export = Column(String(50))
    actif = Column(Boolean, default=True)
    derniere_execution = Column(DateTime(timezone=True))
    prochaine_execution = Column(DateTime(timezone=True))
    cree_par = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class TableauBordOperationnel(Base):
    """Operational dashboard"""
    __tablename__ = "tableaux_bord_operationnels"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    nom = Column(String(200), nullable=False)
    module = Column(String(50))  # "acconage", "transit", "transport", etc.
    metriques = Column(JSON)  # Operational metrics
    graphiques = Column(JSON)  # Charts configuration
    alertes = Column(JSON)  # Alerts configuration
    filtres = Column(JSON)  # Filters
    actualisation = Column(JSON)  # Real-time updates
    derniere_actualisation = Column(DateTime(timezone=True))
    responsable = Column(String(100))
    actif = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class IndicateurFinancier(Base):
    """Financial indicator"""
    __tablename__ = "indicateurs_financiers"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    nom = Column(String(200), nullable=False)
    description = Column(Text)
    categorie = Column(String(50))  # "rentabilite", "liquidite", "endettement", etc.
    periode = Column(String(50))  # "mensuel", "trimestriel", "annuel"
    valeur_actuelle = Column(Numeric)
    valeur_precedente = Column(Numeric)
    objectif = Column(Numeric)
    variation = Column(Numeric)
    tendance = Column(String(20))
    unite = Column(String(20))
    devise = Column(String(3), default="XAF")
    date_mesure = Column(Date)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class IndicateurDouanier(Base):
    """Customs indicator"""
    __tablename__ = "indicateurs_douaniers"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    nom = Column(String(200), nullable=False)
    description = Column(Text)
    categorie = Column(String(50))  # "declarations", "delaies", "litiges", etc.
    periode = Column(String(50))
    valeur_actuelle = Column(Numeric)
    valeur_precedente = Column(Numeric)
    objectif = Column(Numeric)
    variation = Column(Numeric)
    tendance = Column(String(20))
    unite = Column(String(20))
    date_mesure = Column(Date)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
