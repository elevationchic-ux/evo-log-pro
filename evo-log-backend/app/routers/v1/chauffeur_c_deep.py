"""Routeur CRUD genere pour portail-chauffeur (expansion)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List

from app.core.database import get_db
from app.core.permissions import require_perm
from app.models.user import User
from app.models.chauffeur_c_deep import (
    ChfTripSheet,
    ChfDailyVehicleCheck,
    ChfFuelLog,
    ChfDrivingTimeRecord,
    ChfRestBreak,
    ChfTollReceipt,
    ChfParkingSession,
    ChfCargoSeal,
    ChfRoadsideIncident,
    ChfDeliveryStop,
    ChfMileageLog,
    ChfLoadSecuringCheck,
    ChfBorderCrossing,
    ChfDeliveryAppointment,
    ChfPpeIssue,
    ChfShiftHandover,
    ChfBreakdownReport,
    ChfTyreCheck,
    ChfCargoPhoto,
)
from app.schemas.chauffeur_c_deep import (
    ChfTripSheetCreate, ChfTripSheetUpdate, ChfTripSheetOut,
    ChfDailyVehicleCheckCreate, ChfDailyVehicleCheckUpdate, ChfDailyVehicleCheckOut,
    ChfFuelLogCreate, ChfFuelLogUpdate, ChfFuelLogOut,
    ChfDrivingTimeRecordCreate, ChfDrivingTimeRecordUpdate, ChfDrivingTimeRecordOut,
    ChfRestBreakCreate, ChfRestBreakUpdate, ChfRestBreakOut,
    ChfTollReceiptCreate, ChfTollReceiptUpdate, ChfTollReceiptOut,
    ChfParkingSessionCreate, ChfParkingSessionUpdate, ChfParkingSessionOut,
    ChfCargoSealCreate, ChfCargoSealUpdate, ChfCargoSealOut,
    ChfRoadsideIncidentCreate, ChfRoadsideIncidentUpdate, ChfRoadsideIncidentOut,
    ChfDeliveryStopCreate, ChfDeliveryStopUpdate, ChfDeliveryStopOut,
    ChfMileageLogCreate, ChfMileageLogUpdate, ChfMileageLogOut,
    ChfLoadSecuringCheckCreate, ChfLoadSecuringCheckUpdate, ChfLoadSecuringCheckOut,
    ChfBorderCrossingCreate, ChfBorderCrossingUpdate, ChfBorderCrossingOut,
    ChfDeliveryAppointmentCreate, ChfDeliveryAppointmentUpdate, ChfDeliveryAppointmentOut,
    ChfPpeIssueCreate, ChfPpeIssueUpdate, ChfPpeIssueOut,
    ChfShiftHandoverCreate, ChfShiftHandoverUpdate, ChfShiftHandoverOut,
    ChfBreakdownReportCreate, ChfBreakdownReportUpdate, ChfBreakdownReportOut,
    ChfTyreCheckCreate, ChfTyreCheckUpdate, ChfTyreCheckOut,
    ChfCargoPhotoCreate, ChfCargoPhotoUpdate, ChfCargoPhotoOut,
)

router = APIRouter(tags=["portail-chauffeur (expansion)"])


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

@router.get("/nomenclatures", summary="Vocabulaire metier portail-chauffeur")
def nomenclatures(user: User = Depends(require_perm("transport.nomenclature.read"))):
    from app.models import chauffeur_c_deep as _md
    import enum as _pyenum
    out = {}
    for name in dir(_md):
        obj = getattr(_md, name)
        if isinstance(obj, type) and issubclass(obj, _pyenum.Enum) and obj is not _pyenum.Enum:
            out[name.lower()] = [{"code": m.name, "valeur": m.value} for m in obj]
    return out


# ─── Feuilles de route ─────────────────────────────────────────────────

@router.get("/chf-trip-sheets", response_model=List[ChfTripSheetOut])
def list_trip_sheet(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.trip_sheet.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, ChfTripSheet, cid, {"statut": statut})


@router.post("/chf-trip-sheets", response_model=ChfTripSheetOut, status_code=201)
def create_trip_sheet(
    payload: ChfTripSheetCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.trip_sheet.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, ChfTripSheet, "reference", data.get("reference"), "reference", cid)
    obj = ChfTripSheet(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/chf-trip-sheets/{ident}", response_model=ChfTripSheetOut)
def update_trip_sheet(
    ident: int,
    payload: ChfTripSheetUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.trip_sheet.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ChfTripSheet, ident, "Feuilles de route")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/chf-trip-sheets/{ident}", response_model=ChfTripSheetOut)
def delete_trip_sheet(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.trip_sheet.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ChfTripSheet, ident, "Feuilles de route")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Controles quotidiens du vehicule ─────────────────────────────────────────────────

@router.get("/chf-daily-vehicle-checks", response_model=List[ChfDailyVehicleCheckOut])
def list_daily_vehicle_check(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.daily_vehicle_check.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, ChfDailyVehicleCheck, cid, {"statut": statut})


@router.post("/chf-daily-vehicle-checks", response_model=ChfDailyVehicleCheckOut, status_code=201)
def create_daily_vehicle_check(
    payload: ChfDailyVehicleCheckCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.daily_vehicle_check.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, ChfDailyVehicleCheck, "reference", data.get("reference"), "reference", cid)
    obj = ChfDailyVehicleCheck(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/chf-daily-vehicle-checks/{ident}", response_model=ChfDailyVehicleCheckOut)
def update_daily_vehicle_check(
    ident: int,
    payload: ChfDailyVehicleCheckUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.daily_vehicle_check.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ChfDailyVehicleCheck, ident, "Controles quotidiens du vehicule")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/chf-daily-vehicle-checks/{ident}", response_model=ChfDailyVehicleCheckOut)
def delete_daily_vehicle_check(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.daily_vehicle_check.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ChfDailyVehicleCheck, ident, "Controles quotidiens du vehicule")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Carnet carburant ─────────────────────────────────────────────────

@router.get("/chf-fuel-logs", response_model=List[ChfFuelLogOut])
def list_fuel_log(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.fuel_log.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, ChfFuelLog, cid, {"statut": statut})


@router.post("/chf-fuel-logs", response_model=ChfFuelLogOut, status_code=201)
def create_fuel_log(
    payload: ChfFuelLogCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.fuel_log.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, ChfFuelLog, "reference", data.get("reference"), "reference", cid)
    obj = ChfFuelLog(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/chf-fuel-logs/{ident}", response_model=ChfFuelLogOut)
def update_fuel_log(
    ident: int,
    payload: ChfFuelLogUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.fuel_log.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ChfFuelLog, ident, "Carnet carburant")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/chf-fuel-logs/{ident}", response_model=ChfFuelLogOut)
def delete_fuel_log(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.fuel_log.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ChfFuelLog, ident, "Carnet carburant")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Temps de conduite ─────────────────────────────────────────────────

@router.get("/chf-driving-times", response_model=List[ChfDrivingTimeRecordOut])
def list_driving_time(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.driving_time.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, ChfDrivingTimeRecord, cid, {"statut": statut})


@router.post("/chf-driving-times", response_model=ChfDrivingTimeRecordOut, status_code=201)
def create_driving_time(
    payload: ChfDrivingTimeRecordCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.driving_time.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, ChfDrivingTimeRecord, "reference", data.get("reference"), "reference", cid)
    obj = ChfDrivingTimeRecord(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/chf-driving-times/{ident}", response_model=ChfDrivingTimeRecordOut)
def update_driving_time(
    ident: int,
    payload: ChfDrivingTimeRecordUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.driving_time.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ChfDrivingTimeRecord, ident, "Temps de conduite")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/chf-driving-times/{ident}", response_model=ChfDrivingTimeRecordOut)
def delete_driving_time(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.driving_time.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ChfDrivingTimeRecord, ident, "Temps de conduite")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Pauses et repos ─────────────────────────────────────────────────

@router.get("/chf-rest-breaks", response_model=List[ChfRestBreakOut])
def list_rest_break(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.rest_break.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, ChfRestBreak, cid, {"statut": statut})


@router.post("/chf-rest-breaks", response_model=ChfRestBreakOut, status_code=201)
def create_rest_break(
    payload: ChfRestBreakCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.rest_break.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, ChfRestBreak, "reference", data.get("reference"), "reference", cid)
    obj = ChfRestBreak(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/chf-rest-breaks/{ident}", response_model=ChfRestBreakOut)
def update_rest_break(
    ident: int,
    payload: ChfRestBreakUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.rest_break.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ChfRestBreak, ident, "Pauses et repos")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/chf-rest-breaks/{ident}", response_model=ChfRestBreakOut)
def delete_rest_break(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.rest_break.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ChfRestBreak, ident, "Pauses et repos")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Recus de peage ─────────────────────────────────────────────────

@router.get("/chf-toll-receipts", response_model=List[ChfTollReceiptOut])
def list_toll_receipt(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.toll_receipt.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, ChfTollReceipt, cid, {"statut": statut})


@router.post("/chf-toll-receipts", response_model=ChfTollReceiptOut, status_code=201)
def create_toll_receipt(
    payload: ChfTollReceiptCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.toll_receipt.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, ChfTollReceipt, "reference", data.get("reference"), "reference", cid)
    obj = ChfTollReceipt(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/chf-toll-receipts/{ident}", response_model=ChfTollReceiptOut)
def update_toll_receipt(
    ident: int,
    payload: ChfTollReceiptUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.toll_receipt.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ChfTollReceipt, ident, "Recus de peage")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/chf-toll-receipts/{ident}", response_model=ChfTollReceiptOut)
def delete_toll_receipt(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.toll_receipt.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ChfTollReceipt, ident, "Recus de peage")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Sessions de parking ─────────────────────────────────────────────────

@router.get("/chf-parking-sessions", response_model=List[ChfParkingSessionOut])
def list_parking_session(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.parking_session.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, ChfParkingSession, cid, {"statut": statut})


@router.post("/chf-parking-sessions", response_model=ChfParkingSessionOut, status_code=201)
def create_parking_session(
    payload: ChfParkingSessionCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.parking_session.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, ChfParkingSession, "reference", data.get("reference"), "reference", cid)
    obj = ChfParkingSession(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/chf-parking-sessions/{ident}", response_model=ChfParkingSessionOut)
def update_parking_session(
    ident: int,
    payload: ChfParkingSessionUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.parking_session.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ChfParkingSession, ident, "Sessions de parking")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/chf-parking-sessions/{ident}", response_model=ChfParkingSessionOut)
def delete_parking_session(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.parking_session.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ChfParkingSession, ident, "Sessions de parking")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Plombs de cargaison ─────────────────────────────────────────────────

@router.get("/chf-cargo-seals", response_model=List[ChfCargoSealOut])
def list_cargo_seal(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.cargo_seal.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, ChfCargoSeal, cid, {"statut": statut})


@router.post("/chf-cargo-seals", response_model=ChfCargoSealOut, status_code=201)
def create_cargo_seal(
    payload: ChfCargoSealCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.cargo_seal.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, ChfCargoSeal, "reference", data.get("reference"), "reference", cid)
    obj = ChfCargoSeal(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/chf-cargo-seals/{ident}", response_model=ChfCargoSealOut)
def update_cargo_seal(
    ident: int,
    payload: ChfCargoSealUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.cargo_seal.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ChfCargoSeal, ident, "Plombs de cargaison")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/chf-cargo-seals/{ident}", response_model=ChfCargoSealOut)
def delete_cargo_seal(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.cargo_seal.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ChfCargoSeal, ident, "Plombs de cargaison")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Incidents de route ─────────────────────────────────────────────────

@router.get("/chf-roadside-incidents", response_model=List[ChfRoadsideIncidentOut])
def list_roadside_incident(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.roadside_incident.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, ChfRoadsideIncident, cid, {"statut": statut})


@router.post("/chf-roadside-incidents", response_model=ChfRoadsideIncidentOut, status_code=201)
def create_roadside_incident(
    payload: ChfRoadsideIncidentCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.roadside_incident.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, ChfRoadsideIncident, "reference", data.get("reference"), "reference", cid)
    obj = ChfRoadsideIncident(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/chf-roadside-incidents/{ident}", response_model=ChfRoadsideIncidentOut)
def update_roadside_incident(
    ident: int,
    payload: ChfRoadsideIncidentUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.roadside_incident.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ChfRoadsideIncident, ident, "Incidents de route")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/chf-roadside-incidents/{ident}", response_model=ChfRoadsideIncidentOut)
def delete_roadside_incident(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.roadside_incident.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ChfRoadsideIncident, ident, "Incidents de route")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Points de livraison ─────────────────────────────────────────────────

@router.get("/chf-delivery-stops", response_model=List[ChfDeliveryStopOut])
def list_delivery_stop(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.delivery_stop.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, ChfDeliveryStop, cid, {"statut": statut})


@router.post("/chf-delivery-stops", response_model=ChfDeliveryStopOut, status_code=201)
def create_delivery_stop(
    payload: ChfDeliveryStopCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.delivery_stop.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, ChfDeliveryStop, "reference", data.get("reference"), "reference", cid)
    obj = ChfDeliveryStop(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/chf-delivery-stops/{ident}", response_model=ChfDeliveryStopOut)
def update_delivery_stop(
    ident: int,
    payload: ChfDeliveryStopUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.delivery_stop.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ChfDeliveryStop, ident, "Points de livraison")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/chf-delivery-stops/{ident}", response_model=ChfDeliveryStopOut)
def delete_delivery_stop(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.delivery_stop.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ChfDeliveryStop, ident, "Points de livraison")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Releves de kilometrage ─────────────────────────────────────────────────

@router.get("/chf-mileage-logs", response_model=List[ChfMileageLogOut])
def list_mileage_log(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.mileage_log.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, ChfMileageLog, cid, {"statut": statut})


@router.post("/chf-mileage-logs", response_model=ChfMileageLogOut, status_code=201)
def create_mileage_log(
    payload: ChfMileageLogCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.mileage_log.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, ChfMileageLog, "reference", data.get("reference"), "reference", cid)
    obj = ChfMileageLog(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/chf-mileage-logs/{ident}", response_model=ChfMileageLogOut)
def update_mileage_log(
    ident: int,
    payload: ChfMileageLogUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.mileage_log.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ChfMileageLog, ident, "Releves de kilometrage")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/chf-mileage-logs/{ident}", response_model=ChfMileageLogOut)
def delete_mileage_log(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.mileage_log.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ChfMileageLog, ident, "Releves de kilometrage")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Controles d' arrimage ─────────────────────────────────────────────────

@router.get("/chf-load-securing-checks", response_model=List[ChfLoadSecuringCheckOut])
def list_load_securing_check(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.load_securing_check.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, ChfLoadSecuringCheck, cid, {"statut": statut})


@router.post("/chf-load-securing-checks", response_model=ChfLoadSecuringCheckOut, status_code=201)
def create_load_securing_check(
    payload: ChfLoadSecuringCheckCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.load_securing_check.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, ChfLoadSecuringCheck, "reference", data.get("reference"), "reference", cid)
    obj = ChfLoadSecuringCheck(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/chf-load-securing-checks/{ident}", response_model=ChfLoadSecuringCheckOut)
def update_load_securing_check(
    ident: int,
    payload: ChfLoadSecuringCheckUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.load_securing_check.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ChfLoadSecuringCheck, ident, "Controles d' arrimage")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/chf-load-securing-checks/{ident}", response_model=ChfLoadSecuringCheckOut)
def delete_load_securing_check(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.load_securing_check.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ChfLoadSecuringCheck, ident, "Controles d' arrimage")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Postes frontiere ─────────────────────────────────────────────────

@router.get("/chf-border-crossings", response_model=List[ChfBorderCrossingOut])
def list_border_crossing(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.border_crossing.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, ChfBorderCrossing, cid, {"statut": statut})


@router.post("/chf-border-crossings", response_model=ChfBorderCrossingOut, status_code=201)
def create_border_crossing(
    payload: ChfBorderCrossingCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.border_crossing.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, ChfBorderCrossing, "reference", data.get("reference"), "reference", cid)
    obj = ChfBorderCrossing(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/chf-border-crossings/{ident}", response_model=ChfBorderCrossingOut)
def update_border_crossing(
    ident: int,
    payload: ChfBorderCrossingUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.border_crossing.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ChfBorderCrossing, ident, "Postes frontiere")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/chf-border-crossings/{ident}", response_model=ChfBorderCrossingOut)
def delete_border_crossing(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.border_crossing.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ChfBorderCrossing, ident, "Postes frontiere")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── RDV de livraison ─────────────────────────────────────────────────

@router.get("/chf-delivery-appointments", response_model=List[ChfDeliveryAppointmentOut])
def list_delivery_appointment(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.delivery_appointment.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, ChfDeliveryAppointment, cid, {"statut": statut})


@router.post("/chf-delivery-appointments", response_model=ChfDeliveryAppointmentOut, status_code=201)
def create_delivery_appointment(
    payload: ChfDeliveryAppointmentCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.delivery_appointment.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, ChfDeliveryAppointment, "reference", data.get("reference"), "reference", cid)
    obj = ChfDeliveryAppointment(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/chf-delivery-appointments/{ident}", response_model=ChfDeliveryAppointmentOut)
def update_delivery_appointment(
    ident: int,
    payload: ChfDeliveryAppointmentUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.delivery_appointment.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ChfDeliveryAppointment, ident, "RDV de livraison")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/chf-delivery-appointments/{ident}", response_model=ChfDeliveryAppointmentOut)
def delete_delivery_appointment(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.delivery_appointment.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ChfDeliveryAppointment, ident, "RDV de livraison")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Remise d' EPI ─────────────────────────────────────────────────

@router.get("/chf-ppe-issues", response_model=List[ChfPpeIssueOut])
def list_ppe_issue(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.ppe_issue.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, ChfPpeIssue, cid, {"statut": statut})


@router.post("/chf-ppe-issues", response_model=ChfPpeIssueOut, status_code=201)
def create_ppe_issue(
    payload: ChfPpeIssueCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.ppe_issue.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, ChfPpeIssue, "reference", data.get("reference"), "reference", cid)
    obj = ChfPpeIssue(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/chf-ppe-issues/{ident}", response_model=ChfPpeIssueOut)
def update_ppe_issue(
    ident: int,
    payload: ChfPpeIssueUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.ppe_issue.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ChfPpeIssue, ident, "Remise d' EPI")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/chf-ppe-issues/{ident}", response_model=ChfPpeIssueOut)
def delete_ppe_issue(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.ppe_issue.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ChfPpeIssue, ident, "Remise d' EPI")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Relais de conduite ─────────────────────────────────────────────────

@router.get("/chf-shift-handovers", response_model=List[ChfShiftHandoverOut])
def list_shift_handover(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.shift_handover.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, ChfShiftHandover, cid, {"statut": statut})


@router.post("/chf-shift-handovers", response_model=ChfShiftHandoverOut, status_code=201)
def create_shift_handover(
    payload: ChfShiftHandoverCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.shift_handover.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, ChfShiftHandover, "reference", data.get("reference"), "reference", cid)
    obj = ChfShiftHandover(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/chf-shift-handovers/{ident}", response_model=ChfShiftHandoverOut)
def update_shift_handover(
    ident: int,
    payload: ChfShiftHandoverUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.shift_handover.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ChfShiftHandover, ident, "Relais de conduite")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/chf-shift-handovers/{ident}", response_model=ChfShiftHandoverOut)
def delete_shift_handover(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.shift_handover.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ChfShiftHandover, ident, "Relais de conduite")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Signalements de panne ─────────────────────────────────────────────────

@router.get("/chf-breakdown-reports", response_model=List[ChfBreakdownReportOut])
def list_breakdown_report(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.breakdown_report.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, ChfBreakdownReport, cid, {"statut": statut})


@router.post("/chf-breakdown-reports", response_model=ChfBreakdownReportOut, status_code=201)
def create_breakdown_report(
    payload: ChfBreakdownReportCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.breakdown_report.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, ChfBreakdownReport, "reference", data.get("reference"), "reference", cid)
    obj = ChfBreakdownReport(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/chf-breakdown-reports/{ident}", response_model=ChfBreakdownReportOut)
def update_breakdown_report(
    ident: int,
    payload: ChfBreakdownReportUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.breakdown_report.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ChfBreakdownReport, ident, "Signalements de panne")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/chf-breakdown-reports/{ident}", response_model=ChfBreakdownReportOut)
def delete_breakdown_report(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.breakdown_report.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ChfBreakdownReport, ident, "Signalements de panne")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Controles pneumatiques ─────────────────────────────────────────────────

@router.get("/chf-tyre-checks", response_model=List[ChfTyreCheckOut])
def list_tyre_check(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.tyre_check.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, ChfTyreCheck, cid, {"statut": statut})


@router.post("/chf-tyre-checks", response_model=ChfTyreCheckOut, status_code=201)
def create_tyre_check(
    payload: ChfTyreCheckCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.tyre_check.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, ChfTyreCheck, "reference", data.get("reference"), "reference", cid)
    obj = ChfTyreCheck(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/chf-tyre-checks/{ident}", response_model=ChfTyreCheckOut)
def update_tyre_check(
    ident: int,
    payload: ChfTyreCheckUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.tyre_check.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ChfTyreCheck, ident, "Controles pneumatiques")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/chf-tyre-checks/{ident}", response_model=ChfTyreCheckOut)
def delete_tyre_check(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.tyre_check.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ChfTyreCheck, ident, "Controles pneumatiques")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Photos de cargaison ─────────────────────────────────────────────────

@router.get("/chf-cargo-photos", response_model=List[ChfCargoPhotoOut])
def list_cargo_photo(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.cargo_photo.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, ChfCargoPhoto, cid, {"statut": statut})


@router.post("/chf-cargo-photos", response_model=ChfCargoPhotoOut, status_code=201)
def create_cargo_photo(
    payload: ChfCargoPhotoCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.cargo_photo.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, ChfCargoPhoto, "reference", data.get("reference"), "reference", cid)
    obj = ChfCargoPhoto(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/chf-cargo-photos/{ident}", response_model=ChfCargoPhotoOut)
def update_cargo_photo(
    ident: int,
    payload: ChfCargoPhotoUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.cargo_photo.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ChfCargoPhoto, ident, "Photos de cargaison")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/chf-cargo-photos/{ident}", response_model=ChfCargoPhotoOut)
def delete_cargo_photo(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.cargo_photo.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ChfCargoPhoto, ident, "Photos de cargaison")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj

