"""Routeur CRUD genere pour transport-flotte (expansion)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List

from app.core.database import get_db
from app.core.permissions import require_perm
from app.models.user import User
from app.models.transport_deep import (
    VehicleRegistration,
    RoutePlan,
    CheckpointControl,
    CargoInsurance,
    FreightBill,
    Subcontractor,
    DangerousGoodsLoad,
    VehicleDocument,
    GpsDevice,
    TrafficPenalty,
    Convoy,
    FleetKpi,
)
from app.schemas.transport_deep import (
    VehicleRegistrationCreate, VehicleRegistrationUpdate, VehicleRegistrationOut,
    RoutePlanCreate, RoutePlanUpdate, RoutePlanOut,
    CheckpointControlCreate, CheckpointControlUpdate, CheckpointControlOut,
    CargoInsuranceCreate, CargoInsuranceUpdate, CargoInsuranceOut,
    FreightBillCreate, FreightBillUpdate, FreightBillOut,
    SubcontractorCreate, SubcontractorUpdate, SubcontractorOut,
    DangerousGoodsLoadCreate, DangerousGoodsLoadUpdate, DangerousGoodsLoadOut,
    VehicleDocumentCreate, VehicleDocumentUpdate, VehicleDocumentOut,
    GpsDeviceCreate, GpsDeviceUpdate, GpsDeviceOut,
    TrafficPenaltyCreate, TrafficPenaltyUpdate, TrafficPenaltyOut,
    ConvoyCreate, ConvoyUpdate, ConvoyOut,
    FleetKpiCreate, FleetKpiUpdate, FleetKpiOut,
)

router = APIRouter(tags=["transport-flotte (expansion)"])


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

@router.get("/nomenclatures", summary="Vocabulaire metier transport-flotte")
def nomenclatures(user: User = Depends(require_perm("transport.nomenclature.read"))):
    from app.models import transport_deep as _md
    import enum as _pyenum
    out = {}
    for name in dir(_md):
        obj = getattr(_md, name)
        if isinstance(obj, type) and issubclass(obj, _pyenum.Enum) and obj is not _pyenum.Enum:
            out[name.lower()] = [{"code": m.name, "valeur": m.value} for m in obj]
    return out


# ─── Fiche vehicule ─────────────────────────────────────────────────

@router.get("/vehicle-registrations", response_model=List[VehicleRegistrationOut])
def list_vehicle_registry(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.vehicle_registry.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, VehicleRegistration, cid, {"statut": statut})


@router.post("/vehicle-registrations", response_model=VehicleRegistrationOut, status_code=201)
def create_vehicle_registry(
    payload: VehicleRegistrationCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.vehicle_registry.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, VehicleRegistration, "numero_immatriculation", data.get("numero_immatriculation"), "numero_immatriculation", cid)
    obj = VehicleRegistration(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/vehicle-registrations/{ident}", response_model=VehicleRegistrationOut)
def update_vehicle_registry(
    ident: int,
    payload: VehicleRegistrationUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.vehicle_registry.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, VehicleRegistration, ident, "Fiche vehicule")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/vehicle-registrations/{ident}", response_model=VehicleRegistrationOut)
def delete_vehicle_registry(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.vehicle_registry.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, VehicleRegistration, ident, "Fiche vehicule")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Planification tournees ─────────────────────────────────────────────────

@router.get("/route-plans", response_model=List[RoutePlanOut])
def list_route_plan(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.route_plan.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, RoutePlan, cid, {"statut": statut})


@router.post("/route-plans", response_model=RoutePlanOut, status_code=201)
def create_route_plan(
    payload: RoutePlanCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.route_plan.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, RoutePlan, "code_tournee", data.get("code_tournee"), "code_tournee", cid)
    obj = RoutePlan(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/route-plans/{ident}", response_model=RoutePlanOut)
def update_route_plan(
    ident: int,
    payload: RoutePlanUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.route_plan.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, RoutePlan, ident, "Planification tournees")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/route-plans/{ident}", response_model=RoutePlanOut)
def delete_route_plan(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.route_plan.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, RoutePlan, ident, "Planification tournees")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Controles routiers et pesages ─────────────────────────────────────────────────

@router.get("/checkpoint-controls", response_model=List[CheckpointControlOut])
def list_checkpoint(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.checkpoint.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, CheckpointControl, cid, {"statut": statut})


@router.post("/checkpoint-controls", response_model=CheckpointControlOut, status_code=201)
def create_checkpoint(
    payload: CheckpointControlCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.checkpoint.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, CheckpointControl, "numero_pv", data.get("numero_pv"), "numero_pv", cid)
    obj = CheckpointControl(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/checkpoint-controls/{ident}", response_model=CheckpointControlOut)
def update_checkpoint(
    ident: int,
    payload: CheckpointControlUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.checkpoint.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CheckpointControl, ident, "Controles routiers et pesages")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/checkpoint-controls/{ident}", response_model=CheckpointControlOut)
def delete_checkpoint(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.checkpoint.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CheckpointControl, ident, "Controles routiers et pesages")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Assurance marchandise transportee ─────────────────────────────────────────────────

@router.get("/cargo-insurances", response_model=List[CargoInsuranceOut])
def list_cargo_insurance(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.cargo_insurance.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, CargoInsurance, cid, {"statut": statut})


@router.post("/cargo-insurances", response_model=CargoInsuranceOut, status_code=201)
def create_cargo_insurance(
    payload: CargoInsuranceCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.cargo_insurance.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, CargoInsurance, "numero_police", data.get("numero_police"), "numero_police", cid)
    obj = CargoInsurance(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/cargo-insurances/{ident}", response_model=CargoInsuranceOut)
def update_cargo_insurance(
    ident: int,
    payload: CargoInsuranceUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.cargo_insurance.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CargoInsurance, ident, "Assurance marchandise transportee")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/cargo-insurances/{ident}", response_model=CargoInsuranceOut)
def delete_cargo_insurance(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.cargo_insurance.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CargoInsurance, ident, "Assurance marchandise transportee")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Facturation fret ─────────────────────────────────────────────────

@router.get("/freight-bills", response_model=List[FreightBillOut])
def list_freight_billing(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.freight_billing.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, FreightBill, cid, {"statut": statut})


@router.post("/freight-bills", response_model=FreightBillOut, status_code=201)
def create_freight_billing(
    payload: FreightBillCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.freight_billing.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, FreightBill, "numero_facture", data.get("numero_facture"), "numero_facture", cid)
    obj = FreightBill(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/freight-bills/{ident}", response_model=FreightBillOut)
def update_freight_billing(
    ident: int,
    payload: FreightBillUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.freight_billing.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, FreightBill, ident, "Facturation fret")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/freight-bills/{ident}", response_model=FreightBillOut)
def delete_freight_billing(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.freight_billing.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, FreightBill, ident, "Facturation fret")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Transporteurs sous-traitants ─────────────────────────────────────────────────

@router.get("/subcontractors", response_model=List[SubcontractorOut])
def list_subcontractor(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.subcontractor.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, Subcontractor, cid, {"statut": statut})


@router.post("/subcontractors", response_model=SubcontractorOut, status_code=201)
def create_subcontractor(
    payload: SubcontractorCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.subcontractor.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, Subcontractor, "code_sous_traitant", data.get("code_sous_traitant"), "code_sous_traitant", cid)
    obj = Subcontractor(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/subcontractors/{ident}", response_model=SubcontractorOut)
def update_subcontractor(
    ident: int,
    payload: SubcontractorUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.subcontractor.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, Subcontractor, ident, "Transporteurs sous-traitants")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/subcontractors/{ident}", response_model=SubcontractorOut)
def delete_subcontractor(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.subcontractor.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, Subcontractor, ident, "Transporteurs sous-traitants")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Marchandises dangereuses ADR ─────────────────────────────────────────────────

@router.get("/dangerous-goods-loads", response_model=List[DangerousGoodsLoadOut])
def list_dangerous_goods(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.dangerous_goods.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, DangerousGoodsLoad, cid, {"statut": statut})


@router.post("/dangerous-goods-loads", response_model=DangerousGoodsLoadOut, status_code=201)
def create_dangerous_goods(
    payload: DangerousGoodsLoadCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.dangerous_goods.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, DangerousGoodsLoad, "reference", data.get("reference"), "reference", cid)
    obj = DangerousGoodsLoad(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/dangerous-goods-loads/{ident}", response_model=DangerousGoodsLoadOut)
def update_dangerous_goods(
    ident: int,
    payload: DangerousGoodsLoadUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.dangerous_goods.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, DangerousGoodsLoad, ident, "Marchandises dangereuses ADR")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/dangerous-goods-loads/{ident}", response_model=DangerousGoodsLoadOut)
def delete_dangerous_goods(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.dangerous_goods.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, DangerousGoodsLoad, ident, "Marchandises dangereuses ADR")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Cartes grises / assurances / vignettes ─────────────────────────────────────────────────

@router.get("/vehicle-documents", response_model=List[VehicleDocumentOut])
def list_vehicle_document(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.vehicle_document.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, VehicleDocument, cid, {"statut": statut})


@router.post("/vehicle-documents", response_model=VehicleDocumentOut, status_code=201)
def create_vehicle_document(
    payload: VehicleDocumentCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.vehicle_document.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, VehicleDocument, "numero_document", data.get("numero_document"), "numero_document", cid)
    obj = VehicleDocument(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/vehicle-documents/{ident}", response_model=VehicleDocumentOut)
def update_vehicle_document(
    ident: int,
    payload: VehicleDocumentUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.vehicle_document.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, VehicleDocument, ident, "Cartes grises / assurances / vignettes")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/vehicle-documents/{ident}", response_model=VehicleDocumentOut)
def delete_vehicle_document(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.vehicle_document.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, VehicleDocument, ident, "Cartes grises / assurances / vignettes")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Boitiers GPS / telematique ─────────────────────────────────────────────────

@router.get("/gps-devices", response_model=List[GpsDeviceOut])
def list_gps_device(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.gps_device.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, GpsDevice, cid, {"statut": statut})


@router.post("/gps-devices", response_model=GpsDeviceOut, status_code=201)
def create_gps_device(
    payload: GpsDeviceCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.gps_device.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, GpsDevice, "numero_serial_gps", data.get("numero_serial_gps"), "numero_serial_gps", cid)
    obj = GpsDevice(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/gps-devices/{ident}", response_model=GpsDeviceOut)
def update_gps_device(
    ident: int,
    payload: GpsDeviceUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.gps_device.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, GpsDevice, ident, "Boitiers GPS / telematique")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/gps-devices/{ident}", response_model=GpsDeviceOut)
def delete_gps_device(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.gps_device.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, GpsDevice, ident, "Boitiers GPS / telematique")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Infractions et PV routiers ─────────────────────────────────────────────────

@router.get("/traffic-penalties", response_model=List[TrafficPenaltyOut])
def list_penalty(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.penalty.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, TrafficPenalty, cid, {"statut": statut})


@router.post("/traffic-penalties", response_model=TrafficPenaltyOut, status_code=201)
def create_penalty(
    payload: TrafficPenaltyCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.penalty.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, TrafficPenalty, "numero_pv", data.get("numero_pv"), "numero_pv", cid)
    obj = TrafficPenalty(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/traffic-penalties/{ident}", response_model=TrafficPenaltyOut)
def update_penalty(
    ident: int,
    payload: TrafficPenaltyUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.penalty.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TrafficPenalty, ident, "Infractions et PV routiers")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/traffic-penalties/{ident}", response_model=TrafficPenaltyOut)
def delete_penalty(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.penalty.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TrafficPenalty, ident, "Infractions et PV routiers")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Convois et escorte ─────────────────────────────────────────────────

@router.get("/convoys", response_model=List[ConvoyOut])
def list_convoy(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.convoy.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, Convoy, cid, {"statut": statut})


@router.post("/convoys", response_model=ConvoyOut, status_code=201)
def create_convoy(
    payload: ConvoyCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.convoy.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, Convoy, "code_convoi", data.get("code_convoi"), "code_convoi", cid)
    obj = Convoy(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/convoys/{ident}", response_model=ConvoyOut)
def update_convoy(
    ident: int,
    payload: ConvoyUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.convoy.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, Convoy, ident, "Convois et escorte")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/convoys/{ident}", response_model=ConvoyOut)
def delete_convoy(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.convoy.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, Convoy, ident, "Convois et escorte")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── TCO et taux de service ─────────────────────────────────────────────────

@router.get("/fleet-kpis", response_model=List[FleetKpiOut])
def list_performance_kpi(db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.performance_kpi.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, FleetKpi, cid)


@router.post("/fleet-kpis", response_model=FleetKpiOut, status_code=201)
def create_performance_kpi(
    payload: FleetKpiCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.performance_kpi.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, FleetKpi, "reference", data.get("reference"), "reference", cid)
    obj = FleetKpi(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/fleet-kpis/{ident}", response_model=FleetKpiOut)
def update_performance_kpi(
    ident: int,
    payload: FleetKpiUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.performance_kpi.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, FleetKpi, ident, "TCO et taux de service")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/fleet-kpis/{ident}", response_model=FleetKpiOut)
def delete_performance_kpi(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.performance_kpi.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, FleetKpi, ident, "TCO et taux de service")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj

