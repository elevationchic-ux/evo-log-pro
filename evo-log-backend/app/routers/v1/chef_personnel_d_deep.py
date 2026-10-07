"""Routeur CRUD genere pour chef-personnel (expansion)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List

from app.core.database import get_db
from app.core.permissions import require_perm
from app.models.user import User
from app.models.chef_personnel_d_deep import (
    ChpRecruitmentCampaign,
    ChpJobPosting,
    ChpCandidateSelection,
    ChpInterviewSchedule,
    ChpOfferApproval,
    ChpOnboardingChecklist,
    ChpProbationReview,
    ChpExitInterview,
    ChpHeadcountRequest,
    ChpOrgMovement,
    ChpDisciplinaryAction,
    ChpTrainingPlan,
    ChpAbsenceApproval,
    ChpPayrollAdjustmentRequest,
    ChpPolicyAck,
)
from app.schemas.chef_personnel_d_deep import (
    ChpRecruitmentCampaignCreate, ChpRecruitmentCampaignUpdate, ChpRecruitmentCampaignOut,
    ChpJobPostingCreate, ChpJobPostingUpdate, ChpJobPostingOut,
    ChpCandidateSelectionCreate, ChpCandidateSelectionUpdate, ChpCandidateSelectionOut,
    ChpInterviewScheduleCreate, ChpInterviewScheduleUpdate, ChpInterviewScheduleOut,
    ChpOfferApprovalCreate, ChpOfferApprovalUpdate, ChpOfferApprovalOut,
    ChpOnboardingChecklistCreate, ChpOnboardingChecklistUpdate, ChpOnboardingChecklistOut,
    ChpProbationReviewCreate, ChpProbationReviewUpdate, ChpProbationReviewOut,
    ChpExitInterviewCreate, ChpExitInterviewUpdate, ChpExitInterviewOut,
    ChpHeadcountRequestCreate, ChpHeadcountRequestUpdate, ChpHeadcountRequestOut,
    ChpOrgMovementCreate, ChpOrgMovementUpdate, ChpOrgMovementOut,
    ChpDisciplinaryActionCreate, ChpDisciplinaryActionUpdate, ChpDisciplinaryActionOut,
    ChpTrainingPlanCreate, ChpTrainingPlanUpdate, ChpTrainingPlanOut,
    ChpAbsenceApprovalCreate, ChpAbsenceApprovalUpdate, ChpAbsenceApprovalOut,
    ChpPayrollAdjustmentRequestCreate, ChpPayrollAdjustmentRequestUpdate, ChpPayrollAdjustmentRequestOut,
    ChpPolicyAckCreate, ChpPolicyAckUpdate, ChpPolicyAckOut,
)

router = APIRouter(tags=["chef-personnel (expansion)"])


# ─── Helpers generiques ──────────────────────────────────────────────────────

def _get_or_404(db: Session, model, ident: int, label: str):
    row = db.query(model).filter(model.id == ident).first()
    if not row:
        raise HTTPException(status_code=404, detail=f"{label} introuvable (id={ident})")
    return row


def _check_unique(db: Session, model, field: str, value, label: str, company_id: int, exclude_id=None):
    if value is None:
        return
    q = db.query(model).filter(getattr(model, field) == value, model.company_id == company_id)
    if exclude_id is not None:
        q = q.filter(model.id != exclude_id)
    if q.first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"{label} « {value} » existe deja dans votre organisation.",
        )


def _scoped_list(db, model, company_id, filters=None):
    q = db.query(model).filter(model.company_id == company_id)
    if hasattr(model, 'is_active'):
        q = q.filter(model.is_active.is_(True))
    if filters:
        for key, val in filters.items():
            if val is not None and hasattr(model, key):
                q = q.filter(getattr(model, key) == val)
    return q.order_by(model.id.desc()).all()


def _apply(payload: dict, obj):
    for key, value in payload.items():
        setattr(obj, key, value)


def _company_id(user: User) -> int:
    if not user.company_id:
        raise HTTPException(status_code=400, detail="Votre compte n'est rattache a aucune organisation.")
    return user.company_id


# ─── Nomenclatures ───────────────────────────────────────────────────────────

@router.get("/nomenclatures", summary="Vocabulaire metier chef-personnel")
def nomenclatures(user: User = Depends(require_perm("rh.nomenclature.read"))):
    from app.models import chef_personnel_d_deep as _md
    import enum as _pyenum
    out = {}
    for name in dir(_md):
        obj = getattr(_md, name)
        if isinstance(obj, type) and issubclass(obj, _pyenum.Enum) and obj is not _pyenum.Enum:
            out[name.lower()] = [{"code": m.name, "valeur": m.value} for m in obj]
    return out


# ─── Campagnes de recrutement ─────────────────────────────────────────────────

@router.get("/chp-recruitment-campaigns", response_model=List[ChpRecruitmentCampaignOut])
def list_recruitment_campaign(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.recruitment_campaign.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, ChpRecruitmentCampaign, cid, {"statut": statut})


@router.post("/chp-recruitment-campaigns", response_model=ChpRecruitmentCampaignOut, status_code=201)
def create_recruitment_campaign(
    payload: ChpRecruitmentCampaignCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.recruitment_campaign.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, ChpRecruitmentCampaign, "reference", data.get("reference"), "reference", cid)
    obj = ChpRecruitmentCampaign(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/chp-recruitment-campaigns/{ident}", response_model=ChpRecruitmentCampaignOut)
def update_recruitment_campaign(
    ident: int,
    payload: ChpRecruitmentCampaignUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.recruitment_campaign.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ChpRecruitmentCampaign, ident, "Campagnes de recrutement")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/chp-recruitment-campaigns/{ident}", response_model=ChpRecruitmentCampaignOut)
def delete_recruitment_campaign(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.recruitment_campaign.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ChpRecruitmentCampaign, ident, "Campagnes de recrutement")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Offres d' emploi ─────────────────────────────────────────────────

@router.get("/chp-job-postings", response_model=List[ChpJobPostingOut])
def list_job_posting(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.job_posting.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, ChpJobPosting, cid, {"statut": statut})


@router.post("/chp-job-postings", response_model=ChpJobPostingOut, status_code=201)
def create_job_posting(
    payload: ChpJobPostingCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.job_posting.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, ChpJobPosting, "reference", data.get("reference"), "reference", cid)
    obj = ChpJobPosting(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/chp-job-postings/{ident}", response_model=ChpJobPostingOut)
def update_job_posting(
    ident: int,
    payload: ChpJobPostingUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.job_posting.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ChpJobPosting, ident, "Offres d' emploi")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/chp-job-postings/{ident}", response_model=ChpJobPostingOut)
def delete_job_posting(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.job_posting.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ChpJobPosting, ident, "Offres d' emploi")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Selection de candidats ─────────────────────────────────────────────────

@router.get("/chp-candidate-selections", response_model=List[ChpCandidateSelectionOut])
def list_candidate_selection(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.candidate_selection.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, ChpCandidateSelection, cid, {"statut": statut})


@router.post("/chp-candidate-selections", response_model=ChpCandidateSelectionOut, status_code=201)
def create_candidate_selection(
    payload: ChpCandidateSelectionCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.candidate_selection.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, ChpCandidateSelection, "reference", data.get("reference"), "reference", cid)
    obj = ChpCandidateSelection(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/chp-candidate-selections/{ident}", response_model=ChpCandidateSelectionOut)
def update_candidate_selection(
    ident: int,
    payload: ChpCandidateSelectionUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.candidate_selection.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ChpCandidateSelection, ident, "Selection de candidats")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/chp-candidate-selections/{ident}", response_model=ChpCandidateSelectionOut)
def delete_candidate_selection(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.candidate_selection.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ChpCandidateSelection, ident, "Selection de candidats")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Planifications d' entretiens ─────────────────────────────────────────────────

@router.get("/chp-interview-schedules", response_model=List[ChpInterviewScheduleOut])
def list_interview_schedule(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.interview_schedule.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, ChpInterviewSchedule, cid, {"statut": statut})


@router.post("/chp-interview-schedules", response_model=ChpInterviewScheduleOut, status_code=201)
def create_interview_schedule(
    payload: ChpInterviewScheduleCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.interview_schedule.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, ChpInterviewSchedule, "reference", data.get("reference"), "reference", cid)
    obj = ChpInterviewSchedule(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/chp-interview-schedules/{ident}", response_model=ChpInterviewScheduleOut)
def update_interview_schedule(
    ident: int,
    payload: ChpInterviewScheduleUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.interview_schedule.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ChpInterviewSchedule, ident, "Planifications d' entretiens")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/chp-interview-schedules/{ident}", response_model=ChpInterviewScheduleOut)
def delete_interview_schedule(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.interview_schedule.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ChpInterviewSchedule, ident, "Planifications d' entretiens")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Validations d' offres ─────────────────────────────────────────────────

@router.get("/chp-offer-approvals", response_model=List[ChpOfferApprovalOut])
def list_offer_approval(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.offer_approval.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, ChpOfferApproval, cid, {"statut": statut})


@router.post("/chp-offer-approvals", response_model=ChpOfferApprovalOut, status_code=201)
def create_offer_approval(
    payload: ChpOfferApprovalCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.offer_approval.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, ChpOfferApproval, "reference", data.get("reference"), "reference", cid)
    obj = ChpOfferApproval(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/chp-offer-approvals/{ident}", response_model=ChpOfferApprovalOut)
def update_offer_approval(
    ident: int,
    payload: ChpOfferApprovalUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.offer_approval.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ChpOfferApproval, ident, "Validations d' offres")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/chp-offer-approvals/{ident}", response_model=ChpOfferApprovalOut)
def delete_offer_approval(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.offer_approval.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ChpOfferApproval, ident, "Validations d' offres")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Checklists d' integration ─────────────────────────────────────────────────

@router.get("/chp-onboarding-checklists", response_model=List[ChpOnboardingChecklistOut])
def list_onboarding_checklist(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.onboarding_checklist.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, ChpOnboardingChecklist, cid, {"statut": statut})


@router.post("/chp-onboarding-checklists", response_model=ChpOnboardingChecklistOut, status_code=201)
def create_onboarding_checklist(
    payload: ChpOnboardingChecklistCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.onboarding_checklist.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, ChpOnboardingChecklist, "reference", data.get("reference"), "reference", cid)
    obj = ChpOnboardingChecklist(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/chp-onboarding-checklists/{ident}", response_model=ChpOnboardingChecklistOut)
def update_onboarding_checklist(
    ident: int,
    payload: ChpOnboardingChecklistUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.onboarding_checklist.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ChpOnboardingChecklist, ident, "Checklists d' integration")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/chp-onboarding-checklists/{ident}", response_model=ChpOnboardingChecklistOut)
def delete_onboarding_checklist(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.onboarding_checklist.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ChpOnboardingChecklist, ident, "Checklists d' integration")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Revues de periode d' essai ─────────────────────────────────────────────────

@router.get("/chp-probation-reviews", response_model=List[ChpProbationReviewOut])
def list_probation_review(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.probation_review.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, ChpProbationReview, cid, {"statut": statut})


@router.post("/chp-probation-reviews", response_model=ChpProbationReviewOut, status_code=201)
def create_probation_review(
    payload: ChpProbationReviewCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.probation_review.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, ChpProbationReview, "reference", data.get("reference"), "reference", cid)
    obj = ChpProbationReview(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/chp-probation-reviews/{ident}", response_model=ChpProbationReviewOut)
def update_probation_review(
    ident: int,
    payload: ChpProbationReviewUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.probation_review.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ChpProbationReview, ident, "Revues de periode d' essai")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/chp-probation-reviews/{ident}", response_model=ChpProbationReviewOut)
def delete_probation_review(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.probation_review.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ChpProbationReview, ident, "Revues de periode d' essai")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Entretiens de depart ─────────────────────────────────────────────────

@router.get("/chp-exit-interviews", response_model=List[ChpExitInterviewOut])
def list_exit_interview(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.exit_interview.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, ChpExitInterview, cid, {"statut": statut})


@router.post("/chp-exit-interviews", response_model=ChpExitInterviewOut, status_code=201)
def create_exit_interview(
    payload: ChpExitInterviewCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.exit_interview.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, ChpExitInterview, "reference", data.get("reference"), "reference", cid)
    obj = ChpExitInterview(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/chp-exit-interviews/{ident}", response_model=ChpExitInterviewOut)
def update_exit_interview(
    ident: int,
    payload: ChpExitInterviewUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.exit_interview.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ChpExitInterview, ident, "Entretiens de depart")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/chp-exit-interviews/{ident}", response_model=ChpExitInterviewOut)
def delete_exit_interview(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.exit_interview.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ChpExitInterview, ident, "Entretiens de depart")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Demandes de creation de poste ─────────────────────────────────────────────────

@router.get("/chp-headcount-requests", response_model=List[ChpHeadcountRequestOut])
def list_headcount_request(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.headcount_request.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, ChpHeadcountRequest, cid, {"statut": statut})


@router.post("/chp-headcount-requests", response_model=ChpHeadcountRequestOut, status_code=201)
def create_headcount_request(
    payload: ChpHeadcountRequestCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.headcount_request.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, ChpHeadcountRequest, "reference", data.get("reference"), "reference", cid)
    obj = ChpHeadcountRequest(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/chp-headcount-requests/{ident}", response_model=ChpHeadcountRequestOut)
def update_headcount_request(
    ident: int,
    payload: ChpHeadcountRequestUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.headcount_request.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ChpHeadcountRequest, ident, "Demandes de creation de poste")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/chp-headcount-requests/{ident}", response_model=ChpHeadcountRequestOut)
def delete_headcount_request(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.headcount_request.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ChpHeadcountRequest, ident, "Demandes de creation de poste")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Mouvements organisationnels ─────────────────────────────────────────────────

@router.get("/chp-org-movements", response_model=List[ChpOrgMovementOut])
def list_org_movement(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.org_movement.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, ChpOrgMovement, cid, {"statut": statut})


@router.post("/chp-org-movements", response_model=ChpOrgMovementOut, status_code=201)
def create_org_movement(
    payload: ChpOrgMovementCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.org_movement.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, ChpOrgMovement, "reference", data.get("reference"), "reference", cid)
    obj = ChpOrgMovement(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/chp-org-movements/{ident}", response_model=ChpOrgMovementOut)
def update_org_movement(
    ident: int,
    payload: ChpOrgMovementUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.org_movement.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ChpOrgMovement, ident, "Mouvements organisationnels")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/chp-org-movements/{ident}", response_model=ChpOrgMovementOut)
def delete_org_movement(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.org_movement.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ChpOrgMovement, ident, "Mouvements organisationnels")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Mesures disciplinaires ─────────────────────────────────────────────────

@router.get("/chp-disciplinary-actions", response_model=List[ChpDisciplinaryActionOut])
def list_disciplinary_action(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.disciplinary_action.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, ChpDisciplinaryAction, cid, {"statut": statut})


@router.post("/chp-disciplinary-actions", response_model=ChpDisciplinaryActionOut, status_code=201)
def create_disciplinary_action(
    payload: ChpDisciplinaryActionCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.disciplinary_action.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, ChpDisciplinaryAction, "reference", data.get("reference"), "reference", cid)
    obj = ChpDisciplinaryAction(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/chp-disciplinary-actions/{ident}", response_model=ChpDisciplinaryActionOut)
def update_disciplinary_action(
    ident: int,
    payload: ChpDisciplinaryActionUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.disciplinary_action.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ChpDisciplinaryAction, ident, "Mesures disciplinaires")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/chp-disciplinary-actions/{ident}", response_model=ChpDisciplinaryActionOut)
def delete_disciplinary_action(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.disciplinary_action.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ChpDisciplinaryAction, ident, "Mesures disciplinaires")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Plans de formation ─────────────────────────────────────────────────

@router.get("/chp-training-plans", response_model=List[ChpTrainingPlanOut])
def list_training_plan(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.training_plan.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, ChpTrainingPlan, cid, {"statut": statut})


@router.post("/chp-training-plans", response_model=ChpTrainingPlanOut, status_code=201)
def create_training_plan(
    payload: ChpTrainingPlanCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.training_plan.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, ChpTrainingPlan, "reference", data.get("reference"), "reference", cid)
    obj = ChpTrainingPlan(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/chp-training-plans/{ident}", response_model=ChpTrainingPlanOut)
def update_training_plan(
    ident: int,
    payload: ChpTrainingPlanUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.training_plan.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ChpTrainingPlan, ident, "Plans de formation")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/chp-training-plans/{ident}", response_model=ChpTrainingPlanOut)
def delete_training_plan(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.training_plan.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ChpTrainingPlan, ident, "Plans de formation")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Validations d' absences ─────────────────────────────────────────────────

@router.get("/chp-absence-approvals", response_model=List[ChpAbsenceApprovalOut])
def list_absence_approval(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.absence_approval.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, ChpAbsenceApproval, cid, {"statut": statut})


@router.post("/chp-absence-approvals", response_model=ChpAbsenceApprovalOut, status_code=201)
def create_absence_approval(
    payload: ChpAbsenceApprovalCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.absence_approval.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, ChpAbsenceApproval, "reference", data.get("reference"), "reference", cid)
    obj = ChpAbsenceApproval(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/chp-absence-approvals/{ident}", response_model=ChpAbsenceApprovalOut)
def update_absence_approval(
    ident: int,
    payload: ChpAbsenceApprovalUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.absence_approval.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ChpAbsenceApproval, ident, "Validations d' absences")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/chp-absence-approvals/{ident}", response_model=ChpAbsenceApprovalOut)
def delete_absence_approval(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.absence_approval.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ChpAbsenceApproval, ident, "Validations d' absences")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Demandes d' ajustement de paie ─────────────────────────────────────────────────

@router.get("/chp-payroll-adjustment-requests", response_model=List[ChpPayrollAdjustmentRequestOut])
def list_payroll_adjustment_request(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.payroll_adjustment_request.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, ChpPayrollAdjustmentRequest, cid, {"statut": statut})


@router.post("/chp-payroll-adjustment-requests", response_model=ChpPayrollAdjustmentRequestOut, status_code=201)
def create_payroll_adjustment_request(
    payload: ChpPayrollAdjustmentRequestCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.payroll_adjustment_request.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, ChpPayrollAdjustmentRequest, "reference", data.get("reference"), "reference", cid)
    obj = ChpPayrollAdjustmentRequest(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/chp-payroll-adjustment-requests/{ident}", response_model=ChpPayrollAdjustmentRequestOut)
def update_payroll_adjustment_request(
    ident: int,
    payload: ChpPayrollAdjustmentRequestUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.payroll_adjustment_request.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ChpPayrollAdjustmentRequest, ident, "Demandes d' ajustement de paie")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/chp-payroll-adjustment-requests/{ident}", response_model=ChpPayrollAdjustmentRequestOut)
def delete_payroll_adjustment_request(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.payroll_adjustment_request.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ChpPayrollAdjustmentRequest, ident, "Demandes d' ajustement de paie")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Accuses de politique RH ─────────────────────────────────────────────────

@router.get("/chp-policy-acknowledgements", response_model=List[ChpPolicyAckOut])
def list_policy_ack(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.policy_ack.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, ChpPolicyAck, cid, {"statut": statut})


@router.post("/chp-policy-acknowledgements", response_model=ChpPolicyAckOut, status_code=201)
def create_policy_ack(
    payload: ChpPolicyAckCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.policy_ack.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, ChpPolicyAck, "reference", data.get("reference"), "reference", cid)
    obj = ChpPolicyAck(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/chp-policy-acknowledgements/{ident}", response_model=ChpPolicyAckOut)
def update_policy_ack(
    ident: int,
    payload: ChpPolicyAckUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.policy_ack.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ChpPolicyAck, ident, "Accuses de politique RH")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/chp-policy-acknowledgements/{ident}", response_model=ChpPolicyAckOut)
def delete_policy_ack(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.policy_ack.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ChpPolicyAck, ident, "Accuses de politique RH")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj

