"""Routeur CRUD genere pour transport-fluvial (expansion)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List

from app.core.database import get_db
from app.core.permissions import require_perm
from app.models.user import User
from app.models.fluvial_b_deep import (
    FluvialCanalSection,
    FluvialConvoy,
    FluvialBallastOperation,
    FluvialWaterGauge,
    FluvialBerthingSlot,
    FluvialCrewRoster,
    FluvialCargoManifest,
    FluvialPortFee,
    FluvialVesselInspection,
)
from app.schemas.fluvial_b_deep import (
    FluvialCanalSectionCreate, FluvialCanalSectionUpdate, FluvialCanalSectionOut,
    FluvialConvoyCreate, FluvialConvoyUpdate, FluvialConvoyOut,
    FluvialBallastOperationCreate, FluvialBallastOperationUpdate, FluvialBallastOperationOut,
    FluvialWaterGaugeCreate, FluvialWaterGaugeUpdate, FluvialWaterGaugeOut,
    FluvialBerthingSlotCreate, FluvialBerthingSlotUpdate, FluvialBerthingSlotOut,
    FluvialCrewRosterCreate, FluvialCrewRosterUpdate, FluvialCrewRosterOut,
    FluvialCargoManifestCreate, FluvialCargoManifestUpdate, FluvialCargoManifestOut,
    FluvialPortFeeCreate, FluvialPortFeeUpdate, FluvialPortFeeOut,
    FluvialVesselInspectionCreate, FluvialVesselInspectionUpdate, FluvialVesselInspectionOut,
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
    from app.models import fluvial_b_deep as _md
    import enum as _pyenum
    out = {}
    for name in dir(_md):
        obj = getattr(_md, name)
        if isinstance(obj, type) and issubclass(obj, _pyenum.Enum) and obj is not _pyenum.Enum:
            out[name.lower()] = [{"code": m.name, "valeur": m.value} for m in obj]
    return out


# ─── Sections de voie navigable ─────────────────────────────────────────────────

@router.get("/fluvb-canal-sections", response_model=List[FluvialCanalSectionOut])
def list_canal_section(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("fluvial.canal_section.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, FluvialCanalSection, cid, {"statut": statut})


@router.post("/fluvb-canal-sections", response_model=FluvialCanalSectionOut, status_code=201)
def create_canal_section(
    payload: FluvialCanalSectionCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("fluvial.canal_section.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, FluvialCanalSection, "code_section", data.get("code_section"), "code_section", cid)
    obj = FluvialCanalSection(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/fluvb-canal-sections/{ident}", response_model=FluvialCanalSectionOut)
def update_canal_section(
    ident: int,
    payload: FluvialCanalSectionUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("fluvial.canal_section.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, FluvialCanalSection, ident, "Sections de voie navigable")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/fluvb-canal-sections/{ident}", response_model=FluvialCanalSectionOut)
def delete_canal_section(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("fluvial.canal_section.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, FluvialCanalSection, ident, "Sections de voie navigable")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Convois pousses ─────────────────────────────────────────────────

@router.get("/flvb-convoys", response_model=List[FluvialConvoyOut])
def list_convoy(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("fluvial.convoy.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, FluvialConvoy, cid, {"statut": statut})


@router.post("/flvb-convoys", response_model=FluvialConvoyOut, status_code=201)
def create_convoy(
    payload: FluvialConvoyCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("fluvial.convoy.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, FluvialConvoy, "numero_convoi", data.get("numero_convoi"), "numero_convoi", cid)
    obj = FluvialConvoy(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/flvb-convoys/{ident}", response_model=FluvialConvoyOut)
def update_convoy(
    ident: int,
    payload: FluvialConvoyUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("fluvial.convoy.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, FluvialConvoy, ident, "Convois pousses")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/flvb-convoys/{ident}", response_model=FluvialConvoyOut)
def delete_convoy(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("fluvial.convoy.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, FluvialConvoy, ident, "Convois pousses")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Lestage / delestage ─────────────────────────────────────────────────

@router.get("/flvb-ballast-operations", response_model=List[FluvialBallastOperationOut])
def list_ballast_operation(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("fluvial.ballast_operation.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, FluvialBallastOperation, cid, {"statut": statut})


@router.post("/flvb-ballast-operations", response_model=FluvialBallastOperationOut, status_code=201)
def create_ballast_operation(
    payload: FluvialBallastOperationCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("fluvial.ballast_operation.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, FluvialBallastOperation, "reference", data.get("reference"), "reference", cid)
    obj = FluvialBallastOperation(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/flvb-ballast-operations/{ident}", response_model=FluvialBallastOperationOut)
def update_ballast_operation(
    ident: int,
    payload: FluvialBallastOperationUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("fluvial.ballast_operation.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, FluvialBallastOperation, ident, "Lestage / delestage")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/flvb-ballast-operations/{ident}", response_model=FluvialBallastOperationOut)
def delete_ballast_operation(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("fluvial.ballast_operation.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, FluvialBallastOperation, ident, "Lestage / delestage")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Echelles d eau / limnimetres ─────────────────────────────────────────────────

@router.get("/flvb-water-gauges", response_model=List[FluvialWaterGaugeOut])
def list_water_gauge(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("fluvial.water_gauge.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, FluvialWaterGauge, cid, {"statut": statut})


@router.post("/flvb-water-gauges", response_model=FluvialWaterGaugeOut, status_code=201)
def create_water_gauge(
    payload: FluvialWaterGaugeCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("fluvial.water_gauge.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, FluvialWaterGauge, "code_poste", data.get("code_poste"), "code_poste", cid)
    obj = FluvialWaterGauge(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/flvb-water-gauges/{ident}", response_model=FluvialWaterGaugeOut)
def update_water_gauge(
    ident: int,
    payload: FluvialWaterGaugeUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("fluvial.water_gauge.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, FluvialWaterGauge, ident, "Echelles d eau / limnimetres")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/flvb-water-gauges/{ident}", response_model=FluvialWaterGaugeOut)
def delete_water_gauge(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("fluvial.water_gauge.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, FluvialWaterGauge, ident, "Echelles d eau / limnimetres")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Creneaux d amarrage ─────────────────────────────────────────────────

@router.get("/flvb-berthing-slots", response_model=List[FluvialBerthingSlotOut])
def list_berthing_slot(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("fluvial.berthing_slot.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, FluvialBerthingSlot, cid, {"statut": statut})


@router.post("/flvb-berthing-slots", response_model=FluvialBerthingSlotOut, status_code=201)
def create_berthing_slot(
    payload: FluvialBerthingSlotCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("fluvial.berthing_slot.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, FluvialBerthingSlot, "reference", data.get("reference"), "reference", cid)
    obj = FluvialBerthingSlot(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/flvb-berthing-slots/{ident}", response_model=FluvialBerthingSlotOut)
def update_berthing_slot(
    ident: int,
    payload: FluvialBerthingSlotUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("fluvial.berthing_slot.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, FluvialBerthingSlot, ident, "Creneaux d amarrage")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/flvb-berthing-slots/{ident}", response_model=FluvialBerthingSlotOut)
def delete_berthing_slot(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("fluvial.berthing_slot.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, FluvialBerthingSlot, ident, "Creneaux d amarrage")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Equipages fluviaux ─────────────────────────────────────────────────

@router.get("/flvb-crew-rosters", response_model=List[FluvialCrewRosterOut])
def list_crew_roster(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("fluvial.crew_roster.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, FluvialCrewRoster, cid, {"statut": statut})


@router.post("/flvb-crew-rosters", response_model=FluvialCrewRosterOut, status_code=201)
def create_crew_roster(
    payload: FluvialCrewRosterCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("fluvial.crew_roster.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, FluvialCrewRoster, "reference", data.get("reference"), "reference", cid)
    obj = FluvialCrewRoster(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/flvb-crew-rosters/{ident}", response_model=FluvialCrewRosterOut)
def update_crew_roster(
    ident: int,
    payload: FluvialCrewRosterUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("fluvial.crew_roster.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, FluvialCrewRoster, ident, "Equipages fluviaux")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/flvb-crew-rosters/{ident}", response_model=FluvialCrewRosterOut)
def delete_crew_roster(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("fluvial.crew_roster.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, FluvialCrewRoster, ident, "Equipages fluviaux")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Manifestes de chargement fluviaux ─────────────────────────────────────────────────

@router.get("/flvb-cargo-manifests", response_model=List[FluvialCargoManifestOut])
def list_cargo_manifest(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("fluvial.cargo_manifest.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, FluvialCargoManifest, cid, {"statut": statut})


@router.post("/flvb-cargo-manifests", response_model=FluvialCargoManifestOut, status_code=201)
def create_cargo_manifest(
    payload: FluvialCargoManifestCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("fluvial.cargo_manifest.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, FluvialCargoManifest, "numero_manifeste", data.get("numero_manifeste"), "numero_manifeste", cid)
    obj = FluvialCargoManifest(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/flvb-cargo-manifests/{ident}", response_model=FluvialCargoManifestOut)
def update_cargo_manifest(
    ident: int,
    payload: FluvialCargoManifestUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("fluvial.cargo_manifest.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, FluvialCargoManifest, ident, "Manifestes de chargement fluviaux")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/flvb-cargo-manifests/{ident}", response_model=FluvialCargoManifestOut)
def delete_cargo_manifest(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("fluvial.cargo_manifest.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, FluvialCargoManifest, ident, "Manifestes de chargement fluviaux")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Droits de port fluvial ─────────────────────────────────────────────────

@router.get("/flvb-port-fees", response_model=List[FluvialPortFeeOut])
def list_port_fee(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("fluvial.port_fee.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, FluvialPortFee, cid, {"statut": statut})


@router.post("/flvb-port-fees", response_model=FluvialPortFeeOut, status_code=201)
def create_port_fee(
    payload: FluvialPortFeeCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("fluvial.port_fee.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, FluvialPortFee, "code_tarif", data.get("code_tarif"), "code_tarif", cid)
    obj = FluvialPortFee(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/flvb-port-fees/{ident}", response_model=FluvialPortFeeOut)
def update_port_fee(
    ident: int,
    payload: FluvialPortFeeUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("fluvial.port_fee.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, FluvialPortFee, ident, "Droits de port fluvial")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/flvb-port-fees/{ident}", response_model=FluvialPortFeeOut)
def delete_port_fee(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("fluvial.port_fee.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, FluvialPortFee, ident, "Droits de port fluvial")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Visites techniques batellerie ─────────────────────────────────────────────────

@router.get("/flvb-vessel-inspections", response_model=List[FluvialVesselInspectionOut])
def list_vessel_inspection(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("fluvial.vessel_inspection.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, FluvialVesselInspection, cid, {"statut": statut})


@router.post("/flvb-vessel-inspections", response_model=FluvialVesselInspectionOut, status_code=201)
def create_vessel_inspection(
    payload: FluvialVesselInspectionCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("fluvial.vessel_inspection.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, FluvialVesselInspection, "numero_pv", data.get("numero_pv"), "numero_pv", cid)
    obj = FluvialVesselInspection(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/flvb-vessel-inspections/{ident}", response_model=FluvialVesselInspectionOut)
def update_vessel_inspection(
    ident: int,
    payload: FluvialVesselInspectionUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("fluvial.vessel_inspection.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, FluvialVesselInspection, ident, "Visites techniques batellerie")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/flvb-vessel-inspections/{ident}", response_model=FluvialVesselInspectionOut)
def delete_vessel_inspection(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("fluvial.vessel_inspection.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, FluvialVesselInspection, ident, "Visites techniques batellerie")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj

