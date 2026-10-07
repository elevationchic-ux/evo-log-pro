"""Routeur CRUD genere pour portail-commercial (expansion)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List

from app.core.database import get_db
from app.core.permissions import require_perm
from app.models.user import User
from app.models.commercial_d2_deep import (
    CommCompetitorNote,
)
from app.schemas.commercial_d2_deep import (
    CommCompetitorNoteCreate, CommCompetitorNoteUpdate, CommCompetitorNoteOut,
)

router = APIRouter(tags=["portail-commercial (expansion)"])


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

@router.get("/nomenclatures", summary="Vocabulaire metier portail-commercial")
def nomenclatures(user: User = Depends(require_perm("b2b.nomenclature.read"))):
    from app.models import commercial_d2_deep as _md
    import enum as _pyenum
    out = {}
    for name in dir(_md):
        obj = getattr(_md, name)
        if isinstance(obj, type) and issubclass(obj, _pyenum.Enum) and obj is not _pyenum.Enum:
            out[name.lower()] = [{"code": m.name, "valeur": m.value} for m in obj]
    return out


# ─── Notes de veille concurrence ─────────────────────────────────────────────────

@router.get("/comm-competitor-notes", response_model=List[CommCompetitorNoteOut])
def list_competitor_note(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.competitor_note.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, CommCompetitorNote, cid, {"statut": statut})


@router.post("/comm-competitor-notes", response_model=CommCompetitorNoteOut, status_code=201)
def create_competitor_note(
    payload: CommCompetitorNoteCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.competitor_note.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, CommCompetitorNote, "reference", data.get("reference"), "reference", cid)
    obj = CommCompetitorNote(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/comm-competitor-notes/{ident}", response_model=CommCompetitorNoteOut)
def update_competitor_note(
    ident: int,
    payload: CommCompetitorNoteUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.competitor_note.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CommCompetitorNote, ident, "Notes de veille concurrence")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/comm-competitor-notes/{ident}", response_model=CommCompetitorNoteOut)
def delete_competitor_note(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.competitor_note.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CommCompetitorNote, ident, "Notes de veille concurrence")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj

