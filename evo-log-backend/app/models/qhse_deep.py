"""Modeles qhse-securite (expansion approfondie generee).

11 entites de gestion, chacune scoped par company_id.
Convention d'honnetete : aucune valeur par defaut, NULL = "non enregistre".
"""
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean, Float,
    ForeignKey, Date, Numeric, UniqueConstraint, Enum as SAEnum,
)
from sqlalchemy.sql import func
import enum

from app.core.database import Base


def _enum(cls):
    return SAEnum(cls, native_enum=False, create_constraint=False,
                  values_callable=lambda x: [e.value for e in x])


# ─── Enums ────────────────────────────────────────────────────────────────────

class EnvironmentalMeasurement_type_relevé(str, enum.Enum):
    BRUIT = "bruit"
    AIR = "air"
    EAU = "eau"
    SOL = "sol"


class EnvironmentalMeasurement_conformite(str, enum.Enum):
    CONFORME = "conforme"
    NON_CONFORME = "non_conforme"
    LIMITE = "limite"


class WasteRecord_type_dechet(str, enum.Enum):
    ORDINAIRE = "ordinaire"
    INDUSTRIEL = "industriel"
    DANGEREUX = "dangereux"
    RECYCLABLE = "recyclable"


class WasteRecord_statut(str, enum.Enum):
    EMI = "emi"
    TRANSPORTE = "transporte"
    RECU = "recu"
    TRAITE = "traite"


class SafetyDataSheet_classification(str, enum.Enum):
    NON_CLASSE = "non_classe"
    XN = "xn"
    T = "t"
    C = "c"
    E = "e"
    F = "f"


class EmergencyPlan_type_plan(str, enum.Enum):
    EVACUATION = "evacuation"
    INCENDIE = "incendie"
    INONDATION = "inondation"
    ALERT_TOXIQUE = "alert_toxique"


class PpeItem_type_epi(str, enum.Enum):
    CASQUE = "casque"
    LUNETTES = "lunettes"
    GANTS = "gants"
    CHAUSSURES = "chaussures"
    HAUTE_VISIBILITE = "haute_visibilite"
    RESPIRATOIRE = "respiratoire"


class PpeItem_statut(str, enum.Enum):
    EN_SERVICE = "en_service"
    REMPLACE = "remplace"
    PERTE = "perte"
    EXPIRE = "expire"


class HealthVisit_type_visite(str, enum.Enum):
    EMBAUCHE = "embauche"
    PERIODIQUE = "periodique"
    REPRISE = "reprise"
    SUR_DEMANDE = "sur_demande"


class HealthVisit_resultat(str, enum.Enum):
    APTE = "apte"
    APTE_AVEC_RESTRICTION = "apte_avec_restriction"
    INAPTE_TEMPORAIRE = "inapte_temporaire"
    INAPTE_DEFINITIF = "inapte_definitif"


class RiskAssessment_cotation(str, enum.Enum):
    FAIBLE = "faible"
    MOYEN = "moyen"
    ELEVE = "eleve"
    CRITIQUE = "critique"


class CorrectiveAction_statut(str, enum.Enum):
    OUVERT = "ouvert"
    EN_COURS = "en_cours"
    VERIFIE = "verifie"
    CLOTURE = "cloture"


class ManagementReview_statut(str, enum.Enum):
    PLANIFIE = "planifie"
    TENUE = "tenue"
    PV_DIFFUSE = "pv_diffuse"


class ComplianceRecord_domaine(str, enum.Enum):
    ICPE = "icpe"
    ISPS = "isps"
    CNPS = "cnps"
    MARPOL = "marpol"
    TRAVAIL = "travail"
    ENVIRONNEMENT = "environnement"


class ComplianceRecord_statut(str, enum.Enum):
    CONFORME = "conforme"
    PARTIEL = "partiel"
    NON_CONFORME = "non_conforme"


class QualityAudit_type_audit(str, enum.Enum):
    INTERNE = "interne"
    EXTERNE = "externe"
    CERTIFICATION = "certification"
    FOURNISSEUR = "fournisseur"


class QualityAudit_statut(str, enum.Enum):
    PLANIFIE = "planifie"
    EN_COURS = "en_cours"
    TERMINE = "termine"
    CLOTURE = "cloture"


# ─── Modeles ──────────────────────────────────────────────────────────────────

