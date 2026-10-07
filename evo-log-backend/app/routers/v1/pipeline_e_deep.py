"""Routeur CRUD genere pour pipeline-oleoduc (expansion)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List

from app.core.database import get_db
from app.core.permissions import require_perm
from app.models.user import User
from app.models.pipeline_e_deep import (
    Pipe2CustodyTransfer,
    Pipe2PressureLog,
    Pipe2PumpStationRead,
    Pipe2CorrosionReading,
    Pipe2FlowCalibration,
    Pipe2BatchQualityTest,
    Pipe2InterfaceDetection,
    Pipe2IntegrityAssessment,
    Pipe2SpillResponseAction,
)
from app.schemas.pipeline_e_deep import (
    Pipe2CustodyTransferCreate, Pipe2CustodyTransferUpdate, Pipe2CustodyTransferOut,
    Pipe2PressureLogCreate, Pipe2PressureLogUpdate, Pipe2PressureLogOut,
    Pipe2PumpStationReadCreate, Pipe2PumpStationReadUpdate, Pipe2PumpStationReadOut,
    Pipe2CorrosionReadingCreate, Pipe2CorrosionReadingUpdate, Pipe2CorrosionReadingOut,
    Pipe2FlowCalibrationCreate, Pipe2FlowCalibrationUpdate, Pipe2FlowCalibrationOut,
    Pipe2BatchQualityTestCreate, Pipe2BatchQualityTestUpdate, Pipe2BatchQualityTestOut,
    Pipe2InterfaceDetectionCreate, Pipe2InterfaceDetectionUpdate, Pipe2InterfaceDetectionOut,
    Pipe2IntegrityAssessmentCreate, Pipe2IntegrityAssessmentUpdate, Pipe2IntegrityAssessmentOut,
    Pipe2SpillResponseActionCreate, Pipe2SpillResponseActionUpdate, Pipe2SpillResponseActionOut,
)

router = APIRouter(tags=["pipeline-oleoduc (expansion)"])


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

@router.get("/nomenclatures", summary="Vocabulaire metier pipeline-oleoduc")
def nomenclatures(user: User = Depends(require_perm("pipeline.nomenclature.read"))):
    from app.models import pipeline_e_deep as _md
    import enum as _pyenum
    out = {}
    for name in dir(_md):
        obj = getattr(_md, name)
        if isinstance(obj, type) and issubclass(obj, _pyenum.Enum) and obj is not _pyenum.Enum:
            out[name.lower()] = [{"code": m.name, "valeur": m.value} for m in obj]
    return out


# ─── Transferts de custody ─────────────────────────────────────────────────

@router.get("/pipe2-custody-transfers", response_model=List[Pipe2CustodyTransferOut])
def list_custody_transfer(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("pipeline.custody_transfer.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, Pipe2CustodyTransfer, cid, {"statut": statut})


@router.post("/pipe2-custody-transfers", response_model=Pipe2CustodyTransferOut, status_code=201)
def create_custody_transfer(
    payload: Pipe2CustodyTransferCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("pipeline.custody_transfer.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, Pipe2CustodyTransfer, "reference", data.get("reference"), "reference", cid)
    obj = Pipe2CustodyTransfer(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/pipe2-custody-transfers/{ident}", response_model=Pipe2CustodyTransferOut)
def update_custody_transfer(
    ident: int,
    payload: Pipe2CustodyTransferUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("pipeline.custody_transfer.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, Pipe2CustodyTransfer, ident, "Transferts de custody")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/pipe2-custody-transfers/{ident}", response_model=Pipe2CustodyTransferOut)
def delete_custody_transfer(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("pipeline.custody_transfer.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, Pipe2CustodyTransfer, ident, "Transferts de custody")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Releves de pression ─────────────────────────────────────────────────

@router.get("/pipe2-pressure-logs", response_model=List[Pipe2PressureLogOut])
def list_pressure_log(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("pipeline.pressure_log.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, Pipe2PressureLog, cid, {"statut": statut})


@router.post("/pipe2-pressure-logs", response_model=Pipe2PressureLogOut, status_code=201)
def create_pressure_log(
    payload: Pipe2PressureLogCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("pipeline.pressure_log.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, Pipe2PressureLog, "reference", data.get("reference"), "reference", cid)
    obj = Pipe2PressureLog(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/pipe2-pressure-logs/{ident}", response_model=Pipe2PressureLogOut)
def update_pressure_log(
    ident: int,
    payload: Pipe2PressureLogUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("pipeline.pressure_log.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, Pipe2PressureLog, ident, "Releves de pression")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/pipe2-pressure-logs/{ident}", response_model=Pipe2PressureLogOut)
def delete_pressure_log(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("pipeline.pressure_log.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, Pipe2PressureLog, ident, "Releves de pression")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Releves de station de pompage ─────────────────────────────────────────────────

@router.get("/pipe2-pump-station-reads", response_model=List[Pipe2PumpStationReadOut])
def list_pump_station_read(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("pipeline.pump_station_read.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, Pipe2PumpStationRead, cid, {"statut": statut})


@router.post("/pipe2-pump-station-reads", response_model=Pipe2PumpStationReadOut, status_code=201)
def create_pump_station_read(
    payload: Pipe2PumpStationReadCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("pipeline.pump_station_read.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, Pipe2PumpStationRead, "reference", data.get("reference"), "reference", cid)
    obj = Pipe2PumpStationRead(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/pipe2-pump-station-reads/{ident}", response_model=Pipe2PumpStationReadOut)
def update_pump_station_read(
    ident: int,
    payload: Pipe2PumpStationReadUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("pipeline.pump_station_read.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, Pipe2PumpStationRead, ident, "Releves de station de pompage")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/pipe2-pump-station-reads/{ident}", response_model=Pipe2PumpStationReadOut)
def delete_pump_station_read(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("pipeline.pump_station_read.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, Pipe2PumpStationRead, ident, "Releves de station de pompage")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Releves de corrosion ─────────────────────────────────────────────────

@router.get("/pipe2-corrosion-readings", response_model=List[Pipe2CorrosionReadingOut])
def list_corrosion_reading(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("pipeline.corrosion_reading.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, Pipe2CorrosionReading, cid, {"statut": statut})


@router.post("/pipe2-corrosion-readings", response_model=Pipe2CorrosionReadingOut, status_code=201)
def create_corrosion_reading(
    payload: Pipe2CorrosionReadingCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("pipeline.corrosion_reading.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, Pipe2CorrosionReading, "reference", data.get("reference"), "reference", cid)
    obj = Pipe2CorrosionReading(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/pipe2-corrosion-readings/{ident}", response_model=Pipe2CorrosionReadingOut)
def update_corrosion_reading(
    ident: int,
    payload: Pipe2CorrosionReadingUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("pipeline.corrosion_reading.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, Pipe2CorrosionReading, ident, "Releves de corrosion")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/pipe2-corrosion-readings/{ident}", response_model=Pipe2CorrosionReadingOut)
def delete_corrosion_reading(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("pipeline.corrosion_reading.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, Pipe2CorrosionReading, ident, "Releves de corrosion")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Etalonnages de debitmetre ─────────────────────────────────────────────────

@router.get("/pipe2-flow-calibrations", response_model=List[Pipe2FlowCalibrationOut])
def list_flow_calibration(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("pipeline.flow_calibration.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, Pipe2FlowCalibration, cid, {"statut": statut})


@router.post("/pipe2-flow-calibrations", response_model=Pipe2FlowCalibrationOut, status_code=201)
def create_flow_calibration(
    payload: Pipe2FlowCalibrationCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("pipeline.flow_calibration.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, Pipe2FlowCalibration, "reference", data.get("reference"), "reference", cid)
    obj = Pipe2FlowCalibration(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/pipe2-flow-calibrations/{ident}", response_model=Pipe2FlowCalibrationOut)
def update_flow_calibration(
    ident: int,
    payload: Pipe2FlowCalibrationUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("pipeline.flow_calibration.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, Pipe2FlowCalibration, ident, "Etalonnages de debitmetre")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/pipe2-flow-calibrations/{ident}", response_model=Pipe2FlowCalibrationOut)
def delete_flow_calibration(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("pipeline.flow_calibration.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, Pipe2FlowCalibration, ident, "Etalonnages de debitmetre")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Essais qualite de lot ─────────────────────────────────────────────────

@router.get("/pipe2-batch-quality-tests", response_model=List[Pipe2BatchQualityTestOut])
def list_batch_quality_test(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("pipeline.batch_quality_test.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, Pipe2BatchQualityTest, cid, {"statut": statut})


@router.post("/pipe2-batch-quality-tests", response_model=Pipe2BatchQualityTestOut, status_code=201)
def create_batch_quality_test(
    payload: Pipe2BatchQualityTestCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("pipeline.batch_quality_test.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, Pipe2BatchQualityTest, "reference", data.get("reference"), "reference", cid)
    obj = Pipe2BatchQualityTest(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/pipe2-batch-quality-tests/{ident}", response_model=Pipe2BatchQualityTestOut)
def update_batch_quality_test(
    ident: int,
    payload: Pipe2BatchQualityTestUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("pipeline.batch_quality_test.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, Pipe2BatchQualityTest, ident, "Essais qualite de lot")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/pipe2-batch-quality-tests/{ident}", response_model=Pipe2BatchQualityTestOut)
def delete_batch_quality_test(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("pipeline.batch_quality_test.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, Pipe2BatchQualityTest, ident, "Essais qualite de lot")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Detections d' interface ─────────────────────────────────────────────────

@router.get("/pipe2-interface-detections", response_model=List[Pipe2InterfaceDetectionOut])
def list_interface_detection(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("pipeline.interface_detection.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, Pipe2InterfaceDetection, cid, {"statut": statut})


@router.post("/pipe2-interface-detections", response_model=Pipe2InterfaceDetectionOut, status_code=201)
def create_interface_detection(
    payload: Pipe2InterfaceDetectionCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("pipeline.interface_detection.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, Pipe2InterfaceDetection, "reference", data.get("reference"), "reference", cid)
    obj = Pipe2InterfaceDetection(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/pipe2-interface-detections/{ident}", response_model=Pipe2InterfaceDetectionOut)
def update_interface_detection(
    ident: int,
    payload: Pipe2InterfaceDetectionUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("pipeline.interface_detection.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, Pipe2InterfaceDetection, ident, "Detections d' interface")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/pipe2-interface-detections/{ident}", response_model=Pipe2InterfaceDetectionOut)
def delete_interface_detection(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("pipeline.interface_detection.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, Pipe2InterfaceDetection, ident, "Detections d' interface")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Evaluations d' integrite ─────────────────────────────────────────────────

@router.get("/pipe2-integrity-assessments", response_model=List[Pipe2IntegrityAssessmentOut])
def list_integrity_assessment(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("pipeline.integrity_assessment.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, Pipe2IntegrityAssessment, cid, {"statut": statut})


@router.post("/pipe2-integrity-assessments", response_model=Pipe2IntegrityAssessmentOut, status_code=201)
def create_integrity_assessment(
    payload: Pipe2IntegrityAssessmentCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("pipeline.integrity_assessment.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, Pipe2IntegrityAssessment, "reference", data.get("reference"), "reference", cid)
    obj = Pipe2IntegrityAssessment(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/pipe2-integrity-assessments/{ident}", response_model=Pipe2IntegrityAssessmentOut)
def update_integrity_assessment(
    ident: int,
    payload: Pipe2IntegrityAssessmentUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("pipeline.integrity_assessment.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, Pipe2IntegrityAssessment, ident, "Evaluations d' integrite")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/pipe2-integrity-assessments/{ident}", response_model=Pipe2IntegrityAssessmentOut)
def delete_integrity_assessment(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("pipeline.integrity_assessment.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, Pipe2IntegrityAssessment, ident, "Evaluations d' integrite")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Actions de reponse a deversement ─────────────────────────────────────────────────

@router.get("/pipe2-spill-response-actions", response_model=List[Pipe2SpillResponseActionOut])
def list_spill_response_action(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("pipeline.spill_response_action.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, Pipe2SpillResponseAction, cid, {"statut": statut})


@router.post("/pipe2-spill-response-actions", response_model=Pipe2SpillResponseActionOut, status_code=201)
def create_spill_response_action(
    payload: Pipe2SpillResponseActionCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("pipeline.spill_response_action.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, Pipe2SpillResponseAction, "reference", data.get("reference"), "reference", cid)
    obj = Pipe2SpillResponseAction(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/pipe2-spill-response-actions/{ident}", response_model=Pipe2SpillResponseActionOut)
def update_spill_response_action(
    ident: int,
    payload: Pipe2SpillResponseActionUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("pipeline.spill_response_action.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, Pipe2SpillResponseAction, ident, "Actions de reponse a deversement")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/pipe2-spill-response-actions/{ident}", response_model=Pipe2SpillResponseActionOut)
def delete_spill_response_action(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("pipeline.spill_response_action.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, Pipe2SpillResponseAction, ident, "Actions de reponse a deversement")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj

