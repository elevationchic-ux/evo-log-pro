"""Routeur CRUD genere pour courier-express (expansion)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List

from app.core.database import get_db
from app.core.permissions import require_perm
from app.models.user import User
from app.models.courier_e_deep import (
    Cour2RouteScan,
    Cour2LastMileHandoff,
    Cour2DeliveryAttempt,
    Cour2ExceptionParcel,
    Cour2ReturnToSender,
    Cour2CourierShiftLog,
    Cour2SlaBreachLog,
)
from app.schemas.courier_e_deep import (
    Cour2RouteScanCreate, Cour2RouteScanUpdate, Cour2RouteScanOut,
    Cour2LastMileHandoffCreate, Cour2LastMileHandoffUpdate, Cour2LastMileHandoffOut,
    Cour2DeliveryAttemptCreate, Cour2DeliveryAttemptUpdate, Cour2DeliveryAttemptOut,
    Cour2ExceptionParcelCreate, Cour2ExceptionParcelUpdate, Cour2ExceptionParcelOut,
    Cour2ReturnToSenderCreate, Cour2ReturnToSenderUpdate, Cour2ReturnToSenderOut,
    Cour2CourierShiftLogCreate, Cour2CourierShiftLogUpdate, Cour2CourierShiftLogOut,
    Cour2SlaBreachLogCreate, Cour2SlaBreachLogUpdate, Cour2SlaBreachLogOut,
)

router = APIRouter(tags=["courier-express (expansion)"])


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

@router.get("/nomenclatures", summary="Vocabulaire metier courier-express")
def nomenclatures(user: User = Depends(require_perm("courier.nomenclature.read"))):
    from app.models import courier_e_deep as _md
    import enum as _pyenum
    out = {}
    for name in dir(_md):
        obj = getattr(_md, name)
        if isinstance(obj, type) and issubclass(obj, _pyenum.Enum) and obj is not _pyenum.Enum:
            out[name.lower()] = [{"code": m.name, "valeur": m.value} for m in obj]
    return out


# ─── Scans de tournee ─────────────────────────────────────────────────

@router.get("/cour2-route-scans", response_model=List[Cour2RouteScanOut])
def list_route_scan(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("courier.route_scan.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, Cour2RouteScan, cid, {"statut": statut})


@router.post("/cour2-route-scans", response_model=Cour2RouteScanOut, status_code=201)
def create_route_scan(
    payload: Cour2RouteScanCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("courier.route_scan.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, Cour2RouteScan, "reference", data.get("reference"), "reference", cid)
    obj = Cour2RouteScan(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/cour2-route-scans/{ident}", response_model=Cour2RouteScanOut)
def update_route_scan(
    ident: int,
    payload: Cour2RouteScanUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("courier.route_scan.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, Cour2RouteScan, ident, "Scans de tournee")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/cour2-route-scans/{ident}", response_model=Cour2RouteScanOut)
def delete_route_scan(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("courier.route_scan.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, Cour2RouteScan, ident, "Scans de tournee")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Remises dernier kilometre ─────────────────────────────────────────────────

@router.get("/cour2-last-mile-handoffs", response_model=List[Cour2LastMileHandoffOut])
def list_last_mile_handoff(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("courier.last_mile_handoff.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, Cour2LastMileHandoff, cid, {"statut": statut})


@router.post("/cour2-last-mile-handoffs", response_model=Cour2LastMileHandoffOut, status_code=201)
def create_last_mile_handoff(
    payload: Cour2LastMileHandoffCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("courier.last_mile_handoff.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, Cour2LastMileHandoff, "reference", data.get("reference"), "reference", cid)
    obj = Cour2LastMileHandoff(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/cour2-last-mile-handoffs/{ident}", response_model=Cour2LastMileHandoffOut)
def update_last_mile_handoff(
    ident: int,
    payload: Cour2LastMileHandoffUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("courier.last_mile_handoff.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, Cour2LastMileHandoff, ident, "Remises dernier kilometre")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/cour2-last-mile-handoffs/{ident}", response_model=Cour2LastMileHandoffOut)
def delete_last_mile_handoff(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("courier.last_mile_handoff.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, Cour2LastMileHandoff, ident, "Remises dernier kilometre")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Tentatives de livraison ─────────────────────────────────────────────────

@router.get("/cour2-delivery-attempts", response_model=List[Cour2DeliveryAttemptOut])
def list_delivery_attempt(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("courier.delivery_attempt.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, Cour2DeliveryAttempt, cid, {"statut": statut})


@router.post("/cour2-delivery-attempts", response_model=Cour2DeliveryAttemptOut, status_code=201)
def create_delivery_attempt(
    payload: Cour2DeliveryAttemptCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("courier.delivery_attempt.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, Cour2DeliveryAttempt, "reference", data.get("reference"), "reference", cid)
    obj = Cour2DeliveryAttempt(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/cour2-delivery-attempts/{ident}", response_model=Cour2DeliveryAttemptOut)
def update_delivery_attempt(
    ident: int,
    payload: Cour2DeliveryAttemptUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("courier.delivery_attempt.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, Cour2DeliveryAttempt, ident, "Tentatives de livraison")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/cour2-delivery-attempts/{ident}", response_model=Cour2DeliveryAttemptOut)
def delete_delivery_attempt(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("courier.delivery_attempt.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, Cour2DeliveryAttempt, ident, "Tentatives de livraison")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Colis en exception ─────────────────────────────────────────────────

@router.get("/cour2-exception-parcels", response_model=List[Cour2ExceptionParcelOut])
def list_exception_parcel(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("courier.exception_parcel.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, Cour2ExceptionParcel, cid, {"statut": statut})


@router.post("/cour2-exception-parcels", response_model=Cour2ExceptionParcelOut, status_code=201)
def create_exception_parcel(
    payload: Cour2ExceptionParcelCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("courier.exception_parcel.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, Cour2ExceptionParcel, "reference", data.get("reference"), "reference", cid)
    obj = Cour2ExceptionParcel(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/cour2-exception-parcels/{ident}", response_model=Cour2ExceptionParcelOut)
def update_exception_parcel(
    ident: int,
    payload: Cour2ExceptionParcelUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("courier.exception_parcel.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, Cour2ExceptionParcel, ident, "Colis en exception")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/cour2-exception-parcels/{ident}", response_model=Cour2ExceptionParcelOut)
def delete_exception_parcel(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("courier.exception_parcel.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, Cour2ExceptionParcel, ident, "Colis en exception")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Retours expediteur ─────────────────────────────────────────────────

@router.get("/cour2-returns-to-sender", response_model=List[Cour2ReturnToSenderOut])
def list_return_to_sender(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("courier.return_to_sender.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, Cour2ReturnToSender, cid, {"statut": statut})


@router.post("/cour2-returns-to-sender", response_model=Cour2ReturnToSenderOut, status_code=201)
def create_return_to_sender(
    payload: Cour2ReturnToSenderCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("courier.return_to_sender.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, Cour2ReturnToSender, "reference", data.get("reference"), "reference", cid)
    obj = Cour2ReturnToSender(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/cour2-returns-to-sender/{ident}", response_model=Cour2ReturnToSenderOut)
def update_return_to_sender(
    ident: int,
    payload: Cour2ReturnToSenderUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("courier.return_to_sender.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, Cour2ReturnToSender, ident, "Retours expediteur")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/cour2-returns-to-sender/{ident}", response_model=Cour2ReturnToSenderOut)
def delete_return_to_sender(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("courier.return_to_sender.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, Cour2ReturnToSender, ident, "Retours expediteur")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Journal de vacation livreur ─────────────────────────────────────────────────

@router.get("/cour2-courier-shift-logs", response_model=List[Cour2CourierShiftLogOut])
def list_courier_shift_log(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("courier.courier_shift_log.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, Cour2CourierShiftLog, cid, {"statut": statut})


@router.post("/cour2-courier-shift-logs", response_model=Cour2CourierShiftLogOut, status_code=201)
def create_courier_shift_log(
    payload: Cour2CourierShiftLogCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("courier.courier_shift_log.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, Cour2CourierShiftLog, "reference", data.get("reference"), "reference", cid)
    obj = Cour2CourierShiftLog(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/cour2-courier-shift-logs/{ident}", response_model=Cour2CourierShiftLogOut)
def update_courier_shift_log(
    ident: int,
    payload: Cour2CourierShiftLogUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("courier.courier_shift_log.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, Cour2CourierShiftLog, ident, "Journal de vacation livreur")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/cour2-courier-shift-logs/{ident}", response_model=Cour2CourierShiftLogOut)
def delete_courier_shift_log(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("courier.courier_shift_log.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, Cour2CourierShiftLog, ident, "Journal de vacation livreur")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Journaux de rupture SLA ─────────────────────────────────────────────────

@router.get("/cour2-sla-breach-logs", response_model=List[Cour2SlaBreachLogOut])
def list_sla_breach_log(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("courier.sla_breach_log.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, Cour2SlaBreachLog, cid, {"statut": statut})


@router.post("/cour2-sla-breach-logs", response_model=Cour2SlaBreachLogOut, status_code=201)
def create_sla_breach_log(
    payload: Cour2SlaBreachLogCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("courier.sla_breach_log.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, Cour2SlaBreachLog, "reference", data.get("reference"), "reference", cid)
    obj = Cour2SlaBreachLog(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/cour2-sla-breach-logs/{ident}", response_model=Cour2SlaBreachLogOut)
def update_sla_breach_log(
    ident: int,
    payload: Cour2SlaBreachLogUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("courier.sla_breach_log.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, Cour2SlaBreachLog, ident, "Journaux de rupture SLA")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/cour2-sla-breach-logs/{ident}", response_model=Cour2SlaBreachLogOut)
def delete_sla_breach_log(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("courier.sla_breach_log.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, Cour2SlaBreachLog, ident, "Journaux de rupture SLA")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj

