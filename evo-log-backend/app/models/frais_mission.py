"""
Modèles SQLAlchemy pour la gestion des Frais de Mission et Avances Collaborateurs
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey, Numeric
from sqlalchemy.sql import func
from app.core.database import Base


class FraisMission(Base):
    """Note de frais engagée par un collaborateur"""
    __tablename__ = "frais_missions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    nom_collaborateur = Column(String(120), nullable=True)
    mission_id = Column(Integer, nullable=True, index=True)
    titre_mission = Column(String(200), nullable=True)
    
    # Type: CARBURANT, PEAGE, RESTAURATION, HEBERGEMENT, MANUTENTION, PIECE_SECOURS, DIVERS
    type_frais = Column(String(50), nullable=False, default="DIVERS", index=True)
    montant = Column(Float, nullable=False, default=0.0)
    devise = Column(String(10), default="XAF")
    date_depense = Column(DateTime(timezone=True), server_default=func.now())
    fournisseur = Column(String(150), nullable=True)
    ville_lieu = Column(String(100), nullable=True)
    
    # Justificatif
    justificatif_url = Column(String(500), nullable=True)
    numero_recu = Column(String(100), nullable=True)
    
    # Statut: BROUILLON, SOUMIS, VALIDE, REJETE, REMBOURSE
    statut = Column(String(30), default="SOUMIS", index=True)
    commentaire = Column(Text, nullable=True)
    
    # Approbation
    valide_par_id = Column(Integer, nullable=True)
    valide_par_nom = Column(String(120), nullable=True)
    date_validation = Column(DateTime(timezone=True), nullable=True)
    motif_rejet = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class AvanceMission(Base):
    """Demande d'avance de trésorerie avant départ en mission"""
    __tablename__ = "avances_missions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    nom_collaborateur = Column(String(120), nullable=True)
    
    titre_mission = Column(String(200), nullable=False)
    corridor_destination = Column(String(150), nullable=True)
    date_depart = Column(DateTime(timezone=True), nullable=True)
    date_retour_prevue = Column(DateTime(timezone=True), nullable=True)
    
    montant_demande = Column(Float, nullable=False, default=0.0)
    montant_accorde = Column(Float, nullable=True, default=0.0)
    devise = Column(String(10), default="XAF")
    motif = Column(Text, nullable=True)
    
    # Statut: DEMANDEE, ACCORDEE, REFUSEE, SOLDEE
    statut = Column(String(30), default="DEMANDEE", index=True)
    valide_par_nom = Column(String(120), nullable=True)
    date_decision = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
