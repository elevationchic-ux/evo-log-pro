"""CEMAC Transit models - Corridors, Border Posts, TIR/TSD procedures"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, Enum, Date, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class EtatRoute(str, enum.Enum):
    """Route condition enumeration"""
    BON = "bon"
    MOYEN = "moyen"
    MAUVAIS = "mauvais"
    DEGRADE = "degrade"


class TypePosteFrontalier(str, enum.Enum):
    """Border post type enumeration"""
    DOUANE = "douane"
    GENDARMERIE = "gendarmerie"
    POLICE = "police"
    SANTE = "sante"
    PHYTOSANITAIRE = "phytosanitaire"


class CorridorCEMACTransit(Base):
    """Corridor CEMAC (Transit module)"""
    __tablename__ = "corridors_cemac_transit"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(10), unique=True, nullable=False, index=True)  # DOU-NDJ, DOU-BNG, DOU-BRZ
    nom = Column(String(100), nullable=False)
    origine = Column(String(100), nullable=False)  # Douala, Kribi
    destination = Column(String(100), nullable=False)  # Ndjamena, Bangui, Brazzaville
    distance_km = Column(Integer, nullable=False)
    duree_estimee_heures = Column(Integer, nullable=False)
    pays_origine = Column(String(2), nullable=False)  # CM
    pays_destination = Column(String(2), nullable=False)  # TD, CF, CG, GA
    pays_traverses = Column(Text)  # JSON: ["CM", "TD", "CF"]
    etat_route = Column(Enum(EtatRoute), default=EtatRoute.MOYEN)
    description_route = Column(Text)
    risques = Column(Text)  # JSON: ["attaques", "barrières", "mauvais_etat"]
    points_dangers = Column(Text)  # JSON
    alternatives = Column(Text)  # JSON
    est_actif = Column(Boolean, default=True)
    date_derniere_maj = Column(Date)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    postes_frontaliers = relationship("PosteFrontalier", back_populates="corridor")


class PosteFrontalier(Base):
    """Poste Frontalier"""
    __tablename__ = "postes_frontaliers"
    
    id = Column(Integer, primary_key=True, index=True)
    corridor_id = Column(Integer, ForeignKey('corridors_cemac_transit.id'), nullable=False)
    code = Column(String(20), unique=True, nullable=False)
    nom = Column(String(100), nullable=False)
    pays = Column(String(50), nullable=False)
    ville = Column(String(100))
    type_poste = Column(Enum(TypePosteFrontalier), nullable=False)
    coordonnees = Column(String(100))  # Latitude, Longitude
    horaires = Column(Text)
    capacite_journaliere = Column(Integer)
    temps_moyen_traitement_heures = Column(Numeric)
    services_disponibles = Column(Text)  # JSON: ["douane", "gendarmerie", "police"]
    telephone = Column(String(20))
    email = Column(String(100))
    chef_poste = Column(String(100))
    contact_urgence = Column(String(20))
    est_actif = Column(Boolean, default=True)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    corridor = relationship("CorridorCEMACTransit", back_populates="postes_frontaliers")


class ProcedureTIR(Base):
    """Procédure TIR (Transports Internationaux Routiers)"""
    __tablename__ = "procedures_tir"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_carnet = Column(String(50), unique=True, nullable=False, index=True)
    dossier_transit_id = Column(Integer, ForeignKey('dossiers_transit_avance.id'))
    date_delivrance = Column(Date, nullable=False)
    date_validite = Column(Date, nullable=False)
    numero_assurance = Column(String(50), nullable=False)
    assureur = Column(String(100), nullable=False)
    montant_garantie = Column(Numeric, nullable=False)
    devise = Column(String(3), default="XAF")
    bureau_depart = Column(String(100), nullable=False)
    bureau_arrivee = Column(String(100), nullable=False)
    corridor = Column(String(20), nullable=False)
    nombre_volets = Column(Integer, default=4)
    numero_scelle = Column(String(50))
    date_depart = Column(Date)
    date_arrivee = Column(Date)
    statut = Column(String(20), default="en_cours")  # en_cours, arrive, cloture, annule
    observations = Column(Text)
    reference_iru = Column(String(50))  # International Road Union
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ProcedureTSD(Base):
    """Procédure TSD (Transit Simplifié et Dédouané)"""
    __tablename__ = "procedures_tsd"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_tsd = Column(String(50), unique=True, nullable=False, index=True)
    dossier_transit_id = Column(Integer, ForeignKey('dossiers_transit_avance.id'))
    date_delivrance = Column(Date, nullable=False)
    date_validite = Column(Date, nullable=False)
    bureau_depart = Column(String(100), nullable=False)
    bureau_arrivee = Column(String(100), nullable=False)
    corridor = Column(String(20), nullable=False)
    montant_garantie = Column(Numeric)
    devise = Column(String(3), default="XAF")
    duree_transit_jours = Column(Integer, default=15)
    date_depart = Column(Date)
    date_arrivee = Column(Date)
    statut = Column(String(20), default="en_cours")
    observations = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class FraisCorridor(Base):
    """Frais Corridor CEMAC"""
    __tablename__ = "frais_corridor"
    
    id = Column(Integer, primary_key=True, index=True)
    corridor_id = Column(Integer, ForeignKey('corridors_cemac_transit.id'), nullable=False)
    type_frais = Column(String(50), nullable=False)  # PASSEPORT, REDEVANCE, SECURITE, PEAGE
    designation = Column(String(200), nullable=False)
    montant = Column(Numeric, nullable=False)
    devise = Column(String(3), default="XAF")
    unite = Column(String(20))  # PAR_VEHICULE, PAR_TONNE, PAR_PASSAGE
    poste_frontalier_id = Column(Integer, ForeignKey('postes_frontaliers.id'))
    date_application = Column(Date, nullable=False)
    est_actif = Column(Boolean, default=True)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ScelleRoutierTransit(Base):
    """Scellé Routier pour transit"""
    __tablename__ = "scelles_routiers_transit"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_scelle = Column(String(50), unique=True, nullable=False, index=True)
    type_scelle = Column(String(20), nullable=False)  # METAL, PLASTIQUE, HIGH_SECURITY
    dossier_transit_id = Column(Integer, ForeignKey('dossiers_transit_avance.id'))
    procedure_id = Column(Integer)  # TIR ou TSD
    date_pose = Column(Date, nullable=False)
    poste_pose = Column(String(100), nullable=False)
    agent_pose = Column(String(100), nullable=False)
    date_retire = Column(Date)
    poste_retire = Column(String(100))
    agent_retire = Column(String(100))
    etat = Column(String(20), default="intact")  # intact, casse, remplace
    motif_casse = Column(Text)
    photo = Column(String(255))  # URL scan
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class IncidentCorridor(Base):
    """Incident sur corridor"""
    __tablename__ = "incidents_corridor"
    
    id = Column(Integer, primary_key=True, index=True)
    corridor_id = Column(Integer, ForeignKey('corridors_cemac_transit.id'), nullable=False)
    type_incident = Column(String(50), nullable=False)  # ACCIDENT, ATTAQUE, BARRIERE, PANNE
    date_incident = Column(DateTime(timezone=True), nullable=False)
    localisation = Column(String(100), nullable=False)
    kilometrage = Column(Numeric)
    description = Column(Text, nullable=False)
    vehicule_id = Column(Integer, ForeignKey('camions.id'))
    conducteur_id = Column(Integer, ForeignKey('conducteurs.id'))
    degats = Column(Text)  # JSON
    blesses = Column(Text)  # JSON
    montant_degats = Column(Numeric)
    devise = Column(String(3), default="XAF")
    police_id = Column(String(50))
    assurance_id = Column(Integer)
    statut = Column(String(20), default="en_cours")  # en_cours, resolu, classe
    date_resolution = Column(Date)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


# Alias for compatibility
CorridorCEMAC = CorridorCEMACTransit

