"""Container Lifecycle models - Complete container management for Cameroon ports"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, Enum, Date, Numeric, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class TypeConteneur(str, enum.Enum):
    """Container type enumeration"""
    DRY_20 = "dry_20"
    DRY_40 = "dry_40"
    DRY_40_HC = "dry_40_hc"
    REEFER_20 = "reefer_20"
    REEFER_40 = "reefer_40"
    OPEN_TOP_20 = "open_top_20"
    OPEN_TOP_40 = "open_top_40"
    FLAT_RACK_20 = "flat_rack_20"
    FLAT_RACK_40 = "flat_rack_40"
    TANK_20 = "tank_20"
    PLATFORM = "platform"


class EtatConteneur(str, enum.Enum):
    """Container condition enumeration"""
    CLEAN = "clean"
    DIRTY = "dirty"
    DAMAGED = "damaged"
    REPAIR_NEEDED = "repair_needed"


class StatutConteneur(str, enum.Enum):
    """Container status enumeration"""
    ARRIVE = "arrive"
    DECHARGE = "decharge"
    STOCKE = "stocke"
    QUAI = "quai"
    EMPOTE = "empote"
    DEPOTE = "depote"
    SORTI = "sorti"
    TRANSBORD = "transbord"


class ConteneurCycle(Base):
    """Conteneur avec cycle de vie complet"""
    __tablename__ = "conteneurs_cycle"
    __table_args__ = (
        UniqueConstraint('company_id', 'numero', name='uix_conteneur_company_numero'),
    )
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=True, index=True)
    numero = Column(String(20), nullable=False, index=True)
    type_conteneur = Column(Enum(TypeConteneur), nullable=False)
    taille_pieds = Column(Integer, nullable=False)  # 20, 40, 45
    etat = Column(Enum(EtatConteneur), default=EtatConteneur.CLEAN)
    proprietaire = Column(String(100))  # MSC, MAERSK, CMA CGM, etc.
    compagnie = Column(String(100))
    date_fabrication = Column(Date)
    date_derniere_inspection = Column(Date)
    prochaine_inspection = Column(Date)
    tare_kg = Column(Numeric)
    max_payload_kg = Column(Numeric)
    volume_m3 = Column(Numeric)
    temperature_c = Column(Numeric)  # Pour reefer
    est_hazardous = Column(Boolean, default=False)
    classe_hazard = Column(String(20))
    notes = Column(Text)
    photo_avant = Column(String(255))  # URL scan
    photo_apres = Column(String(255))  # URL scan
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    cycles = relationship("CycleConteneur", back_populates="conteneur")
    dommages = relationship("DommageConteneur", back_populates="conteneur")


class CycleConteneur(Base):
    """Cycle de vie conteneur"""
    __tablename__ = "cycle_conteneur_cycle"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=True, index=True)
    conteneur_id = Column(Integer, ForeignKey('conteneurs_cycle.id'), nullable=False)
    navire_id = Column(Integer, ForeignKey('navires.id'))
    voyage = Column(String(50))
    date_arrivee_navire = Column(DateTime(timezone=True))
    date_dechargement = Column(DateTime(timezone=True))
    date_mise_quai = Column(DateTime(timezone=True))
    date_sortie = Column(DateTime(timezone=True))
    terminal_id = Column(Integer, ForeignKey('terminaux_portuaires.id'))
    localisation = Column(String(100))  # Terminal, Quai, Magasin
    statut = Column(Enum(StatutConteneur), default=StatutConteneur.ARRIVE)
    operateur_dechargement = Column(String(100))
    operateur_manutention = Column(String(100))
    grue_utilisee = Column(String(50))
    temps_cycle_heures = Column(Numeric)
    incidents = Column(Text)  # JSON
    photos = Column(Text)  # JSON array
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    conteneur = relationship(
        "app.models.conteneur_cycle.ConteneurCycle", back_populates="cycles"
    )


class DommageConteneur(Base):
    """Dommage et réclamation conteneur"""
    __tablename__ = "dommages_conteneur_cycle"
    
    id = Column(Integer, primary_key=True, index=True)
    conteneur_id = Column(Integer, ForeignKey('conteneurs_cycle.id'), nullable=False)
    cycle_id = Column(Integer, ForeignKey('cycle_conteneur_cycle.id'))
    type_dommage = Column(String(50), nullable=False)  # CAISSE, TOIT, PORTES, SOL, RENFORT
    description = Column(Text, nullable=False)
    gravite = Column(String(20), nullable=False)  # MINEUR, MAJEUR, CRITIQUE
    date_constatation = Column(DateTime(timezone=True), nullable=False)
    lieu_constatation = Column(String(100), nullable=False)
    constatateur = Column(String(100), nullable=False)
    responsable = Column(String(100))
    photos = Column(Text)  # JSON array
    cout_reparation = Column(Numeric)
    devise = Column(String(3), default="XAF")
    numero_reclamation = Column(String(50))
    assurance_id = Column(Integer)
    statut_reclamation = Column(String(20), default="en_attente")  # en_attente, accepte, refuse, resolu
    date_resolution = Column(Date)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    conteneur = relationship(
        "app.models.conteneur_cycle.ConteneurCycle", back_populates="dommages"
    )


class EmpotageDepotage(Base):
    """Empotage/Dépotage conteneur"""
    __tablename__ = "empotage_depotage_cycle"
    
    id = Column(Integer, primary_key=True, index=True)
    conteneur_id = Column(Integer, ForeignKey('conteneurs_cycle.id'), nullable=False)
    type_operation = Column(String(20), nullable=False)  # EMPOTAGE, DEPOTAGE
    date_operation = Column(DateTime(timezone=True), nullable=False)
    terminal_id = Column(Integer, ForeignKey('terminaux_portuaires.id'))
    operateur = Column(String(100), nullable=False)
    chef_equipe = Column(String(100))
    liste_marchandise = Column(Text)  # JSON
    poids_brut_kg = Column(Numeric)
    poids_net_kg = Column(Numeric)
    nombre_colis = Column(Integer)
    temperature_c = Column(Numeric)  # Pour reefer
    temps_operation_heures = Column(Numeric)
    incident = Column(Text)
    controle_qualite = Column(String(20), default="conforme")  # conforme, non_conforme
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class InspectionConteneur(Base):
    """Inspection conteneur"""
    __tablename__ = "inspections_conteneur_cycle"
    
    id = Column(Integer, primary_key=True, index=True)
    conteneur_id = Column(Integer, ForeignKey('conteneurs_cycle.id'), nullable=False)
    type_inspection = Column(String(50), nullable=False)  # PERIODIQUE, INCIDENT, SORTIE
    date_inspection = Column(DateTime(timezone=True), nullable=False)
    inspecteur = Column(String(100), nullable=False)
    certification = Column(String(100))
    resultat = Column(String(20), nullable=False)  # CONFORME, NON_CONFORME, REPARATION_REQUISE
    points_inspection = Column(Text)  # JSON
    etat_caisse = Column(String(20))
    etat_toit = Column(String(20))
    etat_portes = Column(String(20))
    etat_sol = Column(String(20))
    etat_renforts = Column(String(20))
    etat_joints = Column(String(20))
    recommandations = Column(Text)
    prochaine_inspection = Column(Date)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
