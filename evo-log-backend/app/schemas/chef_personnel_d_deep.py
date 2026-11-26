"""Schemas Pydantic pour chef-personnel (genere)."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date


class ChpRecruitmentCampaignCreate(BaseModel):
    reference: str
    poste: Optional[str] = None
    volume: Optional[int] = None
    ouverture: Optional[date] = None
    statut: Optional[str] = None


class ChpRecruitmentCampaignUpdate(BaseModel):
    reference: Optional[str] = None
    poste: Optional[str] = None
    volume: Optional[int] = None
    ouverture: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class ChpRecruitmentCampaignOut(BaseModel):
    id: int
    company_id: int
    reference: str
    poste: Optional[str] = None
    volume: Optional[int] = None
    ouverture: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class ChpJobPostingCreate(BaseModel):
    reference: str
    intitule: Optional[str] = None
    canal: Optional[str] = None
    parution: Optional[date] = None
    candidats: Optional[int] = None
    statut: Optional[str] = None


class ChpJobPostingUpdate(BaseModel):
    reference: Optional[str] = None
    intitule: Optional[str] = None
    canal: Optional[str] = None
    parution: Optional[date] = None
    candidats: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class ChpJobPostingOut(BaseModel):
    id: int
    company_id: int
    reference: str
    intitule: Optional[str] = None
    canal: Optional[str] = None
    parution: Optional[date] = None
    candidats: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class ChpCandidateSelectionCreate(BaseModel):
    reference: str
    candidat: Optional[str] = None
    poste: Optional[str] = None
    phase: Optional[str] = None
    evaluateur: Optional[str] = None
    statut: Optional[str] = None


class ChpCandidateSelectionUpdate(BaseModel):
    reference: Optional[str] = None
    candidat: Optional[str] = None
    poste: Optional[str] = None
    phase: Optional[str] = None
    evaluateur: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class ChpCandidateSelectionOut(BaseModel):
    id: int
    company_id: int
    reference: str
    candidat: Optional[str] = None
    poste: Optional[str] = None
    phase: Optional[str] = None
    evaluateur: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class ChpInterviewScheduleCreate(BaseModel):
    reference: str
    candidat: Optional[str] = None
    date: Optional[datetime] = None
    format: Optional[str] = None
    evaluateur: Optional[str] = None
    statut: Optional[str] = None


class ChpInterviewScheduleUpdate(BaseModel):
    reference: Optional[str] = None
    candidat: Optional[str] = None
    date: Optional[datetime] = None
    format: Optional[str] = None
    evaluateur: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class ChpInterviewScheduleOut(BaseModel):
    id: int
    company_id: int
    reference: str
    candidat: Optional[str] = None
    date: Optional[datetime] = None
    format: Optional[str] = None
    evaluateur: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class ChpOfferApprovalCreate(BaseModel):
    reference: str
    candidat: Optional[str] = None
    poste: Optional[str] = None
    remuneration: Optional[float] = None
    validateur: Optional[str] = None
    statut: Optional[str] = None


class ChpOfferApprovalUpdate(BaseModel):
    reference: Optional[str] = None
    candidat: Optional[str] = None
    poste: Optional[str] = None
    remuneration: Optional[float] = None
    validateur: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class ChpOfferApprovalOut(BaseModel):
    id: int
    company_id: int
    reference: str
    candidat: Optional[str] = None
    poste: Optional[str] = None
    remuneration: Optional[float] = None
    validateur: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class ChpOnboardingChecklistCreate(BaseModel):
    reference: str
    collaborateur: Optional[str] = None
    etapes_total: Optional[int] = None
    etapes_faites: Optional[int] = None
    date_debut: Optional[date] = None
    statut: Optional[str] = None


class ChpOnboardingChecklistUpdate(BaseModel):
    reference: Optional[str] = None
    collaborateur: Optional[str] = None
    etapes_total: Optional[int] = None
    etapes_faites: Optional[int] = None
    date_debut: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class ChpOnboardingChecklistOut(BaseModel):
    id: int
    company_id: int
    reference: str
    collaborateur: Optional[str] = None
    etapes_total: Optional[int] = None
    etapes_faites: Optional[int] = None
    date_debut: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class ChpProbationReviewCreate(BaseModel):
    reference: str
    collaborateur: Optional[str] = None
    date_echeance: Optional[date] = None
    avis: Optional[str] = None
    statut: Optional[str] = None


class ChpProbationReviewUpdate(BaseModel):
    reference: Optional[str] = None
    collaborateur: Optional[str] = None
    date_echeance: Optional[date] = None
    avis: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class ChpProbationReviewOut(BaseModel):
    id: int
    company_id: int
    reference: str
    collaborateur: Optional[str] = None
    date_echeance: Optional[date] = None
    avis: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class ChpExitInterviewCreate(BaseModel):
    reference: str
    collaborateur: Optional[str] = None
    motif: Optional[str] = None
    date: Optional[date] = None
    statut: Optional[str] = None


class ChpExitInterviewUpdate(BaseModel):
    reference: Optional[str] = None
    collaborateur: Optional[str] = None
    motif: Optional[str] = None
    date: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class ChpExitInterviewOut(BaseModel):
    id: int
    company_id: int
    reference: str
    collaborateur: Optional[str] = None
    motif: Optional[str] = None
    date: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class ChpHeadcountRequestCreate(BaseModel):
    reference: str
    departement: Optional[str] = None
    poste: Optional[str] = None
    masse_salariale: Optional[float] = None
    statut: Optional[str] = None


class ChpHeadcountRequestUpdate(BaseModel):
    reference: Optional[str] = None
    departement: Optional[str] = None
    poste: Optional[str] = None
    masse_salariale: Optional[float] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class ChpHeadcountRequestOut(BaseModel):
    id: int
    company_id: int
    reference: str
    departement: Optional[str] = None
    poste: Optional[str] = None
    masse_salariale: Optional[float] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class ChpOrgMovementCreate(BaseModel):
    reference: str
    collaborateur: Optional[str] = None
    type_mouvement: Optional[str] = None
    date_effet: Optional[date] = None
    statut: Optional[str] = None


class ChpOrgMovementUpdate(BaseModel):
    reference: Optional[str] = None
    collaborateur: Optional[str] = None
    type_mouvement: Optional[str] = None
    date_effet: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class ChpOrgMovementOut(BaseModel):
    id: int
    company_id: int
    reference: str
    collaborateur: Optional[str] = None
    type_mouvement: Optional[str] = None
    date_effet: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class ChpDisciplinaryActionCreate(BaseModel):
    reference: str
    collaborateur: Optional[str] = None
    motif: Optional[str] = None
    type_mesure: Optional[str] = None
    date: Optional[date] = None
    statut: Optional[str] = None


class ChpDisciplinaryActionUpdate(BaseModel):
    reference: Optional[str] = None
    collaborateur: Optional[str] = None
    motif: Optional[str] = None
    type_mesure: Optional[str] = None
    date: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class ChpDisciplinaryActionOut(BaseModel):
    id: int
    company_id: int
    reference: str
    collaborateur: Optional[str] = None
    motif: Optional[str] = None
    type_mesure: Optional[str] = None
    date: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class ChpTrainingPlanCreate(BaseModel):
    reference: str
    departement: Optional[str] = None
    exercice: Optional[str] = None
    budget: Optional[float] = None
    actions: Optional[int] = None
    statut: Optional[str] = None


class ChpTrainingPlanUpdate(BaseModel):
    reference: Optional[str] = None
    departement: Optional[str] = None
    exercice: Optional[str] = None
    budget: Optional[float] = None
    actions: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class ChpTrainingPlanOut(BaseModel):
    id: int
    company_id: int
    reference: str
    departement: Optional[str] = None
    exercice: Optional[str] = None
    budget: Optional[float] = None
    actions: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class ChpAbsenceApprovalCreate(BaseModel):
    reference: str
    collaborateur: Optional[str] = None
    manager: Optional[str] = None
    debut: Optional[date] = None
    fin: Optional[date] = None
    statut: Optional[str] = None


class ChpAbsenceApprovalUpdate(BaseModel):
    reference: Optional[str] = None
    collaborateur: Optional[str] = None
    manager: Optional[str] = None
    debut: Optional[date] = None
    fin: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class ChpAbsenceApprovalOut(BaseModel):
    id: int
    company_id: int
    reference: str
    collaborateur: Optional[str] = None
    manager: Optional[str] = None
    debut: Optional[date] = None
    fin: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class ChpPayrollAdjustmentRequestCreate(BaseModel):
    reference: str
    collaborateur: Optional[str] = None
    motif: Optional[str] = None
    montant: Optional[float] = None
    periode: Optional[str] = None
    statut: Optional[str] = None


class ChpPayrollAdjustmentRequestUpdate(BaseModel):
    reference: Optional[str] = None
    collaborateur: Optional[str] = None
    motif: Optional[str] = None
    montant: Optional[float] = None
    periode: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class ChpPayrollAdjustmentRequestOut(BaseModel):
    id: int
    company_id: int
    reference: str
    collaborateur: Optional[str] = None
    motif: Optional[str] = None
    montant: Optional[float] = None
    periode: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class ChpPolicyAckCreate(BaseModel):
    reference: str
    collaborateur: Optional[str] = None
    politique: Optional[str] = None
    version: Optional[str] = None
    date: Optional[date] = None
    statut: Optional[str] = None


class ChpPolicyAckUpdate(BaseModel):
    reference: Optional[str] = None
    collaborateur: Optional[str] = None
    politique: Optional[str] = None
    version: Optional[str] = None
    date: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class ChpPolicyAckOut(BaseModel):
    id: int
    company_id: int
    reference: str
    collaborateur: Optional[str] = None
    politique: Optional[str] = None
    version: Optional[str] = None
    date: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}