class EnvironmentalMeasurement(Base):
    """Suivi environnemental."""
    __tablename__ = "environmental_measurements"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_environmental_measur_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    type_relevé = Column(_enum(EnvironmentalMeasurement_type_relevé), default=EnvironmentalMeasurement_type_relevé.AIR)
    polluant = Column(String(150), nullable=True)
    valeur = Column(Numeric, nullable=True)
    unite = Column(String(150), nullable=True)
    norme_max = Column(Numeric, nullable=True)
    station = Column(String(150), nullable=True)
    date_relevé = Column(DateTime(timezone=True), nullable=True)
    conformite = Column(_enum(EnvironmentalMeasurement_conformite), default=EnvironmentalMeasurement_conformite.CONFORME)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class WasteRecord(Base):
    """Gestion dechets / BSD."""
    __tablename__ = "waste_records"
    __table_args__ = (
        UniqueConstraint('company_id', 'numero_bsd', name='uix_waste_records_company_numero_bsd'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    numero_bsd = Column(String(150), nullable=False, index=True)
    type_dechet = Column(_enum(WasteRecord_type_dechet), default=WasteRecord_type_dechet.ORDINAIRE)
    quantite_kg = Column(Numeric, nullable=True)
    date_production = Column(Date, nullable=True)
    transporteur = Column(String(150), nullable=True)
    destination = Column(String(150), nullable=True)
    statut = Column(_enum(WasteRecord_statut), default=WasteRecord_statut.EMI)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class SafetyDataSheet(Base):
    """FDS et produits chimiques."""
    __tablename__ = "safety_data_sheets"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_safety_data_sheets_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    nom_produit = Column(String(150), nullable=True)
    numero_ce = Column(String(150), nullable=True)
    fournisseur = Column(String(150), nullable=True)
    phrase_risque = Column(Text(2000), nullable=True)
    version_fds = Column(String(150), nullable=True)
    date_revision = Column(Date, nullable=True)
    classification = Column(_enum(SafetyDataSheet_classification), default=SafetyDataSheet_classification.NON_CLASSE)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class EmergencyPlan(Base):
    """Plans d'urgence / exercices."""
    __tablename__ = "emergency_plans"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_emergency_plans_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    type_plan = Column(_enum(EmergencyPlan_type_plan), default=EmergencyPlan_type_plan.EVACUATION)
    zone_concernee = Column(String(150), nullable=True)
    date_elaboration = Column(Date, nullable=True)
    date_dernier_exercice = Column(Date, nullable=True)
    frequence_exercice_mois = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class PpeItem(Base):
    """EPI equipements protection."""
    __tablename__ = "ppe_items"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_ppe_items_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    employe_id = Column(Integer, nullable=True)
    type_epi = Column(_enum(PpeItem_type_epi), default=PpeItem_type_epi.CASQUE)
    taille = Column(String(150), nullable=True)
    date_attribution = Column(Date, nullable=True)
    date_expiration = Column(Date, nullable=True)
    quantite = Column(Integer, nullable=True)
    statut = Column(_enum(PpeItem_statut), default=PpeItem_statut.EN_SERVICE)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class HealthVisit(Base):
    """Medecine du travail."""
    __tablename__ = "health_visits"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_health_visits_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    employe_id = Column(Integer, nullable=True)
    type_visite = Column(_enum(HealthVisit_type_visite), default=HealthVisit_type_visite.EMBAUCHE)
    date_visite = Column(Date, nullable=True)
    medecin = Column(String(150), nullable=True)
    resultat = Column(_enum(HealthVisit_resultat), default=HealthVisit_resultat.APTE)
    prochaine_visite = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class RiskAssessment(Base):
    """Evaluation des risques (DUER)."""
    __tablename__ = "risk_assessments"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_risk_assessments_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    unite_travail = Column(String(150), nullable=True)
    description_risque = Column(Text(2000), nullable=True)
    cotation = Column(_enum(RiskAssessment_cotation), default=RiskAssessment_cotation.MOYEN)
    mesure_prevention = Column(Text(2000), nullable=True)
    date_evaluation = Column(Date, nullable=True)
    responsable = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class CorrectiveAction(Base):
    """Actions correctives / 8D."""
    __tablename__ = "corrective_actions"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_corrective_actions_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    source_ecart = Column(String(150), nullable=True)
    description_probleme = Column(Text(2000), nullable=True)
    cause_racine = Column(Text(2000), nullable=True)
    action_corrective = Column(Text(2000), nullable=True)
    responsable = Column(String(150), nullable=True)
    date_prevue_cloture = Column(Date, nullable=True)
    statut = Column(_enum(CorrectiveAction_statut), default=CorrectiveAction_statut.OUVERT)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ManagementReview(Base):
    """Revues de direction."""
    __tablename__ = "management_reviews"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_management_reviews_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    date_revue = Column(Date, nullable=True)
    participants = Column(Text(2000), nullable=True)
    sujets = Column(Text(2000), nullable=True)
    decisions = Column(Text(2000), nullable=True)
    statut = Column(_enum(ManagementReview_statut), default=ManagementReview_statut.PLANIFIE)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ComplianceRecord(Base):
    """Conformite reglementaire."""
    __tablename__ = "compliance_records"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_compliance_records_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    regulation = Column(String(150), nullable=True)
    domaine = Column(_enum(ComplianceRecord_domaine), default=ComplianceRecord_domaine.ICPE)
    obligation = Column(Text(2000), nullable=True)
    preuve = Column(Text(2000), nullable=True)
    date_constat = Column(Date, nullable=True)
    prochaine_echeance = Column(Date, nullable=True)
    statut = Column(_enum(ComplianceRecord_statut), default=ComplianceRecord_statut.CONFORME)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class QualityAudit(Base):
    """Audits internes qualite."""
    __tablename__ = "quality_audits"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_quality_audits_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    type_audit = Column(_enum(QualityAudit_type_audit), default=QualityAudit_type_audit.INTERNE)
    perimetre = Column(String(150), nullable=True)
    auditeur = Column(String(150), nullable=True)
    date_debut = Column(Date, nullable=True)
    date_fin = Column(Date, nullable=True)
    nb_ecarts = Column(Integer, nullable=True)
    statut = Column(_enum(QualityAudit_statut), default=QualityAudit_statut.PLANIFIE)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

