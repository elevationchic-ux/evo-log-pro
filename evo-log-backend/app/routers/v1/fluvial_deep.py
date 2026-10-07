"""Routeur CRUD genere pour transport-fluvial (expansion)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List

from app.core.database import get_db
from app.core.permissions import require_perm
from app.models.user import User
from app.models.fluvial_deep import (
    FluvialBarge,
    FluvialTowboat,
    LockTransit,
    RiverDepthSurvey,
    FluvialTerminal,
    FluvialBulkOperation,
    FluvialSafetyRecord,
    FluvialTariff,
    FluvialWaybill,
    FluvialPosition,
)
from app.schemas.fluvial_deep import (
    FluvialBargeCreate, FluvialBargeUpdate, FluvialBargeOut,
    FluvialTowboatCreate, FluvialTowboatUpdate, FluvialTowboatOut,
    LockTransitCreate, LockTransitUpdate, LockTransitOut,
    RiverDepthSurveyCreate, RiverDepthSurveyUpdate, RiverDepthSurveyOut,
    FluvialTerminalCreate, FluvialTerminalUpdate, FluvialTerminalOut,
    FluvialBulkOperationCreate, FluvialBulkOperationUpdate, FluvialBulkOperationOut,
    FluvialSafetyRecordCreate, FluvialSafetyRecordUpdate, FluvialSafetyRecordOut,
    FluvialTariffCreate, FluvialTariffUpdate, FluvialTariffOut,
    FluvialWaybillCreate, FluvialWaybillUpdate, FluvialWaybillOut,
    FluvialPositionCreate, FluvialPositionUpdate, FluvialPositionOut,
)

router = APIRouter(tags=["transport-fluvial (expansion)"])


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

@router.get("/nomenclatures", summary="Vocabulaire metier transport-fluvial")
def nomenclatures(user: User = Depends(require_perm("fluvial.nomenclature.read"))):
    from app.models import fluvial_deep as _md
    import enum as _pyenum
    out = {}
    for name in dir(_md):
        obj = getattr(_md, name)
        if isinstance(obj, type) and issubclass(obj, _pyenum.Enum) and obj is not _pyenum.Enum:
            out[name.lower()] = [{"code": m.name, "valeur": m.value} for m in obj]
    return out


# ─── Flotte peniches / chalands ─────────────────────────────────────────────────

@router.get("/fluvial-barges", response_model=List[FluvialBargeOut])
def list_barge_fleet(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("fluvial.barge_fleet.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, FluvialBarge, cid, {"statut": statut})


@router.post("/fluvial-barges", response_model=FluvialBargeOut, status_code=201)
def create_barge_fleet(
    payload: FluvialBargeCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("fluvial.barge_fleet.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, FluvialBarge, "numero_flotte", data.get("numero_flotte"), "numero_flotte", cid)
    obj = FluvialBarge(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/fluvial-barges/{ident}", response_model=FluvialBargeOut)
def update_barge_fleet(
    ident: int,
    payload: FluvialBargeUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("fluvial.barge_fleet.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, FluvialBarge, ident, "Flotte peniches / chalands")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/fluvial-barges/{ident}", response_model=FluvialBargeOut)
def delete_barge_fleet(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("fluvial.barge_fleet.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, FluvialBarge, ident, "Flotte peniches / chalands")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Remorqueurs fluviaux ─────────────────────────────────────────────────

@router.get("/fluvial-towboats", response_model=List[FluvialTowboatOut])
def list_tow_fleet(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("fluvial.tow_fleet.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, FluvialTowboat, cid, {"statut": statut})


@router.post("/fluvial-towboats", response_model=FluvialTowboatOut, status_code=201)
def create_tow_fleet(
    payload: FluvialTowboatCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("fluvial.tow_fleet.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, FluvialTowboat, "numero_tug", data.get("numero_tug"), "numero_tug", cid)
    obj = FluvialTowboat(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/fluvial-towboats/{ident}", response_model=FluvialTowboatOut)
def update_tow_fleet(
    ident: int,
    payload: FluvialTowboatUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("fluvial.tow_fleet.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, FluvialTowboat, ident, "Remorqueurs fluviaux")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/fluvial-towboats/{ident}", response_model=FluvialTowboatOut)
def delete_tow_fleet(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("fluvial.tow_fleet.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, FluvialTowboat, ident, "Remorqueurs fluviaux")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Transits d'ecluses ─────────────────────────────────────────────────

@router.get("/fluvial-lock-transits", response_model=List[LockTransitOut])
def list_locks(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("fluvial.locks.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, LockTransit, cid, {"statut": statut})


@router.post("/fluvial-lock-transits", response_model=LockTransitOut, status_code=201)
def create_locks(
    payload: LockTransitCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("fluvial.locks.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, LockTransit, "reference", data.get("reference"), "reference", cid)
    obj = LockTransit(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/fluvial-lock-transits/{ident}", response_model=LockTransitOut)
def update_locks(
    ident: int,
    payload: LockTransitUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("fluvial.locks.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, LockTransit, ident, "Transits d'ecluses")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/fluvial-lock-transits/{ident}", response_model=LockTransitOut)
def delete_locks(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("fluvial.locks.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, LockTransit, ident, "Transits d'ecluses")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Sondes bathymetriques ─────────────────────────────────────────────────

@router.get("/fluvial-depth-surveys", response_model=List[RiverDepthSurveyOut])
def list_depth(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("fluvial.depth.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, RiverDepthSurvey, cid, {"statut": statut})


@router.post("/fluvial-depth-surveys", response_model=RiverDepthSurveyOut, status_code=201)
def create_depth(
    payload: RiverDepthSurveyCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("fluvial.depth.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, RiverDepthSurvey, "reference", data.get("reference"), "reference", cid)
    obj = RiverDepthSurvey(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/fluvial-depth-surveys/{ident}", response_model=RiverDepthSurveyOut)
def update_depth(
    ident: int,
    payload: RiverDepthSurveyUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("fluvial.depth.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, RiverDepthSurvey, ident, "Sondes bathymetriques")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/fluvial-depth-surveys/{ident}", response_model=RiverDepthSurveyOut)
def delete_depth(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("fluvial.depth.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, RiverDepthSurvey, ident, "Sondes bathymetriques")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Terminaux fluviaux ─────────────────────────────────────────────────

@router.get("/fluvial-terminals", response_model=List[FluvialTerminalOut])
def list_terminals(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("fluvial.terminals.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, FluvialTerminal, cid, {"statut": statut})


@router.post("/fluvial-terminals", response_model=FluvialTerminalOut, status_code=201)
def create_terminals(
    payload: FluvialTerminalCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("fluvial.terminals.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, FluvialTerminal, "code_terminal", data.get("code_terminal"), "code_terminal", cid)
    obj = FluvialTerminal(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/fluvial-terminals/{ident}", response_model=FluvialTerminalOut)
def update_terminals(
    ident: int,
    payload: FluvialTerminalUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("fluvial.terminals.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, FluvialTerminal, ident, "Terminaux fluviaux")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/fluvial-terminals/{ident}", response_model=FluvialTerminalOut)
def delete_terminals(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("fluvial.terminals.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, FluvialTerminal, ident, "Terminaux fluviaux")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Vrac fluvial ─────────────────────────────────────────────────

@router.get("/fluvial-bulk-operations", response_model=List[FluvialBulkOperationOut])
def list_bulk(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("fluvial.bulk.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, FluvialBulkOperation, cid, {"statut": statut})


@router.post("/fluvial-bulk-operations", response_model=FluvialBulkOperationOut, status_code=201)
def create_bulk(
    payload: FluvialBulkOperationCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("fluvial.bulk.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, FluvialBulkOperation, "reference", data.get("reference"), "reference", cid)
    obj = FluvialBulkOperation(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/fluvial-bulk-operations/{ident}", response_model=FluvialBulkOperationOut)
def update_bulk(
    ident: int,
    payload: FluvialBulkOperationUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("fluvial.bulk.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, FluvialBulkOperation, ident, "Vrac fluvial")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/fluvial-bulk-operations/{ident}", response_model=FluvialBulkOperationOut)
def delete_bulk(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("fluvial.bulk.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, FluvialBulkOperation, ident, "Vrac fluvial")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Securite navigation ─────────────────────────────────────────────────

@router.get("/fluvial-safety-records", response_model=List[FluvialSafetyRecordOut])
def list_safety(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("fluvial.safety.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, FluvialSafetyRecord, cid, {"statut": statut})


@router.post("/fluvial-safety-records", response_model=FluvialSafetyRecordOut, status_code=201)
def create_safety(
    payload: FluvialSafetyRecordCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("fluvial.safety.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, FluvialSafetyRecord, "reference", data.get("reference"), "reference", cid)
    obj = FluvialSafetyRecord(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/fluvial-safety-records/{ident}", response_model=FluvialSafetyRecordOut)
def update_safety(
    ident: int,
    payload: FluvialSafetyRecordUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("fluvial.safety.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, FluvialSafetyRecord, ident, "Securite navigation")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/fluvial-safety-records/{ident}", response_model=FluvialSafetyRecordOut)
def delete_safety(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("fluvial.safety.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, FluvialSafetyRecord, ident, "Securite navigation")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Tarification fluviale ─────────────────────────────────────────────────

@router.get("/fluvial-tariffs", response_model=List[FluvialTariffOut])
def list_tariffs(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("fluvial.tariffs.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, FluvialTariff, cid, {"statut": statut})


@router.post("/fluvial-tariffs", response_model=FluvialTariffOut, status_code=201)
def create_tariffs(
    payload: FluvialTariffCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("fluvial.tariffs.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, FluvialTariff, "code_tarif", data.get("code_tarif"), "code_tarif", cid)
    obj = FluvialTariff(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/fluvial-tariffs/{ident}", response_model=FluvialTariffOut)
def update_tariffs(
    ident: int,
    payload: FluvialTariffUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("fluvial.tariffs.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, FluvialTariff, ident, "Tarification fluviale")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/fluvial-tariffs/{ident}", response_model=FluvialTariffOut)
def delete_tariffs(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("fluvial.tariffs.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, FluvialTariff, ident, "Tarification fluviale")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Lettres de voiture fluviale CMNI ─────────────────────────────────────────────────

@router.get("/fluvial-waybills", response_model=List[FluvialWaybillOut])
def list_waybills(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("fluvial.waybills.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, FluvialWaybill, cid, {"statut": statut})


@router.post("/fluvial-waybills", response_model=FluvialWaybillOut, status_code=201)
def create_waybills(
    payload: FluvialWaybillCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("fluvial.waybills.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, FluvialWaybill, "numero", data.get("numero"), "numero", cid)
    obj = FluvialWaybill(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/fluvial-waybills/{ident}", response_model=FluvialWaybillOut)
def update_waybills(
    ident: int,
    payload: FluvialWaybillUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("fluvial.waybills.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, FluvialWaybill, ident, "Lettres de voiture fluviale CMNI")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/fluvial-waybills/{ident}", response_model=FluvialWaybillOut)
def delete_waybills(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("fluvial.waybills.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, FluvialWaybill, ident, "Lettres de voiture fluviale CMNI")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Positionnement flotte fluviale ─────────────────────────────────────────────────

@router.get("/fluvial-positions", response_model=List[FluvialPositionOut])
def list_positions(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("fluvial.positions.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, FluvialPosition, cid, {"statut": statut})


@router.post("/fluvial-positions", response_model=FluvialPositionOut, status_code=201)
def create_positions(
    payload: FluvialPositionCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("fluvial.positions.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, FluvialPosition, "reference", data.get("reference"), "reference", cid)
    obj = FluvialPosition(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/fluvial-positions/{ident}", response_model=FluvialPositionOut)
def update_positions(
    ident: int,
    payload: FluvialPositionUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("fluvial.positions.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, FluvialPosition, ident, "Positionnement flotte fluviale")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/fluvial-positions/{ident}", response_model=FluvialPositionOut)
def delete_positions(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("fluvial.positions.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, FluvialPosition, ident, "Positionnement flotte fluviale")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj

