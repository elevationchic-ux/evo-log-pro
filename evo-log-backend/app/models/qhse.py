"""QHSE models - Quality, Health, Safety, Environment management for Cameroon/CEMAC"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, Enum, Date, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class TypeRisque(str, enum.Enum):
    """Risk type enumeration"""
    PHYSIQUE = "physique"
    CHIMIQUE = "chimique"
    BIOLOGIQUE = "biologique"
    ERGONOMIQUE = "ergonomique"
    PSYCHOSOCIAL = "psychosocial"
    MECANIQUE = "mecanique"
    ELECTRIQUE = "electrique"
    INCENDIE = "incendie"
    ENVIRONNEMENTAL = "environnemental"


class GraviteRisque(str, enum.Enum):
    """Risk severity enumeration"""
    NEGLIGEABLE = "negligeable"
    MINEUR = "mineur"
    MODERE = "modere"
    MAJEUR = "majeur"
    CRITIQUE = "critique"
    CATASTROPHIQUE = "catastrophique"


class TypeEPI(str, enum.Enum):
    """PPE type enumeration"""
    TETE = "tete"
    VISAGE = "visage"
    AUDITION = "audition"
    RESPIRATOIRE = "respiratoire"
    MAINS = "mains"
    CORPS = "corps"
    PIEDS = "pieds"
    ANTICHUTE = "antichute"
    SIGNALISATION = "signalisation"


class StatutAccident(str, enum.Enum):
    """Accident status enumeration"""
    SIGNALE = "signale"
    EN_COURS = "en_cours"
    INVESTIGUE = "investigue"
    CLOTURE = "cloture"
    REJETE = "rejete"


class NormeISO(str, enum.Enum):
    """ISO standard enumeration"""
    ISO9001 = "iso9001"  # Qualité
    ISO14001 = "iso14001"  # Environnement
    ISO45001 = "iso45001"  # Santé et Sécurité
    ISO22000 = "iso22000"  # Sécurité alimentaire
    HACCP = "haccp"  # Analyse dangers et points critiques


class AnalyseRisque(Base):
    """Risk analysis"""
    __tablename__ = "analyses_risques"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_analyse = Column(String(50), unique=True, nullable=False, index=True)
    zone = Column(String(100), nullable=False)
    processus = Column(String(100), nullable=False)
    date_analyse = Column(Date, nullable=False)
    type_risque = Column(Enum(TypeRisque))
    description_danger = Column(Text, nullable=False)
    causes_potentielles = Column(Text)
    consequences = Column(Text)
    population_exposee = Column(Integer)
    frequence = Column(String(50))  # "rare", "peu_frequent", "frequent", "continu"
    gravite = Column(Enum(GraviteRisque))
    probabilite = Column(Integer)  # 1-5
    risque_calcule = Column(Integer)  # gravite x probabilite
    niveau_risque = Column(String(20))  # "faible", "moyen", "eleve", "critique"
    mesures_existantes = Column(Text)
    mesures_recommandees = Column(Text)
    responsable = Column(String(100))
    date_revision = Column(Date)
    statut = Column(String(20), default="actif")  # actif, revision, clos
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    actions_prevention = relationship("ActionPrevention", back_populates="analyse_risque")


class ActionPrevention(Base):
    """Prevention action"""
    __tablename__ = "actions_prevention"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_action = Column(String(50), unique=True, nullable=False, index=True)
    analyse_risque_id = Column(Integer, ForeignKey('analyses_risques.id'))
    type_action = Column(String(50))  # "elimination", "substitution", "protection_collective", "protection_individuelle"
    description = Column(Text, nullable=False)
    priorite = Column(String(20))  # "haute", "moyenne", "basse"
    responsable = Column(String(100), nullable=False)
    date_prevue = Column(Date)
    date_realisation = Column(Date)
    statut = Column(String(20), default="en_attente")  # en_attente, en_cours, realise, annule
    cout_estime = Column(Numeric(15, 2))
    devise = Column(String(3), default="XAF")
    verification = Column(Text)
    efficacite = Column(String(20))  # "efficace", "partielle", "inefficace"
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    analyse_risque = relationship("AnalyseRisque", back_populates="actions_prevention")


class PlanPrevention(Base):
    """Prevention plan"""
    __tablename__ = "plans_prevention"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_plan = Column(String(50), unique=True, nullable=False, index=True)
    type_activite = Column(String(100), nullable=False)
    zone = Column(String(100), nullable=False)
    date_debut = Column(Date, nullable=False)
    date_fin = Column(Date, nullable=False)
    responsable = Column(String(100), nullable=False)
    description = Column(Text)
    risques_identifies = Column(Text)
    mesures_prevention = Column(Text)
    equipements_protection = Column(Text)
    procedures_urgence = Column(Text)
    formation_requise = Column(Text)
    statut = Column(String(20), default="en_cours")  # en_cours, valide, expire
    date_validation = Column(Date)
    valide_par = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    epi_requis = relationship("EPIRequis", back_populates="plan_prevention")


class EPIRequis(Base):
    """Required PPE"""
    __tablename__ = "epi_requis"
    
    id = Column(Integer, primary_key=True, index=True)
    plan_prevention_id = Column(Integer, ForeignKey('plans_prevention.id'))
    type_epi = Column(Enum(TypeEPI), nullable=False)
    designation = Column(String(200), nullable=False)
    marque = Column(String(100))
    modele = Column(String(100))
    quantite = Column(Integer, nullable=False)
    norme = Column(String(50))
    date_expiration = Column(Date)
    statut = Column(String(20), default="disponible")  # disponible, affecte, perime, remplace
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    plan_prevention = relationship("PlanPrevention", back_populates="epi_requis")


class AccidentTravail(Base):
    """Work accident"""
    __tablename__ = "accidents_travail"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_accident = Column(String(50), unique=True, nullable=False, index=True)
    employe_id = Column(Integer, ForeignKey('users.id'))
    date_accident = Column(DateTime(timezone=True), nullable=False)
    lieu = Column(String(200), nullable=False)
    type_accident = Column(String(50))  # "chute", "cramer", "coupure", "brulure", "intoxication", "autre"
    description = Column(Text, nullable=False)
    partie_corps = Column(String(100))
    gravite = Column(String(20))  # "leger", "moyen", "grave", "mortel"
    temoin1 = Column(String(100))
    temoin2 = Column(String(100))
    premier_secours = Column(Text)
    hospitalisation = Column(Boolean, default=False)
    duree_hospitalisation = Column(Integer)
    arret_travail = Column(Integer)  # en jours
    statut = Column(Enum(StatutAccident), default=StatutAccident.SIGNALE)
    declarant = Column(String(100))
    date_declaration = Column(Date)
    rapport_medical = Column(String(255))
    photos = Column(Text)  # JSON array
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    investigation = relationship("InvestigationAccident", back_populates="accident")


class InvestigationAccident(Base):
    """Accident investigation"""
    __tablename__ = "investigations_accidents"
    
    id = Column(Integer, primary_key=True, index=True)
    accident_id = Column(Integer, ForeignKey('accidents_travail.id'))
    numero_investigation = Column(String(50), unique=True, nullable=False, index=True)
    date_investigation = Column(Date, nullable=False)
    investigateur = Column(String(100), nullable=False)
    temoins = Column(Text)
    causes_directes = Column(Text)
    causes_indirectes = Column(Text)
    causes_racines = Column(Text)
    mesures_correctives = Column(Text)
    mesures_preventives = Column(Text)
    delai_mise_oeuvre = Column(Integer)  # en jours
    responsable_suivi = Column(String(100))
    statut = Column(String(20), default="en_cours")  # en_cours, complete, annulee
    conclusions = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    accident = relationship("AccidentTravail", back_populates="investigation")


class NormeCertification(Base):
    """ISO certification"""
    __tablename__ = "normes_certifications"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_certificat = Column(String(50), unique=True, nullable=False, index=True)
    norme = Column(Enum(NormeISO), nullable=False)
    organisme = Column(String(100), nullable=False)
    date_obtention = Column(Date, nullable=False)
    date_expiration = Column(Date, nullable=False)
    scope = Column(Text)
    statut = Column(String(20), default="actif")  # actif, suspendu, expire, annule
    numero_audit = Column(String(50))
    date_dernier_audit = Column(Date)
    resultat_audit = Column(String(50))  # "conforme", "nc_mineur", "nc_majeur"
    non_conformites = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    audits = relationship("AuditQualite", back_populates="certification")


class AuditQualite(Base):
    """Quality audit"""
    __tablename__ = "audits_qualite"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_audit = Column(String(50), unique=True, nullable=False, index=True)
    certification_id = Column(Integer, ForeignKey('normes_certifications.id'))
    type_audit = Column(String(50))  # "interne", "externe", "certification"
    date_debut = Column(Date, nullable=False)
    date_fin = Column(Date, nullable=False)
    auditeur = Column(String(100), nullable=False)
    equipe_audit = Column(Text)
    scope = Column(Text)
    criteres = Column(Text)
    resultats = Column(Text)
    non_conformites = Column(Text)
    actions_correctives = Column(Text)
    delai_correction = Column(Integer)
    statut = Column(String(20), default="en_cours")  # en_cours, complete, annule
    conclusion = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    certification = relationship("NormeCertification", back_populates="audits")


class HACCPPlan(Base):
    """HACCP plan"""
    __tablename__ = "haccp_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_plan = Column(String(50), unique=True, nullable=False, index=True)
    produit = Column(String(200), nullable=False)
    processus = Column(String(200), nullable=False)
    date_creation = Column(Date, nullable=False)
    date_revision = Column(Date)
    responsable = Column(String(100), nullable=False)
    equipe_haccp = Column(Text)
    diagramme_flux = Column(String(255))
    statut = Column(String(20), default="actif")  # actif, revision, desactive
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    points_critiques = relationship("PointCritiqueCCP", back_populates="haccp_plan")


class PointCritiqueCCP(Base):
    """Critical Control Point"""
    __tablename__ = "points_critiques_ccp"
    
    id = Column(Integer, primary_key=True, index=True)
    haccp_plan_id = Column(Integer, ForeignKey('haccp_plans.id'))
    numero_ccp = Column(String(50), nullable=False)
    etape = Column(String(200), nullable=False)
    danger = Column(Text, nullable=False)
    mesures_prevention = Column(Text)
    limites_critiques = Column(Text, nullable=False)
    surveillance = Column(Text, nullable=False)
    frequence_controle = Column(String(50))
    actions_correctives = Column(Text, nullable=False)
    responsable = Column(String(100), nullable=False)
    enregistrements = Column(Text)
    statut = Column(String(20), default="actif")  # actif, non_conforme, critique
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    haccp_plan = relationship("HACCPPlan", back_populates="points_critiques")
    enregistrements = relationship("EnregistrementHACCP", back_populates="point_critique")


class EnregistrementHACCP(Base):
    """HACCP record"""
    __tablename__ = "enregistrements_haccp"
    
    id = Column(Integer, primary_key=True, index=True)
    point_critique_id = Column(Integer, ForeignKey('points_critiques_ccp.id'))
    date_enregistrement = Column(DateTime(timezone=True), nullable=False)
    valeur_mesuree = Column(Numeric)
    unite = Column(String(20))
    conforme = Column(Boolean, default=True)
    operateur = Column(String(100), nullable=False)
    observations = Column(Text)
    action_prise = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    point_critique = relationship("PointCritiqueCCP", back_populates="enregistrements")


class FormationQHSE(Base):
    """QHSE training"""
    __tablename__ = "formations_qhse"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_formation = Column(String(50), unique=True, nullable=False, index=True)
    type_formation = Column(String(50))  # "securite", "environnement", "qualite", "haccp"
    titre = Column(String(200), nullable=False)
    description = Column(Text)
    formateur = Column(String(100))
    date_debut = Column(Date, nullable=False)
    date_fin = Column(Date, nullable=False)
    duree_heures = Column(Integer)
    lieu = Column(String(200))
    participants = Column(Text)  # JSON array
    objectifs = Column(Text)
    contenu = Column(Text)
    evaluation = Column(Text)
    statut = Column(String(20), default="planifie")  # planifie, en_cours, termine, annule
    cout = Column(Numeric(15, 2))
    devise = Column(String(3), default="XAF")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class IndicateurQHSE(Base):
    """QHSE indicator"""
    __tablename__ = "indicateurs_qhse"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, nullable=False, index=True)
    nom = Column(String(200), nullable=False)
    type_indicateur = Column(String(50))  # "securite", "environnement", "qualite"
    unite = Column(String(20))
    objectif = Column(Numeric)
    periode = Column(String(50))  # "mensuel", "trimestriel", "annuel"
    valeur_actuelle = Column(Numeric)
    valeur_previous = Column(Numeric)
    variation = Column(Numeric)
    tendance = Column(String(20))  # "amelioration", "stagnation", "degradation"
    date_mesure = Column(Date)
    statut = Column(String(20), default="actif")  # actif, inactif
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
