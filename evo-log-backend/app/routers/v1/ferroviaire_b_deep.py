"""Routeur CRUD genere pour transport-ferroviaire (expansion)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List

from app.core.database import get_db
from app.core.permissions import require_perm
from app.models.user import User
from app.models.ferroviaire_b_deep import (
    RailWheelSet,
    RailLoadingGauge,
    RailShuntingPlan,
    RailTrainConsist,
    RailPathOccupancy,
    RailWagonDispatch,
    RailTerminalCrane,
)
from app.schemas.ferroviaire_b_deep import (
    RailWheelSetCreate, RailWheelSetUpdate, RailWheelSetOut,
    RailLoadingGaugeCreate, RailLoadingGaugeUpdate, RailLoadingGaugeOut,
    RailShuntingPlanCreate, RailShuntingPlanUpdate, RailShuntingPlanOut,
    RailTrainConsistCreate, RailTrainConsistUpdate, RailTrainConsistOut,
    RailPathOccupancyCreate, RailPathOccupancyUpdate, RailPathOccupancyOut,
    RailWagonDispatchCreate, RailWagonDispatchUpdate, RailWagonDispatchOut,
    RailTerminalCraneCreate, RailTerminalCraneUpdate, RailTerminalCraneOut,
)

router = APIRouter(tags=["transport-ferroviaire (expansion)"])


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

@router.get("/nomenclatures", summary="Vocabulaire metier transport-ferroviaire")
def nomenclatures(user: User = Depends(require_perm("ferroviaire.nomenclature.read"))):
    from app.models import ferroviaire_b_deep as _md
    import enum as _pyenum
    out = {}
    for name in dir(_md):
        obj = getattr(_md, name)
        if isinstance(obj, type) and issubclass(obj, _pyenum.Enum) and obj is not _pyenum.Enum:
            out[name.lower()] = [{"code": m.name, "valeur": m.value} for m in obj]
    return out


# ─── Essieux et roulements ─────────────────────────────────────────────────

@router.get("/railb-wheel-sets", response_model=List[RailWheelSetOut])
def list_wheel_set(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("ferroviaire.wheel_set.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, RailWheelSet, cid, {"statut": statut})


@router.post("/railb-wheel-sets", response_model=RailWheelSetOut, status_code=201)
def create_wheel_set(
    payload: RailWheelSetCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("ferroviaire.wheel_set.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, RailWheelSet, "numero_essieu", data.get("numero_essieu"), "numero_essieu", cid)
    obj = RailWheelSet(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/railb-wheel-sets/{ident}", response_model=RailWheelSetOut)
def update_wheel_set(
    ident: int,
    payload: RailWheelSetUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("ferroviaire.wheel_set.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, RailWheelSet, ident, "Essieux et roulements")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/railb-wheel-sets/{ident}", response_model=RailWheelSetOut)
def delete_wheel_set(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("ferroviaire.wheel_set.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, RailWheelSet, ident, "Essieux et roulements")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Gabarit de chargement ─────────────────────────────────────────────────

@router.get("/railb-loading-gauges", response_model=List[RailLoadingGaugeOut])
def list_loading_gauge(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("ferroviaire.loading_gauge.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, RailLoadingGauge, cid, {"statut": statut})


@router.post("/railb-loading-gauges", response_model=RailLoadingGaugeOut, status_code=201)
def create_loading_gauge(
    payload: RailLoadingGaugeCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("ferroviaire.loading_gauge.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, RailLoadingGauge, "code_gabarit", data.get("code_gabarit"), "code_gabarit", cid)
    obj = RailLoadingGauge(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/railb-loading-gauges/{ident}", response_model=RailLoadingGaugeOut)
def update_loading_gauge(
    ident: int,
    payload: RailLoadingGaugeUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("ferroviaire.loading_gauge.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, RailLoadingGauge, ident, "Gabarit de chargement")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/railb-loading-gauges/{ident}", response_model=RailLoadingGaugeOut)
def delete_loading_gauge(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("ferroviaire.loading_gauge.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, RailLoadingGauge, ident, "Gabarit de chargement")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Plans de manoeuvre ─────────────────────────────────────────────────

@router.get("/railb-shunting-plans", response_model=List[RailShuntingPlanOut])
def list_shunting_plan(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("ferroviaire.shunting_plan.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, RailShuntingPlan, cid, {"statut": statut})


@router.post("/railb-shunting-plans", response_model=RailShuntingPlanOut, status_code=201)
def create_shunting_plan(
    payload: RailShuntingPlanCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("ferroviaire.shunting_plan.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, RailShuntingPlan, "reference", data.get("reference"), "reference", cid)
    obj = RailShuntingPlan(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/railb-shunting-plans/{ident}", response_model=RailShuntingPlanOut)
def update_shunting_plan(
    ident: int,
    payload: RailShuntingPlanUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("ferroviaire.shunting_plan.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, RailShuntingPlan, ident, "Plans de manoeuvre")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/railb-shunting-plans/{ident}", response_model=RailShuntingPlanOut)
def delete_shunting_plan(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("ferroviaire.shunting_plan.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, RailShuntingPlan, ident, "Plans de manoeuvre")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Composition de train ─────────────────────────────────────────────────

@router.get("/railb-train-consists", response_model=List[RailTrainConsistOut])
def list_train_consist(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("ferroviaire.train_consist.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, RailTrainConsist, cid, {"statut": statut})


@router.post("/railb-train-consists", response_model=RailTrainConsistOut, status_code=201)
def create_train_consist(
    payload: RailTrainConsistCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("ferroviaire.train_consist.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, RailTrainConsist, "reference", data.get("reference"), "reference", cid)
    obj = RailTrainConsist(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/railb-train-consists/{ident}", response_model=RailTrainConsistOut)
def update_train_consist(
    ident: int,
    payload: RailTrainConsistUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("ferroviaire.train_consist.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, RailTrainConsist, ident, "Composition de train")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/railb-train-consists/{ident}", response_model=RailTrainConsistOut)
def delete_train_consist(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("ferroviaire.train_consist.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, RailTrainConsist, ident, "Composition de train")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Occupation de sillons ─────────────────────────────────────────────────

@router.get("/railb-path-occupancy", response_model=List[RailPathOccupancyOut])
def list_path_occupancy(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("ferroviaire.path_occupancy.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, RailPathOccupancy, cid, {"statut": statut})


@router.post("/railb-path-occupancy", response_model=RailPathOccupancyOut, status_code=201)
def create_path_occupancy(
    payload: RailPathOccupancyCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("ferroviaire.path_occupancy.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, RailPathOccupancy, "reference", data.get("reference"), "reference", cid)
    obj = RailPathOccupancy(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/railb-path-occupancy/{ident}", response_model=RailPathOccupancyOut)
def update_path_occupancy(
    ident: int,
    payload: RailPathOccupancyUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("ferroviaire.path_occupancy.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, RailPathOccupancy, ident, "Occupation de sillons")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/railb-path-occupancy/{ident}", response_model=RailPathOccupancyOut)
def delete_path_occupancy(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("ferroviaire.path_occupancy.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, RailPathOccupancy, ident, "Occupation de sillons")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Affectation wagons ─────────────────────────────────────────────────

@router.get("/railb-wagon-dispatch", response_model=List[RailWagonDispatchOut])
def list_wagon_dispatch(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("ferroviaire.wagon_dispatch.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, RailWagonDispatch, cid, {"statut": statut})


@router.post("/railb-wagon-dispatch", response_model=RailWagonDispatchOut, status_code=201)
def create_wagon_dispatch(
    payload: RailWagonDispatchCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("ferroviaire.wagon_dispatch.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, RailWagonDispatch, "reference", data.get("reference"), "reference", cid)
    obj = RailWagonDispatch(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/railb-wagon-dispatch/{ident}", response_model=RailWagonDispatchOut)
def update_wagon_dispatch(
    ident: int,
    payload: RailWagonDispatchUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("ferroviaire.wagon_dispatch.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, RailWagonDispatch, ident, "Affectation wagons")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/railb-wagon-dispatch/{ident}", response_model=RailWagonDispatchOut)
def delete_wagon_dispatch(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("ferroviaire.wagon_dispatch.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, RailWagonDispatch, ident, "Affectation wagons")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Portiques terminaux fer ─────────────────────────────────────────────────

@router.get("/railb-terminal-cranes", response_model=List[RailTerminalCraneOut])
def list_terminal_crane(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("ferroviaire.terminal_crane.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, RailTerminalCrane, cid, {"statut": statut})


@router.post("/railb-terminal-cranes", response_model=RailTerminalCraneOut, status_code=201)
def create_terminal_crane(
    payload: RailTerminalCraneCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("ferroviaire.terminal_crane.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, RailTerminalCrane, "code_equipment", data.get("code_equipment"), "code_equipment", cid)
    obj = RailTerminalCrane(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/railb-terminal-cranes/{ident}", response_model=RailTerminalCraneOut)
def update_terminal_crane(
    ident: int,
    payload: RailTerminalCraneUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("ferroviaire.terminal_crane.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, RailTerminalCrane, ident, "Portiques terminaux fer")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/railb-terminal-cranes/{ident}", response_model=RailTerminalCraneOut)
def delete_terminal_crane(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("ferroviaire.terminal_crane.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, RailTerminalCrane, ident, "Portiques terminaux fer")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj

