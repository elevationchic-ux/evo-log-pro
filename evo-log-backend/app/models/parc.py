"""
Parc models for fleet and equipment management
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, Enum, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class VehiculeStatus(str, enum.Enum):
    """Enumeration for vehicle status"""
    DISPONIBLE = "disponible"
    EN_USAGE = "en_usage"
    EN_MAINTENANCE = "en_maintenance"
    HORS_SERVICE = "hors_service"
    RESERVE = "reserve"


class Vehicule(Base):
    """Vehicle model for fleet management"""
    __tablename__ = "vehicules"
    
    id = Column(Integer, primary_key=True, index=True)
    immatriculation = Column(String(20), unique=True, nullable=False, index=True)
    marque = Column(String(50))
    modele = Column(String(50))
    annee = Column(Integer)
    type_vehicule = Column(String(50))  # e.g., "camion", "berline", "pick-up", "van"
    carburant = Column(String(20))  # e.g., "diesel", "essence", "gpl"
    capacite_reservoir = Column(Numeric)
    consommation_moyenne = Column(Numeric)
    status = Column(Enum(VehiculeStatus), default=VehiculeStatus.DISPONIBLE)
    kilometrage = Column(Integer, default=0)
    date_acquisition = Column(DateTime(timezone=True))
    date_mise_service = Column(DateTime(timezone=True))
    valeur_acquisition = Column(Numeric)
    valeur_actuelle = Column(Numeric)
    localisation = Column(String(100))
    assigne_a = Column(Integer, ForeignKey('users.id'))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    maintenance_records = relationship("Maintenance", back_populates="vehicule")


class Equipement(Base):
    """Equipment model for managing port equipment"""
    __tablename__ = "equipements"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    nom = Column(String(100), nullable=False)
    type_equipement = Column(String(50))  # e.g., "grue", "chariot", "conteneur"
    marque = Column(String(50))
    modele = Column(String(50))
    numero_serie = Column(String(50))
    capacite = Column(Numeric)
    status = Column(String(20), default="disponible")
    date_acquisition = Column(DateTime(timezone=True))
    localisation = Column(String(100))
    valeur = Column(Numeric)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Maintenance(Base):
    """Maintenance record model"""
    __tablename__ = "maintenances"
    
    id = Column(Integer, primary_key=True, index=True)
    vehicule_id = Column(Integer, ForeignKey('vehicules.id'))
    type_maintenance = Column(String(50))  # e.g., "preventive", "corrective", "premiere_mise"
    date_debut = Column(DateTime(timezone=True))
    date_fin = Column(DateTime(timezone=True))
    kilometrage = Column(Integer)
    description = Column(Text)
    cout = Column(Numeric)
    realisateur = Column(String(100))
    statut = Column(String(20), default="planifie")
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(Integer, ForeignKey('users.id'))
    
    # Relationships
    vehicule = relationship("Vehicule", back_populates="maintenance_records")