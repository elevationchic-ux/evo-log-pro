"""Routeur CRUD genere pour rh-personnel (expansion)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List

from app.core.database import get_db
from app.core.permissions import require_perm
from app.models.user import User
from app.models.rh_c_deep import (
    RhCTrainingPlan,
    RhCDisciplinaryRecord,
)
from app.schemas.rh_c_deep import (
    RhCTrainingPlanCreate, RhCTrainingPlanUpdate, RhCTrainingPlanOut,
    RhCDisciplinaryRecordCreate, RhCDisciplinaryRecordUpdate, RhCDisciplinaryRecordOut,
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
    from app.models import rh_c_deep as _md
    import enum as _pyenum
    out = {}
    for name in dir(_md):
        obj = getattr(_md, name)
        if isinstance(obj, type) and issubclass(obj, _pyenum.Enum) and obj is not _pyenum.Enum:
            out[name.lower()] = [{"code": m.name, "valeur": m.value} for m in obj]
    return out


# ─── Plans de formation ─────────────────────────────────────────────────

@router.get("/rhc-training-plans", response_model=List[RhCTrainingPlanOut])
def list_training_plan(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.training_plan.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, RhCTrainingPlan, cid, {"statut": statut})


@router.post("/rhc-training-plans", response_model=RhCTrainingPlanOut, status_code=201)
def create_training_plan(
    payload: RhCTrainingPlanCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.training_plan.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, RhCTrainingPlan, "reference", data.get("reference"), "reference", cid)
    obj = RhCTrainingPlan(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/rhc-training-plans/{ident}", response_model=RhCTrainingPlanOut)
def update_training_plan(
    ident: int,
    payload: RhCTrainingPlanUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.training_plan.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, RhCTrainingPlan, ident, "Plans de formation")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/rhc-training-plans/{ident}", response_model=RhCTrainingPlanOut)
def delete_training_plan(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.training_plan.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, RhCTrainingPlan, ident, "Plans de formation")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Registre disciplinaire ─────────────────────────────────────────────────

@router.get("/rhc-disciplinary-records", response_model=List[RhCDisciplinaryRecordOut])
def list_disciplinary_record(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.disciplinary_record.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, RhCDisciplinaryRecord, cid, {"statut": statut})


@router.post("/rhc-disciplinary-records", response_model=RhCDisciplinaryRecordOut, status_code=201)
def create_disciplinary_record(
    payload: RhCDisciplinaryRecordCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.disciplinary_record.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, RhCDisciplinaryRecord, "reference", data.get("reference"), "reference", cid)
    obj = RhCDisciplinaryRecord(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/rhc-disciplinary-records/{ident}", response_model=RhCDisciplinaryRecordOut)
def update_disciplinary_record(
    ident: int,
    payload: RhCDisciplinaryRecordUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.disciplinary_record.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, RhCDisciplinaryRecord, ident, "Registre disciplinaire")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/rhc-disciplinary-records/{ident}", response_model=RhCDisciplinaryRecordOut)
def delete_disciplinary_record(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("rh.disciplinary_record.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, RhCDisciplinaryRecord, ident, "Registre disciplinaire")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj

