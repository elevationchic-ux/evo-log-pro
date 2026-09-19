"""Training and Certification Models - E-learning, User Certification"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, Enum, Date, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class CategorieFormation(str, enum.Enum):
    """Training category enumeration"""
    DOUANE = "douane"
    TRANSPORT = "transport"
    FINANCE = "finance"
    OPERATIONS = "operations"
    QUALITE = "qualite"
    SECURITE = "securite"
    SYSTEME = "systeme"


class NiveauFormation(str, enum.Enum):
    """Training level enumeration"""
    DEBUTANT = "debutant"
    INTERMEDIAIRE = "intermediaire"
    AVANCE = "avance"
    EXPERT = "expert"


class StatutCertification(str, enum.Enum):
    """Certification status enumeration"""
    EN_COURS = "en_cours"
    REUSSI = "reussi"
    ECHOUE = "echoue"
    EXPIRE = "expire"


class ModuleFormation(Base):
    """Module de formation"""
    __tablename__ = "modules_formation"
    
    id = Column(Integer, primary_key=True, index=True)
    titre = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    contenu = Column(Text, nullable=False)  # Markdown
    contenu_html = Column(Text)
    video_url = Column(String(255))
    duree_minutes = Column(Integer, nullable=False)
    categorie = Column(Enum(CategorieFormation), nullable=False)
    sous_categorie = Column(String(50))
    niveau = Column(Enum(NiveauFormation), default=NiveauFormation.DEBUTANT)
    prerequis = Column(Text)  # JSON array des modules requis
    objectifs = Column(Text)  # JSON array des objectifs
    langue = Column(String(10), default="fr")
    ordre = Column(Integer, default=0)
    est_publie = Column(Boolean, default=True)
    date_publication = Column(Date, nullable=False)
    auteur = Column(String(100))
    version = Column(String(20))
    nombre_vues = Column(Integer, default=0)
    note_moyenne = Column(Numeric)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    quizzes = relationship("QuizFormation", back_populates="module")


class QuizFormation(Base):
    """Quiz de formation"""
    __tablename__ = "quizzes_formation"
    
    id = Column(Integer, primary_key=True, index=True)
    module_id = Column(Integer, ForeignKey('modules_formation.id'), nullable=False)
    titre = Column(String(200), nullable=False)
    description = Column(Text)
    nombre_questions = Column(Integer, nullable=False)
    score_reussite = Column(Integer, nullable=False)  # Score minimum pour réussir
    duree_minutes = Column(Integer, default=30)
    melange_questions = Column(Boolean, default=True)  # Questions mélangées
    est_actif = Column(Boolean, default=True)
    date_creation = Column(Date, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    module = relationship("ModuleFormation", back_populates="quizzes")
    questions = relationship("QuestionQuiz", back_populates="quiz")
    tentatives = relationship("TentativeQuiz", back_populates="quiz")


class QuestionQuiz(Base):
    """Question de quiz"""
    __tablename__ = "questions_quiz"
    
    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey('quizzes_formation.id'), nullable=False)
    question = Column(Text, nullable=False)
    type_question = Column(String(20), nullable=False)  # CHOIX_SIMPLE, CHOIX_MULTIPLE, VRAI_FAUX
    options = Column(Text, nullable=False)  # JSON array des options
    reponse_correcte = Column(Text, nullable=False)  # JSON array ou string
    explication = Column(Text)
    points = Column(Integer, default=1)
    ordre = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    quiz = relationship("QuizFormation", back_populates="questions")


class TentativeQuiz(Base):
    """Tentative de quiz"""
    __tablename__ = "tentatives_quiz"
    
    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey('quizzes_formation.id'), nullable=False)
    utilisateur_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    date_debut = Column(DateTime(timezone=True), nullable=False)
    date_fin = Column(DateTime(timezone=True))
    score = Column(Integer)
    score_maximum = Column(Integer)
    pourcentage = Column(Numeric)
    statut = Column(String(20), default="en_cours")  # en_cours, termine
    reponses = Column(Text)  # JSON array des réponses
    duree_minutes = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    quiz = relationship("QuizFormation", back_populates="tentatives")


class CertificationUtilisateur(Base):
    """Certification utilisateur"""
    __tablename__ = "certifications_utilisateurs"
    
    id = Column(Integer, primary_key=True, index=True)
    utilisateur_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    module_id = Column(Integer, ForeignKey('modules_formation.id'), nullable=False)
    date_passage = Column(DateTime(timezone=True), nullable=False)
    score = Column(Integer, nullable=False)
    score_maximum = Column(Integer, nullable=False)
    pourcentage = Column(Numeric, nullable=False)
    statut = Column(Enum(StatutCertification), default=StatutCertification.EN_COURS)
    date_expiration = Column(Date)
    numero_certificat = Column(String(50), unique=True)
    certificat_url = Column(String(255))  # URL scan certificat
    valide_par = Column(String(100))  # Responsable validation
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class SupportUtilisateur(Base):
    """Support utilisateur - Tickets, Chat, Email"""
    __tablename__ = "support_utilisateurs"
    
    id = Column(Integer, primary_key=True, index=True)
    utilisateur_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    type_support = Column(String(20), nullable=False)  # TICKET, CHAT, EMAIL, TELEPHONE
    titre = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    categorie = Column(String(50))  # TECHNIQUE, OPERATIONNEL, FACTURATION, PAIEMENT
    priorite = Column(String(20), default="normale")  # basse, normale, haute, critique
    statut = Column(String(20), default="ouvert")  # ouvert, en_cours, resolu, ferme
    date_creation = Column(DateTime(timezone=True), nullable=False)
    date_resolution = Column(DateTime(timezone=True))
    duree_resolution_heures = Column(Numeric)
    assigne_a = Column(Integer, ForeignKey('users.id'))
    solution = Column(Text)
    satisfaction = Column(Integer)  # 1-5
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
