"""Routeur CRUD genere pour transport-aerien (expansion)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List

from app.core.database import get_db
from app.core.permissions import require_perm
from app.models.user import User
from app.models.aerien_b_deep import (
    HouseAirWaybill,
    PerishableCargo,
    LiveAnimalShipment,
    CharteredFlight,
    AirCustomsClearance,
    ApronMovement,
    NoiseComplianceRecord,
)
from app.schemas.aerien_b_deep import (
    HouseAirWaybillCreate, HouseAirWaybillUpdate, HouseAirWaybillOut,
    PerishableCargoCreate, PerishableCargoUpdate, PerishableCargoOut,
    LiveAnimalShipmentCreate, LiveAnimalShipmentUpdate, LiveAnimalShipmentOut,
    CharteredFlightCreate, CharteredFlightUpdate, CharteredFlightOut,
    AirCustomsClearanceCreate, AirCustomsClearanceUpdate, AirCustomsClearanceOut,
    ApronMovementCreate, ApronMovementUpdate, ApronMovementOut,
    NoiseComplianceRecordCreate, NoiseComplianceRecordUpdate, NoiseComplianceRecordOut,
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
    from app.models import aerien_b_deep as _md
    import enum as _pyenum
    out = {}
    for name in dir(_md):
        obj = getattr(_md, name)
        if isinstance(obj, type) and issubclass(obj, _pyenum.Enum) and obj is not _pyenum.Enum:
            out[name.lower()] = [{"code": m.name, "valeur": m.value} for m in obj]
    return out


# ─── Lettres de transport house (HAWB) ─────────────────────────────────────────────────

@router.get("/airb-house-waybills", response_model=List[HouseAirWaybillOut])
def list_house_waybill(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("aerien.house_waybill.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, HouseAirWaybill, cid, {"statut": statut})


@router.post("/airb-house-waybills", response_model=HouseAirWaybillOut, status_code=201)
def create_house_waybill(
    payload: HouseAirWaybillCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("aerien.house_waybill.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, HouseAirWaybill, "numero_hawb", data.get("numero_hawb"), "numero_hawb", cid)
    obj = HouseAirWaybill(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/airb-house-waybills/{ident}", response_model=HouseAirWaybillOut)
def update_house_waybill(
    ident: int,
    payload: HouseAirWaybillUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("aerien.house_waybill.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, HouseAirWaybill, ident, "Lettres de transport house (HAWB)")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/airb-house-waybills/{ident}", response_model=HouseAirWaybillOut)
def delete_house_waybill(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("aerien.house_waybill.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, HouseAirWaybill, ident, "Lettres de transport house (HAWB)")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Fret perishable (chaine du froid) ─────────────────────────────────────────────────

@router.get("/airb-perishable-cargo", response_model=List[PerishableCargoOut])
def list_perishable_cargo(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("aerien.perishable_cargo.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, PerishableCargo, cid, {"statut": statut})


@router.post("/airb-perishable-cargo", response_model=PerishableCargoOut, status_code=201)
def create_perishable_cargo(
    payload: PerishableCargoCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("aerien.perishable_cargo.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, PerishableCargo, "reference", data.get("reference"), "reference", cid)
    obj = PerishableCargo(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/airb-perishable-cargo/{ident}", response_model=PerishableCargoOut)
def update_perishable_cargo(
    ident: int,
    payload: PerishableCargoUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("aerien.perishable_cargo.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, PerishableCargo, ident, "Fret perishable (chaine du froid)")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/airb-perishable-cargo/{ident}", response_model=PerishableCargoOut)
def delete_perishable_cargo(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("aerien.perishable_cargo.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, PerishableCargo, ident, "Fret perishable (chaine du froid)")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Fret vivant (animaux) ─────────────────────────────────────────────────

@router.get("/airb-live-animals", response_model=List[LiveAnimalShipmentOut])
def list_live_animal(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("aerien.live_animal.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, LiveAnimalShipment, cid, {"statut": statut})


@router.post("/airb-live-animals", response_model=LiveAnimalShipmentOut, status_code=201)
def create_live_animal(
    payload: LiveAnimalShipmentCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("aerien.live_animal.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, LiveAnimalShipment, "reference", data.get("reference"), "reference", cid)
    obj = LiveAnimalShipment(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/airb-live-animals/{ident}", response_model=LiveAnimalShipmentOut)
def update_live_animal(
    ident: int,
    payload: LiveAnimalShipmentUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("aerien.live_animal.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, LiveAnimalShipment, ident, "Fret vivant (animaux)")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/airb-live-animals/{ident}", response_model=LiveAnimalShipmentOut)
def delete_live_animal(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("aerien.live_animal.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, LiveAnimalShipment, ident, "Fret vivant (animaux)")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Vols affretes ─────────────────────────────────────────────────

@router.get("/airb-chartered-flights", response_model=List[CharteredFlightOut])
def list_chartered_flight(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("aerien.chartered_flight.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, CharteredFlight, cid, {"statut": statut})


@router.post("/airb-chartered-flights", response_model=CharteredFlightOut, status_code=201)
def create_chartered_flight(
    payload: CharteredFlightCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("aerien.chartered_flight.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, CharteredFlight, "numero_affretement", data.get("numero_affretement"), "numero_affretement", cid)
    obj = CharteredFlight(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/airb-chartered-flights/{ident}", response_model=CharteredFlightOut)
def update_chartered_flight(
    ident: int,
    payload: CharteredFlightUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("aerien.chartered_flight.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CharteredFlight, ident, "Vols affretes")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/airb-chartered-flights/{ident}", response_model=CharteredFlightOut)
def delete_chartered_flight(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("aerien.chartered_flight.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CharteredFlight, ident, "Vols affretes")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Dedouanement fret aerien ─────────────────────────────────────────────────

@router.get("/airb-customs-clearance", response_model=List[AirCustomsClearanceOut])
def list_customs_clearance(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("aerien.customs_clearance.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, AirCustomsClearance, cid, {"statut": statut})


@router.post("/airb-customs-clearance", response_model=AirCustomsClearanceOut, status_code=201)
def create_customs_clearance(
    payload: AirCustomsClearanceCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("aerien.customs_clearance.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, AirCustomsClearance, "numero_dossier", data.get("numero_dossier"), "numero_dossier", cid)
    obj = AirCustomsClearance(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/airb-customs-clearance/{ident}", response_model=AirCustomsClearanceOut)
def update_customs_clearance(
    ident: int,
    payload: AirCustomsClearanceUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("aerien.customs_clearance.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, AirCustomsClearance, ident, "Dedouanement fret aerien")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/airb-customs-clearance/{ident}", response_model=AirCustomsClearanceOut)
def delete_customs_clearance(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("aerien.customs_clearance.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, AirCustomsClearance, ident, "Dedouanement fret aerien")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Mouvements piste (apron) ─────────────────────────────────────────────────

@router.get("/airb-apron-movements", response_model=List[ApronMovementOut])
def list_apron_movement(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("aerien.apron_movement.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, ApronMovement, cid, {"statut": statut})


@router.post("/airb-apron-movements", response_model=ApronMovementOut, status_code=201)
def create_apron_movement(
    payload: ApronMovementCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("aerien.apron_movement.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, ApronMovement, "reference", data.get("reference"), "reference", cid)
    obj = ApronMovement(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/airb-apron-movements/{ident}", response_model=ApronMovementOut)
def update_apron_movement(
    ident: int,
    payload: ApronMovementUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("aerien.apron_movement.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ApronMovement, ident, "Mouvements piste (apron)")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/airb-apron-movements/{ident}", response_model=ApronMovementOut)
def delete_apron_movement(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("aerien.apron_movement.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ApronMovement, ident, "Mouvements piste (apron)")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Conformite nuisances sonores ─────────────────────────────────────────────────

@router.get("/airb-noise-compliance", response_model=List[NoiseComplianceRecordOut])
def list_noise_compliance(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("aerien.noise_compliance.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, NoiseComplianceRecord, cid, {"statut": statut})


@router.post("/airb-noise-compliance", response_model=NoiseComplianceRecordOut, status_code=201)
def create_noise_compliance(
    payload: NoiseComplianceRecordCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("aerien.noise_compliance.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, NoiseComplianceRecord, "reference", data.get("reference"), "reference", cid)
    obj = NoiseComplianceRecord(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/airb-noise-compliance/{ident}", response_model=NoiseComplianceRecordOut)
def update_noise_compliance(
    ident: int,
    payload: NoiseComplianceRecordUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("aerien.noise_compliance.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, NoiseComplianceRecord, ident, "Conformite nuisances sonores")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/airb-noise-compliance/{ident}", response_model=NoiseComplianceRecordOut)
def delete_noise_compliance(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("aerien.noise_compliance.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, NoiseComplianceRecord, ident, "Conformite nuisances sonores")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj

