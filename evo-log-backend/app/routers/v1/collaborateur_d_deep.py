"""Routeur CRUD genere pour portail-collaborateur (expansion)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List

from app.core.database import get_db
from app.core.permissions import require_perm
from app.models.user import User
from app.models.collaborateur_d_deep import (
    CollAssignment,
    CollActivityLog,
    CollDeliverable,
    CollTimesheet,
    CollSiteAccessLog,
    CollWorkInstructionReceipt,
    CollIncidentReport,
    CollQualityCheck,
    CollTrainingCompletion,
    CollEquipmentIssue,
    CollShiftAttendance,
    CollTravelOrder,
    CollExpenseDeclaration,
    CollCertificationUpload,
    CollTaskCompletion,
    CollFeedback,
    CollAvailability,
    CollContractRenewalRequest,
    CollDocumentRequest,
)
from app.schemas.collaborateur_d_deep import (
    CollAssignmentCreate, CollAssignmentUpdate, CollAssignmentOut,
    CollActivityLogCreate, CollActivityLogUpdate, CollActivityLogOut,
    CollDeliverableCreate, CollDeliverableUpdate, CollDeliverableOut,
    CollTimesheetCreate, CollTimesheetUpdate, CollTimesheetOut,
    CollSiteAccessLogCreate, CollSiteAccessLogUpdate, CollSiteAccessLogOut,
    CollWorkInstructionReceiptCreate, CollWorkInstructionReceiptUpdate, CollWorkInstructionReceiptOut,
    CollIncidentReportCreate, CollIncidentReportUpdate, CollIncidentReportOut,
    CollQualityCheckCreate, CollQualityCheckUpdate, CollQualityCheckOut,
    CollTrainingCompletionCreate, CollTrainingCompletionUpdate, CollTrainingCompletionOut,
    CollEquipmentIssueCreate, CollEquipmentIssueUpdate, CollEquipmentIssueOut,
    CollShiftAttendanceCreate, CollShiftAttendanceUpdate, CollShiftAttendanceOut,
    CollTravelOrderCreate, CollTravelOrderUpdate, CollTravelOrderOut,
    CollExpenseDeclarationCreate, CollExpenseDeclarationUpdate, CollExpenseDeclarationOut,
    CollCertificationUploadCreate, CollCertificationUploadUpdate, CollCertificationUploadOut,
    CollTaskCompletionCreate, CollTaskCompletionUpdate, CollTaskCompletionOut,
    CollFeedbackCreate, CollFeedbackUpdate, CollFeedbackOut,
    CollAvailabilityCreate, CollAvailabilityUpdate, CollAvailabilityOut,
    CollContractRenewalRequestCreate, CollContractRenewalRequestUpdate, CollContractRenewalRequestOut,
    CollDocumentRequestCreate, CollDocumentRequestUpdate, CollDocumentRequestOut,
)

router = APIRouter(tags=["portail-collaborateur (expansion)"])


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

@router.get("/nomenclatures", summary="Vocabulaire metier portail-collaborateur")
def nomenclatures(user: User = Depends(require_perm("rh.nomenclature.read"))):
    from app.models import collaborateur_d_deep as _md
    import enum as _pyenum
    out = {}
    for name in dir(_md):
        obj = getattr(_md, name)
        if isinstance(obj, type) and issubclass(obj, _pyenum.Enum) and obj is not _pyenum.Enum:
            out[name.lower()] = [{"code": m.name, "valeur": m.value} for m in obj]
    return out


# ─── Affectations de mission ─────────────────────────────────────────────────

@router.get("/coll-assignment-records", response_model=List[CollAssignmentOut])
def list_assignment_record(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.assignment_record.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, CollAssignment, cid, {"statut": statut})


@router.post("/coll-assignment-records", response_model=CollAssignmentOut, status_code=201)
def create_assignment_record(
    payload: CollAssignmentCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.assignment_record.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, CollAssignment, "reference", data.get("reference"), "reference", cid)
    obj = CollAssignment(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/coll-assignment-records/{ident}", response_model=CollAssignmentOut)
def update_assignment_record(
    ident: int,
    payload: CollAssignmentUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.assignment_record.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CollAssignment, ident, "Affectations de mission")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/coll-assignment-records/{ident}", response_model=CollAssignmentOut)
def delete_assignment_record(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.assignment_record.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CollAssignment, ident, "Affectations de mission")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Journaux d' activite ─────────────────────────────────────────────────

@router.get("/coll-daily-activity-logs", response_model=List[CollActivityLogOut])
def list_daily_activity_log(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.daily_activity_log.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, CollActivityLog, cid, {"statut": statut})


@router.post("/coll-daily-activity-logs", response_model=CollActivityLogOut, status_code=201)
def create_daily_activity_log(
    payload: CollActivityLogCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.daily_activity_log.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, CollActivityLog, "reference", data.get("reference"), "reference", cid)
    obj = CollActivityLog(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/coll-daily-activity-logs/{ident}", response_model=CollActivityLogOut)
def update_daily_activity_log(
    ident: int,
    payload: CollActivityLogUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.daily_activity_log.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CollActivityLog, ident, "Journaux d' activite")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/coll-daily-activity-logs/{ident}", response_model=CollActivityLogOut)
def delete_daily_activity_log(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.daily_activity_log.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CollActivityLog, ident, "Journaux d' activite")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Remises de livrables ─────────────────────────────────────────────────

@router.get("/coll-deliverable-submissions", response_model=List[CollDeliverableOut])
def list_deliverable_submission(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.deliverable_submission.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, CollDeliverable, cid, {"statut": statut})


@router.post("/coll-deliverable-submissions", response_model=CollDeliverableOut, status_code=201)
def create_deliverable_submission(
    payload: CollDeliverableCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.deliverable_submission.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, CollDeliverable, "reference", data.get("reference"), "reference", cid)
    obj = CollDeliverable(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/coll-deliverable-submissions/{ident}", response_model=CollDeliverableOut)
def update_deliverable_submission(
    ident: int,
    payload: CollDeliverableUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.deliverable_submission.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CollDeliverable, ident, "Remises de livrables")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/coll-deliverable-submissions/{ident}", response_model=CollDeliverableOut)
def delete_deliverable_submission(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.deliverable_submission.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CollDeliverable, ident, "Remises de livrables")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Declarations de temps ─────────────────────────────────────────────────

@router.get("/coll-timesheet-declarations", response_model=List[CollTimesheetOut])
def list_timesheet_declaration(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.timesheet_declaration.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, CollTimesheet, cid, {"statut": statut})


@router.post("/coll-timesheet-declarations", response_model=CollTimesheetOut, status_code=201)
def create_timesheet_declaration(
    payload: CollTimesheetCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.timesheet_declaration.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, CollTimesheet, "reference", data.get("reference"), "reference", cid)
    obj = CollTimesheet(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/coll-timesheet-declarations/{ident}", response_model=CollTimesheetOut)
def update_timesheet_declaration(
    ident: int,
    payload: CollTimesheetUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.timesheet_declaration.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CollTimesheet, ident, "Declarations de temps")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/coll-timesheet-declarations/{ident}", response_model=CollTimesheetOut)
def delete_timesheet_declaration(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.timesheet_declaration.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CollTimesheet, ident, "Declarations de temps")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Journaux d' acces site ─────────────────────────────────────────────────

@router.get("/coll-site-access-logs", response_model=List[CollSiteAccessLogOut])
def list_site_access_log(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.site_access_log.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, CollSiteAccessLog, cid, {"statut": statut})


@router.post("/coll-site-access-logs", response_model=CollSiteAccessLogOut, status_code=201)
def create_site_access_log(
    payload: CollSiteAccessLogCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.site_access_log.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, CollSiteAccessLog, "reference", data.get("reference"), "reference", cid)
    obj = CollSiteAccessLog(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/coll-site-access-logs/{ident}", response_model=CollSiteAccessLogOut)
def update_site_access_log(
    ident: int,
    payload: CollSiteAccessLogUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.site_access_log.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CollSiteAccessLog, ident, "Journaux d' acces site")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/coll-site-access-logs/{ident}", response_model=CollSiteAccessLogOut)
def delete_site_access_log(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.site_access_log.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CollSiteAccessLog, ident, "Journaux d' acces site")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Accuses de consignes ─────────────────────────────────────────────────

@router.get("/coll-work-instruction-receipts", response_model=List[CollWorkInstructionReceiptOut])
def list_work_instruction_receipt(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.work_instruction_receipt.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, CollWorkInstructionReceipt, cid, {"statut": statut})


@router.post("/coll-work-instruction-receipts", response_model=CollWorkInstructionReceiptOut, status_code=201)
def create_work_instruction_receipt(
    payload: CollWorkInstructionReceiptCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.work_instruction_receipt.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, CollWorkInstructionReceipt, "reference", data.get("reference"), "reference", cid)
    obj = CollWorkInstructionReceipt(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/coll-work-instruction-receipts/{ident}", response_model=CollWorkInstructionReceiptOut)
def update_work_instruction_receipt(
    ident: int,
    payload: CollWorkInstructionReceiptUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.work_instruction_receipt.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CollWorkInstructionReceipt, ident, "Accuses de consignes")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/coll-work-instruction-receipts/{ident}", response_model=CollWorkInstructionReceiptOut)
def delete_work_instruction_receipt(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.work_instruction_receipt.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CollWorkInstructionReceipt, ident, "Accuses de consignes")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Signalements d' incident ─────────────────────────────────────────────────

@router.get("/coll-incident-reports", response_model=List[CollIncidentReportOut])
def list_incident_report(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.incident_report.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, CollIncidentReport, cid, {"statut": statut})


@router.post("/coll-incident-reports", response_model=CollIncidentReportOut, status_code=201)
def create_incident_report(
    payload: CollIncidentReportCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.incident_report.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, CollIncidentReport, "reference", data.get("reference"), "reference", cid)
    obj = CollIncidentReport(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/coll-incident-reports/{ident}", response_model=CollIncidentReportOut)
def update_incident_report(
    ident: int,
    payload: CollIncidentReportUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.incident_report.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CollIncidentReport, ident, "Signalements d' incident")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/coll-incident-reports/{ident}", response_model=CollIncidentReportOut)
def delete_incident_report(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.incident_report.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CollIncidentReport, ident, "Signalements d' incident")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Remises de controles qualite ─────────────────────────────────────────────────

@router.get("/coll-quality-check-submissions", response_model=List[CollQualityCheckOut])
def list_quality_check_submission(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.quality_check_submission.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, CollQualityCheck, cid, {"statut": statut})


@router.post("/coll-quality-check-submissions", response_model=CollQualityCheckOut, status_code=201)
def create_quality_check_submission(
    payload: CollQualityCheckCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.quality_check_submission.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, CollQualityCheck, "reference", data.get("reference"), "reference", cid)
    obj = CollQualityCheck(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/coll-quality-check-submissions/{ident}", response_model=CollQualityCheckOut)
def update_quality_check_submission(
    ident: int,
    payload: CollQualityCheckUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.quality_check_submission.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CollQualityCheck, ident, "Remises de controles qualite")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/coll-quality-check-submissions/{ident}", response_model=CollQualityCheckOut)
def delete_quality_check_submission(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.quality_check_submission.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CollQualityCheck, ident, "Remises de controles qualite")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Attestations de formation ─────────────────────────────────────────────────

@router.get("/coll-training-completions", response_model=List[CollTrainingCompletionOut])
def list_training_completion(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.training_completion.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, CollTrainingCompletion, cid, {"statut": statut})


@router.post("/coll-training-completions", response_model=CollTrainingCompletionOut, status_code=201)
def create_training_completion(
    payload: CollTrainingCompletionCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.training_completion.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, CollTrainingCompletion, "reference", data.get("reference"), "reference", cid)
    obj = CollTrainingCompletion(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/coll-training-completions/{ident}", response_model=CollTrainingCompletionOut)
def update_training_completion(
    ident: int,
    payload: CollTrainingCompletionUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.training_completion.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CollTrainingCompletion, ident, "Attestations de formation")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/coll-training-completions/{ident}", response_model=CollTrainingCompletionOut)
def delete_training_completion(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.training_completion.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CollTrainingCompletion, ident, "Attestations de formation")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Signalements de probleme equipement ─────────────────────────────────────────────────

@router.get("/coll-equipment-issues", response_model=List[CollEquipmentIssueOut])
def list_equipment_issue(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.equipment_issue.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, CollEquipmentIssue, cid, {"statut": statut})


@router.post("/coll-equipment-issues", response_model=CollEquipmentIssueOut, status_code=201)
def create_equipment_issue(
    payload: CollEquipmentIssueCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.equipment_issue.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, CollEquipmentIssue, "reference", data.get("reference"), "reference", cid)
    obj = CollEquipmentIssue(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/coll-equipment-issues/{ident}", response_model=CollEquipmentIssueOut)
def update_equipment_issue(
    ident: int,
    payload: CollEquipmentIssueUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.equipment_issue.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CollEquipmentIssue, ident, "Signalements de probleme equipement")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/coll-equipment-issues/{ident}", response_model=CollEquipmentIssueOut)
def delete_equipment_issue(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.equipment_issue.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CollEquipmentIssue, ident, "Signalements de probleme equipement")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Presences par poste ─────────────────────────────────────────────────

@router.get("/coll-shift-attendance", response_model=List[CollShiftAttendanceOut])
def list_shift_attendance(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.shift_attendance.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, CollShiftAttendance, cid, {"statut": statut})


@router.post("/coll-shift-attendance", response_model=CollShiftAttendanceOut, status_code=201)
def create_shift_attendance(
    payload: CollShiftAttendanceCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.shift_attendance.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, CollShiftAttendance, "reference", data.get("reference"), "reference", cid)
    obj = CollShiftAttendance(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/coll-shift-attendance/{ident}", response_model=CollShiftAttendanceOut)
def update_shift_attendance(
    ident: int,
    payload: CollShiftAttendanceUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.shift_attendance.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CollShiftAttendance, ident, "Presences par poste")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/coll-shift-attendance/{ident}", response_model=CollShiftAttendanceOut)
def delete_shift_attendance(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.shift_attendance.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CollShiftAttendance, ident, "Presences par poste")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Ordres de mission ─────────────────────────────────────────────────

@router.get("/coll-travel-orders", response_model=List[CollTravelOrderOut])
def list_travel_order(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.travel_order.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, CollTravelOrder, cid, {"statut": statut})


@router.post("/coll-travel-orders", response_model=CollTravelOrderOut, status_code=201)
def create_travel_order(
    payload: CollTravelOrderCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.travel_order.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, CollTravelOrder, "reference", data.get("reference"), "reference", cid)
    obj = CollTravelOrder(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/coll-travel-orders/{ident}", response_model=CollTravelOrderOut)
def update_travel_order(
    ident: int,
    payload: CollTravelOrderUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.travel_order.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CollTravelOrder, ident, "Ordres de mission")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/coll-travel-orders/{ident}", response_model=CollTravelOrderOut)
def delete_travel_order(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.travel_order.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CollTravelOrder, ident, "Ordres de mission")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Declarations de frais ─────────────────────────────────────────────────

@router.get("/coll-expense-declarations", response_model=List[CollExpenseDeclarationOut])
def list_expense_declaration(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.expense_declaration.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, CollExpenseDeclaration, cid, {"statut": statut})


@router.post("/coll-expense-declarations", response_model=CollExpenseDeclarationOut, status_code=201)
def create_expense_declaration(
    payload: CollExpenseDeclarationCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.expense_declaration.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, CollExpenseDeclaration, "reference", data.get("reference"), "reference", cid)
    obj = CollExpenseDeclaration(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/coll-expense-declarations/{ident}", response_model=CollExpenseDeclarationOut)
def update_expense_declaration(
    ident: int,
    payload: CollExpenseDeclarationUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.expense_declaration.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CollExpenseDeclaration, ident, "Declarations de frais")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/coll-expense-declarations/{ident}", response_model=CollExpenseDeclarationOut)
def delete_expense_declaration(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.expense_declaration.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CollExpenseDeclaration, ident, "Declarations de frais")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Depot de certifications ─────────────────────────────────────────────────

@router.get("/coll-certification-uploads", response_model=List[CollCertificationUploadOut])
def list_certification_upload(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.certification_upload.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, CollCertificationUpload, cid, {"statut": statut})


@router.post("/coll-certification-uploads", response_model=CollCertificationUploadOut, status_code=201)
def create_certification_upload(
    payload: CollCertificationUploadCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.certification_upload.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, CollCertificationUpload, "reference", data.get("reference"), "reference", cid)
    obj = CollCertificationUpload(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/coll-certification-uploads/{ident}", response_model=CollCertificationUploadOut)
def update_certification_upload(
    ident: int,
    payload: CollCertificationUploadUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.certification_upload.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CollCertificationUpload, ident, "Depot de certifications")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/coll-certification-uploads/{ident}", response_model=CollCertificationUploadOut)
def delete_certification_upload(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.certification_upload.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CollCertificationUpload, ident, "Depot de certifications")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Achevements de taches ─────────────────────────────────────────────────

@router.get("/coll-task-completions", response_model=List[CollTaskCompletionOut])
def list_task_completion(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.task_completion.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, CollTaskCompletion, cid, {"statut": statut})


@router.post("/coll-task-completions", response_model=CollTaskCompletionOut, status_code=201)
def create_task_completion(
    payload: CollTaskCompletionCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.task_completion.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, CollTaskCompletion, "reference", data.get("reference"), "reference", cid)
    obj = CollTaskCompletion(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/coll-task-completions/{ident}", response_model=CollTaskCompletionOut)
def update_task_completion(
    ident: int,
    payload: CollTaskCompletionUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.task_completion.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CollTaskCompletion, ident, "Achevements de taches")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/coll-task-completions/{ident}", response_model=CollTaskCompletionOut)
def delete_task_completion(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.task_completion.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CollTaskCompletion, ident, "Achevements de taches")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Remontees terrain ─────────────────────────────────────────────────

@router.get("/coll-feedback-submissions", response_model=List[CollFeedbackOut])
def list_feedback_submission(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.feedback_submission.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, CollFeedback, cid, {"statut": statut})


@router.post("/coll-feedback-submissions", response_model=CollFeedbackOut, status_code=201)
def create_feedback_submission(
    payload: CollFeedbackCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.feedback_submission.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, CollFeedback, "reference", data.get("reference"), "reference", cid)
    obj = CollFeedback(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/coll-feedback-submissions/{ident}", response_model=CollFeedbackOut)
def update_feedback_submission(
    ident: int,
    payload: CollFeedbackUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.feedback_submission.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CollFeedback, ident, "Remontees terrain")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/coll-feedback-submissions/{ident}", response_model=CollFeedbackOut)
def delete_feedback_submission(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.feedback_submission.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CollFeedback, ident, "Remontees terrain")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Declarations de disponibilite ─────────────────────────────────────────────────

@router.get("/coll-availability-declarations", response_model=List[CollAvailabilityOut])
def list_availability_declaration(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.availability_declaration.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, CollAvailability, cid, {"statut": statut})


@router.post("/coll-availability-declarations", response_model=CollAvailabilityOut, status_code=201)
def create_availability_declaration(
    payload: CollAvailabilityCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.availability_declaration.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, CollAvailability, "reference", data.get("reference"), "reference", cid)
    obj = CollAvailability(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/coll-availability-declarations/{ident}", response_model=CollAvailabilityOut)
def update_availability_declaration(
    ident: int,
    payload: CollAvailabilityUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.availability_declaration.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CollAvailability, ident, "Declarations de disponibilite")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/coll-availability-declarations/{ident}", response_model=CollAvailabilityOut)
def delete_availability_declaration(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.availability_declaration.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CollAvailability, ident, "Declarations de disponibilite")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Demandes de renouvellement de contrat ─────────────────────────────────────────────────

@router.get("/coll-contract-renewal-requests", response_model=List[CollContractRenewalRequestOut])
def list_contract_renewal_request(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.contract_renewal_request.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, CollContractRenewalRequest, cid, {"statut": statut})


@router.post("/coll-contract-renewal-requests", response_model=CollContractRenewalRequestOut, status_code=201)
def create_contract_renewal_request(
    payload: CollContractRenewalRequestCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.contract_renewal_request.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, CollContractRenewalRequest, "reference", data.get("reference"), "reference", cid)
    obj = CollContractRenewalRequest(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/coll-contract-renewal-requests/{ident}", response_model=CollContractRenewalRequestOut)
def update_contract_renewal_request(
    ident: int,
    payload: CollContractRenewalRequestUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.contract_renewal_request.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CollContractRenewalRequest, ident, "Demandes de renouvellement de contrat")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/coll-contract-renewal-requests/{ident}", response_model=CollContractRenewalRequestOut)
def delete_contract_renewal_request(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.contract_renewal_request.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CollContractRenewalRequest, ident, "Demandes de renouvellement de contrat")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Demandes de documents ─────────────────────────────────────────────────

@router.get("/coll-document-requests", response_model=List[CollDocumentRequestOut])
def list_document_request(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.document_request.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, CollDocumentRequest, cid, {"statut": statut})


@router.post("/coll-document-requests", response_model=CollDocumentRequestOut, status_code=201)
def create_document_request(
    payload: CollDocumentRequestCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.document_request.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, CollDocumentRequest, "reference", data.get("reference"), "reference", cid)
    obj = CollDocumentRequest(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/coll-document-requests/{ident}", response_model=CollDocumentRequestOut)
def update_document_request(
    ident: int,
    payload: CollDocumentRequestUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.document_request.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CollDocumentRequest, ident, "Demandes de documents")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/coll-document-requests/{ident}", response_model=CollDocumentRequestOut)
def delete_document_request(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.document_request.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CollDocumentRequest, ident, "Demandes de documents")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj

