"""
Modèles pour le Module Chef du Personnel & Rôles Passifs
Supervision N+1 : Secrétaires, Gardiens de Sécurité, Techniciens de Surface, Support IT.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Numeric, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class PlanningGarde(Base):
    """Planning des tours de garde, vacations et permanences des rôles passifs"""
    __tablename__ = "plannings_gardes"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=True, index=True)
    agency_id = Column(Integer, ForeignKey('agencies.id'), nullable=True, index=True)
    employe_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    superviseur_id = Column(Integer, ForeignKey('users.id'), nullable=True) # N+1 Chef du Personnel
    
    date_jour = Column(Date, nullable=False, index=True)
    quart = Column(String(30), nullable=False) # JOUR (07h-19h), NUIT (19h-07h), MATIN (06h-14h), SOIR (14h-22h), STANDARD (08h-17h)
    poste_assigne = Column(String(100), nullable=False) # Ex: 'Poste Garde Quai 14', 'Accueil Hall Siège', 'Entretien Magasin Central', 'Permanence IT Douala'
    statut = Column(String(30), default="PLANIFIE") # PLANIFIE, CONFIRME, EN_POSTE, TERMINE, ABSENT, REMPLACE
    remplacant_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    observations = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    employe = relationship("User", foreign_keys=[employe_id])
    superviseur = relationship("User", foreign_keys=[superviseur_id])
    remplacant = relationship("User", foreign_keys=[remplacant_id])


class PointageVacation(Base):
    """Émargement physique ou biométrique des heures de vacation et primes de nuit"""
    __tablename__ = "pointages_vacations"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=True, index=True)
    employe_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    valide_par_id = Column(Integer, ForeignKey('users.id'), nullable=True) # Chef du Personnel
    
    date_pointage = Column(Date, nullable=False, index=True)
    heure_arrivee = Column(String(10), nullable=False) # HH:MM
    heure_depart = Column(String(10), nullable=True)   # HH:MM
    heures_effectives = Column(Numeric, default=8.0)
    droit_panier_nuit = Column(Boolean, default=False)
    montant_panier = Column(Numeric, default=0) # Ex: 3500 XAF
    est_valide = Column(Boolean, default=True)
    remarques = Column(String(200), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    employe = relationship("User", foreign_keys=[employe_id])
    valide_par = relationship("User", foreign_keys=[valide_par_id])


class DotationEPI(Base):
    """Dotations et matériels assignés aux agents de terrain et support"""
    __tablename__ = "dotations_epi_materiel"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=True, index=True)
    employe_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    attribue_par_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    
    designation = Column(String(150), nullable=False) # 'Gilet Haute Visibilité ISPS', 'Chaussures de Sécurité S3', 'Talkie-Walkie VHF Quai', 'Badge Biométrique'
    categorie = Column(String(50), default="EPI") # EPI, UNIFORME, OUTILLAGE, COMMUNICATION, BADGE
    date_remise = Column(Date, nullable=False)
    date_renouvellement_prevue = Column(Date, nullable=True)
    numero_serie = Column(String(50), nullable=True)
    etat = Column(String(30), default="NEUF") # NEUF, BON, USAGE, A_REMPLACER, PERDU
    est_restitue = Column(Boolean, default=False)
    observations = Column(String(200), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    employe = relationship("User", foreign_keys=[employe_id])
