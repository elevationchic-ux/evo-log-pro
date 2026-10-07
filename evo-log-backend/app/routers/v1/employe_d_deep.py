"""Routeur CRUD genere pour portail-employe (expansion)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List

from app.core.database import get_db
from app.core.permissions import require_perm
from app.models.user import User
from app.models.employe_d_deep import (
    EmpLeaveRequest,
    EmpTimesheetEntry,
    EmpOvertimeRequest,
    EmpAttendanceCorrection,
    EmpShiftSwap,
    EmpTrainingEnrollment,
    EmpSkillDeclaration,
    EmpCertificationRenewal,
    EmpPersonalInfoChange,
    EmpBankDetailsUpdate,
    EmpEmergencyContact,
    EmpBadgeRequest,
    EmpAccessRequest,
    EmpDocumentUpload,
    EmpSelfReview,
    EmpMobilityApplication,
    EmpSicknessDeclaration,
)
from app.schemas.employe_d_deep import (
    EmpLeaveRequestCreate, EmpLeaveRequestUpdate, EmpLeaveRequestOut,
    EmpTimesheetEntryCreate, EmpTimesheetEntryUpdate, EmpTimesheetEntryOut,
    EmpOvertimeRequestCreate, EmpOvertimeRequestUpdate, EmpOvertimeRequestOut,
    EmpAttendanceCorrectionCreate, EmpAttendanceCorrectionUpdate, EmpAttendanceCorrectionOut,
    EmpShiftSwapCreate, EmpShiftSwapUpdate, EmpShiftSwapOut,
    EmpTrainingEnrollmentCreate, EmpTrainingEnrollmentUpdate, EmpTrainingEnrollmentOut,
    EmpSkillDeclarationCreate, EmpSkillDeclarationUpdate, EmpSkillDeclarationOut,
    EmpCertificationRenewalCreate, EmpCertificationRenewalUpdate, EmpCertificationRenewalOut,
    EmpPersonalInfoChangeCreate, EmpPersonalInfoChangeUpdate, EmpPersonalInfoChangeOut,
    EmpBankDetailsUpdateCreate, EmpBankDetailsUpdateUpdate, EmpBankDetailsUpdateOut,
    EmpEmergencyContactCreate, EmpEmergencyContactUpdate, EmpEmergencyContactOut,
    EmpBadgeRequestCreate, EmpBadgeRequestUpdate, EmpBadgeRequestOut,
    EmpAccessRequestCreate, EmpAccessRequestUpdate, EmpAccessRequestOut,
    EmpDocumentUploadCreate, EmpDocumentUploadUpdate, EmpDocumentUploadOut,
    EmpSelfReviewCreate, EmpSelfReviewUpdate, EmpSelfReviewOut,
    EmpMobilityApplicationCreate, EmpMobilityApplicationUpdate, EmpMobilityApplicationOut,
    EmpSicknessDeclarationCreate, EmpSicknessDeclarationUpdate, EmpSicknessDeclarationOut,
)

router = APIRouter(tags=["portail-employe (expansion)"])


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

@router.get("/nomenclatures", summary="Vocabulaire metier portail-employe")
def nomenclatures(user: User = Depends(require_perm("rh.nomenclature.read"))):
    from app.models import employe_d_deep as _md
    import enum as _pyenum
    out = {}
    for name in dir(_md):
        obj = getattr(_md, name)
        if isinstance(obj, type) and issubclass(obj, _pyenum.Enum) and obj is not _pyenum.Enum:
            out[name.lower()] = [{"code": m.name, "valeur": m.value} for m in obj]
    return out


# ─── Demandes de conges ─────────────────────────────────────────────────

@router.get("/emp-leave-requests", response_model=List[EmpLeaveRequestOut])
def list_leave_request(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.leave_request.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, EmpLeaveRequest, cid, {"statut": statut})


@router.post("/emp-leave-requests", response_model=EmpLeaveRequestOut, status_code=201)
def create_leave_request(
    payload: EmpLeaveRequestCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.leave_request.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, EmpLeaveRequest, "reference", data.get("reference"), "reference", cid)
    obj = EmpLeaveRequest(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/emp-leave-requests/{ident}", response_model=EmpLeaveRequestOut)
def update_leave_request(
    ident: int,
    payload: EmpLeaveRequestUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.leave_request.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, EmpLeaveRequest, ident, "Demandes de conges")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/emp-leave-requests/{ident}", response_model=EmpLeaveRequestOut)
def delete_leave_request(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.leave_request.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, EmpLeaveRequest, ident, "Demandes de conges")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Feuilles de temps ─────────────────────────────────────────────────

@router.get("/emp-timesheet-entries", response_model=List[EmpTimesheetEntryOut])
def list_timesheet_entry(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.timesheet_entry.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, EmpTimesheetEntry, cid, {"statut": statut})


@router.post("/emp-timesheet-entries", response_model=EmpTimesheetEntryOut, status_code=201)
def create_timesheet_entry(
    payload: EmpTimesheetEntryCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.timesheet_entry.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, EmpTimesheetEntry, "reference", data.get("reference"), "reference", cid)
    obj = EmpTimesheetEntry(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/emp-timesheet-entries/{ident}", response_model=EmpTimesheetEntryOut)
def update_timesheet_entry(
    ident: int,
    payload: EmpTimesheetEntryUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.timesheet_entry.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, EmpTimesheetEntry, ident, "Feuilles de temps")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/emp-timesheet-entries/{ident}", response_model=EmpTimesheetEntryOut)
def delete_timesheet_entry(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.timesheet_entry.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, EmpTimesheetEntry, ident, "Feuilles de temps")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Demandes d' heures supplementaires ─────────────────────────────────────────────────

@router.get("/emp-overtime-requests", response_model=List[EmpOvertimeRequestOut])
def list_overtime_request(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.overtime_request.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, EmpOvertimeRequest, cid, {"statut": statut})


@router.post("/emp-overtime-requests", response_model=EmpOvertimeRequestOut, status_code=201)
def create_overtime_request(
    payload: EmpOvertimeRequestCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.overtime_request.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, EmpOvertimeRequest, "reference", data.get("reference"), "reference", cid)
    obj = EmpOvertimeRequest(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/emp-overtime-requests/{ident}", response_model=EmpOvertimeRequestOut)
def update_overtime_request(
    ident: int,
    payload: EmpOvertimeRequestUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.overtime_request.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, EmpOvertimeRequest, ident, "Demandes d' heures supplementaires")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/emp-overtime-requests/{ident}", response_model=EmpOvertimeRequestOut)
def delete_overtime_request(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.overtime_request.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, EmpOvertimeRequest, ident, "Demandes d' heures supplementaires")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Regularisations de pointage ─────────────────────────────────────────────────

@router.get("/emp-attendance-corrections", response_model=List[EmpAttendanceCorrectionOut])
def list_attendance_correction(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.attendance_correction.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, EmpAttendanceCorrection, cid, {"statut": statut})


@router.post("/emp-attendance-corrections", response_model=EmpAttendanceCorrectionOut, status_code=201)
def create_attendance_correction(
    payload: EmpAttendanceCorrectionCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.attendance_correction.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, EmpAttendanceCorrection, "reference", data.get("reference"), "reference", cid)
    obj = EmpAttendanceCorrection(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/emp-attendance-corrections/{ident}", response_model=EmpAttendanceCorrectionOut)
def update_attendance_correction(
    ident: int,
    payload: EmpAttendanceCorrectionUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.attendance_correction.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, EmpAttendanceCorrection, ident, "Regularisations de pointage")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/emp-attendance-corrections/{ident}", response_model=EmpAttendanceCorrectionOut)
def delete_attendance_correction(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.attendance_correction.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, EmpAttendanceCorrection, ident, "Regularisations de pointage")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Echanges de poste ─────────────────────────────────────────────────

@router.get("/emp-shift-swaps", response_model=List[EmpShiftSwapOut])
def list_shift_swap(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.shift_swap.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, EmpShiftSwap, cid, {"statut": statut})


@router.post("/emp-shift-swaps", response_model=EmpShiftSwapOut, status_code=201)
def create_shift_swap(
    payload: EmpShiftSwapCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.shift_swap.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, EmpShiftSwap, "reference", data.get("reference"), "reference", cid)
    obj = EmpShiftSwap(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/emp-shift-swaps/{ident}", response_model=EmpShiftSwapOut)
def update_shift_swap(
    ident: int,
    payload: EmpShiftSwapUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.shift_swap.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, EmpShiftSwap, ident, "Echanges de poste")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/emp-shift-swaps/{ident}", response_model=EmpShiftSwapOut)
def delete_shift_swap(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.shift_swap.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, EmpShiftSwap, ident, "Echanges de poste")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Inscriptions formation ─────────────────────────────────────────────────

@router.get("/emp-training-enrollments", response_model=List[EmpTrainingEnrollmentOut])
def list_training_enrollment(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.training_enrollment.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, EmpTrainingEnrollment, cid, {"statut": statut})


@router.post("/emp-training-enrollments", response_model=EmpTrainingEnrollmentOut, status_code=201)
def create_training_enrollment(
    payload: EmpTrainingEnrollmentCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.training_enrollment.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, EmpTrainingEnrollment, "reference", data.get("reference"), "reference", cid)
    obj = EmpTrainingEnrollment(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/emp-training-enrollments/{ident}", response_model=EmpTrainingEnrollmentOut)
def update_training_enrollment(
    ident: int,
    payload: EmpTrainingEnrollmentUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.training_enrollment.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, EmpTrainingEnrollment, ident, "Inscriptions formation")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/emp-training-enrollments/{ident}", response_model=EmpTrainingEnrollmentOut)
def delete_training_enrollment(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.training_enrollment.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, EmpTrainingEnrollment, ident, "Inscriptions formation")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Declarations de competences ─────────────────────────────────────────────────

@router.get("/emp-skill-declarations", response_model=List[EmpSkillDeclarationOut])
def list_skill_declaration(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.skill_declaration.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, EmpSkillDeclaration, cid, {"statut": statut})


@router.post("/emp-skill-declarations", response_model=EmpSkillDeclarationOut, status_code=201)
def create_skill_declaration(
    payload: EmpSkillDeclarationCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.skill_declaration.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, EmpSkillDeclaration, "reference", data.get("reference"), "reference", cid)
    obj = EmpSkillDeclaration(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/emp-skill-declarations/{ident}", response_model=EmpSkillDeclarationOut)
def update_skill_declaration(
    ident: int,
    payload: EmpSkillDeclarationUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.skill_declaration.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, EmpSkillDeclaration, ident, "Declarations de competences")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/emp-skill-declarations/{ident}", response_model=EmpSkillDeclarationOut)
def delete_skill_declaration(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.skill_declaration.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, EmpSkillDeclaration, ident, "Declarations de competences")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Renouvellements de certification ─────────────────────────────────────────────────

@router.get("/emp-certification-renewals", response_model=List[EmpCertificationRenewalOut])
def list_certification_renewal(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.certification_renewal.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, EmpCertificationRenewal, cid, {"statut": statut})


@router.post("/emp-certification-renewals", response_model=EmpCertificationRenewalOut, status_code=201)
def create_certification_renewal(
    payload: EmpCertificationRenewalCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.certification_renewal.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, EmpCertificationRenewal, "reference", data.get("reference"), "reference", cid)
    obj = EmpCertificationRenewal(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/emp-certification-renewals/{ident}", response_model=EmpCertificationRenewalOut)
def update_certification_renewal(
    ident: int,
    payload: EmpCertificationRenewalUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.certification_renewal.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, EmpCertificationRenewal, ident, "Renouvellements de certification")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/emp-certification-renewals/{ident}", response_model=EmpCertificationRenewalOut)
def delete_certification_renewal(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.certification_renewal.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, EmpCertificationRenewal, ident, "Renouvellements de certification")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Modifications d' etat civil ─────────────────────────────────────────────────

@router.get("/emp-personal-info-changes", response_model=List[EmpPersonalInfoChangeOut])
def list_personal_info_change(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.personal_info_change.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, EmpPersonalInfoChange, cid, {"statut": statut})


@router.post("/emp-personal-info-changes", response_model=EmpPersonalInfoChangeOut, status_code=201)
def create_personal_info_change(
    payload: EmpPersonalInfoChangeCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.personal_info_change.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, EmpPersonalInfoChange, "reference", data.get("reference"), "reference", cid)
    obj = EmpPersonalInfoChange(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/emp-personal-info-changes/{ident}", response_model=EmpPersonalInfoChangeOut)
def update_personal_info_change(
    ident: int,
    payload: EmpPersonalInfoChangeUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.personal_info_change.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, EmpPersonalInfoChange, ident, "Modifications d' etat civil")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/emp-personal-info-changes/{ident}", response_model=EmpPersonalInfoChangeOut)
def delete_personal_info_change(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.personal_info_change.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, EmpPersonalInfoChange, ident, "Modifications d' etat civil")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Changements de RIB ─────────────────────────────────────────────────

@router.get("/emp-bank-details-updates", response_model=List[EmpBankDetailsUpdateOut])
def list_bank_details_update(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.bank_details_update.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, EmpBankDetailsUpdate, cid, {"statut": statut})


@router.post("/emp-bank-details-updates", response_model=EmpBankDetailsUpdateOut, status_code=201)
def create_bank_details_update(
    payload: EmpBankDetailsUpdateCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.bank_details_update.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, EmpBankDetailsUpdate, "reference", data.get("reference"), "reference", cid)
    obj = EmpBankDetailsUpdate(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/emp-bank-details-updates/{ident}", response_model=EmpBankDetailsUpdateOut)
def update_bank_details_update(
    ident: int,
    payload: EmpBankDetailsUpdateUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.bank_details_update.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, EmpBankDetailsUpdate, ident, "Changements de RIB")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/emp-bank-details-updates/{ident}", response_model=EmpBankDetailsUpdateOut)
def delete_bank_details_update(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.bank_details_update.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, EmpBankDetailsUpdate, ident, "Changements de RIB")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Contacts d' urgence ─────────────────────────────────────────────────

@router.get("/emp-emergency-contacts", response_model=List[EmpEmergencyContactOut])
def list_emergency_contact(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.emergency_contact.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, EmpEmergencyContact, cid, {"statut": statut})


@router.post("/emp-emergency-contacts", response_model=EmpEmergencyContactOut, status_code=201)
def create_emergency_contact(
    payload: EmpEmergencyContactCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.emergency_contact.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, EmpEmergencyContact, "reference", data.get("reference"), "reference", cid)
    obj = EmpEmergencyContact(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/emp-emergency-contacts/{ident}", response_model=EmpEmergencyContactOut)
def update_emergency_contact(
    ident: int,
    payload: EmpEmergencyContactUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.emergency_contact.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, EmpEmergencyContact, ident, "Contacts d' urgence")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/emp-emergency-contacts/{ident}", response_model=EmpEmergencyContactOut)
def delete_emergency_contact(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.emergency_contact.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, EmpEmergencyContact, ident, "Contacts d' urgence")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Demandes de badge ─────────────────────────────────────────────────

@router.get("/emp-badge-requests", response_model=List[EmpBadgeRequestOut])
def list_badge_request(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.badge_request.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, EmpBadgeRequest, cid, {"statut": statut})


@router.post("/emp-badge-requests", response_model=EmpBadgeRequestOut, status_code=201)
def create_badge_request(
    payload: EmpBadgeRequestCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.badge_request.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, EmpBadgeRequest, "reference", data.get("reference"), "reference", cid)
    obj = EmpBadgeRequest(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/emp-badge-requests/{ident}", response_model=EmpBadgeRequestOut)
def update_badge_request(
    ident: int,
    payload: EmpBadgeRequestUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.badge_request.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, EmpBadgeRequest, ident, "Demandes de badge")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/emp-badge-requests/{ident}", response_model=EmpBadgeRequestOut)
def delete_badge_request(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.badge_request.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, EmpBadgeRequest, ident, "Demandes de badge")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Demandes d' acces ─────────────────────────────────────────────────

@router.get("/emp-access-requests", response_model=List[EmpAccessRequestOut])
def list_access_request(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.access_request.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, EmpAccessRequest, cid, {"statut": statut})


@router.post("/emp-access-requests", response_model=EmpAccessRequestOut, status_code=201)
def create_access_request(
    payload: EmpAccessRequestCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.access_request.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, EmpAccessRequest, "reference", data.get("reference"), "reference", cid)
    obj = EmpAccessRequest(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/emp-access-requests/{ident}", response_model=EmpAccessRequestOut)
def update_access_request(
    ident: int,
    payload: EmpAccessRequestUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.access_request.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, EmpAccessRequest, ident, "Demandes d' acces")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/emp-access-requests/{ident}", response_model=EmpAccessRequestOut)
def delete_access_request(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.access_request.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, EmpAccessRequest, ident, "Demandes d' acces")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Depot de documents RH ─────────────────────────────────────────────────

@router.get("/emp-document-uploads", response_model=List[EmpDocumentUploadOut])
def list_document_upload(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.document_upload.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, EmpDocumentUpload, cid, {"statut": statut})


@router.post("/emp-document-uploads", response_model=EmpDocumentUploadOut, status_code=201)
def create_document_upload(
    payload: EmpDocumentUploadCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.document_upload.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, EmpDocumentUpload, "reference", data.get("reference"), "reference", cid)
    obj = EmpDocumentUpload(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/emp-document-uploads/{ident}", response_model=EmpDocumentUploadOut)
def update_document_upload(
    ident: int,
    payload: EmpDocumentUploadUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.document_upload.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, EmpDocumentUpload, ident, "Depot de documents RH")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/emp-document-uploads/{ident}", response_model=EmpDocumentUploadOut)
def delete_document_upload(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.document_upload.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, EmpDocumentUpload, ident, "Depot de documents RH")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Auto-evaluations ─────────────────────────────────────────────────

@router.get("/emp-self-reviews", response_model=List[EmpSelfReviewOut])
def list_self_review(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.self_review.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, EmpSelfReview, cid, {"statut": statut})


@router.post("/emp-self-reviews", response_model=EmpSelfReviewOut, status_code=201)
def create_self_review(
    payload: EmpSelfReviewCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.self_review.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, EmpSelfReview, "reference", data.get("reference"), "reference", cid)
    obj = EmpSelfReview(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/emp-self-reviews/{ident}", response_model=EmpSelfReviewOut)
def update_self_review(
    ident: int,
    payload: EmpSelfReviewUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.self_review.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, EmpSelfReview, ident, "Auto-evaluations")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/emp-self-reviews/{ident}", response_model=EmpSelfReviewOut)
def delete_self_review(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.self_review.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, EmpSelfReview, ident, "Auto-evaluations")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Candidatures internes ─────────────────────────────────────────────────

@router.get("/emp-internal-mobility-applications", response_model=List[EmpMobilityApplicationOut])
def list_mobility_application(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.mobility_application.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, EmpMobilityApplication, cid, {"statut": statut})


@router.post("/emp-internal-mobility-applications", response_model=EmpMobilityApplicationOut, status_code=201)
def create_mobility_application(
    payload: EmpMobilityApplicationCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.mobility_application.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, EmpMobilityApplication, "reference", data.get("reference"), "reference", cid)
    obj = EmpMobilityApplication(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/emp-internal-mobility-applications/{ident}", response_model=EmpMobilityApplicationOut)
def update_mobility_application(
    ident: int,
    payload: EmpMobilityApplicationUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.mobility_application.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, EmpMobilityApplication, ident, "Candidatures internes")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/emp-internal-mobility-applications/{ident}", response_model=EmpMobilityApplicationOut)
def delete_mobility_application(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.mobility_application.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, EmpMobilityApplication, ident, "Candidatures internes")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Declarations d' arret maladie ─────────────────────────────────────────────────

@router.get("/emp-sickness-declarations", response_model=List[EmpSicknessDeclarationOut])
def list_sickness_declaration(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.sickness_declaration.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, EmpSicknessDeclaration, cid, {"statut": statut})


@router.post("/emp-sickness-declarations", response_model=EmpSicknessDeclarationOut, status_code=201)
def create_sickness_declaration(
    payload: EmpSicknessDeclarationCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.sickness_declaration.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, EmpSicknessDeclaration, "reference", data.get("reference"), "reference", cid)
    obj = EmpSicknessDeclaration(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/emp-sickness-declarations/{ident}", response_model=EmpSicknessDeclarationOut)
def update_sickness_declaration(
    ident: int,
    payload: EmpSicknessDeclarationUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.sickness_declaration.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, EmpSicknessDeclaration, ident, "Declarations d' arret maladie")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/emp-sickness-declarations/{ident}", response_model=EmpSicknessDeclarationOut)
def delete_sickness_declaration(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.sickness_declaration.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, EmpSicknessDeclaration, ident, "Declarations d' arret maladie")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj

