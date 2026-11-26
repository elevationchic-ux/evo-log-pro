"""Schemas Pydantic pour rh-personnel (genere)."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date


class RecruitmentCreate(BaseModel):
    reference: str
    poste: Optional[str] = None
    departement: Optional[str] = None
    type_contrat: Optional[str] = None
    date_ouverture: Optional[date] = None
    date_cloture: Optional[date] = None
    candidats_recus: Optional[int] = None
    statut: Optional[str] = None


class RecruitmentUpdate(BaseModel):
    reference: Optional[str] = None
    poste: Optional[str] = None
    departement: Optional[str] = None
    type_contrat: Optional[str] = None
    date_ouverture: Optional[date] = None
    date_cloture: Optional[date] = None
    candidats_recus: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class RecruitmentOut(BaseModel):
    id: int
    company_id: int
    reference: str
    poste: Optional[str] = None
    departement: Optional[str] = None
    type_contrat: Optional[str] = None
    date_ouverture: Optional[date] = None
    date_cloture: Optional[date] = None
    candidats_recus: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class TrainingPlanCreate(BaseModel):
    reference: str
    intitule: Optional[str] = None
    type_action: Optional[str] = None
    organisme: Optional[str] = None
    date_debut: Optional[date] = None
    date_fin: Optional[date] = None
    duree_heures: Optional[int] = None
    cout_xaf: Optional[float] = None
    statut: Optional[str] = None


class TrainingPlanUpdate(BaseModel):
    reference: Optional[str] = None
    intitule: Optional[str] = None
    type_action: Optional[str] = None
    organisme: Optional[str] = None
    date_debut: Optional[date] = None
    date_fin: Optional[date] = None
    duree_heures: Optional[int] = None
    cout_xaf: Optional[float] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class TrainingPlanOut(BaseModel):
    id: int
    company_id: int
    reference: str
    intitule: Optional[str] = None
    type_action: Optional[str] = None
    organisme: Optional[str] = None
    date_debut: Optional[date] = None
    date_fin: Optional[date] = None
    duree_heures: Optional[int] = None
    cout_xaf: Optional[float] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class PerformanceReviewCreate(BaseModel):
    reference: str
    employe_id: Optional[int] = None
    periode: Optional[str] = None
    date_entretien: Optional[date] = None
    evaluateur: Optional[str] = None
    note_global: Optional[float] = None
    objectifs_atteints_pct: Optional[float] = None
    statut: Optional[str] = None


class PerformanceReviewUpdate(BaseModel):
    reference: Optional[str] = None
    employe_id: Optional[int] = None
    periode: Optional[str] = None
    date_entretien: Optional[date] = None
    evaluateur: Optional[str] = None
    note_global: Optional[float] = None
    objectifs_atteints_pct: Optional[float] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class PerformanceReviewOut(BaseModel):
    id: int
    company_id: int
    reference: str
    employe_id: Optional[int] = None
    periode: Optional[str] = None
    date_entretien: Optional[date] = None
    evaluateur: Optional[str] = None
    note_global: Optional[float] = None
    objectifs_atteints_pct: Optional[float] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class DisciplinaryCaseCreate(BaseModel):
    reference: str
    employe_id: Optional[int] = None
    date_fait: Optional[date] = None
    type_sanction: Optional[str] = None
    motif: Optional[str] = None
    date_convocation: Optional[date] = None
    date_decision: Optional[date] = None
    statut: Optional[str] = None


class DisciplinaryCaseUpdate(BaseModel):
    reference: Optional[str] = None
    employe_id: Optional[int] = None
    date_fait: Optional[date] = None
    type_sanction: Optional[str] = None
    motif: Optional[str] = None
    date_convocation: Optional[date] = None
    date_decision: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class DisciplinaryCaseOut(BaseModel):
    id: int
    company_id: int
    reference: str
    employe_id: Optional[int] = None
    date_fait: Optional[date] = None
    type_sanction: Optional[str] = None
    motif: Optional[str] = None
    date_convocation: Optional[date] = None
    date_decision: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class OrgUnitCreate(BaseModel):
    code_unite: str
    nom: Optional[str] = None
    parent_code: Optional[str] = None
    type_unite: Optional[str] = None
    responsable: Optional[str] = None
    effectif: Optional[int] = None


class OrgUnitUpdate(BaseModel):
    code_unite: Optional[str] = None
    nom: Optional[str] = None
    parent_code: Optional[str] = None
    type_unite: Optional[str] = None
    responsable: Optional[str] = None
    effectif: Optional[int] = None
    is_active: Optional[bool] = None


class OrgUnitOut(BaseModel):
    id: int
    company_id: int
    code_unite: str
    nom: Optional[str] = None
    parent_code: Optional[str] = None
    type_unite: Optional[str] = None
    responsable: Optional[str] = None
    effectif: Optional[int] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class WorkforcePlanCreate(BaseModel):
    reference: str
    exercice: Optional[int] = None
    mois: Optional[str] = None
    masse_salariale_prevue_xaf: Optional[float] = None
    effectif_cadre: Optional[int] = None
    effectif_non_cadre: Optional[int] = None
    hypothese_inflation_pct: Optional[float] = None


class WorkforcePlanUpdate(BaseModel):
    reference: Optional[str] = None
    exercice: Optional[int] = None
    mois: Optional[str] = None
    masse_salariale_prevue_xaf: Optional[float] = None
    effectif_cadre: Optional[int] = None
    effectif_non_cadre: Optional[int] = None
    hypothese_inflation_pct: Optional[float] = None
    is_active: Optional[bool] = None


class WorkforcePlanOut(BaseModel):
    id: int
    company_id: int
    reference: str
    exercice: Optional[int] = None
    mois: Optional[str] = None
    masse_salariale_prevue_xaf: Optional[float] = None
    effectif_cadre: Optional[int] = None
    effectif_non_cadre: Optional[int] = None
    hypothese_inflation_pct: Optional[float] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class EmploymentContractCreate(BaseModel):
    numero_contrat: str
    employe_id: Optional[int] = None
    type_contrat: Optional[str] = None
    date_debut: Optional[date] = None
    date_fin: Optional[date] = None
    avenants: Optional[str] = None
    statut: Optional[str] = None


class EmploymentContractUpdate(BaseModel):
    numero_contrat: Optional[str] = None
    employe_id: Optional[int] = None
    type_contrat: Optional[str] = None
    date_debut: Optional[date] = None
    date_fin: Optional[date] = None
    avenants: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class EmploymentContractOut(BaseModel):
    id: int
    company_id: int
    numero_contrat: str
    employe_id: Optional[int] = None
    type_contrat: Optional[str] = None
    date_debut: Optional[date] = None
    date_fin: Optional[date] = None
    avenants: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class EmployeeBenefitCreate(BaseModel):
    reference: str
    employe_id: Optional[int] = None
    type_avantage: Optional[str] = None
    montant_annuel_xaf: Optional[float] = None
    date_debut: Optional[date] = None
    date_fin: Optional[date] = None
    statut: Optional[str] = None


class EmployeeBenefitUpdate(BaseModel):
    reference: Optional[str] = None
    employe_id: Optional[int] = None
    type_avantage: Optional[str] = None
    montant_annuel_xaf: Optional[float] = None
    date_debut: Optional[date] = None
    date_fin: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class EmployeeBenefitOut(BaseModel):
    id: int
    company_id: int
    reference: str
    employe_id: Optional[int] = None
    type_avantage: Optional[str] = None
    montant_annuel_xaf: Optional[float] = None
    date_debut: Optional[date] = None
    date_fin: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class EmployeeExitCreate(BaseModel):
    reference: str
    employe_id: Optional[int] = None
    type_depart: Optional[str] = None
    date_depart: Optional[date] = None
    preavis_debut: Optional[date] = None
    preavis_fin: Optional[date] = None
    solde_tout_compte_xaf: Optional[float] = None
    statut: Optional[str] = None


class EmployeeExitUpdate(BaseModel):
    reference: Optional[str] = None
    employe_id: Optional[int] = None
    type_depart: Optional[str] = None
    date_depart: Optional[date] = None
    preavis_debut: Optional[date] = None
    preavis_fin: Optional[date] = None
    solde_tout_compte_xaf: Optional[float] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class EmployeeExitOut(BaseModel):
    id: int
    company_id: int
    reference: str
    employe_id: Optional[int] = None
    type_depart: Optional[str] = None
    date_depart: Optional[date] = None
    preavis_debut: Optional[date] = None
    preavis_fin: Optional[date] = None
    solde_tout_compte_xaf: Optional[float] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class AttendanceDeviceCreate(BaseModel):
    code_terminal: str
    lieu: Optional[str] = None
    type_terminal: Optional[str] = None
    adresse_ip: Optional[str] = None
    derniere_synchro: Optional[datetime] = None
    statut: Optional[str] = None


class AttendanceDeviceUpdate(BaseModel):
    code_terminal: Optional[str] = None
    lieu: Optional[str] = None
    type_terminal: Optional[str] = None
    adresse_ip: Optional[str] = None
    derniere_synchro: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class AttendanceDeviceOut(BaseModel):
    id: int
    company_id: int
    code_terminal: str
    lieu: Optional[str] = None
    type_terminal: Optional[str] = None
    adresse_ip: Optional[str] = None
    derniere_synchro: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class LeaveQuotaCreate(BaseModel):
    reference: str
    employe_id: Optional[int] = None
    exercice: Optional[int] = None
    droit_initial_jours: Optional[float] = None
    jours_pris: Optional[float] = None
    jours_reportes: Optional[float] = None
    solde_actuel: Optional[float] = None


class LeaveQuotaUpdate(BaseModel):
    reference: Optional[str] = None
    employe_id: Optional[int] = None
    exercice: Optional[int] = None
    droit_initial_jours: Optional[float] = None
    jours_pris: Optional[float] = None
    jours_reportes: Optional[float] = None
    solde_actuel: Optional[float] = None
    is_active: Optional[bool] = None


class LeaveQuotaOut(BaseModel):
    id: int
    company_id: int
    reference: str
    employe_id: Optional[int] = None
    exercice: Optional[int] = None
    droit_initial_jours: Optional[float] = None
    jours_pris: Optional[float] = None
    jours_reportes: Optional[float] = None
    solde_actuel: Optional[float] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class EmployeeSkillCreate(BaseModel):
    reference: str
    employe_id: Optional[int] = None
    competence: Optional[str] = None
    niveau: Optional[str] = None
    date_evaluation: Optional[date] = None
    date_expiration: Optional[date] = None


class EmployeeSkillUpdate(BaseModel):
    reference: Optional[str] = None
    employe_id: Optional[int] = None
    competence: Optional[str] = None
    niveau: Optional[str] = None
    date_evaluation: Optional[date] = None
    date_expiration: Optional[date] = None
    is_active: Optional[bool] = None


class EmployeeSkillOut(BaseModel):
    id: int
    company_id: int
    reference: str
    employe_id: Optional[int] = None
    competence: Optional[str] = None
    niveau: Optional[str] = None
    date_evaluation: Optional[date] = None
    date_expiration: Optional[date] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class HrReportCreate(BaseModel):
    reference: str
    periode_debut: Optional[date] = None
    periode_fin: Optional[date] = None
    effectif_debut: Optional[int] = None
    effectif_fin: Optional[int] = None
    taux_absent_pct: Optional[float] = None
    taux_turnover_pct: Optional[float] = None
    masse_salariale_xaf: Optional[float] = None


class HrReportUpdate(BaseModel):
    reference: Optional[str] = None
    periode_debut: Optional[date] = None
    periode_fin: Optional[date] = None
    effectif_debut: Optional[int] = None
    effectif_fin: Optional[int] = None
    taux_absent_pct: Optional[float] = None
    taux_turnover_pct: Optional[float] = None
    masse_salariale_xaf: Optional[float] = None
    is_active: Optional[bool] = None


class HrReportOut(BaseModel):
    id: int
    company_id: int
    reference: str
    periode_debut: Optional[date] = None
    periode_fin: Optional[date] = None
    effectif_debut: Optional[int] = None
    effectif_fin: Optional[int] = None
    taux_absent_pct: Optional[float] = None
    taux_turnover_pct: Optional[float] = None
    masse_salariale_xaf: Optional[float] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}

