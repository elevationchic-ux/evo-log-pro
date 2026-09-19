"""Transport International models - Road transport for Cameroon/CEMAC"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, Enum, Date, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class TypeTransitRoutier(str, enum.Enum):
    """Road transit type enumeration"""
    TIR = "tir"  # Carnet TIR
    T1 = "t1"  # Transit communautaire
    T2 = "t2"  # Transit communautaire
    NATIONAL = "national"


class StatutTransport(str, enum.Enum):
    """Transport status enumeration"""
    PLANIFIE = "planifie"
    EN_CHARGEMENT = "en_chargement"
    EN_TRANSIT = "en_transit"
    LIVRE = "livre"
    RETARD = "retard"
    ANNULE = "annule"
    INCIDENT = "incident"


class OrdreTransport(Base):
    """Transport Order - OT"""
    __tablename__ = "ordres_transport"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_ot = Column(String(50), unique=True, nullable=False, index=True)
    client_id = Column(Integer, ForeignKey('tiers.id'))
    transporteur_id = Column(Integer, ForeignKey('tiers.id'))
    camion_id = Column(Integer, ForeignKey('camions.id'))
    conducteur_id = Column(Integer, ForeignKey('conducteurs.id'))
    type_transit = Column(Enum(TypeTransitRoutier))
    statut = Column(Enum(StatutTransport), default=StatutTransport.PLANIFIE)
    date_creation = Column(Date)
    date_chargement_prevue = Column(Date)
    date_chargement_reelle = Column(Date)
    date_livraison_prevue = Column(Date)
    date_livraison_reelle = Column(Date)
    lieu_chargement = Column(String(200))
    lieu_livraison = Column(String(200))
    pays_destination = Column(String(50))
    code_pays_destination = Column(String(2))
    marchandise = Column(Text)
    poids_net = Column(Numeric)
    poids_brut = Column(Numeric)
    nombre_colis = Column(Integer)
    volume_m3 = Column(Numeric)
    valeur_marchandise = Column(Numeric(15, 2))
    devise = Column(String(3), default="XAF")
    montant_freight = Column(Numeric(15, 2))
    devis = Column(String(50))
    observations = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    carnet_tir = relationship("CarnetTIR", back_populates="ordres_transport")
    cmr = relationship("CMR", back_populates="ordre_transport")
    scelles_routiers = relationship("ScelleRoutier", back_populates="ordre_transport")
    positions = relationship("PositionTransport", back_populates="ordre_transport")


class CarnetTIR(Base):
    """TIR Carnet - International road transit"""
    __tablename__ = "carnets_tir"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_carnet = Column(String(50), unique=True, nullable=False, index=True)
    ordre_transport_id = Column(Integer, ForeignKey('ordres_transport.id'))
    pays_emission = Column(String(50))
    code_pays_emission = Column(String(2))
    date_emission = Column(Date)
    date_validite = Column(Date)
    nombre_virements = Column(Integer, default=0)
    bureau_depart = Column(String(100))
    bureau_arrivee = Column(String(100))
    bureau_transit = Column(String(100))
    montant_garantie = Column(Numeric(15, 2))
    devise = Column(String(3), default="XAF")
    statut = Column(String(20), default="actif")  # actif, utilise, cloture, annule
    observations = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    ordres_transport = relationship("OrdreTransport", back_populates="carnet_tir")


class CMR(Base):
    """CMR - Lettre de voiture internationale"""
    __tablename__ = "cmrs"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_cmr = Column(String(50), unique=True, nullable=False, index=True)
    ordre_transport_id = Column(Integer, ForeignKey('ordres_transport.id'))
    expediteur = Column(String(100))
    destinataire = Column(String(100))
    transporteur = Column(String(100))
    lieu_chargement = Column(String(200))
    lieu_livraison = Column(String(200))
    date_emission = Column(Date)
    date_chargement = Column(Date)
    date_livraison = Column(Date)
    marchandise = Column(Text)
    poids_net = Column(Numeric)
    poids_brut = Column(Numeric)
    nombre_colis = Column(Integer)
    type_emballage = Column(String(50))
    valeur_marchandise = Column(Numeric(15, 2))
    devise = Column(String(3), default="XAF")
    instructions_speciales = Column(Text)
    reserve = Column(Text)
    signature_expediteur = Column(Boolean, default=False)
    signature_transporteur = Column(Boolean, default=False)
    signature_destinataire = Column(Boolean, default=False)
    statut = Column(String(20), default="emis")  # emis, signe, livre, annule
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    ordre_transport = relationship("OrdreTransport", back_populates="cmr")


class ScelleRoutier(Base):
    """Road seal - Scellé routier"""
    __tablename__ = "scelles_routiers"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_scelle = Column(String(50), unique=True, nullable=False, index=True)
    ordre_transport_id = Column(Integer, ForeignKey('ordres_transport.id'))
    type_scelle = Column(String(50))  # "douane", "transporteur", "client"
    emplacement = Column(String(50))
    date_pose = Column(DateTime(timezone=True))
    pose_par = Column(String(100))
    date_verification = Column(DateTime(timezone=True))
    verifie_par = Column(String(100))
    intact = Column(Boolean, default=True)
    motif_bris = Column(String(200))
    photo = Column(String(255))
    statut = Column(String(20), default="pose")  # pose, verifie, brise, retire
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    ordre_transport = relationship("OrdreTransport", back_populates="scelles_routiers")


class PositionTransport(Base):
    """Transport position tracking"""
    __tablename__ = "positions_transport"
    
    id = Column(Integer, primary_key=True, index=True)
    ordre_transport_id = Column(Integer, ForeignKey('ordres_transport.id'))
    latitude = Column(Numeric)
    longitude = Column(Numeric)
    adresse = Column(String(200))
    ville = Column(String(100))
    pays = Column(String(50))
    date_position = Column(DateTime(timezone=True))
    vitesse_kmh = Column(Numeric)
    direction = Column(Numeric)
    altitude = Column(Numeric)
    precision = Column(Numeric)
    statut = Column(String(20))  # "en_mouvement", "arrete", "incident"
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    ordre_transport = relationship("OrdreTransport", back_populates="positions")


class CETSuivi(Base):
    """CET - Control of Exchanges of Information"""
    __tablename__ = "cet_suivi"
    
    id = Column(Integer, primary_key=True, index=True)
    ordre_transport_id = Column(Integer, ForeignKey('ordres_transport.id'))
    numero_cet = Column(String(50), unique=True, nullable=False, index=True)
    bureau_douane = Column(String(100))
    date_controle = Column(DateTime(timezone=True))
    type_controle = Column(String(50))  # "sortie", "entree", "transit"
    resultat = Column(String(20))  # "conforme", "non_conforme", "incident"
    observations = Column(Text)
    agent = Column(String(100))
    fonction = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    ordre_transport = relationship("OrdreTransport")


class AssuranceFAP(Base):
    """FAP - Insurance for freight"""
    __tablename__ = "assurances_fap"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_police = Column(String(50), unique=True, nullable=False, index=True)
    ordre_transport_id = Column(Integer, ForeignKey('ordres_transport.id'))
    assureur = Column(String(100))
    type_couverture = Column(String(50))  # "tous_risques", "partielle", "responsabilite"
    valeur_assuree = Column(Numeric(15, 2))
    devise = Column(String(3), default="XAF")
    prime = Column(Numeric(15, 2))
    franchise = Column(Numeric(15, 2))
    date_debut = Column(Date)
    date_fin = Column(Date)
    exclusions = Column(Text)
    statut = Column(String(20), default="actif")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    ordre_transport = relationship("OrdreTransport")


class PlanningLivraison(Base):
    """Delivery planning"""
    __tablename__ = "planning_livraison"
    
    id = Column(Integer, primary_key=True, index=True)
    ordre_transport_id = Column(Integer, ForeignKey('ordres_transport.id'))
    date_livraison = Column(Date)
    heure_debut = Column(String(5))
    heure_fin = Column(String(5))
    adresse_livraison = Column(String(200))
    contact_client = Column(String(100))
    telephone_client = Column(String(50))
    instructions = Column(Text)
    statut = Column(String(20), default="planifie")  # planifie, en_cours, livre, rate
    poids_decharge = Column(Numeric)
    volume_decharge = Column(Numeric)
    duree_estimee_heures = Column(Numeric)
    observations = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    ordre_transport = relationship("OrdreTransport")


class PreuveLivraison(Base):
    """Proof of delivery - POD"""
    __tablename__ = "preuves_livraison"
    
    id = Column(Integer, primary_key=True, index=True)
    ordre_transport_id = Column(Integer, ForeignKey('ordres_transport.id'))
    planning_id = Column(Integer, ForeignKey('planning_livraison.id'))
    date_livraison = Column(DateTime(timezone=True))
    heure_livraison = Column(String(5))
    destinataire = Column(String(100))
    fonction = Column(String(50))
    signature = Column(String(255))
    photo = Column(String(255))
    colis_recus = Column(Integer)
    colis_refuses = Column(Integer)
    motifs_refus = Column(Text)
    etat_marchandise = Column(String(50))  # "conforme", "avarie", "manquant"
    observations = Column(Text)
    latitude = Column(Numeric)
    longitude = Column(Numeric)
    statut = Column(String(20), default="signe")  # signe, refuse, annule
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    ordre_transport = relationship("OrdreTransport")
    planning = relationship("PlanningLivraison")


class IncidentTransport(Base):
    """Transport incident"""
    __tablename__ = "incidents_transport"
    
    id = Column(Integer, primary_key=True, index=True)
    ordre_transport_id = Column(Integer, ForeignKey('ordres_transport.id'))
    type_incident = Column(String(50))  # "accident", "panne", "vol", "retard", "blocage"
    date_incident = Column(DateTime(timezone=True))
    lieu = Column(String(200))
    description = Column(Text)
    gravite = Column(String(20))  # "mineur", "moyen", "majeur", "critique"
    avarie_marchandise = Column(Boolean, default=False)
    valeur_avarie = Column(Numeric(15, 2))
    devise = Column(String(3), default="XAF")
    blesses = Column(Integer, default=0)
    deces = Column(Integer, default=0)
    mesure_prise = Column(Text)
    police_intervention = Column(Boolean, default=False)
    numero_police = Column(String(50))
    photos = Column(Text)  # JSON array
    statut = Column(String(20), default="ouvert")  # ouvert, en_cours, resolu, clos
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    ordre_transport = relationship("OrdreTransport")


class ControleRoutier(Base):
    """Road control - Gendarmerie/Police/Customs"""
    __tablename__ = "controles_routiers"
    
    id = Column(Integer, primary_key=True, index=True)
    ordre_transport_id = Column(Integer, ForeignKey('ordres_transport.id'))
    type_controle = Column(String(50))  # "gendarmerie", "police", "douane", "poids_lourd"
    date_controle = Column(DateTime(timezone=True))
    lieu = Column(String(200))
    autorite = Column(String(100))
    resultat = Column(String(20))  # "conforme", "non_conforme", "verbal"
    motif_infraction = Column(String(200))
    montant_amende = Column(Numeric(15, 2))
    devise = Column(String(3), default="XAF")
    numero_verbal = Column(String(50))
    observations = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    ordre_transport = relationship("OrdreTransport")


class TaxeRoutiere(Base):
    """Road tax - Péages et taxes routières"""
    __tablename__ = "taxes_routieres"
    
    id = Column(Integer, primary_key=True, index=True)
    ordre_transport_id = Column(Integer, ForeignKey('ordres_transport.id'))
    type_taxe = Column(String(50))  # "peage", "taxe_weight", "redevance", "vignette"
    lieu = Column(String(200))
    date_paiement = Column(DateTime(timezone=True))
    montant = Column(Numeric(15, 2))
    devise = Column(String(3), default="XAF")
    numero_ticket = Column(String(50))
    kilometrage = Column(Numeric)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    ordre_transport = relationship("OrdreTransport")


class CorridorCEMAC(Base):
    """CEMAC Corridor routes"""
    __tablename__ = "corridors_cemac"
    
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(100), nullable=False)
    pays_depart = Column(String(50))
    code_pays_depart = Column(String(2))
    pays_arrivee = Column(String(50))
    code_pays_arrivee = Column(String(2))
    distance_km = Column(Numeric)
    duree_estimee_heures = Column(Numeric)
    points_controle = Column(Text)  # JSON array of control points
    dangers = Column(Text)  # JSON array of dangers
    recommandations = Column(Text)
    statut = Column(String(20), default="actif")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
