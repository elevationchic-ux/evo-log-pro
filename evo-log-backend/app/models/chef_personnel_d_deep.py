"""Modeles chef-personnel (expansion approfondie generee).

15 entites de gestion, chacune scoped par company_id.
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

class ChpRecruitmentCampaign_statut(str, enum.Enum):
    OUVERTE = "ouverte"
    EN_COURS = "en_cours"
    POURVUE = "pourvue"
    CLOTUREE = "cloturee"
    GELEE = "gelee"


class ChpJobPosting_canal(str, enum.Enum):
    INTERNE = "interne"
    SITE = "site"
    JOBBOARD = "jobboard"
    RESEAU = "reseau"


class ChpJobPosting_statut(str, enum.Enum):
    BROUILLON = "brouillon"
    PUBLIEE = "publiee"
    PAUSEE = "pausee"
    RETIRE = "retire"


class ChpCandidateSelection_phase(str, enum.Enum):
    TRI = "tri"
    ENTRETIEN = "entretien"
    TEST = "test"
    OFFRE = "offre"
    REFUS = "refus"


class ChpCandidateSelection_statut(str, enum.Enum):
    EN_COURS = "en_cours"
    RETENU = "retenu"
    ECARTE = "ecarte"


class ChpInterviewSchedule_format(str, enum.Enum):
    TELEPHONE = "telephone"
    VISIO = "visio"
    SUR_SITE = "sur_site"


class ChpInterviewSchedule_statut(str, enum.Enum):
    PLANIFIE = "planifie"
    TENU = "tenu"
    MANQUE = "manque"
    REPORTE = "reporte"


class ChpOfferApproval_statut(str, enum.Enum):
    SOUMISE = "soumise"
    EN_COURS = "en_cours"
    APPROUVEE = "approuvee"
    REJETEE = "rejetee"
    NEGOCIEE = "negociee"


class ChpOnboardingChecklist_statut(str, enum.Enum):
    EN_COURS = "en_cours"
    TERMINEE = "terminee"
    PARTIELLE = "partielle"


class ChpProbationReview_avis(str, enum.Enum):
    TITULARISE = "titularise"
    RENOUVELE = "renouvele"
    ROMPU = "rompu"


class ChpProbationReview_statut(str, enum.Enum):
    A_JUGER = "a_juger"
    JUGE = "juge"
    SIGNIFIE = "signifie"


class ChpExitInterview_motif(str, enum.Enum):
    DEMISSION = "demission"
    LICENCIEMENT = "licenciement"
    RETRAITE = "retraite"
    FIN_CDD = "fin_cdd"
    INTERNE = "interne"


class ChpExitInterview_statut(str, enum.Enum):
    PLANIFIE = "planifie"
    TENU = "tenu"
    ANALYSE = "analyse"
    CLASSE = "classe"


class ChpHeadcountRequest_statut(str, enum.Enum):
    SOUMISE = "soumise"
    INSTRUIT = "instruit"
    APPROUVEE = "approuvee"
    REFUSEE = "refusee"


class ChpOrgMovement_type_mouvement(str, enum.Enum):
    PROMOTION = "promotion"
    TRANSFERT = "transfert"
    REASSIGNATION = "reassignation"
    INTERRIM = "interrim"


class ChpOrgMovement_statut(str, enum.Enum):
    PROJETE = "projete"
    VALIDEE = "validee"
    APPLIQUEE = "appliquee"
    ANNULEE = "annulee"


class ChpDisciplinaryAction_type_mesure(str, enum.Enum):
    RAPPEL = "rappel"
    AVERTISSEMENT = "avertissement"
    MISE_PIED = "mise_pied"
    EXCLUSION = "exclusion"
    LICENCIEMENT = "licenciement"


class ChpDisciplinaryAction_statut(str, enum.Enum):
    ENGAGEE = "engagee"
    NOTIFIEE = "notifiee"
    CONTESTEE = "contestee"
    CLOTURE = "cloture"


class ChpTrainingPlan_statut(str, enum.Enum):
    ELABORE = "elabore"
    SOUMIS = "soumis"
    ARBITRE = "arbitre"
    EN_COURS = "en_cours"
    CLOTURE = "cloture"


class ChpAbsenceApproval_statut(str, enum.Enum):
    A_VALIDER = "a_valider"
    ACCEPTEE = "acceptee"
    REFUSEE = "refusee"
    REPORTEE = "reportee"


class ChpPayrollAdjustmentRequest_statut(str, enum.Enum):
    SOUMISE = "soumise"
    INSTRUIT = "instruit"
    APPROUVE = "approuve"
    REJETE = "rejete"
    PAYE = "paye"


class ChpPolicyAck_statut(str, enum.Enum):
    A_SIGNER = "a_signer"
    SIGNEE = "signee"
    EXPIREE = "expiree"
    A_RENOUVELER = "a_renouveler"


# ─── Modeles ──────────────────────────────────────────────────────────────────

class ChpRecruitmentCampaign(Base):
    """Campagnes de recrutement."""
    __tablename__ = "chp_recruitment_campaigns"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_chp_recruitment_camp_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    poste = Column(String(150), nullable=True)
    volume = Column(Integer, nullable=True)
    ouverture = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ChpJobPosting(Base):
    """Offres d' emploi."""
    __tablename__ = "chp_job_postings"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_chp_job_postings_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    intitule = Column(String(150), nullable=True)
    canal = Column(String(150), nullable=True)
    parution = Column(Date, nullable=True)
    candidats = Column(Integer, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ChpCandidateSelection(Base):
    """Selection de candidats."""
    __tablename__ = "chp_candidate_selections"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_chp_candidate_select_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    candidat = Column(String(150), nullable=True)
    poste = Column(String(150), nullable=True)
    phase = Column(String(150), nullable=True)
    evaluateur = Column(String(150), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ChpInterviewSchedule(Base):
    """Planifications d' entretiens."""
    __tablename__ = "chp_interview_schedules"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_chp_interview_schedu_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    candidat = Column(String(150), nullable=True)
    date = Column(DateTime(timezone=True), nullable=True)
    format = Column(String(150), nullable=True)
    evaluateur = Column(String(150), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ChpOfferApproval(Base):
    """Validations d' offres."""
    __tablename__ = "chp_offer_approvals"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_chp_offer_approvals_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    candidat = Column(String(150), nullable=True)
    poste = Column(String(150), nullable=True)
    remuneration = Column(Numeric, nullable=True)
    validateur = Column(String(150), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ChpOnboardingChecklist(Base):
    """Checklists d' integration."""
    __tablename__ = "chp_onboarding_checklists"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_chp_onboarding_check_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    collaborateur = Column(String(150), nullable=True)
    etapes_total = Column(Integer, nullable=True)
    etapes_faites = Column(Integer, nullable=True)
    date_debut = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ChpProbationReview(Base):
    """Revues de periode d' essai."""
    __tablename__ = "chp_probation_reviews"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_chp_probation_review_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    collaborateur = Column(String(150), nullable=True)
    date_echeance = Column(Date, nullable=True)
    avis = Column(String(150), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ChpExitInterview(Base):
    """Entretiens de depart."""
    __tablename__ = "chp_exit_interviews"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_chp_exit_interviews_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    collaborateur = Column(String(150), nullable=True)
    motif = Column(String(150), nullable=True)
    date = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ChpHeadcountRequest(Base):
    """Demandes de creation de poste."""
    __tablename__ = "chp_headcount_requests"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_chp_headcount_reques_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    departement = Column(String(150), nullable=True)
    poste = Column(String(150), nullable=True)
    masse_salariale = Column(Numeric, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ChpOrgMovement(Base):
    """Mouvements organisationnels."""
    __tablename__ = "chp_org_movements"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_chp_org_movements_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    collaborateur = Column(String(150), nullable=True)
    type_mouvement = Column(String(150), nullable=True)
    date_effet = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ChpDisciplinaryAction(Base):
    """Mesures disciplinaires."""
    __tablename__ = "chp_disciplinary_actions"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_chp_disciplinary_act_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    collaborateur = Column(String(150), nullable=True)
    motif = Column(Text, nullable=True)
    type_mesure = Column(String(150), nullable=True)
    date = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ChpTrainingPlan(Base):
    """Plans de formation."""
    __tablename__ = "chp_training_plans"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_chp_training_plans_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    departement = Column(String(150), nullable=True)
    exercice = Column(String(150), nullable=True)
    budget = Column(Numeric, nullable=True)
    actions = Column(Integer, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ChpAbsenceApproval(Base):
    """Validations d' absences."""
    __tablename__ = "chp_absence_approvals"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_chp_absence_approval_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    collaborateur = Column(String(150), nullable=True)
    manager = Column(String(150), nullable=True)
    debut = Column(Date, nullable=True)
    fin = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ChpPayrollAdjustmentRequest(Base):
    """Demandes d' ajustement de paie."""
    __tablename__ = "chp_payroll_adjustments"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_chp_payroll_adjustme_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    collaborateur = Column(String(150), nullable=True)
    motif = Column(String(150), nullable=True)
    montant = Column(Numeric, nullable=True)
    periode = Column(String(150), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ChpPolicyAck(Base):
    """Accuses de politique RH."""
    __tablename__ = "chp_policy_acks"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_chp_policy_acks_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    collaborateur = Column(String(150), nullable=True)
    politique = Column(String(150), nullable=True)
    version = Column(String(150), nullable=True)
    date = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

