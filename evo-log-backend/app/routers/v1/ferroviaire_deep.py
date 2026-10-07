"""Routeur CRUD genere pour transport-ferroviaire (expansion)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List

from app.core.database import get_db
from app.core.permissions import require_perm
from app.models.user import User
from app.models.ferroviaire_deep import (
    RailWagon,
    RailLocomotive,
    RailTrainPath,
    RailShuntingYard,
    RailTerminal,
    RailConsistencyPlan,
    RailWaybill,
    RailTariff,
    RailWagonTracking,
    RailWagonMaintenance,
    RailSafetyRecord,
    RailCorridor,
)
from app.schemas.ferroviaire_deep import (
    RailWagonCreate, RailWagonUpdate, RailWagonOut,
    RailLocomotiveCreate, RailLocomotiveUpdate, RailLocomotiveOut,
    RailTrainPathCreate, RailTrainPathUpdate, RailTrainPathOut,
    RailShuntingYardCreate, RailShuntingYardUpdate, RailShuntingYardOut,
    RailTerminalCreate, RailTerminalUpdate, RailTerminalOut,
    RailConsistencyPlanCreate, RailConsistencyPlanUpdate, RailConsistencyPlanOut,
    RailWaybillCreate, RailWaybillUpdate, RailWaybillOut,
    RailTariffCreate, RailTariffUpdate, RailTariffOut,
    RailWagonTrackingCreate, RailWagonTrackingUpdate, RailWagonTrackingOut,
    RailWagonMaintenanceCreate, RailWagonMaintenanceUpdate, RailWagonMaintenanceOut,
    RailSafetyRecordCreate, RailSafetyRecordUpdate, RailSafetyRecordOut,
    RailCorridorCreate, RailCorridorUpdate, RailCorridorOut,
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
    from app.models import ferroviaire_deep as _md
    import enum as _pyenum
    out = {}
    for name in dir(_md):
        obj = getattr(_md, name)
        if isinstance(obj, type) and issubclass(obj, _pyenum.Enum) and obj is not _pyenum.Enum:
            out[name.lower()] = [{"code": m.name, "valeur": m.value} for m in obj]
    return out


# ─── Parc wagons ─────────────────────────────────────────────────

@router.get("/rail-wagons", response_model=List[RailWagonOut])
def list_wagon_fleet(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("ferroviaire.wagon_fleet.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, RailWagon, cid, {"statut": statut})


@router.post("/rail-wagons", response_model=RailWagonOut, status_code=201)
def create_wagon_fleet(
    payload: RailWagonCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("ferroviaire.wagon_fleet.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, RailWagon, "numeration_wagon", data.get("numeration_wagon"), "numeration_wagon", cid)
    obj = RailWagon(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/rail-wagons/{ident}", response_model=RailWagonOut)
def update_wagon_fleet(
    ident: int,
    payload: RailWagonUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("ferroviaire.wagon_fleet.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, RailWagon, ident, "Parc wagons")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/rail-wagons/{ident}", response_model=RailWagonOut)
def delete_wagon_fleet(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("ferroviaire.wagon_fleet.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, RailWagon, ident, "Parc wagons")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Parc locomotives ─────────────────────────────────────────────────

@router.get("/rail-locomotives", response_model=List[RailLocomotiveOut])
def list_locomotive_fleet(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("ferroviaire.locomotive_fleet.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, RailLocomotive, cid, {"statut": statut})


@router.post("/rail-locomotives", response_model=RailLocomotiveOut, status_code=201)
def create_locomotive_fleet(
    payload: RailLocomotiveCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("ferroviaire.locomotive_fleet.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, RailLocomotive, "numero_series", data.get("numero_series"), "numero_series", cid)
    obj = RailLocomotive(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/rail-locomotives/{ident}", response_model=RailLocomotiveOut)
def update_locomotive_fleet(
    ident: int,
    payload: RailLocomotiveUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("ferroviaire.locomotive_fleet.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, RailLocomotive, ident, "Parc locomotives")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/rail-locomotives/{ident}", response_model=RailLocomotiveOut)
def delete_locomotive_fleet(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("ferroviaire.locomotive_fleet.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, RailLocomotive, ident, "Parc locomotives")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Sillons de circulation ─────────────────────────────────────────────────

@router.get("/rail-train-paths", response_model=List[RailTrainPathOut])
def list_train_paths(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("ferroviaire.train_paths.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, RailTrainPath, cid, {"statut": statut})


@router.post("/rail-train-paths", response_model=RailTrainPathOut, status_code=201)
def create_train_paths(
    payload: RailTrainPathCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("ferroviaire.train_paths.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, RailTrainPath, "code_sillon", data.get("code_sillon"), "code_sillon", cid)
    obj = RailTrainPath(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/rail-train-paths/{ident}", response_model=RailTrainPathOut)
def update_train_paths(
    ident: int,
    payload: RailTrainPathUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("ferroviaire.train_paths.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, RailTrainPath, ident, "Sillons de circulation")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/rail-train-paths/{ident}", response_model=RailTrainPathOut)
def delete_train_paths(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("ferroviaire.train_paths.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, RailTrainPath, ident, "Sillons de circulation")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Gares de triage ─────────────────────────────────────────────────

@router.get("/rail-shunting-yards", response_model=List[RailShuntingYardOut])
def list_shunting_yards(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("ferroviaire.shunting_yards.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, RailShuntingYard, cid, {"statut": statut})


@router.post("/rail-shunting-yards", response_model=RailShuntingYardOut, status_code=201)
def create_shunting_yards(
    payload: RailShuntingYardCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("ferroviaire.shunting_yards.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, RailShuntingYard, "code_triage", data.get("code_triage"), "code_triage", cid)
    obj = RailShuntingYard(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/rail-shunting-yards/{ident}", response_model=RailShuntingYardOut)
def update_shunting_yards(
    ident: int,
    payload: RailShuntingYardUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("ferroviaire.shunting_yards.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, RailShuntingYard, ident, "Gares de triage")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/rail-shunting-yards/{ident}", response_model=RailShuntingYardOut)
def delete_shunting_yards(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("ferroviaire.shunting_yards.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, RailShuntingYard, ident, "Gares de triage")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Terminaux fer portuaires ─────────────────────────────────────────────────

@router.get("/rail-terminals", response_model=List[RailTerminalOut])
def list_rail_terminals(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("ferroviaire.rail_terminals.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, RailTerminal, cid, {"statut": statut})


@router.post("/rail-terminals", response_model=RailTerminalOut, status_code=201)
def create_rail_terminals(
    payload: RailTerminalCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("ferroviaire.rail_terminals.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, RailTerminal, "code_terminal", data.get("code_terminal"), "code_terminal", cid)
    obj = RailTerminal(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/rail-terminals/{ident}", response_model=RailTerminalOut)
def update_rail_terminals(
    ident: int,
    payload: RailTerminalUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("ferroviaire.rail_terminals.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, RailTerminal, ident, "Terminaux fer portuaires")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/rail-terminals/{ident}", response_model=RailTerminalOut)
def delete_rail_terminals(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("ferroviaire.rail_terminals.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, RailTerminal, ident, "Terminaux fer portuaires")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Plans de composition ─────────────────────────────────────────────────

@router.get("/rail-consistency-plans", response_model=List[RailConsistencyPlanOut])
def list_consistency(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("ferroviaire.consistency.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, RailConsistencyPlan, cid, {"statut": statut})


@router.post("/rail-consistency-plans", response_model=RailConsistencyPlanOut, status_code=201)
def create_consistency(
    payload: RailConsistencyPlanCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("ferroviaire.consistency.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, RailConsistencyPlan, "reference", data.get("reference"), "reference", cid)
    obj = RailConsistencyPlan(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/rail-consistency-plans/{ident}", response_model=RailConsistencyPlanOut)
def update_consistency(
    ident: int,
    payload: RailConsistencyPlanUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("ferroviaire.consistency.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, RailConsistencyPlan, ident, "Plans de composition")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/rail-consistency-plans/{ident}", response_model=RailConsistencyPlanOut)
def delete_consistency(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("ferroviaire.consistency.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, RailConsistencyPlan, ident, "Plans de composition")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Lettres de voiture CIM/OTIF ─────────────────────────────────────────────────

@router.get("/rail-waybills", response_model=List[RailWaybillOut])
def list_waybills(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("ferroviaire.waybills.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, RailWaybill, cid, {"statut": statut})


@router.post("/rail-waybills", response_model=RailWaybillOut, status_code=201)
def create_waybills(
    payload: RailWaybillCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("ferroviaire.waybills.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, RailWaybill, "numero_lcv", data.get("numero_lcv"), "numero_lcv", cid)
    obj = RailWaybill(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/rail-waybills/{ident}", response_model=RailWaybillOut)
def update_waybills(
    ident: int,
    payload: RailWaybillUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("ferroviaire.waybills.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, RailWaybill, ident, "Lettres de voiture CIM/OTIF")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/rail-waybills/{ident}", response_model=RailWaybillOut)
def delete_waybills(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("ferroviaire.waybills.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, RailWaybill, ident, "Lettres de voiture CIM/OTIF")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Tarification fret fer ─────────────────────────────────────────────────

@router.get("/rail-tariffs", response_model=List[RailTariffOut])
def list_tariffs(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("ferroviaire.tariffs.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, RailTariff, cid, {"statut": statut})


@router.post("/rail-tariffs", response_model=RailTariffOut, status_code=201)
def create_tariffs(
    payload: RailTariffCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("ferroviaire.tariffs.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, RailTariff, "code_tarif", data.get("code_tarif"), "code_tarif", cid)
    obj = RailTariff(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/rail-tariffs/{ident}", response_model=RailTariffOut)
def update_tariffs(
    ident: int,
    payload: RailTariffUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("ferroviaire.tariffs.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, RailTariff, ident, "Tarification fret fer")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/rail-tariffs/{ident}", response_model=RailTariffOut)
def delete_tariffs(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("ferroviaire.tariffs.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, RailTariff, ident, "Tarification fret fer")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Suivi wagons / telegrammes RID ─────────────────────────────────────────────────

@router.get("/rail-wagon-tracking", response_model=List[RailWagonTrackingOut])
def list_tracking(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("ferroviaire.tracking.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, RailWagonTracking, cid, {"statut": statut})


@router.post("/rail-wagon-tracking", response_model=RailWagonTrackingOut, status_code=201)
def create_tracking(
    payload: RailWagonTrackingCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("ferroviaire.tracking.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, RailWagonTracking, "reference", data.get("reference"), "reference", cid)
    obj = RailWagonTracking(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/rail-wagon-tracking/{ident}", response_model=RailWagonTrackingOut)
def update_tracking(
    ident: int,
    payload: RailWagonTrackingUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("ferroviaire.tracking.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, RailWagonTracking, ident, "Suivi wagons / telegrammes RID")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/rail-wagon-tracking/{ident}", response_model=RailWagonTrackingOut)
def delete_tracking(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("ferroviaire.tracking.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, RailWagonTracking, ident, "Suivi wagons / telegrammes RID")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Maintenance parc wagon ─────────────────────────────────────────────────

@router.get("/rail-wagon-maintenance", response_model=List[RailWagonMaintenanceOut])
def list_maintenance(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("ferroviaire.maintenance.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, RailWagonMaintenance, cid, {"statut": statut})


@router.post("/rail-wagon-maintenance", response_model=RailWagonMaintenanceOut, status_code=201)
def create_maintenance(
    payload: RailWagonMaintenanceCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("ferroviaire.maintenance.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, RailWagonMaintenance, "reference", data.get("reference"), "reference", cid)
    obj = RailWagonMaintenance(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/rail-wagon-maintenance/{ident}", response_model=RailWagonMaintenanceOut)
def update_maintenance(
    ident: int,
    payload: RailWagonMaintenanceUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("ferroviaire.maintenance.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, RailWagonMaintenance, ident, "Maintenance parc wagon")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/rail-wagon-maintenance/{ident}", response_model=RailWagonMaintenanceOut)
def delete_maintenance(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("ferroviaire.maintenance.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, RailWagonMaintenance, ident, "Maintenance parc wagon")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Securite circulations ─────────────────────────────────────────────────

@router.get("/rail-safety-records", response_model=List[RailSafetyRecordOut])
def list_safety(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("ferroviaire.safety.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, RailSafetyRecord, cid, {"statut": statut})


@router.post("/rail-safety-records", response_model=RailSafetyRecordOut, status_code=201)
def create_safety(
    payload: RailSafetyRecordCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("ferroviaire.safety.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, RailSafetyRecord, "reference", data.get("reference"), "reference", cid)
    obj = RailSafetyRecord(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/rail-safety-records/{ident}", response_model=RailSafetyRecordOut)
def update_safety(
    ident: int,
    payload: RailSafetyRecordUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("ferroviaire.safety.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, RailSafetyRecord, ident, "Securite circulations")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/rail-safety-records/{ident}", response_model=RailSafetyRecordOut)
def delete_safety(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("ferroviaire.safety.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, RailSafetyRecord, ident, "Securite circulations")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Corridors fer-port ─────────────────────────────────────────────────

@router.get("/rail-corridors", response_model=List[RailCorridorOut])
def list_corridors(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("ferroviaire.corridors.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, RailCorridor, cid, {"statut": statut})


@router.post("/rail-corridors", response_model=RailCorridorOut, status_code=201)
def create_corridors(
    payload: RailCorridorCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("ferroviaire.corridors.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, RailCorridor, "code_corridor", data.get("code_corridor"), "code_corridor", cid)
    obj = RailCorridor(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/rail-corridors/{ident}", response_model=RailCorridorOut)
def update_corridors(
    ident: int,
    payload: RailCorridorUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("ferroviaire.corridors.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, RailCorridor, ident, "Corridors fer-port")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/rail-corridors/{ident}", response_model=RailCorridorOut)
def delete_corridors(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("ferroviaire.corridors.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, RailCorridor, ident, "Corridors fer-port")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj

