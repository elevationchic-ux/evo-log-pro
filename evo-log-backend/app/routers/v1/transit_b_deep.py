"""Routeur CRUD genere pour transit-douane (expansion)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List

from app.core.database import get_db
from app.core.permissions import require_perm
from app.models.user import User
from app.models.transit_b_deep import (
    TransitbIncoterm,
    TransitbInspectionRecord,
)
from app.schemas.transit_b_deep import (
    TransitbIncotermCreate, TransitbIncotermUpdate, TransitbIncotermOut,
    TransitbInspectionRecordCreate, TransitbInspectionRecordUpdate, TransitbInspectionRecordOut,
)

router = APIRouter(tags=["transit-douane (expansion)"])


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

@router.get("/nomenclatures", summary="Vocabulaire metier transit-douane")
def nomenclatures(user: User = Depends(require_perm("transit.nomenclature.read"))):
    from app.models import transit_b_deep as _md
    import enum as _pyenum
    out = {}
    for name in dir(_md):
        obj = getattr(_md, name)
        if isinstance(obj, type) and issubclass(obj, _pyenum.Enum) and obj is not _pyenum.Enum:
            out[name.lower()] = [{"code": m.name, "valeur": m.value} for m in obj]
    return out


# ─── Incoterms applicables ─────────────────────────────────────────────────

@router.get("/transitb-incoterms", response_model=List[TransitbIncotermOut])
def list_incoterm_term(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.incoterm_term.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, TransitbIncoterm, cid, {"statut": statut})


@router.post("/transitb-incoterms", response_model=TransitbIncotermOut, status_code=201)
def create_incoterm_term(
    payload: TransitbIncotermCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.incoterm_term.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, TransitbIncoterm, "code", data.get("code"), "code", cid)
    obj = TransitbIncoterm(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/transitb-incoterms/{ident}", response_model=TransitbIncotermOut)
def update_incoterm_term(
    ident: int,
    payload: TransitbIncotermUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.incoterm_term.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TransitbIncoterm, ident, "Incoterms applicables")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/transitb-incoterms/{ident}", response_model=TransitbIncotermOut)
def delete_incoterm_term(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.incoterm_term.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TransitbIncoterm, ident, "Incoterms applicables")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Proces-verbaux de visite douaniere ─────────────────────────────────────────────────

@router.get("/transitb-customs-inspections", response_model=List[TransitbInspectionRecordOut])
def list_inspection_record(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.inspection_record.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, TransitbInspectionRecord, cid, {"statut": statut})


@router.post("/transitb-customs-inspections", response_model=TransitbInspectionRecordOut, status_code=201)
def create_inspection_record(
    payload: TransitbInspectionRecordCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.inspection_record.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, TransitbInspectionRecord, "reference", data.get("reference"), "reference", cid)
    obj = TransitbInspectionRecord(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/transitb-customs-inspections/{ident}", response_model=TransitbInspectionRecordOut)
def update_inspection_record(
    ident: int,
    payload: TransitbInspectionRecordUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.inspection_record.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TransitbInspectionRecord, ident, "Proces-verbaux de visite douaniere")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/transitb-customs-inspections/{ident}", response_model=TransitbInspectionRecordOut)
def delete_inspection_record(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.inspection_record.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TransitbInspectionRecord, ident, "Proces-verbaux de visite douaniere")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj

