"""Routeur CRUD genere pour courier-express (expansion wave 5)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List

from app.core.database import get_db
from app.core.permissions import require_perm
from app.models.user import User
from app.models.courier_deep import (
    CourierParcel,
    CourierWaybill,
    CourierHub,
    CourierDeliveryZone,
    CourierRoute,
    CourierCourier,
    CourierPod,
    CourierSla,
    CourierLocker,
    CourierVehicule,
    CourierTarif,
    CourierException,
)
from app.schemas.courier_deep import (
    CourierParcelCreate, CourierParcelUpdate, CourierParcelOut,
    CourierWaybillCreate, CourierWaybillUpdate, CourierWaybillOut,
    CourierHubCreate, CourierHubUpdate, CourierHubOut,
    CourierDeliveryZoneCreate, CourierDeliveryZoneUpdate, CourierDeliveryZoneOut,
    CourierRouteCreate, CourierRouteUpdate, CourierRouteOut,
    CourierCourierCreate, CourierCourierUpdate, CourierCourierOut,
    CourierPodCreate, CourierPodUpdate, CourierPodOut,
    CourierSlaCreate, CourierSlaUpdate, CourierSlaOut,
    CourierLockerCreate, CourierLockerUpdate, CourierLockerOut,
    CourierVehiculeCreate, CourierVehiculeUpdate, CourierVehiculeOut,
    CourierTarifCreate, CourierTarifUpdate, CourierTarifOut,
    CourierExceptionCreate, CourierExceptionUpdate, CourierExceptionOut,
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

@router.get("/nomenclatures", summary=f"Vocabulaire metier {tag_label}")
def nomenclatures(user: User = Depends(require_perm("courier.nomenclature.read"))):
    from app.models import courier_deep as _md
    import enum as _pyenum
    out = {}
    for name in dir(_md):
        obj = getattr(_md, name)
        if isinstance(obj, type) and issubclass(obj, _pyenum.Enum) and obj is not _pyenum.Enum:
            out[name.lower()] = [{"code": m.name, "valeur": m.value} for m in obj]
    return out


# ─── Colis ─────────────────────────────────────────────

@router.get("/parcels", response_model=List[CourierParcelOut])
def list_parcels(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("courier.parcels.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, CourierParcel, cid, {'statut': statut})


@router.post("/parcels", response_model=CourierParcelOut, status_code=201)
def create_parcels(
    payload: CourierParcelCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("courier.parcels.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, CourierParcel, "numero_colis", data.get("numero_colis"), "numero_colis", cid)
    obj = CourierParcel(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/parcels/{ident}", response_model=CourierParcelOut)
def update_parcels(
    ident: int,
    payload: CourierParcelUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("courier.parcels.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CourierParcel, ident, "Colis")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/parcels/{ident}", response_model=CourierParcelOut)
def delete_parcels(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("courier.parcels.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CourierParcel, ident, "Colis")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Lettre voiture express ─────────────────────────────────────────────

@router.get("/waybills", response_model=List[CourierWaybillOut])
def list_waybills(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("courier.waybills.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, CourierWaybill, cid, {'statut': statut})


@router.post("/waybills", response_model=CourierWaybillOut, status_code=201)
def create_waybills(
    payload: CourierWaybillCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("courier.waybills.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, CourierWaybill, "numero_lse", data.get("numero_lse"), "numero_lse", cid)
    obj = CourierWaybill(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/waybills/{ident}", response_model=CourierWaybillOut)
def update_waybills(
    ident: int,
    payload: CourierWaybillUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("courier.waybills.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CourierWaybill, ident, "Lettre voiture express")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/waybills/{ident}", response_model=CourierWaybillOut)
def delete_waybills(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("courier.waybills.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CourierWaybill, ident, "Lettre voiture express")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Hub ─────────────────────────────────────────────

@router.get("/hubs", response_model=List[CourierHubOut])
def list_hubs(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("courier.hubs.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, CourierHub, cid, {'statut': statut})


@router.post("/hubs", response_model=CourierHubOut, status_code=201)
def create_hubs(
    payload: CourierHubCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("courier.hubs.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, CourierHub, "code_hub", data.get("code_hub"), "code_hub", cid)
    obj = CourierHub(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/hubs/{ident}", response_model=CourierHubOut)
def update_hubs(
    ident: int,
    payload: CourierHubUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("courier.hubs.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CourierHub, ident, "Hub")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/hubs/{ident}", response_model=CourierHubOut)
def delete_hubs(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("courier.hubs.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CourierHub, ident, "Hub")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Zone de livraison ─────────────────────────────────────────────

@router.get("/delivery-zones", response_model=List[CourierDeliveryZoneOut])
def list_delivery_zones(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("courier.delivery_zones.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, CourierDeliveryZone, cid, {'statut': statut})


@router.post("/delivery-zones", response_model=CourierDeliveryZoneOut, status_code=201)
def create_delivery_zones(
    payload: CourierDeliveryZoneCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("courier.delivery_zones.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, CourierDeliveryZone, "code_zone", data.get("code_zone"), "code_zone", cid)
    obj = CourierDeliveryZone(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/delivery-zones/{ident}", response_model=CourierDeliveryZoneOut)
def update_delivery_zones(
    ident: int,
    payload: CourierDeliveryZoneUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("courier.delivery_zones.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CourierDeliveryZone, ident, "Zone de livraison")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/delivery-zones/{ident}", response_model=CourierDeliveryZoneOut)
def delete_delivery_zones(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("courier.delivery_zones.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CourierDeliveryZone, ident, "Zone de livraison")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Tournee ─────────────────────────────────────────────

@router.get("/routes", response_model=List[CourierRouteOut])
def list_routes(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("courier.routes.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, CourierRoute, cid, {'statut': statut})


@router.post("/routes", response_model=CourierRouteOut, status_code=201)
def create_routes(
    payload: CourierRouteCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("courier.routes.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, CourierRoute, "code_tournee", data.get("code_tournee"), "code_tournee", cid)
    obj = CourierRoute(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/routes/{ident}", response_model=CourierRouteOut)
def update_routes(
    ident: int,
    payload: CourierRouteUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("courier.routes.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CourierRoute, ident, "Tournee")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/routes/{ident}", response_model=CourierRouteOut)
def delete_routes(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("courier.routes.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CourierRoute, ident, "Tournee")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Coursier ─────────────────────────────────────────────

@router.get("/couriers", response_model=List[CourierCourierOut])
def list_couriers(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("courier.couriers.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, CourierCourier, cid, {'statut': statut})


@router.post("/couriers", response_model=CourierCourierOut, status_code=201)
def create_couriers(
    payload: CourierCourierCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("courier.couriers.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, CourierCourier, "code_coursier", data.get("code_coursier"), "code_coursier", cid)
    obj = CourierCourier(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/couriers/{ident}", response_model=CourierCourierOut)
def update_couriers(
    ident: int,
    payload: CourierCourierUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("courier.couriers.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CourierCourier, ident, "Coursier")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/couriers/{ident}", response_model=CourierCourierOut)
def delete_couriers(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("courier.couriers.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CourierCourier, ident, "Coursier")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── POD ─────────────────────────────────────────────

@router.get("/pods", response_model=List[CourierPodOut])
def list_pods(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("courier.pods.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, CourierPod, cid, {'statut': statut})


@router.post("/pods", response_model=CourierPodOut, status_code=201)
def create_pods(
    payload: CourierPodCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("courier.pods.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, CourierPod, "reference_pod", data.get("reference_pod"), "reference_pod", cid)
    obj = CourierPod(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/pods/{ident}", response_model=CourierPodOut)
def update_pods(
    ident: int,
    payload: CourierPodUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("courier.pods.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CourierPod, ident, "POD")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/pods/{ident}", response_model=CourierPodOut)
def delete_pods(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("courier.pods.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CourierPod, ident, "POD")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── SLA ─────────────────────────────────────────────

@router.get("/slas", response_model=List[CourierSlaOut])
def list_slas(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("courier.slas.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, CourierSla, cid, {'statut': statut})


@router.post("/slas", response_model=CourierSlaOut, status_code=201)
def create_slas(
    payload: CourierSlaCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("courier.slas.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, CourierSla, "code_sla", data.get("code_sla"), "code_sla", cid)
    obj = CourierSla(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/slas/{ident}", response_model=CourierSlaOut)
def update_slas(
    ident: int,
    payload: CourierSlaUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("courier.slas.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CourierSla, ident, "SLA")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/slas/{ident}", response_model=CourierSlaOut)
def delete_slas(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("courier.slas.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CourierSla, ident, "SLA")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Consigne ─────────────────────────────────────────────

@router.get("/lockers", response_model=List[CourierLockerOut])
def list_lockers(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("courier.lockers.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, CourierLocker, cid, {'statut': statut})


@router.post("/lockers", response_model=CourierLockerOut, status_code=201)
def create_lockers(
    payload: CourierLockerCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("courier.lockers.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, CourierLocker, "code_locker", data.get("code_locker"), "code_locker", cid)
    obj = CourierLocker(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/lockers/{ident}", response_model=CourierLockerOut)
def update_lockers(
    ident: int,
    payload: CourierLockerUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("courier.lockers.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CourierLocker, ident, "Consigne")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/lockers/{ident}", response_model=CourierLockerOut)
def delete_lockers(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("courier.lockers.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CourierLocker, ident, "Consigne")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Vehicule ─────────────────────────────────────────────

@router.get("/vehicules", response_model=List[CourierVehiculeOut])
def list_vehicules(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("courier.vehicules.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, CourierVehicule, cid, {'statut': statut})


@router.post("/vehicules", response_model=CourierVehiculeOut, status_code=201)
def create_vehicules(
    payload: CourierVehiculeCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("courier.vehicules.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, CourierVehicule, "plaque", data.get("plaque"), "plaque", cid)
    obj = CourierVehicule(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/vehicules/{ident}", response_model=CourierVehiculeOut)
def update_vehicules(
    ident: int,
    payload: CourierVehiculeUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("courier.vehicules.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CourierVehicule, ident, "Vehicule")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/vehicules/{ident}", response_model=CourierVehiculeOut)
def delete_vehicules(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("courier.vehicules.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CourierVehicule, ident, "Vehicule")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Tarif ─────────────────────────────────────────────

@router.get("/tarifs", response_model=List[CourierTarifOut])
def list_tarifs(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("courier.tarifs.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, CourierTarif, cid, {'statut': statut})


@router.post("/tarifs", response_model=CourierTarifOut, status_code=201)
def create_tarifs(
    payload: CourierTarifCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("courier.tarifs.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, CourierTarif, "code_tarif", data.get("code_tarif"), "code_tarif", cid)
    obj = CourierTarif(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/tarifs/{ident}", response_model=CourierTarifOut)
def update_tarifs(
    ident: int,
    payload: CourierTarifUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("courier.tarifs.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CourierTarif, ident, "Tarif")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/tarifs/{ident}", response_model=CourierTarifOut)
def delete_tarifs(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("courier.tarifs.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CourierTarif, ident, "Tarif")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Exception ─────────────────────────────────────────────

@router.get("/exceptions", response_model=List[CourierExceptionOut])
def list_exceptions(db: Session = Depends(get_db),
    user: User = Depends(require_perm("courier.exceptions.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, CourierException, cid)


@router.post("/exceptions", response_model=CourierExceptionOut, status_code=201)
def create_exceptions(
    payload: CourierExceptionCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("courier.exceptions.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, CourierException, "reference", data.get("reference"), "reference", cid)
    obj = CourierException(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/exceptions/{ident}", response_model=CourierExceptionOut)
def update_exceptions(
    ident: int,
    payload: CourierExceptionUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("courier.exceptions.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CourierException, ident, "Exception")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/exceptions/{ident}", response_model=CourierExceptionOut)
def delete_exceptions(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("courier.exceptions.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CourierException, ident, "Exception")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj

