"""Routeur CRUD genere pour logistique-3pl (expansion)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List

from app.core.database import get_db
from app.core.permissions import require_perm
from app.models.user import User
from app.models.log3pl_b_deep import (
    TplDockAppointment,
    TplLoadingPlan,
    TplShipmentManifest,
    TplInventoryTransfer,
    TplColdChainLog,
    TplReturnAuthorization,
    TplCarrierRate,
    TplOrderNode,
    TplDamageClaim,
)
from app.schemas.log3pl_b_deep import (
    TplDockAppointmentCreate, TplDockAppointmentUpdate, TplDockAppointmentOut,
    TplLoadingPlanCreate, TplLoadingPlanUpdate, TplLoadingPlanOut,
    TplShipmentManifestCreate, TplShipmentManifestUpdate, TplShipmentManifestOut,
    TplInventoryTransferCreate, TplInventoryTransferUpdate, TplInventoryTransferOut,
    TplColdChainLogCreate, TplColdChainLogUpdate, TplColdChainLogOut,
    TplReturnAuthorizationCreate, TplReturnAuthorizationUpdate, TplReturnAuthorizationOut,
    TplCarrierRateCreate, TplCarrierRateUpdate, TplCarrierRateOut,
    TplOrderNodeCreate, TplOrderNodeUpdate, TplOrderNodeOut,
    TplDamageClaimCreate, TplDamageClaimUpdate, TplDamageClaimOut,
)

router = APIRouter(tags=["logistique-3pl (expansion)"])


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

@router.get("/nomenclatures", summary="Vocabulaire metier logistique-3pl")
def nomenclatures(user: User = Depends(require_perm("log3pl.nomenclature.read"))):
    from app.models import log3pl_b_deep as _md
    import enum as _pyenum
    out = {}
    for name in dir(_md):
        obj = getattr(_md, name)
        if isinstance(obj, type) and issubclass(obj, _pyenum.Enum) and obj is not _pyenum.Enum:
            out[name.lower()] = [{"code": m.name, "valeur": m.value} for m in obj]
    return out


# ─── Rendez-vous quais (dock scheduling) ─────────────────────────────────────────────────

@router.get("/tplb-dock-appointments", response_model=List[TplDockAppointmentOut])
def list_dock_appointment(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("log3pl.dock_appointment.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, TplDockAppointment, cid, {"statut": statut})


@router.post("/tplb-dock-appointments", response_model=TplDockAppointmentOut, status_code=201)
def create_dock_appointment(
    payload: TplDockAppointmentCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("log3pl.dock_appointment.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, TplDockAppointment, "reference", data.get("reference"), "reference", cid)
    obj = TplDockAppointment(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/tplb-dock-appointments/{ident}", response_model=TplDockAppointmentOut)
def update_dock_appointment(
    ident: int,
    payload: TplDockAppointmentUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("log3pl.dock_appointment.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TplDockAppointment, ident, "Rendez-vous quais (dock scheduling)")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/tplb-dock-appointments/{ident}", response_model=TplDockAppointmentOut)
def delete_dock_appointment(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("log3pl.dock_appointment.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TplDockAppointment, ident, "Rendez-vous quais (dock scheduling)")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Plans de chargement camion ─────────────────────────────────────────────────

@router.get("/tplb-loading-plans", response_model=List[TplLoadingPlanOut])
def list_loading_plan(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("log3pl.loading_plan.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, TplLoadingPlan, cid, {"statut": statut})


@router.post("/tplb-loading-plans", response_model=TplLoadingPlanOut, status_code=201)
def create_loading_plan(
    payload: TplLoadingPlanCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("log3pl.loading_plan.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, TplLoadingPlan, "reference", data.get("reference"), "reference", cid)
    obj = TplLoadingPlan(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/tplb-loading-plans/{ident}", response_model=TplLoadingPlanOut)
def update_loading_plan(
    ident: int,
    payload: TplLoadingPlanUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("log3pl.loading_plan.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TplLoadingPlan, ident, "Plans de chargement camion")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/tplb-loading-plans/{ident}", response_model=TplLoadingPlanOut)
def delete_loading_plan(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("log3pl.loading_plan.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TplLoadingPlan, ident, "Plans de chargement camion")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Manifestes d' expedition ─────────────────────────────────────────────────

@router.get("/tplb-shipment-manifests", response_model=List[TplShipmentManifestOut])
def list_shipment_manifest(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("log3pl.shipment_manifest.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, TplShipmentManifest, cid, {"statut": statut})


@router.post("/tplb-shipment-manifests", response_model=TplShipmentManifestOut, status_code=201)
def create_shipment_manifest(
    payload: TplShipmentManifestCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("log3pl.shipment_manifest.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, TplShipmentManifest, "numero_manifeste", data.get("numero_manifeste"), "numero_manifeste", cid)
    obj = TplShipmentManifest(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/tplb-shipment-manifests/{ident}", response_model=TplShipmentManifestOut)
def update_shipment_manifest(
    ident: int,
    payload: TplShipmentManifestUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("log3pl.shipment_manifest.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TplShipmentManifest, ident, "Manifestes d' expedition")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/tplb-shipment-manifests/{ident}", response_model=TplShipmentManifestOut)
def delete_shipment_manifest(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("log3pl.shipment_manifest.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TplShipmentManifest, ident, "Manifestes d' expedition")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Transferts inter-entrepots ─────────────────────────────────────────────────

@router.get("/tplb-inventory-transfers", response_model=List[TplInventoryTransferOut])
def list_inventory_transfer(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("log3pl.inventory_transfer.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, TplInventoryTransfer, cid, {"statut": statut})


@router.post("/tplb-inventory-transfers", response_model=TplInventoryTransferOut, status_code=201)
def create_inventory_transfer(
    payload: TplInventoryTransferCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("log3pl.inventory_transfer.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, TplInventoryTransfer, "reference", data.get("reference"), "reference", cid)
    obj = TplInventoryTransfer(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/tplb-inventory-transfers/{ident}", response_model=TplInventoryTransferOut)
def update_inventory_transfer(
    ident: int,
    payload: TplInventoryTransferUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("log3pl.inventory_transfer.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TplInventoryTransfer, ident, "Transferts inter-entrepots")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/tplb-inventory-transfers/{ident}", response_model=TplInventoryTransferOut)
def delete_inventory_transfer(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("log3pl.inventory_transfer.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TplInventoryTransfer, ident, "Transferts inter-entrepots")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Journal chaine du froid ─────────────────────────────────────────────────

@router.get("/tplb-cold-chain-logs", response_model=List[TplColdChainLogOut])
def list_cold_chain_log(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("log3pl.cold_chain_log.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, TplColdChainLog, cid, {"statut": statut})


@router.post("/tplb-cold-chain-logs", response_model=TplColdChainLogOut, status_code=201)
def create_cold_chain_log(
    payload: TplColdChainLogCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("log3pl.cold_chain_log.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, TplColdChainLog, "reference", data.get("reference"), "reference", cid)
    obj = TplColdChainLog(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/tplb-cold-chain-logs/{ident}", response_model=TplColdChainLogOut)
def update_cold_chain_log(
    ident: int,
    payload: TplColdChainLogUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("log3pl.cold_chain_log.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TplColdChainLog, ident, "Journal chaine du froid")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/tplb-cold-chain-logs/{ident}", response_model=TplColdChainLogOut)
def delete_cold_chain_log(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("log3pl.cold_chain_log.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TplColdChainLog, ident, "Journal chaine du froid")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Autorisations de retour (RMA) ─────────────────────────────────────────────────

@router.get("/tplb-return-authorizations", response_model=List[TplReturnAuthorizationOut])
def list_return_authorization(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("log3pl.return_authorization.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, TplReturnAuthorization, cid, {"statut": statut})


@router.post("/tplb-return-authorizations", response_model=TplReturnAuthorizationOut, status_code=201)
def create_return_authorization(
    payload: TplReturnAuthorizationCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("log3pl.return_authorization.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, TplReturnAuthorization, "numero_rma", data.get("numero_rma"), "numero_rma", cid)
    obj = TplReturnAuthorization(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/tplb-return-authorizations/{ident}", response_model=TplReturnAuthorizationOut)
def update_return_authorization(
    ident: int,
    payload: TplReturnAuthorizationUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("log3pl.return_authorization.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TplReturnAuthorization, ident, "Autorisations de retour (RMA)")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/tplb-return-authorizations/{ident}", response_model=TplReturnAuthorizationOut)
def delete_return_authorization(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("log3pl.return_authorization.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TplReturnAuthorization, ident, "Autorisations de retour (RMA)")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Grille tarifaire transporteurs ─────────────────────────────────────────────────

@router.get("/tplb-carrier-rates", response_model=List[TplCarrierRateOut])
def list_carrier_rate(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("log3pl.carrier_rate.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, TplCarrierRate, cid, {"statut": statut})


@router.post("/tplb-carrier-rates", response_model=TplCarrierRateOut, status_code=201)
def create_carrier_rate(
    payload: TplCarrierRateCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("log3pl.carrier_rate.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, TplCarrierRate, "code_tarif", data.get("code_tarif"), "code_tarif", cid)
    obj = TplCarrierRate(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/tplb-carrier-rates/{ident}", response_model=TplCarrierRateOut)
def update_carrier_rate(
    ident: int,
    payload: TplCarrierRateUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("log3pl.carrier_rate.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TplCarrierRate, ident, "Grille tarifaire transporteurs")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/tplb-carrier-rates/{ident}", response_model=TplCarrierRateOut)
def delete_carrier_rate(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("log3pl.carrier_rate.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TplCarrierRate, ident, "Grille tarifaire transporteurs")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Jalons de commande (track & trace) ─────────────────────────────────────────────────

@router.get("/tplb-order-nodes", response_model=List[TplOrderNodeOut])
def list_order_node(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("log3pl.order_node.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, TplOrderNode, cid, {"statut": statut})


@router.post("/tplb-order-nodes", response_model=TplOrderNodeOut, status_code=201)
def create_order_node(
    payload: TplOrderNodeCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("log3pl.order_node.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, TplOrderNode, "reference", data.get("reference"), "reference", cid)
    obj = TplOrderNode(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/tplb-order-nodes/{ident}", response_model=TplOrderNodeOut)
def update_order_node(
    ident: int,
    payload: TplOrderNodeUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("log3pl.order_node.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TplOrderNode, ident, "Jalons de commande (track & trace)")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/tplb-order-nodes/{ident}", response_model=TplOrderNodeOut)
def delete_order_node(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("log3pl.order_node.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TplOrderNode, ident, "Jalons de commande (track & trace)")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Reclamations avaries 3PL ─────────────────────────────────────────────────

@router.get("/tplb-damage-claims", response_model=List[TplDamageClaimOut])
def list_damage_claim(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("log3pl.damage_claim.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, TplDamageClaim, cid, {"statut": statut})


@router.post("/tplb-damage-claims", response_model=TplDamageClaimOut, status_code=201)
def create_damage_claim(
    payload: TplDamageClaimCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("log3pl.damage_claim.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, TplDamageClaim, "numero_dossier", data.get("numero_dossier"), "numero_dossier", cid)
    obj = TplDamageClaim(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/tplb-damage-claims/{ident}", response_model=TplDamageClaimOut)
def update_damage_claim(
    ident: int,
    payload: TplDamageClaimUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("log3pl.damage_claim.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TplDamageClaim, ident, "Reclamations avaries 3PL")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/tplb-damage-claims/{ident}", response_model=TplDamageClaimOut)
def delete_damage_claim(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("log3pl.damage_claim.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TplDamageClaim, ident, "Reclamations avaries 3PL")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj

