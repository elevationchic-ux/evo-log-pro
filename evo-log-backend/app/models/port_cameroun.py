"""Cameroon Ports models - Specific ports: Douala (PAD), Kribi (PK), Limbé, Tiko"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, Enum, Date, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class TypePort(str, enum.Enum):
    """Port type enumeration"""
    MARCHANDISES = "marchandises"
    PETROLIER = "petrolier"
    MIXTE = "mixte"
    PECHE = "peche"
    BANANES = "bananes"


class TypeTerminal(str, enum.Enum):
    """Terminal type enumeration"""
    CONTENEURS = "conteneurs"
    VRAC = "vrac"
    RO_RO = "ro_ro"
    MULTIPURPOSE = "multipurpose"
    PETROLIER = "petrolier"


class PortCameroun(Base):
    """Port spécifique Cameroun"""
    __tablename__ = "ports_cameroun"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(10), unique=True, nullable=False, index=True)  # DOU, KRI, LIM, TIK
    nom = Column(String(100), nullable=False)  # Port de Douala, Port de Kribi
    type_port = Column(Enum(TypePort), nullable=False)
    localisation = Column(String(100))  # Latitude, Longitude
    capacite_annuelle_tonnes = Column(Numeric)
    profondeur_m = Column(Numeric)
    nombre_postes_quai = Column(Integer)
    operateur = Column(String(100))  # PAD, PAK
    zone_franche = Column(Boolean, default=False)
    adresse = Column(String(200))
    ville = Column(String(50))
    region = Column(String(50))
    telephone = Column(String(20))
    email = Column(String(100))
    website = Column(String(255))
    est_actif = Column(Boolean, default=True)
    date_ouverture = Column(Date)
    description = Column(Text)
    caracteristiques = Column(Text)  # JSON
    services_disponibles = Column(Text)  # JSON
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    terminaux = relationship("TerminalPortuaire", back_populates="port")


class TerminalPortuaire(Base):
    """Terminal portuaire"""
    __tablename__ = "terminaux_portuaires"
    
    id = Column(Integer, primary_key=True, index=True)
    port_id = Column(Integer, ForeignKey('ports_cameroun.id'), nullable=False)
    code = Column(String(20), unique=True, nullable=False)  # TCO, TVT, TMK
    nom = Column(String(100), nullable=False)
    type_terminal = Column(Enum(TypeTerminal), nullable=False)
    operateur = Column(String(100))  # Bolloré, MSC, etc.
    capacite_teus = Column(Integer)
    superficie_ha = Column(Numeric)
    longueur_quai_m = Column(Numeric)
    profondeur_m = Column(Numeric)
    nombre_grues = Column(Integer)
    nombre_chariots = Column(Integer)
    capacite_stockage = Column(Integer)
    services = Column(Text)  # JSON
    est_actif = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    port = relationship("PortCameroun", back_populates="terminaux")
    tarifs = relationship("TarifPortuaire", back_populates="terminal")


class TarifPortuaire(Base):
    """Tarif portuaire Cameroun (TPC - Tarif Portuaire Cameroun)"""
    __tablename__ = "tarifs_portuaires"
    
    id = Column(Integer, primary_key=True, index=True)
    code_tarif = Column(String(20), unique=True, nullable=False)
    designation = Column(String(200), nullable=False)
    categorie = Column(String(50), nullable=False)  # ACconage, Manutention, Stockage, THC
    sous_categorie = Column(String(50))
    unite = Column(String(20), nullable=False)  # TONNE, TEU, M3, CONTENEUR
    prix_unitaire = Column(Numeric, nullable=False)
    devise = Column(String(3), default="XAF")
    date_application = Column(Date, nullable=False)
    date_expiration = Column(Date)
    taux_tva = Column(Numeric, default=19.25)
    est_actif = Column(Boolean, default=True)
    terminal_id = Column(Integer, ForeignKey('terminaux_portuaires.id'))
    notes = Column(Text)
    reference_reglementaire = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    terminal = relationship("TerminalPortuaire", back_populates="tarifs")


class EquipementPortuaire(Base):
    """Équipement portuaire"""
    __tablename__ = "equipements_portuaires"
    
    id = Column(Integer, primary_key=True, index=True)
    terminal_id = Column(Integer, ForeignKey('terminaux_portuaires.id'))
    type_equipement = Column(String(50), nullable=False)  # GRUE, CHARIOT, REACH_STACKER, CHASSIS
    modele = Column(String(100))
    fabricant = Column(String(100))
    numero_serie = Column(String(50))
    capacite_tonnes = Column(Numeric)
    date_acquisition = Column(Date)
    date_mise_service = Column(Date)
    date_derniere_maintenance = Column(Date)
    prochaine_maintenance = Column(Date)
    statut = Column(String(20), default="operationnel")  # operationnel, maintenance, hors_service
    emplacement = Column(String(100))
    est_disponible = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ZonePortuaire(Base):
    """Zone portuaire"""
    __tablename__ = "zones_portuaires"
    
    id = Column(Integer, primary_key=True, index=True)
    terminal_id = Column(Integer, ForeignKey('terminaux_portuaires.id'))
    code = Column(String(20), unique=True, nullable=False)
    nom = Column(String(100), nullable=False)
    type_zone = Column(String(50))  # STOCKAGE, QUAI, MANUTENTION, SECURITE
    capacite = Column(Integer)
    capacite_utilisee = Column(Integer, default=0)
    superficie_m2 = Column(Numeric)
    localisation = Column(String(100))
    restrictions = Column(Text)  # JSON
    est_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
