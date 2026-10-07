"""Routeur CRUD genere pour port-operations (expansion)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List

from app.core.database import get_db
from app.core.permissions import require_perm
from app.models.user import User
from app.models.port_ops_b_deep import (
    PortbBerthSchedule,
    PortbVesselTrafficLog,
)
from app.schemas.port_ops_b_deep import (
    PortbBerthScheduleCreate, PortbBerthScheduleUpdate, PortbBerthScheduleOut,
    PortbVesselTrafficLogCreate, PortbVesselTrafficLogUpdate, PortbVesselTrafficLogOut,
)

router = APIRouter(tags=["port-operations (expansion)"])


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

@router.get("/nomenclatures", summary="Vocabulaire metier port-operations")
def nomenclatures(user: User = Depends(require_perm("port.nomenclature.read"))):
    from app.models import port_ops_b_deep as _md
    import enum as _pyenum
    out = {}
    for name in dir(_md):
        obj = getattr(_md, name)
        if isinstance(obj, type) and issubclass(obj, _pyenum.Enum) and obj is not _pyenum.Enum:
            out[name.lower()] = [{"code": m.name, "valeur": m.value} for m in obj]
    return out


# ─── Plans d'escale et postes d'amarrage ─────────────────────────────────────────────────

@router.get("/portb-berth-schedules", response_model=List[PortbBerthScheduleOut])
def list_berth_schedule(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("port.berth_schedule.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, PortbBerthSchedule, cid, {"statut": statut})


@router.post("/portb-berth-schedules", response_model=PortbBerthScheduleOut, status_code=201)
def create_berth_schedule(
    payload: PortbBerthScheduleCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("port.berth_schedule.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, PortbBerthSchedule, "reference", data.get("reference"), "reference", cid)
    obj = PortbBerthSchedule(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/portb-berth-schedules/{ident}", response_model=PortbBerthScheduleOut)
def update_berth_schedule(
    ident: int,
    payload: PortbBerthScheduleUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("port.berth_schedule.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, PortbBerthSchedule, ident, "Plans d'escale et postes d'amarrage")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/portb-berth-schedules/{ident}", response_model=PortbBerthScheduleOut)
def delete_berth_schedule(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("port.berth_schedule.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, PortbBerthSchedule, ident, "Plans d'escale et postes d'amarrage")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Journal de trafic maritime (VTS) ─────────────────────────────────────────────────

@router.get("/portb-vessel-traffic-logs", response_model=List[PortbVesselTrafficLogOut])
def list_vessel_traffic_log(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("port.vessel_traffic_log.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, PortbVesselTrafficLog, cid, {"statut": statut})


@router.post("/portb-vessel-traffic-logs", response_model=PortbVesselTrafficLogOut, status_code=201)
def create_vessel_traffic_log(
    payload: PortbVesselTrafficLogCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("port.vessel_traffic_log.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, PortbVesselTrafficLog, "reference", data.get("reference"), "reference", cid)
    obj = PortbVesselTrafficLog(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/portb-vessel-traffic-logs/{ident}", response_model=PortbVesselTrafficLogOut)
def update_vessel_traffic_log(
    ident: int,
    payload: PortbVesselTrafficLogUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("port.vessel_traffic_log.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, PortbVesselTrafficLog, ident, "Journal de trafic maritime (VTS)")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/portb-vessel-traffic-logs/{ident}", response_model=PortbVesselTrafficLogOut)
def delete_vessel_traffic_log(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("port.vessel_traffic_log.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, PortbVesselTrafficLog, ident, "Journal de trafic maritime (VTS)")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj

