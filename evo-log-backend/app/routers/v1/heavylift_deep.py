"""Routeur CRUD genere pour convoi-exceptionnel (expansion wave 5)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List

from app.core.database import get_db
from app.core.permissions import require_perm
from app.models.user import User
from app.models.heavylift_deep import (
    HeavyLiftProject,
    HeavyLiftCrane,
    HeavyLiftModularTrailer,
    HeavyLiftRouteSurvey,
    HeavyLiftLiftPlan,
    HeavyLiftPermit,
    HeavyLiftEscort,
    HeavyLiftLashing,
    HeavyLiftBallast,
    HeavyLiftRiggingMethod,
)
from app.schemas.heavylift_deep import (
    HeavyLiftProjectCreate, HeavyLiftProjectUpdate, HeavyLiftProjectOut,
    HeavyLiftCraneCreate, HeavyLiftCraneUpdate, HeavyLiftCraneOut,
    HeavyLiftModularTrailerCreate, HeavyLiftModularTrailerUpdate, HeavyLiftModularTrailerOut,
    HeavyLiftRouteSurveyCreate, HeavyLiftRouteSurveyUpdate, HeavyLiftRouteSurveyOut,
    HeavyLiftLiftPlanCreate, HeavyLiftLiftPlanUpdate, HeavyLiftLiftPlanOut,
    HeavyLiftPermitCreate, HeavyLiftPermitUpdate, HeavyLiftPermitOut,
    HeavyLiftEscortCreate, HeavyLiftEscortUpdate, HeavyLiftEscortOut,
    HeavyLiftLashingCreate, HeavyLiftLashingUpdate, HeavyLiftLashingOut,
    HeavyLiftBallastCreate, HeavyLiftBallastUpdate, HeavyLiftBallastOut,
    HeavyLiftRiggingMethodCreate, HeavyLiftRiggingMethodUpdate, HeavyLiftRiggingMethodOut,
)

router = APIRouter(tags=["convoi-exceptionnel (expansion)"])


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

@router.get("/nomenclatures", summary=f"Vocabulaire metier {tag_label}")
def nomenclatures(user: User = Depends(require_perm("heavylift.nomenclature.read"))):
    from app.models import heavylift_deep as _md
    import enum as _pyenum
    out = {}
    for name in dir(_md):
        obj = getattr(_md, name)
        if isinstance(obj, type) and issubclass(obj, _pyenum.Enum) and obj is not _pyenum.Enum:
            out[name.lower()] = [{"code": m.name, "valeur": m.value} for m in obj]
    return out


# ─── Projet heavy-lift ─────────────────────────────────────────────

@router.get("/projects", response_model=List[HeavyLiftProjectOut])
def list_projects(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("heavylift.projects.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, HeavyLiftProject, cid, {'statut': statut})


@router.post("/projects", response_model=HeavyLiftProjectOut, status_code=201)
def create_projects(
    payload: HeavyLiftProjectCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("heavylift.projects.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, HeavyLiftProject, "code_projet", data.get("code_projet"), "code_projet", cid)
    obj = HeavyLiftProject(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/projects/{ident}", response_model=HeavyLiftProjectOut)
def update_projects(
    ident: int,
    payload: HeavyLiftProjectUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("heavylift.projects.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, HeavyLiftProject, ident, "Projet heavy-lift")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/projects/{ident}", response_model=HeavyLiftProjectOut)
def delete_projects(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("heavylift.projects.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, HeavyLiftProject, ident, "Projet heavy-lift")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Grue ─────────────────────────────────────────────

@router.get("/cranes", response_model=List[HeavyLiftCraneOut])
def list_cranes(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("heavylift.cranes.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, HeavyLiftCrane, cid, {'statut': statut})


@router.post("/cranes", response_model=HeavyLiftCraneOut, status_code=201)
def create_cranes(
    payload: HeavyLiftCraneCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("heavylift.cranes.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, HeavyLiftCrane, "numero_grue", data.get("numero_grue"), "numero_grue", cid)
    obj = HeavyLiftCrane(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/cranes/{ident}", response_model=HeavyLiftCraneOut)
def update_cranes(
    ident: int,
    payload: HeavyLiftCraneUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("heavylift.cranes.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, HeavyLiftCrane, ident, "Grue")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/cranes/{ident}", response_model=HeavyLiftCraneOut)
def delete_cranes(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("heavylift.cranes.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, HeavyLiftCrane, ident, "Grue")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Remorque modulaire ─────────────────────────────────────────────

@router.get("/modular-trailers", response_model=List[HeavyLiftModularTrailerOut])
def list_modular_trailers(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("heavylift.modular_trailers.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, HeavyLiftModularTrailer, cid, {'statut': statut})


@router.post("/modular-trailers", response_model=HeavyLiftModularTrailerOut, status_code=201)
def create_modular_trailers(
    payload: HeavyLiftModularTrailerCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("heavylift.modular_trailers.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, HeavyLiftModularTrailer, "plaque", data.get("plaque"), "plaque", cid)
    obj = HeavyLiftModularTrailer(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/modular-trailers/{ident}", response_model=HeavyLiftModularTrailerOut)
def update_modular_trailers(
    ident: int,
    payload: HeavyLiftModularTrailerUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("heavylift.modular_trailers.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, HeavyLiftModularTrailer, ident, "Remorque modulaire")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/modular-trailers/{ident}", response_model=HeavyLiftModularTrailerOut)
def delete_modular_trailers(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("heavylift.modular_trailers.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, HeavyLiftModularTrailer, ident, "Remorque modulaire")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Etude itineraire ─────────────────────────────────────────────

@router.get("/route-surveys", response_model=List[HeavyLiftRouteSurveyOut])
def list_route_surveys(db: Session = Depends(get_db),
    user: User = Depends(require_perm("heavylift.route_surveys.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, HeavyLiftRouteSurvey, cid)


@router.post("/route-surveys", response_model=HeavyLiftRouteSurveyOut, status_code=201)
def create_route_surveys(
    payload: HeavyLiftRouteSurveyCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("heavylift.route_surveys.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, HeavyLiftRouteSurvey, "reference", data.get("reference"), "reference", cid)
    obj = HeavyLiftRouteSurvey(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/route-surveys/{ident}", response_model=HeavyLiftRouteSurveyOut)
def update_route_surveys(
    ident: int,
    payload: HeavyLiftRouteSurveyUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("heavylift.route_surveys.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, HeavyLiftRouteSurvey, ident, "Etude itineraire")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/route-surveys/{ident}", response_model=HeavyLiftRouteSurveyOut)
def delete_route_surveys(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("heavylift.route_surveys.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, HeavyLiftRouteSurvey, ident, "Etude itineraire")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Plan de levage ─────────────────────────────────────────────

@router.get("/lift-plans", response_model=List[HeavyLiftLiftPlanOut])
def list_lift_plans(db: Session = Depends(get_db),
    user: User = Depends(require_perm("heavylift.lift_plans.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, HeavyLiftLiftPlan, cid)


@router.post("/lift-plans", response_model=HeavyLiftLiftPlanOut, status_code=201)
def create_lift_plans(
    payload: HeavyLiftLiftPlanCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("heavylift.lift_plans.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, HeavyLiftLiftPlan, "reference", data.get("reference"), "reference", cid)
    obj = HeavyLiftLiftPlan(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/lift-plans/{ident}", response_model=HeavyLiftLiftPlanOut)
def update_lift_plans(
    ident: int,
    payload: HeavyLiftLiftPlanUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("heavylift.lift_plans.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, HeavyLiftLiftPlan, ident, "Plan de levage")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/lift-plans/{ident}", response_model=HeavyLiftLiftPlanOut)
def delete_lift_plans(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("heavylift.lift_plans.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, HeavyLiftLiftPlan, ident, "Plan de levage")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Permis ─────────────────────────────────────────────

@router.get("/permits", response_model=List[HeavyLiftPermitOut])
def list_permits(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("heavylift.permits.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, HeavyLiftPermit, cid, {'statut': statut})


@router.post("/permits", response_model=HeavyLiftPermitOut, status_code=201)
def create_permits(
    payload: HeavyLiftPermitCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("heavylift.permits.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, HeavyLiftPermit, "numero_permis", data.get("numero_permis"), "numero_permis", cid)
    obj = HeavyLiftPermit(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/permits/{ident}", response_model=HeavyLiftPermitOut)
def update_permits(
    ident: int,
    payload: HeavyLiftPermitUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("heavylift.permits.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, HeavyLiftPermit, ident, "Permis")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/permits/{ident}", response_model=HeavyLiftPermitOut)
def delete_permits(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("heavylift.permits.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, HeavyLiftPermit, ident, "Permis")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Escorte ─────────────────────────────────────────────

@router.get("/escorts", response_model=List[HeavyLiftEscortOut])
def list_escorts(db: Session = Depends(get_db),
    user: User = Depends(require_perm("heavylift.escorts.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, HeavyLiftEscort, cid)


@router.post("/escorts", response_model=HeavyLiftEscortOut, status_code=201)
def create_escorts(
    payload: HeavyLiftEscortCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("heavylift.escorts.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, HeavyLiftEscort, "reference", data.get("reference"), "reference", cid)
    obj = HeavyLiftEscort(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/escorts/{ident}", response_model=HeavyLiftEscortOut)
def update_escorts(
    ident: int,
    payload: HeavyLiftEscortUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("heavylift.escorts.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, HeavyLiftEscort, ident, "Escorte")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/escorts/{ident}", response_model=HeavyLiftEscortOut)
def delete_escorts(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("heavylift.escorts.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, HeavyLiftEscort, ident, "Escorte")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Amarrage ─────────────────────────────────────────────

@router.get("/lashings", response_model=List[HeavyLiftLashingOut])
def list_lashings(db: Session = Depends(get_db),
    user: User = Depends(require_perm("heavylift.lashings.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, HeavyLiftLashing, cid)


@router.post("/lashings", response_model=HeavyLiftLashingOut, status_code=201)
def create_lashings(
    payload: HeavyLiftLashingCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("heavylift.lashings.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, HeavyLiftLashing, "reference", data.get("reference"), "reference", cid)
    obj = HeavyLiftLashing(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/lashings/{ident}", response_model=HeavyLiftLashingOut)
def update_lashings(
    ident: int,
    payload: HeavyLiftLashingUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("heavylift.lashings.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, HeavyLiftLashing, ident, "Amarrage")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/lashings/{ident}", response_model=HeavyLiftLashingOut)
def delete_lashings(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("heavylift.lashings.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, HeavyLiftLashing, ident, "Amarrage")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Ballast ─────────────────────────────────────────────

@router.get("/ballasts", response_model=List[HeavyLiftBallastOut])
def list_ballasts(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("heavylift.ballasts.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, HeavyLiftBallast, cid, {'statut': statut})


@router.post("/ballasts", response_model=HeavyLiftBallastOut, status_code=201)
def create_ballasts(
    payload: HeavyLiftBallastCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("heavylift.ballasts.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, HeavyLiftBallast, "code_ballast", data.get("code_ballast"), "code_ballast", cid)
    obj = HeavyLiftBallast(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/ballasts/{ident}", response_model=HeavyLiftBallastOut)
def update_ballasts(
    ident: int,
    payload: HeavyLiftBallastUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("heavylift.ballasts.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, HeavyLiftBallast, ident, "Ballast")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/ballasts/{ident}", response_model=HeavyLiftBallastOut)
def delete_ballasts(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("heavylift.ballasts.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, HeavyLiftBallast, ident, "Ballast")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Methode de greage ─────────────────────────────────────────────

@router.get("/rigging-methods", response_model=List[HeavyLiftRiggingMethodOut])
def list_rigging_methods(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("heavylift.rigging_methods.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, HeavyLiftRiggingMethod, cid, {'statut': statut})


@router.post("/rigging-methods", response_model=HeavyLiftRiggingMethodOut, status_code=201)
def create_rigging_methods(
    payload: HeavyLiftRiggingMethodCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("heavylift.rigging_methods.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, HeavyLiftRiggingMethod, "code_methode", data.get("code_methode"), "code_methode", cid)
    obj = HeavyLiftRiggingMethod(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/rigging-methods/{ident}", response_model=HeavyLiftRiggingMethodOut)
def update_rigging_methods(
    ident: int,
    payload: HeavyLiftRiggingMethodUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("heavylift.rigging_methods.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, HeavyLiftRiggingMethod, ident, "Methode de greage")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/rigging-methods/{ident}", response_model=HeavyLiftRiggingMethodOut)
def delete_rigging_methods(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("heavylift.rigging_methods.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, HeavyLiftRiggingMethod, ident, "Methode de greage")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj

