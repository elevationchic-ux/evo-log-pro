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
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=True, index=True)
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


class ZoneParc(Base):
    """Zone du parc de stockage (decoupage physique de l'entrepot/parc)."""
    __tablename__ = "parc_zones"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=True, index=True)
    code = Column(String(30), nullable=False, index=True)
    nom = Column(String(100), nullable=False)
    type_zone = Column(String(50))  # e.g., "stockage", "quai", "parking", "refrigerie"
    superficie_m2 = Column(Numeric)
    capacite = Column(Integer, default=0)
    statut = Column(String(20), default="active")  # active / maintenance / fermee
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    emplacements = relationship(
        "EmplacementParc", back_populates="zone", cascade="all, delete-orphan"
    )


class EmplacementParc(Base):
    """Emplacement (position de stockage) rattache a une zone du parc."""
    __tablename__ = "parc_emplacements"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=True, index=True)
    zone_id = Column(Integer, ForeignKey('parc_zones.id'), index=True)
    code = Column(String(30), nullable=False, index=True)
    type_emplacement = Column(String(50))  # e.g., "sol", "rayonnage", "bac", "silos"
    statut = Column(String(20), default="libre")  # libre / occupe / reserve / bloque
    max_weight_kg = Column(Numeric)
    contenu = Column(String(200))  # ce qui y est stocke (libelle libre)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    zone = relationship("ZoneParc", back_populates="emplacements")


class MouvementParc(Base):
    """Evenement gate in / gate out : entree ou sortie d'un conteneur
    (ou vehicule) dans une emplacement du parc."""
    __tablename__ = "parc_mouvements"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=True, index=True)
    sens = Column(String(10), nullable=False)  # entree / sortie
    numero_conteneur = Column(String(20), index=True)
    type_conteneur = Column(String(20))   # e.g., 20DRY, 40HC
    etat = Column(String(30))             # e.g., BON_ETAT, AVARIE
    poids_tare_kg = Column(Numeric)
    emplacement_id = Column(Integer, ForeignKey('parc_emplacements.id'), index=True)
    immatriculation = Column(String(20))  # si vehicule associe
    chauffeur = Column(String(100))
    motif = Column(String(200))
    enregistre_par = Column(Integer, ForeignKey('users.id'))
    horodatage = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class CarburantRecord(Base):
    """Ticket de carburant / plein effectue pour un vehicule de la flotte."""
    __tablename__ = "fleet_carburant_records"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=True, index=True)
    vehicule_id = Column(Integer, ForeignKey('vehicules.id'), index=True)
    immatriculation = Column(String(20))  # redondance utile si vehicule absent
    date_plein = Column(DateTime(timezone=True), server_default=func.now())
    litres = Column(Numeric)
    cout = Column(Numeric)
    station = Column(String(100))
    mode_paiement = Column(String(30))
    kilometrage = Column(Integer)
    notes = Column(Text)
    # Exploitation carburant (Tranche D) : le ticket saisi par le chauffeur porte
    # son numero physique, le prix au litre releve a la pompe et le rattachement a
    # la mission / au conducteur qui a effectue le plein.
    numero_ticket = Column(String(50))
    prix_litre = Column(Numeric)
    mission_id = Column(Integer, ForeignKey('missions.id'))
    conducteur_id = Column(Integer, ForeignKey('conducteurs.id'))
    statut = Column(String(20), default="valide")  # valide, en_attente, rejete
    # Index releve au plein precedent : sans lui, aucune consommation aux 100 km
    # n'est calculable (le controle FuelGuard reste alors sans mesure).
    index_precedent = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())