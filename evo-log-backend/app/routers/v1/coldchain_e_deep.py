"""Routeur CRUD genere pour chaine-froid (expansion)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List

from app.core.database import get_db
from app.core.permissions import require_perm
from app.models.user import User
from app.models.coldchain_e_deep import (
    Cold2TemperatureLog,
    Cold2ColdExcursion,
    Cold2ProbeCalibration,
    Cold2BlastFreezeCycle,
    Cold2DoorOpenEvent,
    Cold2HumidityLog,
    Cold2RefrigerantCharge,
    Cold2ShipmentApproval,
    Cold2IceBatteryCharge,
)
from app.schemas.coldchain_e_deep import (
    Cold2TemperatureLogCreate, Cold2TemperatureLogUpdate, Cold2TemperatureLogOut,
    Cold2ColdExcursionCreate, Cold2ColdExcursionUpdate, Cold2ColdExcursionOut,
    Cold2ProbeCalibrationCreate, Cold2ProbeCalibrationUpdate, Cold2ProbeCalibrationOut,
    Cold2BlastFreezeCycleCreate, Cold2BlastFreezeCycleUpdate, Cold2BlastFreezeCycleOut,
    Cold2DoorOpenEventCreate, Cold2DoorOpenEventUpdate, Cold2DoorOpenEventOut,
    Cold2HumidityLogCreate, Cold2HumidityLogUpdate, Cold2HumidityLogOut,
    Cold2RefrigerantChargeCreate, Cold2RefrigerantChargeUpdate, Cold2RefrigerantChargeOut,
    Cold2ShipmentApprovalCreate, Cold2ShipmentApprovalUpdate, Cold2ShipmentApprovalOut,
    Cold2IceBatteryChargeCreate, Cold2IceBatteryChargeUpdate, Cold2IceBatteryChargeOut,
)

router = APIRouter(tags=["chaine-froid (expansion)"])


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

@router.get("/nomenclatures", summary="Vocabulaire metier chaine-froid")
def nomenclatures(user: User = Depends(require_perm("coldchain.nomenclature.read"))):
    from app.models import coldchain_e_deep as _md
    import enum as _pyenum
    out = {}
    for name in dir(_md):
        obj = getattr(_md, name)
        if isinstance(obj, type) and issubclass(obj, _pyenum.Enum) and obj is not _pyenum.Enum:
            out[name.lower()] = [{"code": m.name, "valeur": m.value} for m in obj]
    return out


# ─── Releves de temperature ─────────────────────────────────────────────────

@router.get("/cold2-temperature-logs", response_model=List[Cold2TemperatureLogOut])
def list_temperature_log(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("coldchain.temperature_log.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, Cold2TemperatureLog, cid, {"statut": statut})


@router.post("/cold2-temperature-logs", response_model=Cold2TemperatureLogOut, status_code=201)
def create_temperature_log(
    payload: Cold2TemperatureLogCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("coldchain.temperature_log.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, Cold2TemperatureLog, "reference", data.get("reference"), "reference", cid)
    obj = Cold2TemperatureLog(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/cold2-temperature-logs/{ident}", response_model=Cold2TemperatureLogOut)
def update_temperature_log(
    ident: int,
    payload: Cold2TemperatureLogUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("coldchain.temperature_log.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, Cold2TemperatureLog, ident, "Releves de temperature")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/cold2-temperature-logs/{ident}", response_model=Cold2TemperatureLogOut)
def delete_temperature_log(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("coldchain.temperature_log.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, Cold2TemperatureLog, ident, "Releves de temperature")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Excursions de temperature ─────────────────────────────────────────────────

@router.get("/cold2-cold-excursion-events", response_model=List[Cold2ColdExcursionOut])
def list_cold_excursion_event(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("coldchain.cold_excursion_event.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, Cold2ColdExcursion, cid, {"statut": statut})


@router.post("/cold2-cold-excursion-events", response_model=Cold2ColdExcursionOut, status_code=201)
def create_cold_excursion_event(
    payload: Cold2ColdExcursionCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("coldchain.cold_excursion_event.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, Cold2ColdExcursion, "reference", data.get("reference"), "reference", cid)
    obj = Cold2ColdExcursion(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/cold2-cold-excursion-events/{ident}", response_model=Cold2ColdExcursionOut)
def update_cold_excursion_event(
    ident: int,
    payload: Cold2ColdExcursionUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("coldchain.cold_excursion_event.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, Cold2ColdExcursion, ident, "Excursions de temperature")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/cold2-cold-excursion-events/{ident}", response_model=Cold2ColdExcursionOut)
def delete_cold_excursion_event(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("coldchain.cold_excursion_event.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, Cold2ColdExcursion, ident, "Excursions de temperature")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Etalonnages de sonde ─────────────────────────────────────────────────

@router.get("/cold2-probe-calibrations", response_model=List[Cold2ProbeCalibrationOut])
def list_probe_calibration(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("coldchain.probe_calibration.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, Cold2ProbeCalibration, cid, {"statut": statut})


@router.post("/cold2-probe-calibrations", response_model=Cold2ProbeCalibrationOut, status_code=201)
def create_probe_calibration(
    payload: Cold2ProbeCalibrationCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("coldchain.probe_calibration.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, Cold2ProbeCalibration, "reference", data.get("reference"), "reference", cid)
    obj = Cold2ProbeCalibration(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/cold2-probe-calibrations/{ident}", response_model=Cold2ProbeCalibrationOut)
def update_probe_calibration(
    ident: int,
    payload: Cold2ProbeCalibrationUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("coldchain.probe_calibration.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, Cold2ProbeCalibration, ident, "Etalonnages de sonde")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/cold2-probe-calibrations/{ident}", response_model=Cold2ProbeCalibrationOut)
def delete_probe_calibration(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("coldchain.probe_calibration.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, Cold2ProbeCalibration, ident, "Etalonnages de sonde")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Cycles de surgelation ─────────────────────────────────────────────────

@router.get("/cold2-blast-freeze-cycles", response_model=List[Cold2BlastFreezeCycleOut])
def list_blast_freeze_cycle(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("coldchain.blast_freeze_cycle.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, Cold2BlastFreezeCycle, cid, {"statut": statut})


@router.post("/cold2-blast-freeze-cycles", response_model=Cold2BlastFreezeCycleOut, status_code=201)
def create_blast_freeze_cycle(
    payload: Cold2BlastFreezeCycleCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("coldchain.blast_freeze_cycle.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, Cold2BlastFreezeCycle, "reference", data.get("reference"), "reference", cid)
    obj = Cold2BlastFreezeCycle(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/cold2-blast-freeze-cycles/{ident}", response_model=Cold2BlastFreezeCycleOut)
def update_blast_freeze_cycle(
    ident: int,
    payload: Cold2BlastFreezeCycleUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("coldchain.blast_freeze_cycle.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, Cold2BlastFreezeCycle, ident, "Cycles de surgelation")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/cold2-blast-freeze-cycles/{ident}", response_model=Cold2BlastFreezeCycleOut)
def delete_blast_freeze_cycle(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("coldchain.blast_freeze_cycle.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, Cold2BlastFreezeCycle, ident, "Cycles de surgelation")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Evenements d' ouverture de porte ─────────────────────────────────────────────────

@router.get("/cold2-door-open-events", response_model=List[Cold2DoorOpenEventOut])
def list_door_open_event(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("coldchain.door_open_event.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, Cold2DoorOpenEvent, cid, {"statut": statut})


@router.post("/cold2-door-open-events", response_model=Cold2DoorOpenEventOut, status_code=201)
def create_door_open_event(
    payload: Cold2DoorOpenEventCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("coldchain.door_open_event.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, Cold2DoorOpenEvent, "reference", data.get("reference"), "reference", cid)
    obj = Cold2DoorOpenEvent(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/cold2-door-open-events/{ident}", response_model=Cold2DoorOpenEventOut)
def update_door_open_event(
    ident: int,
    payload: Cold2DoorOpenEventUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("coldchain.door_open_event.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, Cold2DoorOpenEvent, ident, "Evenements d' ouverture de porte")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/cold2-door-open-events/{ident}", response_model=Cold2DoorOpenEventOut)
def delete_door_open_event(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("coldchain.door_open_event.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, Cold2DoorOpenEvent, ident, "Evenements d' ouverture de porte")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Releves d' hygrometrie ─────────────────────────────────────────────────

@router.get("/cold2-humidity-logs", response_model=List[Cold2HumidityLogOut])
def list_humidity_log(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("coldchain.humidity_log.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, Cold2HumidityLog, cid, {"statut": statut})


@router.post("/cold2-humidity-logs", response_model=Cold2HumidityLogOut, status_code=201)
def create_humidity_log(
    payload: Cold2HumidityLogCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("coldchain.humidity_log.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, Cold2HumidityLog, "reference", data.get("reference"), "reference", cid)
    obj = Cold2HumidityLog(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/cold2-humidity-logs/{ident}", response_model=Cold2HumidityLogOut)
def update_humidity_log(
    ident: int,
    payload: Cold2HumidityLogUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("coldchain.humidity_log.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, Cold2HumidityLog, ident, "Releves d' hygrometrie")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/cold2-humidity-logs/{ident}", response_model=Cold2HumidityLogOut)
def delete_humidity_log(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("coldchain.humidity_log.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, Cold2HumidityLog, ident, "Releves d' hygrometrie")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Recharges de fluide frigorigene ─────────────────────────────────────────────────

@router.get("/cold2-refrigerant-charges", response_model=List[Cold2RefrigerantChargeOut])
def list_refrigerant_charge(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("coldchain.refrigerant_charge.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, Cold2RefrigerantCharge, cid, {"statut": statut})


@router.post("/cold2-refrigerant-charges", response_model=Cold2RefrigerantChargeOut, status_code=201)
def create_refrigerant_charge(
    payload: Cold2RefrigerantChargeCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("coldchain.refrigerant_charge.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, Cold2RefrigerantCharge, "reference", data.get("reference"), "reference", cid)
    obj = Cold2RefrigerantCharge(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/cold2-refrigerant-charges/{ident}", response_model=Cold2RefrigerantChargeOut)
def update_refrigerant_charge(
    ident: int,
    payload: Cold2RefrigerantChargeUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("coldchain.refrigerant_charge.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, Cold2RefrigerantCharge, ident, "Recharges de fluide frigorigene")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/cold2-refrigerant-charges/{ident}", response_model=Cold2RefrigerantChargeOut)
def delete_refrigerant_charge(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("coldchain.refrigerant_charge.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, Cold2RefrigerantCharge, ident, "Recharges de fluide frigorigene")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Validations d' expedition froide ─────────────────────────────────────────────────

@router.get("/cold2-cold-shipment-approvals", response_model=List[Cold2ShipmentApprovalOut])
def list_cold_shipment_approval(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("coldchain.cold_shipment_approval.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, Cold2ShipmentApproval, cid, {"statut": statut})


@router.post("/cold2-cold-shipment-approvals", response_model=Cold2ShipmentApprovalOut, status_code=201)
def create_cold_shipment_approval(
    payload: Cold2ShipmentApprovalCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("coldchain.cold_shipment_approval.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, Cold2ShipmentApproval, "reference", data.get("reference"), "reference", cid)
    obj = Cold2ShipmentApproval(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/cold2-cold-shipment-approvals/{ident}", response_model=Cold2ShipmentApprovalOut)
def update_cold_shipment_approval(
    ident: int,
    payload: Cold2ShipmentApprovalUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("coldchain.cold_shipment_approval.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, Cold2ShipmentApproval, ident, "Validations d' expedition froide")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/cold2-cold-shipment-approvals/{ident}", response_model=Cold2ShipmentApprovalOut)
def delete_cold_shipment_approval(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("coldchain.cold_shipment_approval.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, Cold2ShipmentApproval, ident, "Validations d' expedition froide")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Recharges de batteries de glace ─────────────────────────────────────────────────

@router.get("/cold2-ice-battery-charges", response_model=List[Cold2IceBatteryChargeOut])
def list_ice_battery_charge(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("coldchain.ice_battery_charge.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, Cold2IceBatteryCharge, cid, {"statut": statut})


@router.post("/cold2-ice-battery-charges", response_model=Cold2IceBatteryChargeOut, status_code=201)
def create_ice_battery_charge(
    payload: Cold2IceBatteryChargeCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("coldchain.ice_battery_charge.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, Cold2IceBatteryCharge, "reference", data.get("reference"), "reference", cid)
    obj = Cold2IceBatteryCharge(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/cold2-ice-battery-charges/{ident}", response_model=Cold2IceBatteryChargeOut)
def update_ice_battery_charge(
    ident: int,
    payload: Cold2IceBatteryChargeUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("coldchain.ice_battery_charge.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, Cold2IceBatteryCharge, ident, "Recharges de batteries de glace")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/cold2-ice-battery-charges/{ident}", response_model=Cold2IceBatteryChargeOut)
def delete_ice_battery_charge(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("coldchain.ice_battery_charge.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, Cold2IceBatteryCharge, ident, "Recharges de batteries de glace")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj

