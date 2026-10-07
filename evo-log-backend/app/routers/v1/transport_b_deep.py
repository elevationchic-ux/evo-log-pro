"""Routeur CRUD genere pour transport-flotte (expansion)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List

from app.core.database import get_db
from app.core.permissions import require_perm
from app.models.user import User
from app.models.transport_b_deep import (
    TransportbDispatch,
    TransportbPod,
)
from app.schemas.transport_b_deep import (
    TransportbDispatchCreate, TransportbDispatchUpdate, TransportbDispatchOut,
    TransportbPodCreate, TransportbPodUpdate, TransportbPodOut,
)

router = APIRouter(tags=["transport-flotte (expansion)"])


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

@router.get("/nomenclatures", summary="Vocabulaire metier transport-flotte")
def nomenclatures(user: User = Depends(require_perm("transport.nomenclature.read"))):
    from app.models import transport_b_deep as _md
    import enum as _pyenum
    out = {}
    for name in dir(_md):
        obj = getattr(_md, name)
        if isinstance(obj, type) and issubclass(obj, _pyenum.Enum) and obj is not _pyenum.Enum:
            out[name.lower()] = [{"code": m.name, "valeur": m.value} for m in obj]
    return out


# ─── Bons de mission / affectation ─────────────────────────────────────────────────

@router.get("/transportb-dispatches", response_model=List[TransportbDispatchOut])
def list_dispatch(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.dispatch.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, TransportbDispatch, cid, {"statut": statut})


@router.post("/transportb-dispatches", response_model=TransportbDispatchOut, status_code=201)
def create_dispatch(
    payload: TransportbDispatchCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.dispatch.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, TransportbDispatch, "reference", data.get("reference"), "reference", cid)
    obj = TransportbDispatch(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/transportb-dispatches/{ident}", response_model=TransportbDispatchOut)
def update_dispatch(
    ident: int,
    payload: TransportbDispatchUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.dispatch.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TransportbDispatch, ident, "Bons de mission / affectation")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/transportb-dispatches/{ident}", response_model=TransportbDispatchOut)
def delete_dispatch(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.dispatch.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TransportbDispatch, ident, "Bons de mission / affectation")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Preuves de livraison (POD) ─────────────────────────────────────────────────

@router.get("/transportb-proof-delivery", response_model=List[TransportbPodOut])
def list_pod(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.pod.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, TransportbPod, cid, {"statut": statut})


@router.post("/transportb-proof-delivery", response_model=TransportbPodOut, status_code=201)
def create_pod(
    payload: TransportbPodCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.pod.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, TransportbPod, "reference", data.get("reference"), "reference", cid)
    obj = TransportbPod(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/transportb-proof-delivery/{ident}", response_model=TransportbPodOut)
def update_pod(
    ident: int,
    payload: TransportbPodUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.pod.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TransportbPod, ident, "Preuves de livraison (POD)")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/transportb-proof-delivery/{ident}", response_model=TransportbPodOut)
def delete_pod(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.pod.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TransportbPod, ident, "Preuves de livraison (POD)")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj

