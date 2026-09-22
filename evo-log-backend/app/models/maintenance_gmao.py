"""Maintenance models - CMMS/GMAO for Cameroon/CEMAC"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, Enum, Date, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class TypeMaintenance(str, enum.Enum):
    """Maintenance type enumeration"""
    PREVENTIVE = "preventive"
    CORRECTIVE = "corrective"
    PREDICTIVE = "predictive"
    CONDITIONNELLE = "conditionnelle"
    AMELIORATIVE = "ameliorative"


class PrioriteMaintenance(str, enum.Enum):
    """Maintenance priority enumeration"""
    CRITIQUE = "critique"
    HAUTE = "haute"
    MOYENNE = "moyenne"
    BASSE = "basse"


class StatutMaintenance(str, enum.Enum):
    """Maintenance status enumeration"""
    PLANIFIEE = "planifiee"
    EN_COURS = "en_cours"
    EN_ATTENTE = "en_attente"
    VALIDE = "valide"
    ANNULEE = "annulee"
    REJETE = "rejete"


class TypeEquipement(str, enum.Enum):
    """Equipment type enumeration"""
    GRUE = "grue"
    CHARIOT = "chariot"
    CAMION = "camion"
    CONTENEUR = "conteneur"
    PORTIQUE = "portique"
    GENERATEUR = "generateur"
    AUTRE = "autre"


class StatutEquipement(str, enum.Enum):
    """Equipment status enumeration"""
    OPERATIONNEL = "operationnel"
    EN_MAINTENANCE = "en_maintenance"
    HORS_SERVICE = "hors_service"
    RETRAITE = "retire"


class OrdreMaintenance(Base):
    """Maintenance work order"""
    __tablename__ = "ordres_maintenance"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_ordre = Column(String(50), unique=True, nullable=False, index=True)
    equipement_id = Column(Integer, ForeignKey('equipements_gmao.id'))
    type_maintenance = Column(Enum(TypeMaintenance))
    priorite = Column(Enum(PrioriteMaintenance))
    date_creation = Column(DateTime(timezone=True), server_default=func.now())
    date_planifiee = Column(Date)
    date_debut = Column(DateTime(timezone=True))
    date_fin = Column(DateTime(timezone=True))
    duree_estimee = Column(Integer)  # en heures
    duree_reelle = Column(Integer)
    description = Column(Text, nullable=False)
    travaux = Column(Text)
    technicien_id = Column(Integer, ForeignKey('users.id'))
    statut = Column(Enum(StatutMaintenance), default=StatutMaintenance.PLANIFIEE)
    cout_pieces = Column(Numeric(15, 2), default=0)
    cout_main_oeuvre = Column(Numeric(15, 2), default=0)
    cout_total = Column(Numeric(15, 2), default=0)
    devise = Column(String(3), default="XAF")
    observations = Column(Text)
    validation_technicien = Column(Boolean, default=False)
    date_validation = Column(Date)
    valide_par = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    equipement = relationship("EquipementGMAO", back_populates="ordres_maintenance")
    pieces_utilisees = relationship("PieceUtilisee", back_populates="ordre_maintenance")


class EquipementGMAO(Base):
    """Equipment/Asset"""
    __tablename__ = "equipements_gmao"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_serie = Column(String(50), unique=True, nullable=False, index=True)
    designation = Column(String(200), nullable=False)
    type_equipement = Column(Enum(TypeEquipement))
    marque = Column(String(100))
    modele = Column(String(100))
    annee_fabrication = Column(Integer)
    date_mise_service = Column(Date)
    localisation = Column(String(200))
    departement = Column(String(100))
    responsable = Column(String(100))
    statut = Column(Enum(StatutEquipement), default=StatutEquipement.OPERATIONNEL)
    date_achat = Column(Date)
    fournisseur = Column(String(200))
    cout_achat = Column(Numeric(15, 2))
    devise = Column(String(3), default="XAF")
    valeur_residuelle = Column(Numeric(15, 2))
    duree_vie_estimee = Column(Integer)  # en années
    description = Column(Text)
    caracteristiques = Column(Text)  # JSON
    manuel_fabricant = Column(String(255))
    manuel_maintenance = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    ordres_maintenance = relationship("OrdreMaintenance", back_populates="equipement")
    pieces_rechange = relationship("PieceRechangeGMAO", back_populates="equipement")
    calibrations = relationship("Calibration", back_populates="equipement")


class PlanMaintenance(Base):
    """Maintenance plan"""
    __tablename__ = "plans_maintenance"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_plan = Column(String(50), unique=True, nullable=False, index=True)
    equipement_id = Column(Integer, ForeignKey('equipements_gmao.id'))
    type_maintenance = Column(Enum(TypeMaintenance))
    frequence = Column(String(50))  # "journalier", "hebdomadaire", "mensuel", "trimestriel", "annuel"
    intervalle_jours = Column(Integer)
    date_debut = Column(Date, nullable=False)
    date_fin = Column(Date)
    description = Column(Text)
    taches = Column(Text)  # JSON array
    duree_estimee = Column(Integer)  # en heures
    technicien_assigne = Column(String(100))
    pieces_requises = Column(Text)  # JSON array
    statut = Column(String(20), default="actif")  # actif, suspendu, expire
    dernier_execution = Column(Date)
    prochaine_execution = Column(Date)
    nombre_executions = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class PieceRechangeGMAO(Base):
    """Spare part"""
    __tablename__ = "pieces_rechange_gmao"
    
    id = Column(Integer, primary_key=True, index=True)
    reference = Column(String(50), unique=True, nullable=False, index=True)
    designation = Column(String(200), nullable=False)
    equipement_id = Column(Integer, ForeignKey('equipements_gmao.id'))
    categorie = Column(String(100))
    marque = Column(String(100))
    modele = Column(String(100))
    description = Column(Text)
    stock_minimum = Column(Integer, default=0)
    stock_actuel = Column(Integer, default=0)
    stock_maximum = Column(Integer)
    unite = Column(String(20))
    prix_unitaire = Column(Numeric(15, 2))
    devise = Column(String(3), default="XAF")
    fournisseur = Column(String(200))
    reference_fournisseur = Column(String(100))
    emplacement_stockage = Column(String(200))
    date_achat = Column(Date)
    date_expiration = Column(Date)
    perissable = Column(Boolean, default=False)
    statut = Column(String(20), default="disponible")  # disponible, rupture, commande, perime
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    equipement = relationship("EquipementGMAO", back_populates="pieces_rechange")
    utilisations = relationship("PieceUtilisee", back_populates="piece_rechange")


class PieceUtilisee(Base):
    """Used spare part"""
    __tablename__ = "pieces_utilisees"
    
    id = Column(Integer, primary_key=True, index=True)
    ordre_maintenance_id = Column(Integer, ForeignKey('ordres_maintenance.id'))
    piece_rechange_id = Column(Integer, ForeignKey('pieces_rechange_gmao.id'))
    quantite = Column(Integer, nullable=False)
    cout_unitaire = Column(Numeric(15, 2))
    cout_total = Column(Numeric(15, 2))
    devise = Column(String(3), default="XAF")
    date_utilisation = Column(DateTime(timezone=True), server_default=func.now())
    technicien = Column(String(100))
    observations = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    ordre_maintenance = relationship("OrdreMaintenance", back_populates="pieces_utilisees")
    piece_rechange = relationship("PieceRechangeGMAO", back_populates="utilisations")


class Calibration(Base):
    """Calibration record"""
    __tablename__ = "calibrations"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_calibration = Column(String(50), unique=True, nullable=False, index=True)
    equipement_id = Column(Integer, ForeignKey('equipements_gmao.id'))
    instrument = Column(String(200), nullable=False)
    date_calibration = Column(Date, nullable=False)
    date_prochaine = Column(Date)
    intervalle_mois = Column(Integer)
    laboratoire = Column(String(200))
    technicien = Column(String(100))
    valeurs_avant = Column(Text)  # JSON
    valeurs_apres = Column(Text)  # JSON
    tolerance = Column(String(100))
    resultat = Column(String(20))  # "conforme", "non_conforme", "ajustable"
    actions = Column(Text)
    certificat = Column(String(255))
    statut = Column(String(20), default="valide")  # valide, expire, a_calibrer
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    equipement = relationship("EquipementGMAO", back_populates="calibrations")


class PerformanceEquipement(Base):
    """Equipment performance metrics"""
    __tablename__ = "performance_equipement"
    
    id = Column(Integer, primary_key=True, index=True)
    equipement_id = Column(Integer, ForeignKey('equipements_gmao.id'))
    periode = Column(String(50), nullable=False)  # "2026-01", "2026-Q1"
    date_mesure = Column(Date, nullable=False)
    temps_fonctionnement = Column(Numeric)  # en heures
    temps_arret = Column(Numeric)  # en heures
    nombre_pannes = Column(Integer)
    temps_maintenance = Column(Numeric)  # en heures
    mtbf = Column(Numeric)  # Mean Time Between Failures
    mttr = Column(Numeric)  # Mean Time To Repair
    disponibilite = Column(Numeric)  # %
    taux_panne = Column(Numeric)  # %
    cout_maintenance = Column(Numeric(15, 2))
    devise = Column(String(3), default="XAF")
    observations = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class HistoriqueMaintenance(Base):
    """Maintenance history"""
    __tablename__ = "historique_maintenance"
    
    id = Column(Integer, primary_key=True, index=True)
    equipement_id = Column(Integer, ForeignKey('equipements_gmao.id'))
    ordre_maintenance_id = Column(Integer, ForeignKey('ordres_maintenance.id'))
    date_action = Column(DateTime(timezone=True), server_default=func.now())
    action = Column(String(100), nullable=False)
    description = Column(Text)
    utilisateur_id = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
