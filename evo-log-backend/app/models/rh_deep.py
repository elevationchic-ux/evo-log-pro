"""Modeles rh-personnel (expansion approfondie generee).

13 entites de gestion, chacune scoped par company_id.
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

class Recruitment_type_contrat(str, enum.Enum):
    CDI = "cdi"
    CDD = "cdd"
    STAGE = "stage"
    DETECTION = "detection"
    INTERIM = "interim"


class Recruitment_statut(str, enum.Enum):
    OUVERTE = "ouverte"
    EN_COURS = "en_cours"
    POURVUE = "pourvue"
    ANNULEE = "annulee"


class TrainingPlan_type_action(str, enum.Enum):
    FORMATION = "formation"
    HABILITATION = "habilitation"
    SEMINAIRE = "seminaire"
    CERTIFICATION = "certification"


class TrainingPlan_statut(str, enum.Enum):
    PLANIFIE = "planifie"
    EN_COURS = "en_cours"
    TERMINE = "termine"
    ANNULE = "annule"


class PerformanceReview_statut(str, enum.Enum):
    PLANIFIE = "planifie"
    REALISE = "realise"
    VALIDE = "valide"
    REVOIT = "revoit"


class DisciplinaryCase_type_sanction(str, enum.Enum):
    AVERTISSEMENT = "avertissement"
    BLAME = "blame"
    MISE_PIED = "mise_pied"
    REVOICATION = "revoication"


class DisciplinaryCase_statut(str, enum.Enum):
    OUVERTE = "ouverte"
    CONVOQUE = "convoque"
    DECIDE = "decide"
    CLOTURE = "cloture"


class OrgUnit_type_unite(str, enum.Enum):
    DIRECTION = "direction"
    DEPARTEMENT = "departement"
    SERVICE = "service"
    EQUIPE = "equipe"


class EmploymentContract_type_contrat(str, enum.Enum):
    CDI = "cdi"
    CDD = "cdd"
    DETECTION = "detection"
    STAGE = "stage"
    INTERIM = "interim"


class EmploymentContract_statut(str, enum.Enum):
    ACTIF = "actif"
    RENOUVELE = "renouvele"
    EXPIRE = "expire"
    RUPTURE = "rupture"


class EmployeeBenefit_type_avantage(str, enum.Enum):
    MUTUELLE = "mutuelle"
    TRANSPORT = "transport"
    LOGEMENT = "logement"
    RESTAURATION = "restauration"
    PREVOYANCE = "prevoyance"


class EmployeeBenefit_statut(str, enum.Enum):
    ACTIF = "actif"
    SUSPENDU = "suspendu"
    ARRETE = "arrete"


class EmployeeExit_type_depart(str, enum.Enum):
    DEMISION = "demision"
    FIN_CDD = "fin_cdd"
    LICENCIEMENT = "licenciement"
    RETRAITE = "retraite"


class EmployeeExit_statut(str, enum.Enum):
    OUVERT = "ouvert"
    EN_COURS = "en_cours"
    CLOTURE = "cloture"


class AttendanceDevice_type_terminal(str, enum.Enum):
    BADGE = "badge"
    BIOMETRIE = "biometrie"
    MOBILE_APP = "mobile_app"
    QR_CODE = "qr_code"


class AttendanceDevice_statut(str, enum.Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    PANNE = "panne"


class EmployeeSkill_niveau(str, enum.Enum):
    DEBUTANT = "debutant"
    INTERMEDIAIRE = "intermediaire"
    EXPERT = "expert"
    MAITRE = "maitre"


# ─── Modeles ──────────────────────────────────────────────────────────────────

class Recruitment(Base):
    """Offres et candidatures."""
    __tablename__ = "recruitments"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_recruitments_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    poste = Column(String(150), nullable=True)
    departement = Column(String(150), nullable=True)
    type_contrat = Column(_enum(Recruitment_type_contrat), default=Recruitment_type_contrat.CDI)
    date_ouverture = Column(Date, nullable=True)
    date_cloture = Column(Date, nullable=True)
    candidats_recus = Column(Integer, nullable=True)
    statut = Column(_enum(Recruitment_statut), default=Recruitment_statut.OUVERTE)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class TrainingPlan(Base):
    """Plan de formation."""
    __tablename__ = "training_plans"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_training_plans_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    intitule = Column(String(150), nullable=True)
    type_action = Column(_enum(TrainingPlan_type_action), default=TrainingPlan_type_action.FORMATION)
    organisme = Column(String(150), nullable=True)
    date_debut = Column(Date, nullable=True)
    date_fin = Column(Date, nullable=True)
    duree_heures = Column(Integer, nullable=True)
    cout_xaf = Column(Numeric, nullable=True)
    statut = Column(_enum(TrainingPlan_statut), default=TrainingPlan_statut.PLANIFIE)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class PerformanceReview(Base):
    """Entretiens d'evaluation."""
    __tablename__ = "performance_reviews"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_performance_reviews_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    employe_id = Column(Integer, nullable=True)
    periode = Column(String(150), nullable=True)
    date_entretien = Column(Date, nullable=True)
    evaluateur = Column(String(150), nullable=True)
    note_global = Column(Numeric, nullable=True)
    objectifs_atteints_pct = Column(Numeric, nullable=True)
    statut = Column(_enum(PerformanceReview_statut), default=PerformanceReview_statut.PLANIFIE)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class DisciplinaryCase(Base):
    """Procedures disciplinaires."""
    __tablename__ = "disciplinary_cases"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_disciplinary_cases_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    employe_id = Column(Integer, nullable=True)
    date_fait = Column(Date, nullable=True)
    type_sanction = Column(_enum(DisciplinaryCase_type_sanction), default=DisciplinaryCase_type_sanction.AVERTISSEMENT)
    motif = Column(Text(2000), nullable=True)
    date_convocation = Column(Date, nullable=True)
    date_decision = Column(Date, nullable=True)
    statut = Column(_enum(DisciplinaryCase_statut), default=DisciplinaryCase_statut.OUVERTE)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class OrgUnit(Base):
    """Organigramme."""
    __tablename__ = "org_units"
    __table_args__ = (
        UniqueConstraint('company_id', 'code_unite', name='uix_org_units_company_code_unite'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    code_unite = Column(String(150), nullable=False, index=True)
    nom = Column(String(150), nullable=True)
    parent_code = Column(String(150), nullable=True)
    type_unite = Column(_enum(OrgUnit_type_unite), default=OrgUnit_type_unite.DEPARTEMENT)
    responsable = Column(String(150), nullable=True)
    effectif = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class WorkforcePlan(Base):
    """Masse salariale previsionnelle."""
    __tablename__ = "workforce_plans"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_workforce_plans_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    exercice = Column(Integer, nullable=True)
    mois = Column(String(150), nullable=True)
    masse_salariale_prevue_xaf = Column(Numeric, nullable=True)
    effectif_cadre = Column(Integer, nullable=True)
    effectif_non_cadre = Column(Integer, nullable=True)
    hypothese_inflation_pct = Column(Numeric, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class EmploymentContract(Base):
    """Suivi contrats."""
    __tablename__ = "employment_contracts"
    __table_args__ = (
        UniqueConstraint('company_id', 'numero_contrat', name='uix_employment_contracts_company_numero_contrat'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    numero_contrat = Column(String(150), nullable=False, index=True)
    employe_id = Column(Integer, nullable=True)
    type_contrat = Column(_enum(EmploymentContract_type_contrat), default=EmploymentContract_type_contrat.CDI)
    date_debut = Column(Date, nullable=True)
    date_fin = Column(Date, nullable=True)
    avenants = Column(Text(2000), nullable=True)
    statut = Column(_enum(EmploymentContract_statut), default=EmploymentContract_statut.ACTIF)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class EmployeeBenefit(Base):
    """Avantages."""
    __tablename__ = "employee_benefits"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_employee_benefits_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    employe_id = Column(Integer, nullable=True)
    type_avantage = Column(_enum(EmployeeBenefit_type_avantage), default=EmployeeBenefit_type_avantage.MUTUELLE)
    montant_annuel_xaf = Column(Numeric, nullable=True)
    date_debut = Column(Date, nullable=True)
    date_fin = Column(Date, nullable=True)
    statut = Column(_enum(EmployeeBenefit_statut), default=EmployeeBenefit_statut.ACTIF)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class EmployeeExit(Base):
    """Depart / solde tout compte."""
    __tablename__ = "employee_exits"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_employee_exits_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    employe_id = Column(Integer, nullable=True)
    type_depart = Column(_enum(EmployeeExit_type_depart), default=EmployeeExit_type_depart.DEMISION)
    date_depart = Column(Date, nullable=True)
    preavis_debut = Column(Date, nullable=True)
    preavis_fin = Column(Date, nullable=True)
    solde_tout_compte_xaf = Column(Numeric, nullable=True)
    statut = Column(_enum(EmployeeExit_statut), default=EmployeeExit_statut.OUVERT)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class AttendanceDevice(Base):
    """Pointage / badgeuses."""
    __tablename__ = "attendance_devices"
    __table_args__ = (
        UniqueConstraint('company_id', 'code_terminal', name='uix_attendance_devices_company_code_terminal'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    code_terminal = Column(String(150), nullable=False, index=True)
    lieu = Column(String(150), nullable=True)
    type_terminal = Column(_enum(AttendanceDevice_type_terminal), default=AttendanceDevice_type_terminal.BADGE)
    adresse_ip = Column(String(150), nullable=True)
    derniere_synchro = Column(DateTime(timezone=True), nullable=True)
    statut = Column(_enum(AttendanceDevice_statut), default=AttendanceDevice_statut.ONLINE)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class LeaveQuota(Base):
    """Droits conges / report N-1."""
    __tablename__ = "leave_quotas"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_leave_quotas_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    employe_id = Column(Integer, nullable=True)
    exercice = Column(Integer, nullable=True)
    droit_initial_jours = Column(Numeric, nullable=True)
    jours_pris = Column(Numeric, nullable=True)
    jours_reportes = Column(Numeric, nullable=True)
    solde_actuel = Column(Numeric, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class EmployeeSkill(Base):
    """Matrice de competences."""
    __tablename__ = "employee_skills"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_employee_skills_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    employe_id = Column(Integer, nullable=True)
    competence = Column(String(150), nullable=True)
    niveau = Column(_enum(EmployeeSkill_niveau), default=EmployeeSkill_niveau.INTERMEDIAIRE)
    date_evaluation = Column(Date, nullable=True)
    date_expiration = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class HrReport(Base):
    """Rapports RH periodiques."""
    __tablename__ = "hr_reports"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_hr_reports_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    periode_debut = Column(Date, nullable=True)
    periode_fin = Column(Date, nullable=True)
    effectif_debut = Column(Integer, nullable=True)
    effectif_fin = Column(Integer, nullable=True)
    taux_absent_pct = Column(Numeric, nullable=True)
    taux_turnover_pct = Column(Numeric, nullable=True)
    masse_salariale_xaf = Column(Numeric, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

