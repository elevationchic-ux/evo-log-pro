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
    # Exploitation flotte (Tranche D) : blocage administratif et atelage.
    # Un camion bloque (panne grave, assurance, immobilisation judiciaire) ne
    # doit plus etre affectable a une mission ; l'information est portee par la
    # fiche vehicule, pas par un faux statut.
    est_bloque = Column(Boolean, default=False, nullable=True)
    motif_blocage = Column(Text)
    date_blocage = Column(DateTime(timezone=True))
    bloque_par = Column(String(100))
    # Semi-remorque accouplee au tracteur (dissociation = historique d'atelage).
    remorque_immatriculation = Column(String(20))
    remorque_type = Column(String(30))  # benne, citerne, frigorifique, porte-conteneur
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    missions = relationship("Mission", back_populates="camion")
    pannes = relationship("Panne", back_populates="camion", cascade="all, delete-orphan")
    atelages = relationship("Atelage", back_populates="camion", cascade="all, delete-orphan")


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
    # Dossier administratif du conducteur (Tranche D) : documents exiges par la
    # reglementation camerounaise pour le transport routier de marchandises.
    date_naissance = Column(DateTime(timezone=True))
    categorie_permis = Column(String(10))  # C, C1, C+E, D ...
    numero_cnps = Column(String(30))
    expiration_visite_medicale = Column(DateTime(timezone=True))
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
    # Rattachement a la chaine documentaire (migration 024) : conteneur livre
    # et/ou B/L de la marchandise transportee. NULLable, jamais devine.
    conteneur_id = Column(Integer, ForeignKey('conteneurs.id'), index=True)
    numero_bl = Column(String(50), index=True)
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
    # Preuve de livraison (POD) collectee a la cloture de la mission.
    nom_receptionnaire = Column(String(100))
    signature_receptionnaire = Column(Text)
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


class Panne(Base):
    """Panne constatee sur un camion (journal d'exploitation atelier).

    Un camion en panne grave est automatiquement bloque (est_bloque) pour
    empecher toute affectation a une mission tant qu'il n'est pas repare.
    """
    __tablename__ = "transport_pannes"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=True, index=True)
    reference = Column(String(50), nullable=False, index=True)
    camion_id = Column(Integer, ForeignKey('camions.id'), nullable=False, index=True)
    mission_id = Column(Integer, ForeignKey('missions.id'), nullable=True)
    date_panne = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    type_panne = Column(String(30))  # mecanique, electrique, pneumatique, carrosserie, refroidissement
    gravite = Column(String(20), default="legere")  # legere, moyenne, grave, bloquante
    description = Column(Text, nullable=False)
    localisation = Column(String(200))  # lieu de constat (carrefour, depot, atelier)
    kilometrage = Column(Integer)
    technicien = Column(String(100))
    garage = Column(String(100))
    statut = Column(String(20), default="signalee")  # signalee, en_cours, reparee, immobilisee
    date_reparation = Column(DateTime(timezone=True))
    cout_reparation = Column(Numeric)
    immobilisation = Column(Boolean, default=False)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    camion = relationship("Camion", back_populates="pannes")


class Atelage(Base):
    """Historique des accouplements tracteur / semi-remorque.

    La dissociation cloture la ligne (date_dissociation) plutot que de la
    supprimer : le kilometre parcouru avec chaque remorque doit rester auditable.
    """
    __tablename__ = "transport_atelages"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=True, index=True)
    camion_id = Column(Integer, ForeignKey('camions.id'), nullable=False, index=True)
    remorque_immatriculation = Column(String(20), nullable=False, index=True)
    remorque_type = Column(String(30))
    date_attelage = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    date_dissociation = Column(DateTime(timezone=True))
    motif_dissociation = Column(String(200))
    lieu_attelage = Column(String(200))
    operateur = Column(String(100))
    kilometrage_debut = Column(Integer)
    kilometrage_fin = Column(Integer)
    statut = Column(String(20), default="attelle")  # attelle, dissocie
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    camion = relationship("Camion", back_populates="atelages")