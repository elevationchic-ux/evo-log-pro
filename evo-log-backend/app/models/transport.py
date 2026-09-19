"""
Transport models for managing vehicles, drivers, and missions
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, Enum, Numeric, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class CamionStatus(str, enum.Enum):
    """Enumeration for truck status"""
    ACTIVE = "active"
    IN_MAINTENANCE = "in_maintenance"
    OUT_OF_SERVICE = "out_of_service"
    RESERVED = "reserved"


class Camion(Base):
    """Truck/Vehicle model with multi-tenant company_id"""
    __tablename__ = "camions"
    __table_args__ = (
        UniqueConstraint('company_id', 'immatriculation', name='uq_camion_company_immat'),
    )
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=True, index=True)
    immatriculation = Column(String(20), nullable=False, index=True)
    marque = Column(String(50))
    modele = Column(String(50))
    annee = Column(Integer)
    capacite_tonnage = Column(Float)
    status = Column(Enum(CamionStatus), default=CamionStatus.ACTIVE)
    kilometrage = Column(Integer, default=0)
    date_mise_service = Column(DateTime(timezone=True))
    derniere_maintenance = Column(DateTime(timezone=True))
    prochaine_maintenance = Column(DateTime(timezone=True))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    missions = relationship("Mission", back_populates="camion")


class Conducteur(Base):
    """Driver model with multi-tenant company_id"""
    __tablename__ = "conducteurs"
    __table_args__ = (
        UniqueConstraint('company_id', 'numero_permis', name='uq_conducteur_company_permis'),
    )
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=True, index=True)
    nom = Column(String(100), nullable=False)
    prenom = Column(String(100), nullable=False)
    numero_permis = Column(String(50), nullable=False)
    date_expiration_permis = Column(DateTime(timezone=True))
    telephone = Column(String(20), nullable=False)
    email = Column(String(100))
    adresse = Column(Text)
    date_embauche = Column(DateTime(timezone=True))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    missions = relationship("Mission", back_populates="conducteur")


class MissionStatus(str, enum.Enum):
    """Enumeration for mission status"""
    PLANIFIEE = "planifiee"
    EN_COURS = "en_cours"
    TERMINEE = "terminee"
    ANNULEE = "annulee"
    EN_RETARD = "en_retard"


class Mission(Base):
    """Transport mission model with multi-tenant company_id"""
    __tablename__ = "missions"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uq_mission_company_ref'),
    )
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=True, index=True)
    reference = Column(String(50), nullable=False, index=True)
    camion_id = Column(Integer, ForeignKey('camions.id'))
    conducteur_id = Column(Integer, ForeignKey('conducteurs.id'))
    client_id = Column(Integer, ForeignKey('clients.id'))
    type_mission = Column(String(50))  # e.g., "livraison", "collecte", "transfert"
    statut = Column(Enum(MissionStatus), default=MissionStatus.PLANIFIEE)
    date_debut_prevue = Column(DateTime(timezone=True))
    date_fin_prevue = Column(DateTime(timezone=True))
    date_debut_reelle = Column(DateTime(timezone=True))
    date_fin_reelle = Column(DateTime(timezone=True))
    point_depart = Column(String(200))
    point_arrivee = Column(String(200))
    distance_km = Column(Numeric)
    cout_estime = Column(Numeric)
    cout_reel = Column(Numeric)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    camion = relationship("Camion", back_populates="missions")
    conducteur = relationship("Conducteur", back_populates="missions")
    trajets = relationship("Trajet", back_populates="mission")


class Trajet(Base):
    """Route/Journey model for tracking mission progress"""
    __tablename__ = "trajets"
    
    id = Column(Integer, primary_key=True, index=True)
    mission_id = Column(Integer, ForeignKey('missions.id'))
    sequence = Column(Integer)
    point_arret = Column(String(200))
    latitude = Column(Numeric)
    longitude = Column(Numeric)
    heure_arrivee_prevue = Column(DateTime(timezone=True))
    heure_arrivee_reelle = Column(DateTime(timezone=True))
    distance_parcourue = Column(Numeric)
    statut = Column(String(20), default="en_attente")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    mission = relationship("Mission", back_populates="trajets")