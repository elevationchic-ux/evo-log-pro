"""Routeur CRUD genere pour departement (expansion)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List

from app.core.database import get_db
from app.core.permissions import require_perm
from app.models.user import User
from app.models.departement_d5_deep import (
    DepObjective,
    DepServiceMeeting,
    DepProject,
    DepServiceRequest,
)
from app.schemas.departement_d5_deep import (
    DepObjectiveCreate, DepObjectiveUpdate, DepObjectiveOut,
    DepServiceMeetingCreate, DepServiceMeetingUpdate, DepServiceMeetingOut,
    DepProjectCreate, DepProjectUpdate, DepProjectOut,
    DepServiceRequestCreate, DepServiceRequestUpdate, DepServiceRequestOut,
)

router = APIRouter(tags=["departement (expansion)"])


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

@router.get("/nomenclatures", summary="Vocabulaire metier departement")
def nomenclatures(user: User = Depends(require_perm("departments.nomenclature.read"))):
    from app.models import departement_d5_deep as _md
    import enum as _pyenum
    out = {}
    for name in dir(_md):
        obj = getattr(_md, name)
        if isinstance(obj, type) and issubclass(obj, _pyenum.Enum) and obj is not _pyenum.Enum:
            out[name.lower()] = [{"code": m.name, "valeur": m.value} for m in obj]
    return out


# ─── Objectifs de service ─────────────────────────────────────────────────

@router.get("/dep-objectives", response_model=List[DepObjectiveOut])
def list_objective(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("departments.objective.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, DepObjective, cid, {"statut": statut})


@router.post("/dep-objectives", response_model=DepObjectiveOut, status_code=201)
def create_objective(
    payload: DepObjectiveCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("departments.objective.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, DepObjective, "reference", data.get("reference"), "reference", cid)
    obj = DepObjective(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/dep-objectives/{ident}", response_model=DepObjectiveOut)
def update_objective(
    ident: int,
    payload: DepObjectiveUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("departments.objective.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, DepObjective, ident, "Objectifs de service")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/dep-objectives/{ident}", response_model=DepObjectiveOut)
def delete_objective(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("departments.objective.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, DepObjective, ident, "Objectifs de service")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Reunions de service ─────────────────────────────────────────────────

@router.get("/dep-service-meetings", response_model=List[DepServiceMeetingOut])
def list_service_meeting(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("departments.service_meeting.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, DepServiceMeeting, cid, {"statut": statut})


@router.post("/dep-service-meetings", response_model=DepServiceMeetingOut, status_code=201)
def create_service_meeting(
    payload: DepServiceMeetingCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("departments.service_meeting.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, DepServiceMeeting, "reference", data.get("reference"), "reference", cid)
    obj = DepServiceMeeting(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/dep-service-meetings/{ident}", response_model=DepServiceMeetingOut)
def update_service_meeting(
    ident: int,
    payload: DepServiceMeetingUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("departments.service_meeting.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, DepServiceMeeting, ident, "Reunions de service")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/dep-service-meetings/{ident}", response_model=DepServiceMeetingOut)
def delete_service_meeting(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("departments.service_meeting.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, DepServiceMeeting, ident, "Reunions de service")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Projets internes du service ─────────────────────────────────────────────────

@router.get("/dep-projects", response_model=List[DepProjectOut])
def list_project(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("departments.project.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, DepProject, cid, {"statut": statut})


@router.post("/dep-projects", response_model=DepProjectOut, status_code=201)
def create_project(
    payload: DepProjectCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("departments.project.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, DepProject, "reference", data.get("reference"), "reference", cid)
    obj = DepProject(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/dep-projects/{ident}", response_model=DepProjectOut)
def update_project(
    ident: int,
    payload: DepProjectUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("departments.project.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, DepProject, ident, "Projets internes du service")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/dep-projects/{ident}", response_model=DepProjectOut)
def delete_project(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("departments.project.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, DepProject, ident, "Projets internes du service")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Demandes inter-services ─────────────────────────────────────────────────

@router.get("/dep-service-requests", response_model=List[DepServiceRequestOut])
def list_service_request(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("departments.service_request.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, DepServiceRequest, cid, {"statut": statut})


@router.post("/dep-service-requests", response_model=DepServiceRequestOut, status_code=201)
def create_service_request(
    payload: DepServiceRequestCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("departments.service_request.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, DepServiceRequest, "reference", data.get("reference"), "reference", cid)
    obj = DepServiceRequest(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/dep-service-requests/{ident}", response_model=DepServiceRequestOut)
def update_service_request(
    ident: int,
    payload: DepServiceRequestUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("departments.service_request.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, DepServiceRequest, ident, "Demandes inter-services")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/dep-service-requests/{ident}", response_model=DepServiceRequestOut)
def delete_service_request(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("departments.service_request.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, DepServiceRequest, ident, "Demandes inter-services")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj

