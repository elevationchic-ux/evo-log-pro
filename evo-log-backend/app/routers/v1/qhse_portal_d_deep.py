"""Routeur CRUD genere pour portail-qhse (expansion)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List

from app.core.database import get_db
from app.core.permissions import require_perm
from app.models.user import User
from app.models.qhse_portal_d_deep import (
    QspHazardReport,
    QspNearMiss,
    QspSafetyObservation,
    QspPpeAttestation,
    QspToolboxTalk,
    QspWorkPermitRequest,
    QspSafetyTrainingLog,
    QspExposureRecord,
    QspFirstAidLog,
    QspSafetySuggestion,
    QspStopWorkAuthority,
    QspSpillReport,
    QspMsdsAck,
    QspErgonomicsAssessment,
    QspHygieneCheck,
    QspInspectionFinding,
    QspCapaReply,
    QspRiskAssessmentInput,
    QspEvacuationDrill,
)
from app.schemas.qhse_portal_d_deep import (
    QspHazardReportCreate, QspHazardReportUpdate, QspHazardReportOut,
    QspNearMissCreate, QspNearMissUpdate, QspNearMissOut,
    QspSafetyObservationCreate, QspSafetyObservationUpdate, QspSafetyObservationOut,
    QspPpeAttestationCreate, QspPpeAttestationUpdate, QspPpeAttestationOut,
    QspToolboxTalkCreate, QspToolboxTalkUpdate, QspToolboxTalkOut,
    QspWorkPermitRequestCreate, QspWorkPermitRequestUpdate, QspWorkPermitRequestOut,
    QspSafetyTrainingLogCreate, QspSafetyTrainingLogUpdate, QspSafetyTrainingLogOut,
    QspExposureRecordCreate, QspExposureRecordUpdate, QspExposureRecordOut,
    QspFirstAidLogCreate, QspFirstAidLogUpdate, QspFirstAidLogOut,
    QspSafetySuggestionCreate, QspSafetySuggestionUpdate, QspSafetySuggestionOut,
    QspStopWorkAuthorityCreate, QspStopWorkAuthorityUpdate, QspStopWorkAuthorityOut,
    QspSpillReportCreate, QspSpillReportUpdate, QspSpillReportOut,
    QspMsdsAckCreate, QspMsdsAckUpdate, QspMsdsAckOut,
    QspErgonomicsAssessmentCreate, QspErgonomicsAssessmentUpdate, QspErgonomicsAssessmentOut,
    QspHygieneCheckCreate, QspHygieneCheckUpdate, QspHygieneCheckOut,
    QspInspectionFindingCreate, QspInspectionFindingUpdate, QspInspectionFindingOut,
    QspCapaReplyCreate, QspCapaReplyUpdate, QspCapaReplyOut,
    QspRiskAssessmentInputCreate, QspRiskAssessmentInputUpdate, QspRiskAssessmentInputOut,
    QspEvacuationDrillCreate, QspEvacuationDrillUpdate, QspEvacuationDrillOut,
)

router = APIRouter(tags=["portail-qhse (expansion)"])


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

@router.get("/nomenclatures", summary="Vocabulaire metier portail-qhse")
def nomenclatures(user: User = Depends(require_perm("qhse.nomenclature.read"))):
    from app.models import qhse_portal_d_deep as _md
    import enum as _pyenum
    out = {}
    for name in dir(_md):
        obj = getattr(_md, name)
        if isinstance(obj, type) and issubclass(obj, _pyenum.Enum) and obj is not _pyenum.Enum:
            out[name.lower()] = [{"code": m.name, "valeur": m.value} for m in obj]
    return out


# ─── Signalements de dangers ─────────────────────────────────────────────────

@router.get("/qsp-hazard-reports", response_model=List[QspHazardReportOut])
def list_hazard_report(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.hazard_report.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, QspHazardReport, cid, {"statut": statut})


@router.post("/qsp-hazard-reports", response_model=QspHazardReportOut, status_code=201)
def create_hazard_report(
    payload: QspHazardReportCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.hazard_report.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, QspHazardReport, "reference", data.get("reference"), "reference", cid)
    obj = QspHazardReport(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/qsp-hazard-reports/{ident}", response_model=QspHazardReportOut)
def update_hazard_report(
    ident: int,
    payload: QspHazardReportUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.hazard_report.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, QspHazardReport, ident, "Signalements de dangers")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/qsp-hazard-reports/{ident}", response_model=QspHazardReportOut)
def delete_hazard_report(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.hazard_report.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, QspHazardReport, ident, "Signalements de dangers")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Presqu' accidents ─────────────────────────────────────────────────

@router.get("/qsp-near-misses", response_model=List[QspNearMissOut])
def list_near_miss(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.near_miss.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, QspNearMiss, cid, {"statut": statut})


@router.post("/qsp-near-misses", response_model=QspNearMissOut, status_code=201)
def create_near_miss(
    payload: QspNearMissCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.near_miss.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, QspNearMiss, "reference", data.get("reference"), "reference", cid)
    obj = QspNearMiss(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/qsp-near-misses/{ident}", response_model=QspNearMissOut)
def update_near_miss(
    ident: int,
    payload: QspNearMissUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.near_miss.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, QspNearMiss, ident, "Presqu' accidents")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/qsp-near-misses/{ident}", response_model=QspNearMissOut)
def delete_near_miss(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.near_miss.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, QspNearMiss, ident, "Presqu' accidents")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Observations de securite ─────────────────────────────────────────────────

@router.get("/qsp-safety-observations", response_model=List[QspSafetyObservationOut])
def list_safety_observation(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.safety_observation.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, QspSafetyObservation, cid, {"statut": statut})


@router.post("/qsp-safety-observations", response_model=QspSafetyObservationOut, status_code=201)
def create_safety_observation(
    payload: QspSafetyObservationCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.safety_observation.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, QspSafetyObservation, "reference", data.get("reference"), "reference", cid)
    obj = QspSafetyObservation(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/qsp-safety-observations/{ident}", response_model=QspSafetyObservationOut)
def update_safety_observation(
    ident: int,
    payload: QspSafetyObservationUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.safety_observation.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, QspSafetyObservation, ident, "Observations de securite")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/qsp-safety-observations/{ident}", response_model=QspSafetyObservationOut)
def delete_safety_observation(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.safety_observation.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, QspSafetyObservation, ident, "Observations de securite")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Attestations de port d' EPI ─────────────────────────────────────────────────

@router.get("/qsp-ppe-attestations", response_model=List[QspPpeAttestationOut])
def list_ppe_attestation(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.ppe_attestation.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, QspPpeAttestation, cid, {"statut": statut})


@router.post("/qsp-ppe-attestations", response_model=QspPpeAttestationOut, status_code=201)
def create_ppe_attestation(
    payload: QspPpeAttestationCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.ppe_attestation.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, QspPpeAttestation, "reference", data.get("reference"), "reference", cid)
    obj = QspPpeAttestation(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/qsp-ppe-attestations/{ident}", response_model=QspPpeAttestationOut)
def update_ppe_attestation(
    ident: int,
    payload: QspPpeAttestationUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.ppe_attestation.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, QspPpeAttestation, ident, "Attestations de port d' EPI")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/qsp-ppe-attestations/{ident}", response_model=QspPpeAttestationOut)
def delete_ppe_attestation(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.ppe_attestation.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, QspPpeAttestation, ident, "Attestations de port d' EPI")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Quarts d' heure securite ─────────────────────────────────────────────────

@router.get("/qsp-toolbox-talks", response_model=List[QspToolboxTalkOut])
def list_toolbox_talk(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.toolbox_talk.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, QspToolboxTalk, cid, {"statut": statut})


@router.post("/qsp-toolbox-talks", response_model=QspToolboxTalkOut, status_code=201)
def create_toolbox_talk(
    payload: QspToolboxTalkCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.toolbox_talk.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, QspToolboxTalk, "reference", data.get("reference"), "reference", cid)
    obj = QspToolboxTalk(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/qsp-toolbox-talks/{ident}", response_model=QspToolboxTalkOut)
def update_toolbox_talk(
    ident: int,
    payload: QspToolboxTalkUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.toolbox_talk.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, QspToolboxTalk, ident, "Quarts d' heure securite")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/qsp-toolbox-talks/{ident}", response_model=QspToolboxTalkOut)
def delete_toolbox_talk(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.toolbox_talk.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, QspToolboxTalk, ident, "Quarts d' heure securite")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Demandes de permis de travail ─────────────────────────────────────────────────

@router.get("/qsp-work-permit-requests", response_model=List[QspWorkPermitRequestOut])
def list_work_permit_request(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.work_permit_request.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, QspWorkPermitRequest, cid, {"statut": statut})


@router.post("/qsp-work-permit-requests", response_model=QspWorkPermitRequestOut, status_code=201)
def create_work_permit_request(
    payload: QspWorkPermitRequestCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.work_permit_request.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, QspWorkPermitRequest, "reference", data.get("reference"), "reference", cid)
    obj = QspWorkPermitRequest(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/qsp-work-permit-requests/{ident}", response_model=QspWorkPermitRequestOut)
def update_work_permit_request(
    ident: int,
    payload: QspWorkPermitRequestUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.work_permit_request.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, QspWorkPermitRequest, ident, "Demandes de permis de travail")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/qsp-work-permit-requests/{ident}", response_model=QspWorkPermitRequestOut)
def delete_work_permit_request(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.work_permit_request.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, QspWorkPermitRequest, ident, "Demandes de permis de travail")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Suivi formation securite ─────────────────────────────────────────────────

@router.get("/qsp-safety-training-log", response_model=List[QspSafetyTrainingLogOut])
def list_safety_training_log(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.safety_training_log.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, QspSafetyTrainingLog, cid, {"statut": statut})


@router.post("/qsp-safety-training-log", response_model=QspSafetyTrainingLogOut, status_code=201)
def create_safety_training_log(
    payload: QspSafetyTrainingLogCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.safety_training_log.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, QspSafetyTrainingLog, "reference", data.get("reference"), "reference", cid)
    obj = QspSafetyTrainingLog(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/qsp-safety-training-log/{ident}", response_model=QspSafetyTrainingLogOut)
def update_safety_training_log(
    ident: int,
    payload: QspSafetyTrainingLogUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.safety_training_log.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, QspSafetyTrainingLog, ident, "Suivi formation securite")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/qsp-safety-training-log/{ident}", response_model=QspSafetyTrainingLogOut)
def delete_safety_training_log(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.safety_training_log.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, QspSafetyTrainingLog, ident, "Suivi formation securite")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Registres d' exposition ─────────────────────────────────────────────────

@router.get("/qsp-exposure-records", response_model=List[QspExposureRecordOut])
def list_exposure_record(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.exposure_record.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, QspExposureRecord, cid, {"statut": statut})


@router.post("/qsp-exposure-records", response_model=QspExposureRecordOut, status_code=201)
def create_exposure_record(
    payload: QspExposureRecordCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.exposure_record.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, QspExposureRecord, "reference", data.get("reference"), "reference", cid)
    obj = QspExposureRecord(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/qsp-exposure-records/{ident}", response_model=QspExposureRecordOut)
def update_exposure_record(
    ident: int,
    payload: QspExposureRecordUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.exposure_record.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, QspExposureRecord, ident, "Registres d' exposition")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/qsp-exposure-records/{ident}", response_model=QspExposureRecordOut)
def delete_exposure_record(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.exposure_record.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, QspExposureRecord, ident, "Registres d' exposition")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Registre de premiers secours ─────────────────────────────────────────────────

@router.get("/qsp-first-aid-log", response_model=List[QspFirstAidLogOut])
def list_first_aid_log(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.first_aid_log.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, QspFirstAidLog, cid, {"statut": statut})


@router.post("/qsp-first-aid-log", response_model=QspFirstAidLogOut, status_code=201)
def create_first_aid_log(
    payload: QspFirstAidLogCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.first_aid_log.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, QspFirstAidLog, "reference", data.get("reference"), "reference", cid)
    obj = QspFirstAidLog(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/qsp-first-aid-log/{ident}", response_model=QspFirstAidLogOut)
def update_first_aid_log(
    ident: int,
    payload: QspFirstAidLogUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.first_aid_log.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, QspFirstAidLog, ident, "Registre de premiers secours")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/qsp-first-aid-log/{ident}", response_model=QspFirstAidLogOut)
def delete_first_aid_log(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.first_aid_log.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, QspFirstAidLog, ident, "Registre de premiers secours")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Suggestions de securite ─────────────────────────────────────────────────

@router.get("/qsp-safety-suggestions", response_model=List[QspSafetySuggestionOut])
def list_safety_suggestion(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.safety_suggestion.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, QspSafetySuggestion, cid, {"statut": statut})


@router.post("/qsp-safety-suggestions", response_model=QspSafetySuggestionOut, status_code=201)
def create_safety_suggestion(
    payload: QspSafetySuggestionCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.safety_suggestion.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, QspSafetySuggestion, "reference", data.get("reference"), "reference", cid)
    obj = QspSafetySuggestion(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/qsp-safety-suggestions/{ident}", response_model=QspSafetySuggestionOut)
def update_safety_suggestion(
    ident: int,
    payload: QspSafetySuggestionUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.safety_suggestion.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, QspSafetySuggestion, ident, "Suggestions de securite")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/qsp-safety-suggestions/{ident}", response_model=QspSafetySuggestionOut)
def delete_safety_suggestion(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.safety_suggestion.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, QspSafetySuggestion, ident, "Suggestions de securite")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Droits de retrait ─────────────────────────────────────────────────

@router.get("/qsp-stop-work-authorities", response_model=List[QspStopWorkAuthorityOut])
def list_stop_work(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.stop_work.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, QspStopWorkAuthority, cid, {"statut": statut})


@router.post("/qsp-stop-work-authorities", response_model=QspStopWorkAuthorityOut, status_code=201)
def create_stop_work(
    payload: QspStopWorkAuthorityCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.stop_work.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, QspStopWorkAuthority, "reference", data.get("reference"), "reference", cid)
    obj = QspStopWorkAuthority(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/qsp-stop-work-authorities/{ident}", response_model=QspStopWorkAuthorityOut)
def update_stop_work(
    ident: int,
    payload: QspStopWorkAuthorityUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.stop_work.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, QspStopWorkAuthority, ident, "Droits de retrait")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/qsp-stop-work-authorities/{ident}", response_model=QspStopWorkAuthorityOut)
def delete_stop_work(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.stop_work.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, QspStopWorkAuthority, ident, "Droits de retrait")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Signalements de deversement ─────────────────────────────────────────────────

@router.get("/qsp-spill-reports", response_model=List[QspSpillReportOut])
def list_spill_report(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.spill_report.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, QspSpillReport, cid, {"statut": statut})


@router.post("/qsp-spill-reports", response_model=QspSpillReportOut, status_code=201)
def create_spill_report(
    payload: QspSpillReportCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.spill_report.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, QspSpillReport, "reference", data.get("reference"), "reference", cid)
    obj = QspSpillReport(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/qsp-spill-reports/{ident}", response_model=QspSpillReportOut)
def update_spill_report(
    ident: int,
    payload: QspSpillReportUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.spill_report.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, QspSpillReport, ident, "Signalements de deversement")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/qsp-spill-reports/{ident}", response_model=QspSpillReportOut)
def delete_spill_report(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.spill_report.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, QspSpillReport, ident, "Signalements de deversement")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Accuses FDS ─────────────────────────────────────────────────

@router.get("/qsp-msds-acknowledgements", response_model=List[QspMsdsAckOut])
def list_msds_ack(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.msds_ack.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, QspMsdsAck, cid, {"statut": statut})


@router.post("/qsp-msds-acknowledgements", response_model=QspMsdsAckOut, status_code=201)
def create_msds_ack(
    payload: QspMsdsAckCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.msds_ack.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, QspMsdsAck, "reference", data.get("reference"), "reference", cid)
    obj = QspMsdsAck(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/qsp-msds-acknowledgements/{ident}", response_model=QspMsdsAckOut)
def update_msds_ack(
    ident: int,
    payload: QspMsdsAckUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.msds_ack.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, QspMsdsAck, ident, "Accuses FDS")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/qsp-msds-acknowledgements/{ident}", response_model=QspMsdsAckOut)
def delete_msds_ack(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.msds_ack.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, QspMsdsAck, ident, "Accuses FDS")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Evaluations ergonomiques ─────────────────────────────────────────────────

@router.get("/qsp-ergonomics-assessments", response_model=List[QspErgonomicsAssessmentOut])
def list_ergonomics_assessment(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.ergonomics_assessment.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, QspErgonomicsAssessment, cid, {"statut": statut})


@router.post("/qsp-ergonomics-assessments", response_model=QspErgonomicsAssessmentOut, status_code=201)
def create_ergonomics_assessment(
    payload: QspErgonomicsAssessmentCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.ergonomics_assessment.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, QspErgonomicsAssessment, "reference", data.get("reference"), "reference", cid)
    obj = QspErgonomicsAssessment(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/qsp-ergonomics-assessments/{ident}", response_model=QspErgonomicsAssessmentOut)
def update_ergonomics_assessment(
    ident: int,
    payload: QspErgonomicsAssessmentUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.ergonomics_assessment.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, QspErgonomicsAssessment, ident, "Evaluations ergonomiques")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/qsp-ergonomics-assessments/{ident}", response_model=QspErgonomicsAssessmentOut)
def delete_ergonomics_assessment(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.ergonomics_assessment.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, QspErgonomicsAssessment, ident, "Evaluations ergonomiques")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Controles d' hygiene ─────────────────────────────────────────────────

@router.get("/qsp-hygiene-checks", response_model=List[QspHygieneCheckOut])
def list_hygiene_check(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.hygiene_check.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, QspHygieneCheck, cid, {"statut": statut})


@router.post("/qsp-hygiene-checks", response_model=QspHygieneCheckOut, status_code=201)
def create_hygiene_check(
    payload: QspHygieneCheckCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.hygiene_check.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, QspHygieneCheck, "reference", data.get("reference"), "reference", cid)
    obj = QspHygieneCheck(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/qsp-hygiene-checks/{ident}", response_model=QspHygieneCheckOut)
def update_hygiene_check(
    ident: int,
    payload: QspHygieneCheckUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.hygiene_check.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, QspHygieneCheck, ident, "Controles d' hygiene")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/qsp-hygiene-checks/{ident}", response_model=QspHygieneCheckOut)
def delete_hygiene_check(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.hygiene_check.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, QspHygieneCheck, ident, "Controles d' hygiene")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Constats d' inspection ─────────────────────────────────────────────────

@router.get("/qsp-inspection-findings", response_model=List[QspInspectionFindingOut])
def list_inspection_finding(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.inspection_finding.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, QspInspectionFinding, cid, {"statut": statut})


@router.post("/qsp-inspection-findings", response_model=QspInspectionFindingOut, status_code=201)
def create_inspection_finding(
    payload: QspInspectionFindingCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.inspection_finding.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, QspInspectionFinding, "reference", data.get("reference"), "reference", cid)
    obj = QspInspectionFinding(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/qsp-inspection-findings/{ident}", response_model=QspInspectionFindingOut)
def update_inspection_finding(
    ident: int,
    payload: QspInspectionFindingUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.inspection_finding.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, QspInspectionFinding, ident, "Constats d' inspection")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/qsp-inspection-findings/{ident}", response_model=QspInspectionFindingOut)
def delete_inspection_finding(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.inspection_finding.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, QspInspectionFinding, ident, "Constats d' inspection")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Reponses aux actions correctives ─────────────────────────────────────────────────

@router.get("/qsp-corrective-action-replies", response_model=List[QspCapaReplyOut])
def list_capa_reply(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.capa_reply.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, QspCapaReply, cid, {"statut": statut})


@router.post("/qsp-corrective-action-replies", response_model=QspCapaReplyOut, status_code=201)
def create_capa_reply(
    payload: QspCapaReplyCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.capa_reply.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, QspCapaReply, "reference", data.get("reference"), "reference", cid)
    obj = QspCapaReply(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/qsp-corrective-action-replies/{ident}", response_model=QspCapaReplyOut)
def update_capa_reply(
    ident: int,
    payload: QspCapaReplyUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.capa_reply.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, QspCapaReply, ident, "Reponses aux actions correctives")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/qsp-corrective-action-replies/{ident}", response_model=QspCapaReplyOut)
def delete_capa_reply(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.capa_reply.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, QspCapaReply, ident, "Reponses aux actions correctives")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Contributions a l' evaluation des risques ─────────────────────────────────────────────────

@router.get("/qsp-risk-assessment-inputs", response_model=List[QspRiskAssessmentInputOut])
def list_risk_assessment_input(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.risk_assessment_input.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, QspRiskAssessmentInput, cid, {"statut": statut})


@router.post("/qsp-risk-assessment-inputs", response_model=QspRiskAssessmentInputOut, status_code=201)
def create_risk_assessment_input(
    payload: QspRiskAssessmentInputCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.risk_assessment_input.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, QspRiskAssessmentInput, "reference", data.get("reference"), "reference", cid)
    obj = QspRiskAssessmentInput(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/qsp-risk-assessment-inputs/{ident}", response_model=QspRiskAssessmentInputOut)
def update_risk_assessment_input(
    ident: int,
    payload: QspRiskAssessmentInputUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.risk_assessment_input.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, QspRiskAssessmentInput, ident, "Contributions a l' evaluation des risques")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/qsp-risk-assessment-inputs/{ident}", response_model=QspRiskAssessmentInputOut)
def delete_risk_assessment_input(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.risk_assessment_input.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, QspRiskAssessmentInput, ident, "Contributions a l' evaluation des risques")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Exercices d' evacuation ─────────────────────────────────────────────────

@router.get("/qsp-evacuation-drills", response_model=List[QspEvacuationDrillOut])
def list_evacuation_drill(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.evacuation_drill.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, QspEvacuationDrill, cid, {"statut": statut})


@router.post("/qsp-evacuation-drills", response_model=QspEvacuationDrillOut, status_code=201)
def create_evacuation_drill(
    payload: QspEvacuationDrillCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.evacuation_drill.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, QspEvacuationDrill, "reference", data.get("reference"), "reference", cid)
    obj = QspEvacuationDrill(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/qsp-evacuation-drills/{ident}", response_model=QspEvacuationDrillOut)
def update_evacuation_drill(
    ident: int,
    payload: QspEvacuationDrillUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.evacuation_drill.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, QspEvacuationDrill, ident, "Exercices d' evacuation")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/qsp-evacuation-drills/{ident}", response_model=QspEvacuationDrillOut)
def delete_evacuation_drill(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.evacuation_drill.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, QspEvacuationDrill, ident, "Exercices d' evacuation")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj

