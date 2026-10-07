"""Routeur CRUD genere pour transit-douane (expansion)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List

from app.core.database import get_db
from app.core.permissions import require_perm
from app.models.user import User
from app.models.transit_deep import (
    HsClassification,
    CustomsValuation,
    OriginCertificate,
    BondedWarehouse,
    TransitGuarantee,
    ExportDeclaration,
    ProhibitedGood,
    CustomsRegime,
    PhysicalInspection,
    DutyPayment,
    TraderRegistration,
    TariffReference,
)
from app.schemas.transit_deep import (
    HsClassificationCreate, HsClassificationUpdate, HsClassificationOut,
    CustomsValuationCreate, CustomsValuationUpdate, CustomsValuationOut,
    OriginCertificateCreate, OriginCertificateUpdate, OriginCertificateOut,
    BondedWarehouseCreate, BondedWarehouseUpdate, BondedWarehouseOut,
    TransitGuaranteeCreate, TransitGuaranteeUpdate, TransitGuaranteeOut,
    ExportDeclarationCreate, ExportDeclarationUpdate, ExportDeclarationOut,
    ProhibitedGoodCreate, ProhibitedGoodUpdate, ProhibitedGoodOut,
    CustomsRegimeCreate, CustomsRegimeUpdate, CustomsRegimeOut,
    PhysicalInspectionCreate, PhysicalInspectionUpdate, PhysicalInspectionOut,
    DutyPaymentCreate, DutyPaymentUpdate, DutyPaymentOut,
    TraderRegistrationCreate, TraderRegistrationUpdate, TraderRegistrationOut,
    TariffReferenceCreate, TariffReferenceUpdate, TariffReferenceOut,
)

router = APIRouter(tags=["transit-douane (expansion)"])


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

@router.get("/nomenclatures", summary="Vocabulaire metier transit-douane")
def nomenclatures(user: User = Depends(require_perm("transit.nomenclature.read"))):
    from app.models import transit_deep as _md
    import enum as _pyenum
    out = {}
    for name in dir(_md):
        obj = getattr(_md, name)
        if isinstance(obj, type) and issubclass(obj, _pyenum.Enum) and obj is not _pyenum.Enum:
            out[name.lower()] = [{"code": m.name, "valeur": m.value} for m in obj]
    return out


# ─── Classification tarifaire SH ─────────────────────────────────────────────────

@router.get("/hs-classifications", response_model=List[HsClassificationOut])
def list_hs_classification(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.hs_classification.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, HsClassification, cid, {"statut": statut})


@router.post("/hs-classifications", response_model=HsClassificationOut, status_code=201)
def create_hs_classification(
    payload: HsClassificationCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.hs_classification.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, HsClassification, "code_hs", data.get("code_hs"), "code_hs", cid)
    obj = HsClassification(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/hs-classifications/{ident}", response_model=HsClassificationOut)
def update_hs_classification(
    ident: int,
    payload: HsClassificationUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.hs_classification.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, HsClassification, ident, "Classification tarifaire SH")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/hs-classifications/{ident}", response_model=HsClassificationOut)
def delete_hs_classification(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.hs_classification.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, HsClassification, ident, "Classification tarifaire SH")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Valeur en douane / INCOTERMS ─────────────────────────────────────────────────

@router.get("/customs-valuations", response_model=List[CustomsValuationOut])
def list_customs_valuation(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.customs_valuation.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, CustomsValuation, cid, {"statut": statut})


@router.post("/customs-valuations", response_model=CustomsValuationOut, status_code=201)
def create_customs_valuation(
    payload: CustomsValuationCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.customs_valuation.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, CustomsValuation, "reference_dossier", data.get("reference_dossier"), "reference_dossier", cid)
    obj = CustomsValuation(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/customs-valuations/{ident}", response_model=CustomsValuationOut)
def update_customs_valuation(
    ident: int,
    payload: CustomsValuationUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.customs_valuation.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CustomsValuation, ident, "Valeur en douane / INCOTERMS")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/customs-valuations/{ident}", response_model=CustomsValuationOut)
def delete_customs_valuation(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.customs_valuation.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CustomsValuation, ident, "Valeur en douane / INCOTERMS")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Certificats d'origine ─────────────────────────────────────────────────

@router.get("/origin-certificates", response_model=List[OriginCertificateOut])
def list_origin_certificate(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.origin_certificate.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, OriginCertificate, cid, {"statut": statut})


@router.post("/origin-certificates", response_model=OriginCertificateOut, status_code=201)
def create_origin_certificate(
    payload: OriginCertificateCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.origin_certificate.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, OriginCertificate, "numero_certificat", data.get("numero_certificat"), "numero_certificat", cid)
    obj = OriginCertificate(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/origin-certificates/{ident}", response_model=OriginCertificateOut)
def update_origin_certificate(
    ident: int,
    payload: OriginCertificateUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.origin_certificate.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, OriginCertificate, ident, "Certificats d'origine")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/origin-certificates/{ident}", response_model=OriginCertificateOut)
def delete_origin_certificate(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.origin_certificate.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, OriginCertificate, ident, "Certificats d'origine")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Entrepots sous douane ─────────────────────────────────────────────────

@router.get("/bonded-warehouses", response_model=List[BondedWarehouseOut])
def list_bonded_warehouse(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.bonded_warehouse.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, BondedWarehouse, cid, {"statut": statut})


@router.post("/bonded-warehouses", response_model=BondedWarehouseOut, status_code=201)
def create_bonded_warehouse(
    payload: BondedWarehouseCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.bonded_warehouse.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, BondedWarehouse, "code_entrepot", data.get("code_entrepot"), "code_entrepot", cid)
    obj = BondedWarehouse(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/bonded-warehouses/{ident}", response_model=BondedWarehouseOut)
def update_bonded_warehouse(
    ident: int,
    payload: BondedWarehouseUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.bonded_warehouse.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, BondedWarehouse, ident, "Entrepots sous douane")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/bonded-warehouses/{ident}", response_model=BondedWarehouseOut)
def delete_bonded_warehouse(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.bonded_warehouse.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, BondedWarehouse, ident, "Entrepots sous douane")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Cautions et garanties ─────────────────────────────────────────────────

@router.get("/transit-guarantees", response_model=List[TransitGuaranteeOut])
def list_transit_guarantee(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.transit_guarantee.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, TransitGuarantee, cid, {"statut": statut})


@router.post("/transit-guarantees", response_model=TransitGuaranteeOut, status_code=201)
def create_transit_guarantee(
    payload: TransitGuaranteeCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.transit_guarantee.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, TransitGuarantee, "reference_caution", data.get("reference_caution"), "reference_caution", cid)
    obj = TransitGuarantee(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/transit-guarantees/{ident}", response_model=TransitGuaranteeOut)
def update_transit_guarantee(
    ident: int,
    payload: TransitGuaranteeUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.transit_guarantee.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TransitGuarantee, ident, "Cautions et garanties")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/transit-guarantees/{ident}", response_model=TransitGuaranteeOut)
def delete_transit_guarantee(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.transit_guarantee.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TransitGuarantee, ident, "Cautions et garanties")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Declarations export ─────────────────────────────────────────────────

@router.get("/export-declarations", response_model=List[ExportDeclarationOut])
def list_export_declaration(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.export_declaration.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, ExportDeclaration, cid, {"statut": statut})


@router.post("/export-declarations", response_model=ExportDeclarationOut, status_code=201)
def create_export_declaration(
    payload: ExportDeclarationCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.export_declaration.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, ExportDeclaration, "numero_dge", data.get("numero_dge"), "numero_dge", cid)
    obj = ExportDeclaration(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/export-declarations/{ident}", response_model=ExportDeclarationOut)
def update_export_declaration(
    ident: int,
    payload: ExportDeclarationUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.export_declaration.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ExportDeclaration, ident, "Declarations export")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/export-declarations/{ident}", response_model=ExportDeclarationOut)
def delete_export_declaration(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.export_declaration.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ExportDeclaration, ident, "Declarations export")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Marchandises prohibees / contingentees ─────────────────────────────────────────────────

@router.get("/prohibited-goods", response_model=List[ProhibitedGoodOut])
def list_prohibited_good(db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.prohibited_good.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, ProhibitedGood, cid)


@router.post("/prohibited-goods", response_model=ProhibitedGoodOut, status_code=201)
def create_prohibited_good(
    payload: ProhibitedGoodCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.prohibited_good.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, ProhibitedGood, "code_produit", data.get("code_produit"), "code_produit", cid)
    obj = ProhibitedGood(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/prohibited-goods/{ident}", response_model=ProhibitedGoodOut)
def update_prohibited_good(
    ident: int,
    payload: ProhibitedGoodUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.prohibited_good.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ProhibitedGood, ident, "Marchandises prohibees / contingentees")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/prohibited-goods/{ident}", response_model=ProhibitedGoodOut)
def delete_prohibited_good(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.prohibited_good.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ProhibitedGood, ident, "Marchandises prohibees / contingentees")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Regimes economiques ─────────────────────────────────────────────────

@router.get("/customs-regimes", response_model=List[CustomsRegimeOut])
def list_customs_regime(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.customs_regime.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, CustomsRegime, cid, {"statut": statut})


@router.post("/customs-regimes", response_model=CustomsRegimeOut, status_code=201)
def create_customs_regime(
    payload: CustomsRegimeCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.customs_regime.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, CustomsRegime, "reference_regime", data.get("reference_regime"), "reference_regime", cid)
    obj = CustomsRegime(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/customs-regimes/{ident}", response_model=CustomsRegimeOut)
def update_customs_regime(
    ident: int,
    payload: CustomsRegimeUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.customs_regime.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CustomsRegime, ident, "Regimes economiques")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/customs-regimes/{ident}", response_model=CustomsRegimeOut)
def delete_customs_regime(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.customs_regime.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CustomsRegime, ident, "Regimes economiques")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Visites et inspections physiques ─────────────────────────────────────────────────

@router.get("/physical-inspections", response_model=List[PhysicalInspectionOut])
def list_physical_inspection(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.physical_inspection.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, PhysicalInspection, cid, {"statut": statut})


@router.post("/physical-inspections", response_model=PhysicalInspectionOut, status_code=201)
def create_physical_inspection(
    payload: PhysicalInspectionCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.physical_inspection.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, PhysicalInspection, "numero_pv", data.get("numero_pv"), "numero_pv", cid)
    obj = PhysicalInspection(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/physical-inspections/{ident}", response_model=PhysicalInspectionOut)
def update_physical_inspection(
    ident: int,
    payload: PhysicalInspectionUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.physical_inspection.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, PhysicalInspection, ident, "Visites et inspections physiques")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/physical-inspections/{ident}", response_model=PhysicalInspectionOut)
def delete_physical_inspection(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.physical_inspection.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, PhysicalInspection, ident, "Visites et inspections physiques")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Paiement droits et taxes ─────────────────────────────────────────────────

@router.get("/duty-payments", response_model=List[DutyPaymentOut])
def list_duty_payment(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.duty_payment.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, DutyPayment, cid, {"statut": statut})


@router.post("/duty-payments", response_model=DutyPaymentOut, status_code=201)
def create_duty_payment(
    payload: DutyPaymentCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.duty_payment.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, DutyPayment, "numero_quittance", data.get("numero_quittance"), "numero_quittance", cid)
    obj = DutyPayment(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/duty-payments/{ident}", response_model=DutyPaymentOut)
def update_duty_payment(
    ident: int,
    payload: DutyPaymentUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.duty_payment.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, DutyPayment, ident, "Paiement droits et taxes")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/duty-payments/{ident}", response_model=DutyPaymentOut)
def delete_duty_payment(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.duty_payment.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, DutyPayment, ident, "Paiement droits et taxes")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Enregistrement operateur economique ─────────────────────────────────────────────────

@router.get("/trader-registrations", response_model=List[TraderRegistrationOut])
def list_trader_registration(db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.trader_registration.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, TraderRegistration, cid)


@router.post("/trader-registrations", response_model=TraderRegistrationOut, status_code=201)
def create_trader_registration(
    payload: TraderRegistrationCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.trader_registration.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, TraderRegistration, "numero_operateur", data.get("numero_operateur"), "numero_operateur", cid)
    obj = TraderRegistration(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/trader-registrations/{ident}", response_model=TraderRegistrationOut)
def update_trader_registration(
    ident: int,
    payload: TraderRegistrationUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.trader_registration.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TraderRegistration, ident, "Enregistrement operateur economique")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/trader-registrations/{ident}", response_model=TraderRegistrationOut)
def delete_trader_registration(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.trader_registration.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TraderRegistration, ident, "Enregistrement operateur economique")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Tarif integre CEMAC ─────────────────────────────────────────────────

@router.get("/tariff-references", response_model=List[TariffReferenceOut])
def list_tariff_reference(db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.tariff_reference.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, TariffReference, cid)


@router.post("/tariff-references", response_model=TariffReferenceOut, status_code=201)
def create_tariff_reference(
    payload: TariffReferenceCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.tariff_reference.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, TariffReference, "code_ligne_tarifaire", data.get("code_ligne_tarifaire"), "code_ligne_tarifaire", cid)
    obj = TariffReference(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/tariff-references/{ident}", response_model=TariffReferenceOut)
def update_tariff_reference(
    ident: int,
    payload: TariffReferenceUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.tariff_reference.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TariffReference, ident, "Tarif integre CEMAC")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/tariff-references/{ident}", response_model=TariffReferenceOut)
def delete_tariff_reference(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.tariff_reference.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TariffReference, ident, "Tarif integre CEMAC")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj

