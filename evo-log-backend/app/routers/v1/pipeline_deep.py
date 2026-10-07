"""Routeur CRUD genere pour pipeline-oleoduc (expansion wave 5)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List

from app.core.database import get_db
from app.core.permissions import require_perm
from app.models.user import User
from app.models.pipeline_deep import (
    PipelineSection,
    PipelinePumpStation,
    PipelineStorageTank,
    PipelineMeteringPoint,
    PipelineProductBatch,
    PipelinePressureReading,
    PipelineLeakDetection,
    PipelineMaintenanceWork,
    PipelineInjectionCampaign,
    PipelineShipNomination,
)
from app.schemas.pipeline_deep import (
    PipelineSectionCreate, PipelineSectionUpdate, PipelineSectionOut,
    PipelinePumpStationCreate, PipelinePumpStationUpdate, PipelinePumpStationOut,
    PipelineStorageTankCreate, PipelineStorageTankUpdate, PipelineStorageTankOut,
    PipelineMeteringPointCreate, PipelineMeteringPointUpdate, PipelineMeteringPointOut,
    PipelineProductBatchCreate, PipelineProductBatchUpdate, PipelineProductBatchOut,
    PipelinePressureReadingCreate, PipelinePressureReadingUpdate, PipelinePressureReadingOut,
    PipelineLeakDetectionCreate, PipelineLeakDetectionUpdate, PipelineLeakDetectionOut,
    PipelineMaintenanceWorkCreate, PipelineMaintenanceWorkUpdate, PipelineMaintenanceWorkOut,
    PipelineInjectionCampaignCreate, PipelineInjectionCampaignUpdate, PipelineInjectionCampaignOut,
    PipelineShipNominationCreate, PipelineShipNominationUpdate, PipelineShipNominationOut,
)

router = APIRouter(tags=["pipeline-oleoduc (expansion)"])


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

@router.get("/nomenclatures", summary="Vocabulaire metier pipeline-oleoduc")
def nomenclatures(user: User = Depends(require_perm("pipeline.nomenclature.read"))):
    from app.models import pipeline_deep as _md
    import enum as _pyenum
    out = {}
    for name in dir(_md):
        obj = getattr(_md, name)
        if isinstance(obj, type) and issubclass(obj, _pyenum.Enum) and obj is not _pyenum.Enum:
            out[name.lower()] = [{"code": m.name, "valeur": m.value} for m in obj]
    return out


# ─── Troncons physiques ─────────────────────────────────────────

@router.get("/sections", response_model=List[PipelineSectionOut])
def list_sections(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("pipeline.sections.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, PipelineSection, cid, {"statut": statut})


@router.post("/sections", response_model=PipelineSectionOut, status_code=201)
def create_section(
    payload: PipelineSectionCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("pipeline.sections.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, PipelineSection, "code_section", data.get("code_section"), "code_section", cid)
    obj = PipelineSection(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/sections/{ident}", response_model=PipelineSectionOut)
def update_section(
    ident: int,
    payload: PipelineSectionUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("pipeline.sections.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, PipelineSection, ident, "Troncons physiques")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/sections/{ident}", response_model=PipelineSectionOut)
def delete_section(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("pipeline.sections.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, PipelineSection, ident, "Troncons physiques")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Stations de pompage ────────────────────────────────────────

@router.get("/pump-stations", response_model=List[PipelinePumpStationOut])
def list_pump_stations(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("pipeline.pump_stations.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, PipelinePumpStation, cid, {"statut": statut})


@router.post("/pump-stations", response_model=PipelinePumpStationOut, status_code=201)
def create_pump_station(
    payload: PipelinePumpStationCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("pipeline.pump_stations.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, PipelinePumpStation, "code_station", data.get("code_station"), "code_station", cid)
    obj = PipelinePumpStation(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/pump-stations/{ident}", response_model=PipelinePumpStationOut)
def update_pump_station(
    ident: int,
    payload: PipelinePumpStationUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("pipeline.pump_stations.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, PipelinePumpStation, ident, "Stations de pompage")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/pump-stations/{ident}", response_model=PipelinePumpStationOut)
def delete_pump_station(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("pipeline.pump_stations.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, PipelinePumpStation, ident, "Stations de pompage")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Cuves de stockage ──────────────────────────────────────────

@router.get("/storage-tanks", response_model=List[PipelineStorageTankOut])
def list_storage_tanks(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("pipeline.storage_tanks.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, PipelineStorageTank, cid, {"statut": statut})


@router.post("/storage-tanks", response_model=PipelineStorageTankOut, status_code=201)
def create_storage_tank(
    payload: PipelineStorageTankCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("pipeline.storage_tanks.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, PipelineStorageTank, "code_cuve", data.get("code_cuve"), "code_cuve", cid)
    obj = PipelineStorageTank(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/storage-tanks/{ident}", response_model=PipelineStorageTankOut)
def update_storage_tank(
    ident: int,
    payload: PipelineStorageTankUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("pipeline.storage_tanks.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, PipelineStorageTank, ident, "Cuves de stockage")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/storage-tanks/{ident}", response_model=PipelineStorageTankOut)
def delete_storage_tank(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("pipeline.storage_tanks.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, PipelineStorageTank, ident, "Cuves de stockage")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Points de comptage ─────────────────────────────────────────

@router.get("/metering-points", response_model=List[PipelineMeteringPointOut])
def list_metering_points(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("pipeline.metering_points.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, PipelineMeteringPoint, cid, {"statut": statut})


@router.post("/metering-points", response_model=PipelineMeteringPointOut, status_code=201)
def create_metering_point(
    payload: PipelineMeteringPointCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("pipeline.metering_points.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, PipelineMeteringPoint, "code_point", data.get("code_point"), "code_point", cid)
    obj = PipelineMeteringPoint(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/metering-points/{ident}", response_model=PipelineMeteringPointOut)
def update_metering_point(
    ident: int,
    payload: PipelineMeteringPointUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("pipeline.metering_points.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, PipelineMeteringPoint, ident, "Points de comptage")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/metering-points/{ident}", response_model=PipelineMeteringPointOut)
def delete_metering_point(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("pipeline.metering_points.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, PipelineMeteringPoint, ident, "Points de comptage")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Lots produit ───────────────────────────────────────────────

@router.get("/product-batches", response_model=List[PipelineProductBatchOut])
def list_product_batches(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("pipeline.product_batches.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, PipelineProductBatch, cid, {"statut": statut})


@router.post("/product-batches", response_model=PipelineProductBatchOut, status_code=201)
def create_product_batch(
    payload: PipelineProductBatchCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("pipeline.product_batches.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, PipelineProductBatch, "numero_lot", data.get("numero_lot"), "numero_lot", cid)
    obj = PipelineProductBatch(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/product-batches/{ident}", response_model=PipelineProductBatchOut)
def update_product_batch(
    ident: int,
    payload: PipelineProductBatchUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("pipeline.product_batches.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, PipelineProductBatch, ident, "Lots produit")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/product-batches/{ident}", response_model=PipelineProductBatchOut)
def delete_product_batch(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("pipeline.product_batches.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, PipelineProductBatch, ident, "Lots produit")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Releves pression SCADA ─────────────────────────────────────

@router.get("/pressure-readings", response_model=List[PipelinePressureReadingOut])
def list_pressure_readings(db: Session = Depends(get_db),
    user: User = Depends(require_perm("pipeline.pressure_readings.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, PipelinePressureReading, cid)


@router.post("/pressure-readings", response_model=PipelinePressureReadingOut, status_code=201)
def create_pressure_reading(
    payload: PipelinePressureReadingCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("pipeline.pressure_readings.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, PipelinePressureReading, "reference", data.get("reference"), "reference", cid)
    obj = PipelinePressureReading(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/pressure-readings/{ident}", response_model=PipelinePressureReadingOut)
def update_pressure_reading(
    ident: int,
    payload: PipelinePressureReadingUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("pipeline.pressure_readings.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, PipelinePressureReading, ident, "Releves pression")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/pressure-readings/{ident}", response_model=PipelinePressureReadingOut)
def delete_pressure_reading(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("pipeline.pressure_readings.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, PipelinePressureReading, ident, "Releves pression")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Detection de fuite ─────────────────────────────────────────

@router.get("/leak-detections", response_model=List[PipelineLeakDetectionOut])
def list_leak_detections(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("pipeline.leak_detections.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, PipelineLeakDetection, cid, {"statut": statut})


@router.post("/leak-detections", response_model=PipelineLeakDetectionOut, status_code=201)
def create_leak_detection(
    payload: PipelineLeakDetectionCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("pipeline.leak_detections.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, PipelineLeakDetection, "reference", data.get("reference"), "reference", cid)
    obj = PipelineLeakDetection(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/leak-detections/{ident}", response_model=PipelineLeakDetectionOut)
def update_leak_detection(
    ident: int,
    payload: PipelineLeakDetectionUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("pipeline.leak_detections.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, PipelineLeakDetection, ident, "Detection de fuite")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/leak-detections/{ident}", response_model=PipelineLeakDetectionOut)
def delete_leak_detection(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("pipeline.leak_detections.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, PipelineLeakDetection, ident, "Detection de fuite")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Travaux maintenance ────────────────────────────────────────

@router.get("/maintenance-works", response_model=List[PipelineMaintenanceWorkOut])
def list_maintenance_works(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("pipeline.maintenance_works.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, PipelineMaintenanceWork, cid, {"statut": statut})


@router.post("/maintenance-works", response_model=PipelineMaintenanceWorkOut, status_code=201)
def create_maintenance_work(
    payload: PipelineMaintenanceWorkCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("pipeline.maintenance_works.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, PipelineMaintenanceWork, "reference", data.get("reference"), "reference", cid)
    obj = PipelineMaintenanceWork(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/maintenance-works/{ident}", response_model=PipelineMaintenanceWorkOut)
def update_maintenance_work(
    ident: int,
    payload: PipelineMaintenanceWorkUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("pipeline.maintenance_works.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, PipelineMaintenanceWork, ident, "Travaux maintenance")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/maintenance-works/{ident}", response_model=PipelineMaintenanceWorkOut)
def delete_maintenance_work(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("pipeline.maintenance_works.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, PipelineMaintenanceWork, ident, "Travaux maintenance")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Campagnes injection ────────────────────────────────────────

@router.get("/injection-campaigns", response_model=List[PipelineInjectionCampaignOut])
def list_injection_campaigns(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("pipeline.injection_campaigns.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, PipelineInjectionCampaign, cid, {"statut": statut})


@router.post("/injection-campaigns", response_model=PipelineInjectionCampaignOut, status_code=201)
def create_injection_campaign(
    payload: PipelineInjectionCampaignCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("pipeline.injection_campaigns.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, PipelineInjectionCampaign, "reference", data.get("reference"), "reference", cid)
    obj = PipelineInjectionCampaign(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/injection-campaigns/{ident}", response_model=PipelineInjectionCampaignOut)
def update_injection_campaign(
    ident: int,
    payload: PipelineInjectionCampaignUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("pipeline.injection_campaigns.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, PipelineInjectionCampaign, ident, "Campagnes injection")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/injection-campaigns/{ident}", response_model=PipelineInjectionCampaignOut)
def delete_injection_campaign(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("pipeline.injection_campaigns.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, PipelineInjectionCampaign, ident, "Campagnes injection")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Nominations navires ────────────────────────────────────────

@router.get("/ship-nominations", response_model=List[PipelineShipNominationOut])
def list_ship_nominations(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("pipeline.ship_nominations.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, PipelineShipNomination, cid, {"statut": statut})


@router.post("/ship-nominations", response_model=PipelineShipNominationOut, status_code=201)
def create_ship_nomination(
    payload: PipelineShipNominationCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("pipeline.ship_nominations.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, PipelineShipNomination, "reference", data.get("reference"), "reference", cid)
    obj = PipelineShipNomination(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/ship-nominations/{ident}", response_model=PipelineShipNominationOut)
def update_ship_nomination(
    ident: int,
    payload: PipelineShipNominationUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("pipeline.ship_nominations.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, PipelineShipNomination, ident, "Nominations navires")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/ship-nominations/{ident}", response_model=PipelineShipNominationOut)
def delete_ship_nomination(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("pipeline.ship_nominations.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, PipelineShipNomination, ident, "Nominations navires")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj
