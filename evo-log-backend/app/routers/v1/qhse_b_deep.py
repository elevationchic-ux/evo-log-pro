"""Routeur CRUD genere pour qhse-securite (expansion)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List

from app.core.database import get_db
from app.core.permissions import require_perm
from app.models.user import User
from app.models.qhse_b_deep import (
    QhseNearMiss,
    QhseCalibration,
    QhseWasteManifest,
    QhseTrainingRecord,
    QhseWorkPermit,
)
from app.schemas.qhse_b_deep import (
    QhseNearMissCreate, QhseNearMissUpdate, QhseNearMissOut,
    QhseCalibrationCreate, QhseCalibrationUpdate, QhseCalibrationOut,
    QhseWasteManifestCreate, QhseWasteManifestUpdate, QhseWasteManifestOut,
    QhseTrainingRecordCreate, QhseTrainingRecordUpdate, QhseTrainingRecordOut,
    QhseWorkPermitCreate, QhseWorkPermitUpdate, QhseWorkPermitOut,
)

router = APIRouter(tags=["qhse-securite (expansion)"])


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

@router.get("/nomenclatures", summary="Vocabulaire metier qhse-securite")
def nomenclatures(user: User = Depends(require_perm("qhse.nomenclature.read"))):
    from app.models import qhse_b_deep as _md
    import enum as _pyenum
    out = {}
    for name in dir(_md):
        obj = getattr(_md, name)
        if isinstance(obj, type) and issubclass(obj, _pyenum.Enum) and obj is not _pyenum.Enum:
            out[name.lower()] = [{"code": m.name, "valeur": m.value} for m in obj]
    return out


# ─── Quasi-accidents (situations dangereuses) ─────────────────────────────────────────────────

@router.get("/qhseb-near-misses", response_model=List[QhseNearMissOut])
def list_near_miss(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.near_miss.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, QhseNearMiss, cid, {"statut": statut})


@router.post("/qhseb-near-misses", response_model=QhseNearMissOut, status_code=201)
def create_near_miss(
    payload: QhseNearMissCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.near_miss.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, QhseNearMiss, "reference", data.get("reference"), "reference", cid)
    obj = QhseNearMiss(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/qhseb-near-misses/{ident}", response_model=QhseNearMissOut)
def update_near_miss(
    ident: int,
    payload: QhseNearMissUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.near_miss.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, QhseNearMiss, ident, "Quasi-accidents (situations dangereuses)")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/qhseb-near-misses/{ident}", response_model=QhseNearMissOut)
def delete_near_miss(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.near_miss.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, QhseNearMiss, ident, "Quasi-accidents (situations dangereuses)")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Etalonnage instruments de mesure ─────────────────────────────────────────────────

@router.get("/qhseb-calibrations", response_model=List[QhseCalibrationOut])
def list_calibration(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.calibration.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, QhseCalibration, cid, {"statut": statut})


@router.post("/qhseb-calibrations", response_model=QhseCalibrationOut, status_code=201)
def create_calibration(
    payload: QhseCalibrationCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.calibration.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, QhseCalibration, "numero_instrument", data.get("numero_instrument"), "numero_instrument", cid)
    obj = QhseCalibration(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/qhseb-calibrations/{ident}", response_model=QhseCalibrationOut)
def update_calibration(
    ident: int,
    payload: QhseCalibrationUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.calibration.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, QhseCalibration, ident, "Etalonnage instruments de mesure")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/qhseb-calibrations/{ident}", response_model=QhseCalibrationOut)
def delete_calibration(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.calibration.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, QhseCalibration, ident, "Etalonnage instruments de mesure")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Bordereaux de suivi des dechets (BSD) ─────────────────────────────────────────────────

@router.get("/qhseb-waste-manifests", response_model=List[QhseWasteManifestOut])
def list_waste_manifest(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.waste_manifest.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, QhseWasteManifest, cid, {"statut": statut})


@router.post("/qhseb-waste-manifests", response_model=QhseWasteManifestOut, status_code=201)
def create_waste_manifest(
    payload: QhseWasteManifestCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.waste_manifest.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, QhseWasteManifest, "numero_bsd", data.get("numero_bsd"), "numero_bsd", cid)
    obj = QhseWasteManifest(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/qhseb-waste-manifests/{ident}", response_model=QhseWasteManifestOut)
def update_waste_manifest(
    ident: int,
    payload: QhseWasteManifestUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.waste_manifest.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, QhseWasteManifest, ident, "Bordereaux de suivi des dechets (BSD)")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/qhseb-waste-manifests/{ident}", response_model=QhseWasteManifestOut)
def delete_waste_manifest(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.waste_manifest.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, QhseWasteManifest, ident, "Bordereaux de suivi des dechets (BSD)")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Habilitations et formations securite ─────────────────────────────────────────────────

@router.get("/qhseb-training-records", response_model=List[QhseTrainingRecordOut])
def list_training_record(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.training_record.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, QhseTrainingRecord, cid, {"statut": statut})


@router.post("/qhseb-training-records", response_model=QhseTrainingRecordOut, status_code=201)
def create_training_record(
    payload: QhseTrainingRecordCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.training_record.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, QhseTrainingRecord, "reference", data.get("reference"), "reference", cid)
    obj = QhseTrainingRecord(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/qhseb-training-records/{ident}", response_model=QhseTrainingRecordOut)
def update_training_record(
    ident: int,
    payload: QhseTrainingRecordUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.training_record.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, QhseTrainingRecord, ident, "Habilitations et formations securite")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/qhseb-training-records/{ident}", response_model=QhseTrainingRecordOut)
def delete_training_record(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.training_record.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, QhseTrainingRecord, ident, "Habilitations et formations securite")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Permis de travail (PTW) ─────────────────────────────────────────────────

@router.get("/qhseb-work-permits", response_model=List[QhseWorkPermitOut])
def list_work_permit(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.work_permit.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, QhseWorkPermit, cid, {"statut": statut})


@router.post("/qhseb-work-permits", response_model=QhseWorkPermitOut, status_code=201)
def create_work_permit(
    payload: QhseWorkPermitCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.work_permit.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, QhseWorkPermit, "numero_ptw", data.get("numero_ptw"), "numero_ptw", cid)
    obj = QhseWorkPermit(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/qhseb-work-permits/{ident}", response_model=QhseWorkPermitOut)
def update_work_permit(
    ident: int,
    payload: QhseWorkPermitUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.work_permit.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, QhseWorkPermit, ident, "Permis de travail (PTW)")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/qhseb-work-permits/{ident}", response_model=QhseWorkPermitOut)
def delete_work_permit(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.work_permit.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, QhseWorkPermit, ident, "Permis de travail (PTW)")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj

