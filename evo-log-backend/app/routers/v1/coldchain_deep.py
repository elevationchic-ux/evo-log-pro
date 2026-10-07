"""Routeur CRUD genere pour chaine-froid (expansion wave 5)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List

from app.core.database import get_db
from app.core.permissions import require_perm
from app.models.user import User
from app.models.coldchain_deep import (
    ColdChainChamber,
    ColdChainReefer,
    ColdChainLogger,
    ColdChainProduct,
    ColdChainExcursion,
    ColdChainVaccinBatch,
    ColdChainHaccpRecord,
    ColdChainDefrostCycle,
    ColdChainEnergyMeter,
    ColdChainTransportLeg,
)
from app.schemas.coldchain_deep import (
    ColdChainChamberCreate, ColdChainChamberUpdate, ColdChainChamberOut,
    ColdChainReeferCreate, ColdChainReeferUpdate, ColdChainReeferOut,
    ColdChainLoggerCreate, ColdChainLoggerUpdate, ColdChainLoggerOut,
    ColdChainProductCreate, ColdChainProductUpdate, ColdChainProductOut,
    ColdChainExcursionCreate, ColdChainExcursionUpdate, ColdChainExcursionOut,
    ColdChainVaccinBatchCreate, ColdChainVaccinBatchUpdate, ColdChainVaccinBatchOut,
    ColdChainHaccpRecordCreate, ColdChainHaccpRecordUpdate, ColdChainHaccpRecordOut,
    ColdChainDefrostCycleCreate, ColdChainDefrostCycleUpdate, ColdChainDefrostCycleOut,
    ColdChainEnergyMeterCreate, ColdChainEnergyMeterUpdate, ColdChainEnergyMeterOut,
    ColdChainTransportLegCreate, ColdChainTransportLegUpdate, ColdChainTransportLegOut,
)

router = APIRouter(tags=["chaine-froid (expansion)"])


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

@router.get("/nomenclatures", summary="Vocabulaire metier chaine-froid")
def nomenclatures(user: User = Depends(require_perm("coldchain.nomenclature.read"))):
    from app.models import coldchain_deep as _md
    import enum as _pyenum
    out = {}
    for name in dir(_md):
        obj = getattr(_md, name)
        if isinstance(obj, type) and issubclass(obj, _pyenum.Enum) and obj is not _pyenum.Enum:
            out[name.lower()] = [{"code": m.name, "valeur": m.value} for m in obj]
    return out


# ─── Chambre froide ─────────────────────────────────────────────

@router.get("/chambers", response_model=List[ColdChainChamberOut])
def list_chambers(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("coldchain.chambers.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, ColdChainChamber, cid, {'statut': statut})


@router.post("/chambers", response_model=ColdChainChamberOut, status_code=201)
def create_chambers(
    payload: ColdChainChamberCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("coldchain.chambers.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, ColdChainChamber, "code_chambre", data.get("code_chambre"), "code_chambre", cid)
    obj = ColdChainChamber(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/chambers/{ident}", response_model=ColdChainChamberOut)
def update_chambers(
    ident: int,
    payload: ColdChainChamberUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("coldchain.chambers.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ColdChainChamber, ident, "Chambre froide")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/chambers/{ident}", response_model=ColdChainChamberOut)
def delete_chambers(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("coldchain.chambers.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ColdChainChamber, ident, "Chambre froide")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Reefer ─────────────────────────────────────────────

@router.get("/reefers", response_model=List[ColdChainReeferOut])
def list_reefers(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("coldchain.reefers.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, ColdChainReefer, cid, {'statut': statut})


@router.post("/reefers", response_model=ColdChainReeferOut, status_code=201)
def create_reefers(
    payload: ColdChainReeferCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("coldchain.reefers.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, ColdChainReefer, "numero_reefer", data.get("numero_reefer"), "numero_reefer", cid)
    obj = ColdChainReefer(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/reefers/{ident}", response_model=ColdChainReeferOut)
def update_reefers(
    ident: int,
    payload: ColdChainReeferUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("coldchain.reefers.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ColdChainReefer, ident, "Reefer")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/reefers/{ident}", response_model=ColdChainReeferOut)
def delete_reefers(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("coldchain.reefers.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ColdChainReefer, ident, "Reefer")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Logger temperature ─────────────────────────────────────────────

@router.get("/loggers", response_model=List[ColdChainLoggerOut])
def list_loggers(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("coldchain.loggers.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, ColdChainLogger, cid, {'statut': statut})


@router.post("/loggers", response_model=ColdChainLoggerOut, status_code=201)
def create_loggers(
    payload: ColdChainLoggerCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("coldchain.loggers.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, ColdChainLogger, "numero_logger", data.get("numero_logger"), "numero_logger", cid)
    obj = ColdChainLogger(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/loggers/{ident}", response_model=ColdChainLoggerOut)
def update_loggers(
    ident: int,
    payload: ColdChainLoggerUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("coldchain.loggers.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ColdChainLogger, ident, "Logger temperature")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/loggers/{ident}", response_model=ColdChainLoggerOut)
def delete_loggers(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("coldchain.loggers.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ColdChainLogger, ident, "Logger temperature")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Produit ─────────────────────────────────────────────

@router.get("/products", response_model=List[ColdChainProductOut])
def list_products(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("coldchain.products.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, ColdChainProduct, cid, {'statut': statut})


@router.post("/products", response_model=ColdChainProductOut, status_code=201)
def create_products(
    payload: ColdChainProductCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("coldchain.products.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, ColdChainProduct, "code_sku", data.get("code_sku"), "code_sku", cid)
    obj = ColdChainProduct(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/products/{ident}", response_model=ColdChainProductOut)
def update_products(
    ident: int,
    payload: ColdChainProductUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("coldchain.products.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ColdChainProduct, ident, "Produit")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/products/{ident}", response_model=ColdChainProductOut)
def delete_products(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("coldchain.products.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ColdChainProduct, ident, "Produit")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Excursion ─────────────────────────────────────────────

@router.get("/excursions", response_model=List[ColdChainExcursionOut])
def list_excursions(db: Session = Depends(get_db),
    user: User = Depends(require_perm("coldchain.excursions.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, ColdChainExcursion, cid)


@router.post("/excursions", response_model=ColdChainExcursionOut, status_code=201)
def create_excursions(
    payload: ColdChainExcursionCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("coldchain.excursions.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, ColdChainExcursion, "reference", data.get("reference"), "reference", cid)
    obj = ColdChainExcursion(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/excursions/{ident}", response_model=ColdChainExcursionOut)
def update_excursions(
    ident: int,
    payload: ColdChainExcursionUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("coldchain.excursions.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ColdChainExcursion, ident, "Excursion")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/excursions/{ident}", response_model=ColdChainExcursionOut)
def delete_excursions(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("coldchain.excursions.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ColdChainExcursion, ident, "Excursion")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Lot vaccin ─────────────────────────────────────────────

@router.get("/vaccin-batches", response_model=List[ColdChainVaccinBatchOut])
def list_vaccin_batches(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("coldchain.vaccin_batches.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, ColdChainVaccinBatch, cid, {'statut': statut})


@router.post("/vaccin-batches", response_model=ColdChainVaccinBatchOut, status_code=201)
def create_vaccin_batches(
    payload: ColdChainVaccinBatchCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("coldchain.vaccin_batches.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, ColdChainVaccinBatch, "numero_lot", data.get("numero_lot"), "numero_lot", cid)
    obj = ColdChainVaccinBatch(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/vaccin-batches/{ident}", response_model=ColdChainVaccinBatchOut)
def update_vaccin_batches(
    ident: int,
    payload: ColdChainVaccinBatchUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("coldchain.vaccin_batches.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ColdChainVaccinBatch, ident, "Lot vaccin")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/vaccin-batches/{ident}", response_model=ColdChainVaccinBatchOut)
def delete_vaccin_batches(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("coldchain.vaccin_batches.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ColdChainVaccinBatch, ident, "Lot vaccin")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Enregistrement HACCP ─────────────────────────────────────────────

@router.get("/haccp-records", response_model=List[ColdChainHaccpRecordOut])
def list_haccp_records(db: Session = Depends(get_db),
    user: User = Depends(require_perm("coldchain.haccp_records.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, ColdChainHaccpRecord, cid)


@router.post("/haccp-records", response_model=ColdChainHaccpRecordOut, status_code=201)
def create_haccp_records(
    payload: ColdChainHaccpRecordCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("coldchain.haccp_records.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, ColdChainHaccpRecord, "reference", data.get("reference"), "reference", cid)
    obj = ColdChainHaccpRecord(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/haccp-records/{ident}", response_model=ColdChainHaccpRecordOut)
def update_haccp_records(
    ident: int,
    payload: ColdChainHaccpRecordUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("coldchain.haccp_records.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ColdChainHaccpRecord, ident, "Enregistrement HACCP")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/haccp-records/{ident}", response_model=ColdChainHaccpRecordOut)
def delete_haccp_records(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("coldchain.haccp_records.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ColdChainHaccpRecord, ident, "Enregistrement HACCP")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Cycle degivrage ─────────────────────────────────────────────

@router.get("/defrost-cycles", response_model=List[ColdChainDefrostCycleOut])
def list_defrost_cycles(db: Session = Depends(get_db),
    user: User = Depends(require_perm("coldchain.defrost_cycles.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, ColdChainDefrostCycle, cid)


@router.post("/defrost-cycles", response_model=ColdChainDefrostCycleOut, status_code=201)
def create_defrost_cycles(
    payload: ColdChainDefrostCycleCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("coldchain.defrost_cycles.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, ColdChainDefrostCycle, "reference", data.get("reference"), "reference", cid)
    obj = ColdChainDefrostCycle(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/defrost-cycles/{ident}", response_model=ColdChainDefrostCycleOut)
def update_defrost_cycles(
    ident: int,
    payload: ColdChainDefrostCycleUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("coldchain.defrost_cycles.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ColdChainDefrostCycle, ident, "Cycle degivrage")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/defrost-cycles/{ident}", response_model=ColdChainDefrostCycleOut)
def delete_defrost_cycles(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("coldchain.defrost_cycles.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ColdChainDefrostCycle, ident, "Cycle degivrage")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Compteur energie ─────────────────────────────────────────────

@router.get("/energy-meters", response_model=List[ColdChainEnergyMeterOut])
def list_energy_meters(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("coldchain.energy_meters.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, ColdChainEnergyMeter, cid, {'statut': statut})


@router.post("/energy-meters", response_model=ColdChainEnergyMeterOut, status_code=201)
def create_energy_meters(
    payload: ColdChainEnergyMeterCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("coldchain.energy_meters.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, ColdChainEnergyMeter, "code_compteur", data.get("code_compteur"), "code_compteur", cid)
    obj = ColdChainEnergyMeter(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/energy-meters/{ident}", response_model=ColdChainEnergyMeterOut)
def update_energy_meters(
    ident: int,
    payload: ColdChainEnergyMeterUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("coldchain.energy_meters.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ColdChainEnergyMeter, ident, "Compteur energie")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/energy-meters/{ident}", response_model=ColdChainEnergyMeterOut)
def delete_energy_meters(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("coldchain.energy_meters.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ColdChainEnergyMeter, ident, "Compteur energie")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Leg transport ─────────────────────────────────────────────

@router.get("/transport-legs", response_model=List[ColdChainTransportLegOut])
def list_transport_legs(db: Session = Depends(get_db),
    user: User = Depends(require_perm("coldchain.transport_legs.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, ColdChainTransportLeg, cid)


@router.post("/transport-legs", response_model=ColdChainTransportLegOut, status_code=201)
def create_transport_legs(
    payload: ColdChainTransportLegCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("coldchain.transport_legs.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, ColdChainTransportLeg, "reference", data.get("reference"), "reference", cid)
    obj = ColdChainTransportLeg(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/transport-legs/{ident}", response_model=ColdChainTransportLegOut)
def update_transport_legs(
    ident: int,
    payload: ColdChainTransportLegUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("coldchain.transport_legs.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ColdChainTransportLeg, ident, "Leg transport")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/transport-legs/{ident}", response_model=ColdChainTransportLegOut)
def delete_transport_legs(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("coldchain.transport_legs.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ColdChainTransportLeg, ident, "Leg transport")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj

