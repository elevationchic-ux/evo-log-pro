"""Routeur CRUD genere pour rh-personnel (expansion)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List

from app.core.database import get_db
from app.core.permissions import require_perm
from app.models.user import User
from app.models.rh_deep import (
    Recruitment,
    TrainingPlan,
    PerformanceReview,
    DisciplinaryCase,
    OrgUnit,
    WorkforcePlan,
    EmploymentContract,
    EmployeeBenefit,
    EmployeeExit,
    AttendanceDevice,
    LeaveQuota,
    EmployeeSkill,
    HrReport,
)
from app.schemas.rh_deep import (
    RecruitmentCreate, RecruitmentUpdate, RecruitmentOut,
    TrainingPlanCreate, TrainingPlanUpdate, TrainingPlanOut,
    PerformanceReviewCreate, PerformanceReviewUpdate, PerformanceReviewOut,
    DisciplinaryCaseCreate, DisciplinaryCaseUpdate, DisciplinaryCaseOut,
    OrgUnitCreate, OrgUnitUpdate, OrgUnitOut,
    WorkforcePlanCreate, WorkforcePlanUpdate, WorkforcePlanOut,
    EmploymentContractCreate, EmploymentContractUpdate, EmploymentContractOut,
    EmployeeBenefitCreate, EmployeeBenefitUpdate, EmployeeBenefitOut,
    EmployeeExitCreate, EmployeeExitUpdate, EmployeeExitOut,
    AttendanceDeviceCreate, AttendanceDeviceUpdate, AttendanceDeviceOut,
    LeaveQuotaCreate, LeaveQuotaUpdate, LeaveQuotaOut,
    EmployeeSkillCreate, EmployeeSkillUpdate, EmployeeSkillOut,
    HrReportCreate, HrReportUpdate, HrReportOut,
)

router = APIRouter(tags=["rh-personnel (expansion)"])


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

@router.get("/nomenclatures", summary="Vocabulaire metier rh-personnel")
def nomenclatures(user: User = Depends(require_perm("rh.nomenclature.read"))):
    from app.models import rh_deep as _md
    import enum as _pyenum
    out = {}
    for name in dir(_md):
        obj = getattr(_md, name)
        if isinstance(obj, type) and issubclass(obj, _pyenum.Enum) and obj is not _pyenum.Enum:
            out[name.lower()] = [{"code": m.name, "valeur": m.value} for m in obj]
    return out


# ─── Offres et candidatures ─────────────────────────────────────────────────

@router.get("/recruitments", response_model=List[RecruitmentOut])
def list_recruitment(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.recruitment.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, Recruitment, cid, {"statut": statut})


@router.post("/recruitments", response_model=RecruitmentOut, status_code=201)
def create_recruitment(
    payload: RecruitmentCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.recruitment.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, Recruitment, "reference", data.get("reference"), "reference", cid)
    obj = Recruitment(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/recruitments/{ident}", response_model=RecruitmentOut)
def update_recruitment(
    ident: int,
    payload: RecruitmentUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.recruitment.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, Recruitment, ident, "Offres et candidatures")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/recruitments/{ident}", response_model=RecruitmentOut)
def delete_recruitment(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.recruitment.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, Recruitment, ident, "Offres et candidatures")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Plan de formation ─────────────────────────────────────────────────

@router.get("/training-plans", response_model=List[TrainingPlanOut])
def list_training(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.training.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, TrainingPlan, cid, {"statut": statut})


@router.post("/training-plans", response_model=TrainingPlanOut, status_code=201)
def create_training(
    payload: TrainingPlanCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.training.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, TrainingPlan, "reference", data.get("reference"), "reference", cid)
    obj = TrainingPlan(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/training-plans/{ident}", response_model=TrainingPlanOut)
def update_training(
    ident: int,
    payload: TrainingPlanUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.training.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TrainingPlan, ident, "Plan de formation")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/training-plans/{ident}", response_model=TrainingPlanOut)
def delete_training(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.training.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TrainingPlan, ident, "Plan de formation")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Entretiens d'evaluation ─────────────────────────────────────────────────

@router.get("/performance-reviews", response_model=List[PerformanceReviewOut])
def list_performance_review(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.performance_review.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, PerformanceReview, cid, {"statut": statut})


@router.post("/performance-reviews", response_model=PerformanceReviewOut, status_code=201)
def create_performance_review(
    payload: PerformanceReviewCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.performance_review.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, PerformanceReview, "reference", data.get("reference"), "reference", cid)
    obj = PerformanceReview(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/performance-reviews/{ident}", response_model=PerformanceReviewOut)
def update_performance_review(
    ident: int,
    payload: PerformanceReviewUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.performance_review.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, PerformanceReview, ident, "Entretiens d'evaluation")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/performance-reviews/{ident}", response_model=PerformanceReviewOut)
def delete_performance_review(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.performance_review.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, PerformanceReview, ident, "Entretiens d'evaluation")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Procedures disciplinaires ─────────────────────────────────────────────────

@router.get("/disciplinary-cases", response_model=List[DisciplinaryCaseOut])
def list_disciplinary(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.disciplinary.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, DisciplinaryCase, cid, {"statut": statut})


@router.post("/disciplinary-cases", response_model=DisciplinaryCaseOut, status_code=201)
def create_disciplinary(
    payload: DisciplinaryCaseCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.disciplinary.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, DisciplinaryCase, "reference", data.get("reference"), "reference", cid)
    obj = DisciplinaryCase(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/disciplinary-cases/{ident}", response_model=DisciplinaryCaseOut)
def update_disciplinary(
    ident: int,
    payload: DisciplinaryCaseUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.disciplinary.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, DisciplinaryCase, ident, "Procedures disciplinaires")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/disciplinary-cases/{ident}", response_model=DisciplinaryCaseOut)
def delete_disciplinary(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.disciplinary.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, DisciplinaryCase, ident, "Procedures disciplinaires")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Organigramme ─────────────────────────────────────────────────

@router.get("/org-units", response_model=List[OrgUnitOut])
def list_org_chart(db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.org_chart.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, OrgUnit, cid)


@router.post("/org-units", response_model=OrgUnitOut, status_code=201)
def create_org_chart(
    payload: OrgUnitCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.org_chart.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, OrgUnit, "code_unite", data.get("code_unite"), "code_unite", cid)
    obj = OrgUnit(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/org-units/{ident}", response_model=OrgUnitOut)
def update_org_chart(
    ident: int,
    payload: OrgUnitUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.org_chart.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, OrgUnit, ident, "Organigramme")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/org-units/{ident}", response_model=OrgUnitOut)
def delete_org_chart(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.org_chart.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, OrgUnit, ident, "Organigramme")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Masse salariale previsionnelle ─────────────────────────────────────────────────

@router.get("/workforce-plans", response_model=List[WorkforcePlanOut])
def list_workforce_planning(db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.workforce_planning.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, WorkforcePlan, cid)


@router.post("/workforce-plans", response_model=WorkforcePlanOut, status_code=201)
def create_workforce_planning(
    payload: WorkforcePlanCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.workforce_planning.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, WorkforcePlan, "reference", data.get("reference"), "reference", cid)
    obj = WorkforcePlan(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/workforce-plans/{ident}", response_model=WorkforcePlanOut)
def update_workforce_planning(
    ident: int,
    payload: WorkforcePlanUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.workforce_planning.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, WorkforcePlan, ident, "Masse salariale previsionnelle")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/workforce-plans/{ident}", response_model=WorkforcePlanOut)
def delete_workforce_planning(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.workforce_planning.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, WorkforcePlan, ident, "Masse salariale previsionnelle")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Suivi contrats ─────────────────────────────────────────────────

@router.get("/employment-contracts", response_model=List[EmploymentContractOut])
def list_contract_management(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.contract_management.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, EmploymentContract, cid, {"statut": statut})


@router.post("/employment-contracts", response_model=EmploymentContractOut, status_code=201)
def create_contract_management(
    payload: EmploymentContractCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.contract_management.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, EmploymentContract, "numero_contrat", data.get("numero_contrat"), "numero_contrat", cid)
    obj = EmploymentContract(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/employment-contracts/{ident}", response_model=EmploymentContractOut)
def update_contract_management(
    ident: int,
    payload: EmploymentContractUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.contract_management.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, EmploymentContract, ident, "Suivi contrats")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/employment-contracts/{ident}", response_model=EmploymentContractOut)
def delete_contract_management(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.contract_management.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, EmploymentContract, ident, "Suivi contrats")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Avantages ─────────────────────────────────────────────────

@router.get("/employee-benefits", response_model=List[EmployeeBenefitOut])
def list_benefits(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.benefits.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, EmployeeBenefit, cid, {"statut": statut})


@router.post("/employee-benefits", response_model=EmployeeBenefitOut, status_code=201)
def create_benefits(
    payload: EmployeeBenefitCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.benefits.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, EmployeeBenefit, "reference", data.get("reference"), "reference", cid)
    obj = EmployeeBenefit(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/employee-benefits/{ident}", response_model=EmployeeBenefitOut)
def update_benefits(
    ident: int,
    payload: EmployeeBenefitUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.benefits.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, EmployeeBenefit, ident, "Avantages")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/employee-benefits/{ident}", response_model=EmployeeBenefitOut)
def delete_benefits(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.benefits.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, EmployeeBenefit, ident, "Avantages")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Depart / solde tout compte ─────────────────────────────────────────────────

@router.get("/employee-exits", response_model=List[EmployeeExitOut])
def list_exit_management(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.exit_management.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, EmployeeExit, cid, {"statut": statut})


@router.post("/employee-exits", response_model=EmployeeExitOut, status_code=201)
def create_exit_management(
    payload: EmployeeExitCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.exit_management.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, EmployeeExit, "reference", data.get("reference"), "reference", cid)
    obj = EmployeeExit(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/employee-exits/{ident}", response_model=EmployeeExitOut)
def update_exit_management(
    ident: int,
    payload: EmployeeExitUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.exit_management.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, EmployeeExit, ident, "Depart / solde tout compte")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/employee-exits/{ident}", response_model=EmployeeExitOut)
def delete_exit_management(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.exit_management.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, EmployeeExit, ident, "Depart / solde tout compte")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Pointage / badgeuses ─────────────────────────────────────────────────

@router.get("/attendance-devices", response_model=List[AttendanceDeviceOut])
def list_attendance_device(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.attendance_device.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, AttendanceDevice, cid, {"statut": statut})


@router.post("/attendance-devices", response_model=AttendanceDeviceOut, status_code=201)
def create_attendance_device(
    payload: AttendanceDeviceCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.attendance_device.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, AttendanceDevice, "code_terminal", data.get("code_terminal"), "code_terminal", cid)
    obj = AttendanceDevice(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/attendance-devices/{ident}", response_model=AttendanceDeviceOut)
def update_attendance_device(
    ident: int,
    payload: AttendanceDeviceUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.attendance_device.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, AttendanceDevice, ident, "Pointage / badgeuses")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/attendance-devices/{ident}", response_model=AttendanceDeviceOut)
def delete_attendance_device(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.attendance_device.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, AttendanceDevice, ident, "Pointage / badgeuses")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Droits conges / report N-1 ─────────────────────────────────────────────────

@router.get("/leave-quotas", response_model=List[LeaveQuotaOut])
def list_leave_quota(db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.leave_quota.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, LeaveQuota, cid)


@router.post("/leave-quotas", response_model=LeaveQuotaOut, status_code=201)
def create_leave_quota(
    payload: LeaveQuotaCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.leave_quota.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, LeaveQuota, "reference", data.get("reference"), "reference", cid)
    obj = LeaveQuota(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/leave-quotas/{ident}", response_model=LeaveQuotaOut)
def update_leave_quota(
    ident: int,
    payload: LeaveQuotaUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.leave_quota.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, LeaveQuota, ident, "Droits conges / report N-1")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/leave-quotas/{ident}", response_model=LeaveQuotaOut)
def delete_leave_quota(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.leave_quota.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, LeaveQuota, ident, "Droits conges / report N-1")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Matrice de competences ─────────────────────────────────────────────────

@router.get("/employee-skills", response_model=List[EmployeeSkillOut])
def list_skills_matrix(db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.skills_matrix.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, EmployeeSkill, cid)


@router.post("/employee-skills", response_model=EmployeeSkillOut, status_code=201)
def create_skills_matrix(
    payload: EmployeeSkillCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.skills_matrix.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, EmployeeSkill, "reference", data.get("reference"), "reference", cid)
    obj = EmployeeSkill(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/employee-skills/{ident}", response_model=EmployeeSkillOut)
def update_skills_matrix(
    ident: int,
    payload: EmployeeSkillUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.skills_matrix.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, EmployeeSkill, ident, "Matrice de competences")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/employee-skills/{ident}", response_model=EmployeeSkillOut)
def delete_skills_matrix(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.skills_matrix.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, EmployeeSkill, ident, "Matrice de competences")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Rapports RH periodiques ─────────────────────────────────────────────────

@router.get("/hr-reports", response_model=List[HrReportOut])
def list_hr_reports(db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.hr_reports.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, HrReport, cid)


@router.post("/hr-reports", response_model=HrReportOut, status_code=201)
def create_hr_reports(
    payload: HrReportCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.hr_reports.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, HrReport, "reference", data.get("reference"), "reference", cid)
    obj = HrReport(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/hr-reports/{ident}", response_model=HrReportOut)
def update_hr_reports(
    ident: int,
    payload: HrReportUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.hr_reports.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, HrReport, ident, "Rapports RH periodiques")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/hr-reports/{ident}", response_model=HrReportOut)
def delete_hr_reports(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.hr_reports.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, HrReport, ident, "Rapports RH periodiques")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj

