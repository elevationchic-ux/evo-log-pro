"""Routeur CRUD genere pour transport-aerien (expansion)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List

from app.core.database import get_db
from app.core.permissions import require_perm
from app.models.user import User
from app.models.aerien_deep import (
    Aircraft,
    AirWaybill,
    AirSlot,
    GroundHandlingJob,
    ULDInventory,
    CargoSecurityScreen,
    AirDangerousGoods,
    FlightOperation,
    CrewRoster,
    AircraftCheck,
    AirportCargoWarehouse,
    AirTariff,
)
from app.schemas.aerien_deep import (
    AircraftCreate, AircraftUpdate, AircraftOut,
    AirWaybillCreate, AirWaybillUpdate, AirWaybillOut,
    AirSlotCreate, AirSlotUpdate, AirSlotOut,
    GroundHandlingJobCreate, GroundHandlingJobUpdate, GroundHandlingJobOut,
    ULDInventoryCreate, ULDInventoryUpdate, ULDInventoryOut,
    CargoSecurityScreenCreate, CargoSecurityScreenUpdate, CargoSecurityScreenOut,
    AirDangerousGoodsCreate, AirDangerousGoodsUpdate, AirDangerousGoodsOut,
    FlightOperationCreate, FlightOperationUpdate, FlightOperationOut,
    CrewRosterCreate, CrewRosterUpdate, CrewRosterOut,
    AircraftCheckCreate, AircraftCheckUpdate, AircraftCheckOut,
    AirportCargoWarehouseCreate, AirportCargoWarehouseUpdate, AirportCargoWarehouseOut,
    AirTariffCreate, AirTariffUpdate, AirTariffOut,
)

router = APIRouter(tags=["transport-aerien (expansion)"])


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

@router.get("/nomenclatures", summary="Vocabulaire metier transport-aerien")
def nomenclatures(user: User = Depends(require_perm("aerien.nomenclature.read"))):
    from app.models import aerien_deep as _md
    import enum as _pyenum
    out = {}
    for name in dir(_md):
        obj = getattr(_md, name)
        if isinstance(obj, type) and issubclass(obj, _pyenum.Enum) and obj is not _pyenum.Enum:
            out[name.lower()] = [{"code": m.name, "valeur": m.value} for m in obj]
    return out


# ─── Flotte aeronefs ─────────────────────────────────────────────────

@router.get("/air-aircraft", response_model=List[AircraftOut])
def list_fleet(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("aerien.fleet.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, Aircraft, cid, {"statut": statut})


@router.post("/air-aircraft", response_model=AircraftOut, status_code=201)
def create_fleet(
    payload: AircraftCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("aerien.fleet.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, Aircraft, "immatriculation", data.get("immatriculation"), "immatriculation", cid)
    obj = Aircraft(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/air-aircraft/{ident}", response_model=AircraftOut)
def update_fleet(
    ident: int,
    payload: AircraftUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("aerien.fleet.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, Aircraft, ident, "Flotte aeronefs")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/air-aircraft/{ident}", response_model=AircraftOut)
def delete_fleet(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("aerien.fleet.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, Aircraft, ident, "Flotte aeronefs")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Lia / lettres de transport aerien ─────────────────────────────────────────────────

@router.get("/air-waybills", response_model=List[AirWaybillOut])
def list_awb(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("aerien.awb.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, AirWaybill, cid, {"statut": statut})


@router.post("/air-waybills", response_model=AirWaybillOut, status_code=201)
def create_awb(
    payload: AirWaybillCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("aerien.awb.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, AirWaybill, "numero_awb", data.get("numero_awb"), "numero_awb", cid)
    obj = AirWaybill(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/air-waybills/{ident}", response_model=AirWaybillOut)
def update_awb(
    ident: int,
    payload: AirWaybillUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("aerien.awb.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, AirWaybill, ident, "Lia / lettres de transport aerien")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/air-waybills/{ident}", response_model=AirWaybillOut)
def delete_awb(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("aerien.awb.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, AirWaybill, ident, "Lia / lettres de transport aerien")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Creneaux aeroportuaires ─────────────────────────────────────────────────

@router.get("/air-slots", response_model=List[AirSlotOut])
def list_slots(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("aerien.slots.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, AirSlot, cid, {"statut": statut})


@router.post("/air-slots", response_model=AirSlotOut, status_code=201)
def create_slots(
    payload: AirSlotCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("aerien.slots.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, AirSlot, "reference", data.get("reference"), "reference", cid)
    obj = AirSlot(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/air-slots/{ident}", response_model=AirSlotOut)
def update_slots(
    ident: int,
    payload: AirSlotUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("aerien.slots.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, AirSlot, ident, "Creneaux aeroportuaires")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/air-slots/{ident}", response_model=AirSlotOut)
def delete_slots(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("aerien.slots.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, AirSlot, ident, "Creneaux aeroportuaires")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Traitement au sol ─────────────────────────────────────────────────

@router.get("/air-handling-jobs", response_model=List[GroundHandlingJobOut])
def list_handling(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("aerien.handling.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, GroundHandlingJob, cid, {"statut": statut})


@router.post("/air-handling-jobs", response_model=GroundHandlingJobOut, status_code=201)
def create_handling(
    payload: GroundHandlingJobCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("aerien.handling.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, GroundHandlingJob, "reference", data.get("reference"), "reference", cid)
    obj = GroundHandlingJob(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/air-handling-jobs/{ident}", response_model=GroundHandlingJobOut)
def update_handling(
    ident: int,
    payload: GroundHandlingJobUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("aerien.handling.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, GroundHandlingJob, ident, "Traitement au sol")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/air-handling-jobs/{ident}", response_model=GroundHandlingJobOut)
def delete_handling(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("aerien.handling.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, GroundHandlingJob, ident, "Traitement au sol")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Parc ULD ─────────────────────────────────────────────────

@router.get("/air-uld-inventory", response_model=List[ULDInventoryOut])
def list_uld(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("aerien.uld.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, ULDInventory, cid, {"statut": statut})


@router.post("/air-uld-inventory", response_model=ULDInventoryOut, status_code=201)
def create_uld(
    payload: ULDInventoryCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("aerien.uld.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, ULDInventory, "numero_uld", data.get("numero_uld"), "numero_uld", cid)
    obj = ULDInventory(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/air-uld-inventory/{ident}", response_model=ULDInventoryOut)
def update_uld(
    ident: int,
    payload: ULDInventoryUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("aerien.uld.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ULDInventory, ident, "Parc ULD")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/air-uld-inventory/{ident}", response_model=ULDInventoryOut)
def delete_uld(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("aerien.uld.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ULDInventory, ident, "Parc ULD")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Sûreté fret arien ─────────────────────────────────────────────────

@router.get("/air-cargo-security-screens", response_model=List[CargoSecurityScreenOut])
def list_security(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("aerien.security.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, CargoSecurityScreen, cid, {"statut": statut})


@router.post("/air-cargo-security-screens", response_model=CargoSecurityScreenOut, status_code=201)
def create_security(
    payload: CargoSecurityScreenCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("aerien.security.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, CargoSecurityScreen, "reference", data.get("reference"), "reference", cid)
    obj = CargoSecurityScreen(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/air-cargo-security-screens/{ident}", response_model=CargoSecurityScreenOut)
def update_security(
    ident: int,
    payload: CargoSecurityScreenUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("aerien.security.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CargoSecurityScreen, ident, "Sûreté fret arien")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/air-cargo-security-screens/{ident}", response_model=CargoSecurityScreenOut)
def delete_security(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("aerien.security.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CargoSecurityScreen, ident, "Sûreté fret arien")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Marchandises dangereuses IATA ─────────────────────────────────────────────────

@router.get("/air-dangerous-goods", response_model=List[AirDangerousGoodsOut])
def list_dgr(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("aerien.dgr.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, AirDangerousGoods, cid, {"statut": statut})


@router.post("/air-dangerous-goods", response_model=AirDangerousGoodsOut, status_code=201)
def create_dgr(
    payload: AirDangerousGoodsCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("aerien.dgr.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, AirDangerousGoods, "reference", data.get("reference"), "reference", cid)
    obj = AirDangerousGoods(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/air-dangerous-goods/{ident}", response_model=AirDangerousGoodsOut)
def update_dgr(
    ident: int,
    payload: AirDangerousGoodsUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("aerien.dgr.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, AirDangerousGoods, ident, "Marchandises dangereuses IATA")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/air-dangerous-goods/{ident}", response_model=AirDangerousGoodsOut)
def delete_dgr(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("aerien.dgr.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, AirDangerousGoods, ident, "Marchandises dangereuses IATA")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Operations vol ─────────────────────────────────────────────────

@router.get("/air-flight-operations", response_model=List[FlightOperationOut])
def list_flightops(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("aerien.flightops.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, FlightOperation, cid, {"statut": statut})


@router.post("/air-flight-operations", response_model=FlightOperationOut, status_code=201)
def create_flightops(
    payload: FlightOperationCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("aerien.flightops.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, FlightOperation, "reference", data.get("reference"), "reference", cid)
    obj = FlightOperation(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/air-flight-operations/{ident}", response_model=FlightOperationOut)
def update_flightops(
    ident: int,
    payload: FlightOperationUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("aerien.flightops.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, FlightOperation, ident, "Operations vol")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/air-flight-operations/{ident}", response_model=FlightOperationOut)
def delete_flightops(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("aerien.flightops.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, FlightOperation, ident, "Operations vol")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Navigation planning ─────────────────────────────────────────────────

@router.get("/air-crew-rosters", response_model=List[CrewRosterOut])
def list_crew(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("aerien.crew.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, CrewRoster, cid, {"statut": statut})


@router.post("/air-crew-rosters", response_model=CrewRosterOut, status_code=201)
def create_crew(
    payload: CrewRosterCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("aerien.crew.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, CrewRoster, "reference", data.get("reference"), "reference", cid)
    obj = CrewRoster(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/air-crew-rosters/{ident}", response_model=CrewRosterOut)
def update_crew(
    ident: int,
    payload: CrewRosterUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("aerien.crew.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CrewRoster, ident, "Navigation planning")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/air-crew-rosters/{ident}", response_model=CrewRosterOut)
def delete_crew(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("aerien.crew.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CrewRoster, ident, "Navigation planning")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Maintenance aeronefs (MRO) ─────────────────────────────────────────────────

@router.get("/air-mro-checks", response_model=List[AircraftCheckOut])
def list_mro(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("aerien.mro.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, AircraftCheck, cid, {"statut": statut})


@router.post("/air-mro-checks", response_model=AircraftCheckOut, status_code=201)
def create_mro(
    payload: AircraftCheckCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("aerien.mro.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, AircraftCheck, "reference", data.get("reference"), "reference", cid)
    obj = AircraftCheck(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/air-mro-checks/{ident}", response_model=AircraftCheckOut)
def update_mro(
    ident: int,
    payload: AircraftCheckUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("aerien.mro.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, AircraftCheck, ident, "Maintenance aeronefs (MRO)")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/air-mro-checks/{ident}", response_model=AircraftCheckOut)
def delete_mro(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("aerien.mro.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, AircraftCheck, ident, "Maintenance aeronefs (MRO)")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Terminal fret aerien ─────────────────────────────────────────────────

@router.get("/air-cargo-warehouses", response_model=List[AirportCargoWarehouseOut])
def list_cargo(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("aerien.cargo.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, AirportCargoWarehouse, cid, {"statut": statut})


@router.post("/air-cargo-warehouses", response_model=AirportCargoWarehouseOut, status_code=201)
def create_cargo(
    payload: AirportCargoWarehouseCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("aerien.cargo.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, AirportCargoWarehouse, "code_entrepot", data.get("code_entrepot"), "code_entrepot", cid)
    obj = AirportCargoWarehouse(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/air-cargo-warehouses/{ident}", response_model=AirportCargoWarehouseOut)
def update_cargo(
    ident: int,
    payload: AirportCargoWarehouseUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("aerien.cargo.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, AirportCargoWarehouse, ident, "Terminal fret aerien")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/air-cargo-warehouses/{ident}", response_model=AirportCargoWarehouseOut)
def delete_cargo(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("aerien.cargo.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, AirportCargoWarehouse, ident, "Terminal fret aerien")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Tarification aerienne ─────────────────────────────────────────────────

@router.get("/air-tariffs", response_model=List[AirTariffOut])
def list_tariffs(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("aerien.tariffs.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, AirTariff, cid, {"statut": statut})


@router.post("/air-tariffs", response_model=AirTariffOut, status_code=201)
def create_tariffs(
    payload: AirTariffCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("aerien.tariffs.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, AirTariff, "code_tarif", data.get("code_tarif"), "code_tarif", cid)
    obj = AirTariff(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/air-tariffs/{ident}", response_model=AirTariffOut)
def update_tariffs(
    ident: int,
    payload: AirTariffUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("aerien.tariffs.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, AirTariff, ident, "Tarification aerienne")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/air-tariffs/{ident}", response_model=AirTariffOut)
def delete_tariffs(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("aerien.tariffs.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, AirTariff, ident, "Tarification aerienne")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj

