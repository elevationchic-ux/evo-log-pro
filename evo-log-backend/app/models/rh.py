"""
RH models - Complete HR management for Cameroon/CEMAC compliance
Includes all missing HR functionality for professional HR management
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, Enum, Date, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class TypeConge(str, enum.Enum):
    """Leave types compliant with Cameroon labor law"""
    CONGE_ANNUEL = "conge_annuel"
    CONGE_MALADIE = "conge_maladie"
    CONGE_MATERNITE = "conge_maternite"
    CONGE_PATERNITE = "conge_paternite"
    CONGE_EXCEPTIONNEL = "conge_exceptionnel"
    CONGE_SANS_SOLDE = "conge_sans_solde"
    ABSENCE_AUTORISEE = "absence_autorisee"


class StatutConge(str, enum.Enum):
    """Leave status"""
    EN_ATTENTE = "en_attente"
    APPROUVE = "approuve"
    REFUSE = "refuse"
    EN_COURS = "en_cours"
    TERMINE = "termine"
    ANNULE = "annule"


class Conge(Base):
    """Leave management model - Cameroon labor law compliant"""
    __tablename__ = "conges"
    
    id = Column(Integer, primary_key=True, index=True)
    employe_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    type_conge = Column(Enum(TypeConge), nullable=False)
    date_debut = Column(Date, nullable=False)
    date_fin = Column(Date, nullable=False)
    nombre_jours = Column(Integer, nullable=False)
    statut = Column(Enum(StatutConge), default=StatutConge.EN_ATTENTE)
    motif = Column(Text)
    date_demande = Column(Date, server_default=func.current_date())
    date_approbation = Column(Date)
    approbateur_id = Column(Integer, ForeignKey('users.id'))
    commentaires_approbation = Column(Text)
    solde_conge = Column(Integer, default=0)  # Remaining leave days
    pieces_jointes = Column(Text)  # Medical certificates, etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    employe = relationship("User", foreign_keys=[employe_id])
    approbateur = relationship("User", foreign_keys=[approbateur_id])


class Absence(Base):
    """Absence tracking model"""
    __tablename__ = "absences"
    
    id = Column(Integer, primary_key=True, index=True)
    employe_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    date = Column(Date, nullable=False)
    type_absence = Column(String(50))  # maladie, famille, personnelle
    motif = Column(Text)
    justifiee = Column(Boolean, default=False)
    heure_debut = Column(String(10))  # HH:MM format
    heure_fin = Column(String(10))
    nombre_heures = Column(Numeric, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    employe = relationship("User", foreign_keys=[employe_id])


class TempsTravail(Base):
    """Work time tracking model - Timesheets"""
    __tablename__ = "temps_travail"
    
    id = Column(Integer, primary_key=True, index=True)
    employe_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    date = Column(Date, nullable=False)
    heure_arrivee = Column(String(10))
    heure_depart = Column(String(10))
    heures_travaillees = Column(Numeric, default=0)
    heures_supplementaires = Column(Numeric, default=0)
    projet_id = Column(Integer)  # Project code
    tache = Column(String(200))
    statut = Column(String(20), default="valide")  # valide, en_attente, refuse
    validateur_id = Column(Integer, ForeignKey('users.id'))
    date_validation = Column(Date)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    employe = relationship("User", foreign_keys=[employe_id])
    validateur = relationship("User", foreign_keys=[validateur_id])


class Formation(Base):
    """Training management model"""
    __tablename__ = "formations"
    
    id = Column(Integer, primary_key=True, index=True)
    titre = Column(String(200), nullable=False)
    description = Column(Text)
    type_formation = Column(String(50))  # interne, externe, certification
    fournisseur = Column(String(100))
    duree_heures = Column(Integer)
    duree_jours = Column(Integer)
    cout = Column(Numeric)
    lieu = Column(String(100))
    date_debut = Column(Date)
    date_fin = Column(Date)
    nombre_places = Column(Integer)
    competences_visees = Column(Text)  # JSON array of skills
    est_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    participations = relationship("ParticipationFormation", back_populates="formation")


class ParticipationFormation(Base):
    """Training participation model"""
    __tablename__ = "participations_formations"
    
    id = Column(Integer, primary_key=True, index=True)
    formation_id = Column(Integer, ForeignKey('formations.id'), nullable=False)
    employe_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    statut = Column(String(20), default="inscrit")  # inscrit, en_cours, termine, annule
    note = Column(Numeric)
    certification_obtenue = Column(Boolean, default=False)
    date_certification = Column(Date)
    commentaire = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    formation = relationship("Formation", back_populates="participations")
    employe = relationship("User", foreign_keys=[employe_id])


class EvaluationPerformance(Base):
    """Performance evaluation model"""
    __tablename__ = "evaluations_performance"
    
    id = Column(Integer, primary_key=True, index=True)
    employe_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    evaluateur_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    periode_debut = Column(Date, nullable=False)
    periode_fin = Column(Date, nullable=False)
    note_globale = Column(Numeric)
    note_competence_technique = Column(Numeric)
    note_comportement = Column(Numeric)
    note_productivite = Column(Numeric)
    note_assiduite = Column(Numeric)
    objectifs_atteints = Column(Text)
    objectifs_non_atteints = Column(Text)
    points_forts = Column(Text)
    points_amelioration = Column(Text)
    commentaire_global = Column(Text)
    plan_action = Column(Text)
    date_evaluation = Column(Date, server_default=func.current_date())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    employe = relationship("User", foreign_keys=[employe_id])
    evaluateur = relationship("User", foreign_keys=[evaluateur_id])


class ContratTravail(Base):
    """Employment contract model - Cameroon labor law compliant"""
    __tablename__ = "contrats_travail"
    
    id = Column(Integer, primary_key=True, index=True)
    employe_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    type_contrat = Column(String(50), nullable=False)  # CDI, CDD, STAGE, APPRENTISSAGE
    date_debut = Column(Date, nullable=False)
    date_fin = Column(Date)
    salaire_base = Column(Numeric, nullable=False)
    devise = Column(String(10), default="XAF")
    poste = Column(String(100), nullable=False)
    departement = Column(String(100))
    horaire_travail = Column(String(50))  # 35h, 40h, etc.
    lieu_travail = Column(String(200))
    convention_collective = Column(String(100))
    periode_essai = Column(Integer)  # Essai en mois
    statut = Column(String(20), default="actif")  # actif, expire, resilie, suspendu
    motif_fin = Column(Text)
    date_fin_reelle = Column(Date)
    preavis = Column(Integer)  # Jours de préavis
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    employe = relationship("User", foreign_keys=[employe_id])


class Salaire(Base):
    """Salary management model - CEMAC compliant"""
    __tablename__ = "salaires"
    
    id = Column(Integer, primary_key=True, index=True)
    employe_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    periode_debut = Column(Date, nullable=False)
    periode_fin = Column(Date, nullable=False)
    salaire_base = Column(Numeric, nullable=False)
    heures_supplementaires = Column(Numeric, default=0)
    taux_horaire_sup = Column(Numeric, default=0)
    prime_anciennete = Column(Numeric, default=0)
    prime_performance = Column(Numeric, default=0)
    prime_responsabilite = Column(Numeric, default=0)
    prime_logement = Column(Numeric, default=0)
    prime_transport = Column(Numeric, default=0)
    prime_autre = Column(Numeric, default=0)
    deductions_cnps = Column(Numeric, default=0)  # CEMAC social security
    deductions_impot = Column(Numeric, default=0)
    deductions_avances = Column(Numeric, default=0)
    autres_deductions = Column(Numeric, default=0)
    salaire_net = Column(Numeric, nullable=False)
    devise = Column(String(10), default="XAF")
    date_paiement = Column(Date)
    statut = Column(String(20), default="en_attente")  # en_attente, paye, annule
    nombre_heures_travaillees = Column(Numeric, default=0)
    taux_imposition = Column(Numeric, default=0)  # Cameroon tax rate
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    employe = relationship("User", foreign_keys=[employe_id])


class Prime(Base):
    """Bonus management model"""
    __tablename__ = "primes"
    
    id = Column(Integer, primary_key=True, index=True)
    employe_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    type_prime = Column(String(50), nullable=False)  # performance, exceptionnelle, projet, logement
    montant = Column(Numeric, nullable=False)
    devise = Column(String(10), default="XAF")
    motif = Column(Text)
    periode = Column(String(20))  # YYYY-MM
    date_octroi = Column(Date, server_default=func.current_date())
    approuve_par = Column(Integer, ForeignKey('users.id'))
    statut = Column(String(20), default="en_attente")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    employe = relationship("User", foreign_keys=[employe_id])


class DocumentEmploye(Base):
    """Employee document management model"""
    __tablename__ = "documents_employe"
    
    id = Column(Integer, primary_key=True, index=True)
    employe_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    type_document = Column(String(50), nullable=False)  # cv, diplome, contrat, casier, certificat
    nom_fichier = Column(String(255), nullable=False)
    url_fichier = Column(String(500))
    date_emission = Column(Date)
    date_expiration = Column(Date)
    numero_document = Column(String(100))
    organisme_emetteur = Column(String(200))
    est_valide = Column(Boolean, default=True)
    statut = Column(String(20), default="en_cours")  # en_cours, approuve, refuse, expire
    commentaire = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    employe = relationship("User", foreign_keys=[employe_id])


class Organigramme(Base):
    """Organization chart model"""
    __tablename__ = "organigramme"
    
    id = Column(Integer, primary_key=True, index=True)
    employe_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    manager_id = Column(Integer, ForeignKey('users.id'))
    poste = Column(String(100), nullable=False)
    departement = Column(String(100), nullable=False)
    niveau_hierarchique = Column(Integer)  # 1 = top, 2 = middle, etc.
    sous_ordinates = Column(Text)  # JSON array of subordinate IDs
    date_debut_poste = Column(Date, nullable=False)
    date_fin_poste = Column(Date)
    est_actif = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    employe = relationship("User", foreign_keys=[employe_id])
    manager = relationship("User", foreign_keys=[manager_id])


class Competence(Base):
    """Skills/Competencies model"""
    __tablename__ = "competences"
    
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(100), nullable=False)
    categorie = Column(String(50))  # technique, comportementale, linguistique
    description = Column(Text)
    niveau_maitrise = Column(String(20))  # debutant, intermediaire, avance, expert
    est_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class CompetenceEmploye(Base):
    """Employee skills model"""
    __tablename__ = "competences_employe"
    
    id = Column(Integer, primary_key=True, index=True)
    employe_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    competence_id = Column(Integer, ForeignKey('competences.id'), nullable=False)
    niveau = Column(String(20))
    date_evaluation = Column(Date)
    evaluateur_id = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    employe = relationship("User", foreign_keys=[employe_id])
    competence = relationship("Competence", foreign_keys=[competence_id])
    evaluateur = relationship("User", foreign_keys=[evaluateur_id])