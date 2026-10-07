"""Routeur CRUD genere pour amenagement-portuaire (expansion)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List

from app.core.database import get_db
from app.core.permissions import require_perm
from app.models.user import User
from app.models.amenagement_b_deep import (
    AmgtbDredgingProject,
    AmgtbConcessionPlot,
)
from app.schemas.amenagement_b_deep import (
    AmgtbDredgingProjectCreate, AmgtbDredgingProjectUpdate, AmgtbDredgingProjectOut,
    AmgtbConcessionPlotCreate, AmgtbConcessionPlotUpdate, AmgtbConcessionPlotOut,
)

router = APIRouter(tags=["amenagement-portuaire (expansion)"])


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

@router.get("/nomenclatures", summary="Vocabulaire metier amenagement-portuaire")
def nomenclatures(user: User = Depends(require_perm("amenagement.nomenclature.read"))):
    from app.models import amenagement_b_deep as _md
    import enum as _pyenum
    out = {}
    for name in dir(_md):
        obj = getattr(_md, name)
        if isinstance(obj, type) and issubclass(obj, _pyenum.Enum) and obj is not _pyenum.Enum:
            out[name.lower()] = [{"code": m.name, "valeur": m.value} for m in obj]
    return out


# ─── Projets de dragage ─────────────────────────────────────────────────

@router.get("/amgtb-dredging-projects", response_model=List[AmgtbDredgingProjectOut])
def list_dredging_project(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("amenagement.dredging_project.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, AmgtbDredgingProject, cid, {"statut": statut})


@router.post("/amgtb-dredging-projects", response_model=AmgtbDredgingProjectOut, status_code=201)
def create_dredging_project(
    payload: AmgtbDredgingProjectCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("amenagement.dredging_project.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, AmgtbDredgingProject, "reference", data.get("reference"), "reference", cid)
    obj = AmgtbDredgingProject(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/amgtb-dredging-projects/{ident}", response_model=AmgtbDredgingProjectOut)
def update_dredging_project(
    ident: int,
    payload: AmgtbDredgingProjectUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("amenagement.dredging_project.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, AmgtbDredgingProject, ident, "Projets de dragage")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/amgtb-dredging-projects/{ident}", response_model=AmgtbDredgingProjectOut)
def delete_dredging_project(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("amenagement.dredging_project.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, AmgtbDredgingProject, ident, "Projets de dragage")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Parcelles sous concession ─────────────────────────────────────────────────

@router.get("/amgtb-concession-plots", response_model=List[AmgtbConcessionPlotOut])
def list_concession_plot(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("amenagement.concession_plot.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, AmgtbConcessionPlot, cid, {"statut": statut})


@router.post("/amgtb-concession-plots", response_model=AmgtbConcessionPlotOut, status_code=201)
def create_concession_plot(
    payload: AmgtbConcessionPlotCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("amenagement.concession_plot.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, AmgtbConcessionPlot, "reference", data.get("reference"), "reference", cid)
    obj = AmgtbConcessionPlot(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/amgtb-concession-plots/{ident}", response_model=AmgtbConcessionPlotOut)
def update_concession_plot(
    ident: int,
    payload: AmgtbConcessionPlotUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("amenagement.concession_plot.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, AmgtbConcessionPlot, ident, "Parcelles sous concession")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/amgtb-concession-plots/{ident}", response_model=AmgtbConcessionPlotOut)
def delete_concession_plot(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("amenagement.concession_plot.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, AmgtbConcessionPlot, ident, "Parcelles sous concession")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj

