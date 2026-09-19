"""
Modèle Prestataire & Annuaire Sous-traitants pour l'ERP Portuaire Cameroun/CEMAC
Réservé aux départements Achats, Logistique & Direction Générale.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Prestataire(Base):
    """Fournisseurs de services logistiques, manutention, gardiennage et entretien"""
    __tablename__ = "prestataires"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=True, index=True)
    
    # Identification officielle
    code = Column(String(50), unique=True, nullable=False, index=True)
    raison_sociale = Column(String(150), nullable=False, index=True)
    sigle = Column(String(30), nullable=True)
    specialite = Column(String(80), nullable=False, index=True) 
    # Ex: 'MANUTENTION_PORTUAIRE', 'GARDIENNAGE_ISPS', 'NETTOYAGE_INDUSTRIEL', 
    # 'TRANSPORT_LOURD', 'MAINTENANCE_ENGINS', 'BUNKERING_CARBURANT', 'DOUANE_TRANSIT'
    
    # Immatriculation Cameroun / CEMAC
    tax_id = Column(String(50), nullable=True) # NIF / Numéro Contribuable
    rccm = Column(String(50), nullable=True)
    agrement_portuaire = Column(String(80), nullable=True) # Agrément PAD (Douala) / PAK (Kribi)
    est_homologue = Column(Boolean, default=True)
    statut_agrement = Column(String(30), default="VALIDE") # VALIDE, EN_COURS, EXPIRE
    
    # Localisation & Intervention
    ville = Column(String(50), default="Douala", index=True)
    zone_portuaire = Column(String(100), nullable=True) # 'Douala Quai 14', 'Kribi Mboro', 'Zone Industrielle Bassa'
    adresse = Column(String(200), nullable=True)
    
    # Contacts Directs & Astreinte 24/7
    contact_nom = Column(String(100), nullable=True)
    contact_telephone = Column(String(40), nullable=False)
    contact_email = Column(String(100), nullable=True)
    telephone_astreinte_24h = Column(String(40), nullable=True)
    
    # Notation & Évaluation SLA
    note_globale = Column(Float, default=4.5) # Sur 5.0
    nb_missions_realisees = Column(Integer, default=0)
    taux_ponctualite = Column(Float, default=95.0) # %
    taux_conformite_qhse = Column(Float, default=98.0) # %
    
    # Grille Tarifaire Indicative
    devise = Column(String(10), default="XAF")
    taux_journalier_indicatif = Column(Numeric, nullable=True)
    conditions_reglement = Column(String(100), default="Virement 30j fin de mois")
    
    # Remarques et habilitations
    observations = Column(Text, nullable=True)
    est_actif = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relations
    company = relationship("Company", foreign_keys=[company_id])
    cotations = relationship("DemandeCotation", back_populates="prestataire", cascade="all, delete-orphan")


class DemandeCotation(Base):
    """Demande de devis ou de mise à disposition de sous-traitance"""
    __tablename__ = "demandes_cotation_prestataires"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=True, index=True)
    prestataire_id = Column(Integer, ForeignKey('prestataires.id'), nullable=False, index=True)
    demandeur_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    numero_dossier = Column(String(50), unique=True, nullable=False, index=True)
    titre_besoin = Column(String(200), nullable=False)
    description_besoin = Column(Text, nullable=False)
    urgence = Column(String(20), default="NORMALE") # FAIBLE, NORMALE, URGENTE, IMMEDIATE
    date_intervention_souhaitee = Column(String(30), nullable=True)
    lieu_intervention = Column(String(100), nullable=False)
    budget_max_estime = Column(Numeric, nullable=True)
    statut = Column(String(30), default="EN_ATTENTE") # EN_ATTENTE, TRANSMIS, CHIFFRE, RETENU, REFUSE
    reponse_montant = Column(Numeric, nullable=True)
    commentaires_prestataire = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    prestataire = relationship("Prestataire", back_populates="cotations")
    demandeur = relationship("User", foreign_keys=[demandeur_id])
