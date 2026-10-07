"""Routeur CRUD genere pour portail-declarant (expansion)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List

from app.core.database import get_db
from app.core.permissions import require_perm
from app.models.user import User
from app.models.declarant_d_deep import (
    DeclCustomsDeclaration,
    DeclHsClassification,
    DeclOriginCertificate,
    DeclCustomsValuation,
    DeclIncotermsRecord,
    DeclImportLicense,
    DeclExportLicense,
    DeclPreClearance,
    DeclCustomsInvoice,
    DeclPackingList,
    DeclCertificateAnalysis,
    DeclPhytosanitaryApp,
    DeclCustomsPayment,
    DeclTransitDocument,
    DeclDangerousGoods,
    DeclBondedWarehouseEntry,
    DeclDutyReliefClaim,
    DeclManifestCorrection,
    DeclCustomsAuditSupport,
)
from app.schemas.declarant_d_deep import (
    DeclCustomsDeclarationCreate, DeclCustomsDeclarationUpdate, DeclCustomsDeclarationOut,
    DeclHsClassificationCreate, DeclHsClassificationUpdate, DeclHsClassificationOut,
    DeclOriginCertificateCreate, DeclOriginCertificateUpdate, DeclOriginCertificateOut,
    DeclCustomsValuationCreate, DeclCustomsValuationUpdate, DeclCustomsValuationOut,
    DeclIncotermsRecordCreate, DeclIncotermsRecordUpdate, DeclIncotermsRecordOut,
    DeclImportLicenseCreate, DeclImportLicenseUpdate, DeclImportLicenseOut,
    DeclExportLicenseCreate, DeclExportLicenseUpdate, DeclExportLicenseOut,
    DeclPreClearanceCreate, DeclPreClearanceUpdate, DeclPreClearanceOut,
    DeclCustomsInvoiceCreate, DeclCustomsInvoiceUpdate, DeclCustomsInvoiceOut,
    DeclPackingListCreate, DeclPackingListUpdate, DeclPackingListOut,
    DeclCertificateAnalysisCreate, DeclCertificateAnalysisUpdate, DeclCertificateAnalysisOut,
    DeclPhytosanitaryAppCreate, DeclPhytosanitaryAppUpdate, DeclPhytosanitaryAppOut,
    DeclCustomsPaymentCreate, DeclCustomsPaymentUpdate, DeclCustomsPaymentOut,
    DeclTransitDocumentCreate, DeclTransitDocumentUpdate, DeclTransitDocumentOut,
    DeclDangerousGoodsCreate, DeclDangerousGoodsUpdate, DeclDangerousGoodsOut,
    DeclBondedWarehouseEntryCreate, DeclBondedWarehouseEntryUpdate, DeclBondedWarehouseEntryOut,
    DeclDutyReliefClaimCreate, DeclDutyReliefClaimUpdate, DeclDutyReliefClaimOut,
    DeclManifestCorrectionCreate, DeclManifestCorrectionUpdate, DeclManifestCorrectionOut,
    DeclCustomsAuditSupportCreate, DeclCustomsAuditSupportUpdate, DeclCustomsAuditSupportOut,
)

router = APIRouter(tags=["portail-declarant (expansion)"])


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

@router.get("/nomenclatures", summary="Vocabulaire metier portail-declarant")
def nomenclatures(user: User = Depends(require_perm("transit.nomenclature.read"))):
    from app.models import declarant_d_deep as _md
    import enum as _pyenum
    out = {}
    for name in dir(_md):
        obj = getattr(_md, name)
        if isinstance(obj, type) and issubclass(obj, _pyenum.Enum) and obj is not _pyenum.Enum:
            out[name.lower()] = [{"code": m.name, "valeur": m.value} for m in obj]
    return out


# ─── Declarations en douane ─────────────────────────────────────────────────

@router.get("/decl-customs-declarations", response_model=List[DeclCustomsDeclarationOut])
def list_customs_declaration(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.customs_declaration.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, DeclCustomsDeclaration, cid, {"statut": statut})


@router.post("/decl-customs-declarations", response_model=DeclCustomsDeclarationOut, status_code=201)
def create_customs_declaration(
    payload: DeclCustomsDeclarationCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.customs_declaration.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, DeclCustomsDeclaration, "reference", data.get("reference"), "reference", cid)
    obj = DeclCustomsDeclaration(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/decl-customs-declarations/{ident}", response_model=DeclCustomsDeclarationOut)
def update_customs_declaration(
    ident: int,
    payload: DeclCustomsDeclarationUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.customs_declaration.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, DeclCustomsDeclaration, ident, "Declarations en douane")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/decl-customs-declarations/{ident}", response_model=DeclCustomsDeclarationOut)
def delete_customs_declaration(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.customs_declaration.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, DeclCustomsDeclaration, ident, "Declarations en douane")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Classifications douanieres (HS) ─────────────────────────────────────────────────

@router.get("/decl-hs-classifications", response_model=List[DeclHsClassificationOut])
def list_hs_classification(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.hs_classification.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, DeclHsClassification, cid, {"statut": statut})


@router.post("/decl-hs-classifications", response_model=DeclHsClassificationOut, status_code=201)
def create_hs_classification(
    payload: DeclHsClassificationCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.hs_classification.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, DeclHsClassification, "reference", data.get("reference"), "reference", cid)
    obj = DeclHsClassification(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/decl-hs-classifications/{ident}", response_model=DeclHsClassificationOut)
def update_hs_classification(
    ident: int,
    payload: DeclHsClassificationUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.hs_classification.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, DeclHsClassification, ident, "Classifications douanieres (HS)")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/decl-hs-classifications/{ident}", response_model=DeclHsClassificationOut)
def delete_hs_classification(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.hs_classification.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, DeclHsClassification, ident, "Classifications douanieres (HS)")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Certificats d' origine ─────────────────────────────────────────────────

@router.get("/decl-origin-certificates", response_model=List[DeclOriginCertificateOut])
def list_origin_certificate(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.origin_certificate.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, DeclOriginCertificate, cid, {"statut": statut})


@router.post("/decl-origin-certificates", response_model=DeclOriginCertificateOut, status_code=201)
def create_origin_certificate(
    payload: DeclOriginCertificateCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.origin_certificate.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, DeclOriginCertificate, "reference", data.get("reference"), "reference", cid)
    obj = DeclOriginCertificate(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/decl-origin-certificates/{ident}", response_model=DeclOriginCertificateOut)
def update_origin_certificate(
    ident: int,
    payload: DeclOriginCertificateUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.origin_certificate.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, DeclOriginCertificate, ident, "Certificats d' origine")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/decl-origin-certificates/{ident}", response_model=DeclOriginCertificateOut)
def delete_origin_certificate(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.origin_certificate.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, DeclOriginCertificate, ident, "Certificats d' origine")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Valeurs en douane ─────────────────────────────────────────────────

@router.get("/decl-customs-valuations", response_model=List[DeclCustomsValuationOut])
def list_customs_valuation(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.customs_valuation.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, DeclCustomsValuation, cid, {"statut": statut})


@router.post("/decl-customs-valuations", response_model=DeclCustomsValuationOut, status_code=201)
def create_customs_valuation(
    payload: DeclCustomsValuationCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.customs_valuation.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, DeclCustomsValuation, "reference", data.get("reference"), "reference", cid)
    obj = DeclCustomsValuation(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/decl-customs-valuations/{ident}", response_model=DeclCustomsValuationOut)
def update_customs_valuation(
    ident: int,
    payload: DeclCustomsValuationUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.customs_valuation.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, DeclCustomsValuation, ident, "Valeurs en douane")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/decl-customs-valuations/{ident}", response_model=DeclCustomsValuationOut)
def delete_customs_valuation(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.customs_valuation.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, DeclCustomsValuation, ident, "Valeurs en douane")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Incoterms ─────────────────────────────────────────────────

@router.get("/decl-incoterms-records", response_model=List[DeclIncotermsRecordOut])
def list_incoterms_record(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.incoterms_record.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, DeclIncotermsRecord, cid, {"statut": statut})


@router.post("/decl-incoterms-records", response_model=DeclIncotermsRecordOut, status_code=201)
def create_incoterms_record(
    payload: DeclIncotermsRecordCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.incoterms_record.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, DeclIncotermsRecord, "reference", data.get("reference"), "reference", cid)
    obj = DeclIncotermsRecord(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/decl-incoterms-records/{ident}", response_model=DeclIncotermsRecordOut)
def update_incoterms_record(
    ident: int,
    payload: DeclIncotermsRecordUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.incoterms_record.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, DeclIncotermsRecord, ident, "Incoterms")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/decl-incoterms-records/{ident}", response_model=DeclIncotermsRecordOut)
def delete_incoterms_record(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.incoterms_record.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, DeclIncotermsRecord, ident, "Incoterms")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Licences d' importation ─────────────────────────────────────────────────

@router.get("/decl-import-licenses", response_model=List[DeclImportLicenseOut])
def list_import_license(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.import_license.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, DeclImportLicense, cid, {"statut": statut})


@router.post("/decl-import-licenses", response_model=DeclImportLicenseOut, status_code=201)
def create_import_license(
    payload: DeclImportLicenseCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.import_license.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, DeclImportLicense, "reference", data.get("reference"), "reference", cid)
    obj = DeclImportLicense(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/decl-import-licenses/{ident}", response_model=DeclImportLicenseOut)
def update_import_license(
    ident: int,
    payload: DeclImportLicenseUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.import_license.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, DeclImportLicense, ident, "Licences d' importation")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/decl-import-licenses/{ident}", response_model=DeclImportLicenseOut)
def delete_import_license(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.import_license.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, DeclImportLicense, ident, "Licences d' importation")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Licences d' exportation ─────────────────────────────────────────────────

@router.get("/decl-export-licenses", response_model=List[DeclExportLicenseOut])
def list_export_license(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.export_license.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, DeclExportLicense, cid, {"statut": statut})


@router.post("/decl-export-licenses", response_model=DeclExportLicenseOut, status_code=201)
def create_export_license(
    payload: DeclExportLicenseCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.export_license.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, DeclExportLicense, "reference", data.get("reference"), "reference", cid)
    obj = DeclExportLicense(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/decl-export-licenses/{ident}", response_model=DeclExportLicenseOut)
def update_export_license(
    ident: int,
    payload: DeclExportLicenseUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.export_license.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, DeclExportLicense, ident, "Licences d' exportation")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/decl-export-licenses/{ident}", response_model=DeclExportLicenseOut)
def delete_export_license(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.export_license.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, DeclExportLicense, ident, "Licences d' exportation")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Pre-dedouanements ─────────────────────────────────────────────────

@router.get("/decl-pre-clearance-submissions", response_model=List[DeclPreClearanceOut])
def list_pre_clearance(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.pre_clearance.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, DeclPreClearance, cid, {"statut": statut})


@router.post("/decl-pre-clearance-submissions", response_model=DeclPreClearanceOut, status_code=201)
def create_pre_clearance(
    payload: DeclPreClearanceCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.pre_clearance.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, DeclPreClearance, "reference", data.get("reference"), "reference", cid)
    obj = DeclPreClearance(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/decl-pre-clearance-submissions/{ident}", response_model=DeclPreClearanceOut)
def update_pre_clearance(
    ident: int,
    payload: DeclPreClearanceUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.pre_clearance.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, DeclPreClearance, ident, "Pre-dedouanements")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/decl-pre-clearance-submissions/{ident}", response_model=DeclPreClearanceOut)
def delete_pre_clearance(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.pre_clearance.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, DeclPreClearance, ident, "Pre-dedouanements")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Factures commerciales ─────────────────────────────────────────────────

@router.get("/decl-customs-invoices", response_model=List[DeclCustomsInvoiceOut])
def list_customs_invoice(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.customs_invoice.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, DeclCustomsInvoice, cid, {"statut": statut})


@router.post("/decl-customs-invoices", response_model=DeclCustomsInvoiceOut, status_code=201)
def create_customs_invoice(
    payload: DeclCustomsInvoiceCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.customs_invoice.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, DeclCustomsInvoice, "reference", data.get("reference"), "reference", cid)
    obj = DeclCustomsInvoice(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/decl-customs-invoices/{ident}", response_model=DeclCustomsInvoiceOut)
def update_customs_invoice(
    ident: int,
    payload: DeclCustomsInvoiceUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.customs_invoice.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, DeclCustomsInvoice, ident, "Factures commerciales")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/decl-customs-invoices/{ident}", response_model=DeclCustomsInvoiceOut)
def delete_customs_invoice(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.customs_invoice.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, DeclCustomsInvoice, ident, "Factures commerciales")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Colisages douaniers ─────────────────────────────────────────────────

@router.get("/decl-packing-lists", response_model=List[DeclPackingListOut])
def list_packing_list(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.packing_list.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, DeclPackingList, cid, {"statut": statut})


@router.post("/decl-packing-lists", response_model=DeclPackingListOut, status_code=201)
def create_packing_list(
    payload: DeclPackingListCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.packing_list.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, DeclPackingList, "reference", data.get("reference"), "reference", cid)
    obj = DeclPackingList(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/decl-packing-lists/{ident}", response_model=DeclPackingListOut)
def update_packing_list(
    ident: int,
    payload: DeclPackingListUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.packing_list.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, DeclPackingList, ident, "Colisages douaniers")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/decl-packing-lists/{ident}", response_model=DeclPackingListOut)
def delete_packing_list(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.packing_list.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, DeclPackingList, ident, "Colisages douaniers")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Certificats d' analyse ─────────────────────────────────────────────────

@router.get("/decl-certificates-of-analysis", response_model=List[DeclCertificateAnalysisOut])
def list_certificate_analysis(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.certificate_analysis.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, DeclCertificateAnalysis, cid, {"statut": statut})


@router.post("/decl-certificates-of-analysis", response_model=DeclCertificateAnalysisOut, status_code=201)
def create_certificate_analysis(
    payload: DeclCertificateAnalysisCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.certificate_analysis.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, DeclCertificateAnalysis, "reference", data.get("reference"), "reference", cid)
    obj = DeclCertificateAnalysis(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/decl-certificates-of-analysis/{ident}", response_model=DeclCertificateAnalysisOut)
def update_certificate_analysis(
    ident: int,
    payload: DeclCertificateAnalysisUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.certificate_analysis.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, DeclCertificateAnalysis, ident, "Certificats d' analyse")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/decl-certificates-of-analysis/{ident}", response_model=DeclCertificateAnalysisOut)
def delete_certificate_analysis(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.certificate_analysis.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, DeclCertificateAnalysis, ident, "Certificats d' analyse")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Demandes phytosanitaires ─────────────────────────────────────────────────

@router.get("/decl-phytosanitary-applications", response_model=List[DeclPhytosanitaryAppOut])
def list_phytosanitary_app(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.phytosanitary_app.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, DeclPhytosanitaryApp, cid, {"statut": statut})


@router.post("/decl-phytosanitary-applications", response_model=DeclPhytosanitaryAppOut, status_code=201)
def create_phytosanitary_app(
    payload: DeclPhytosanitaryAppCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.phytosanitary_app.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, DeclPhytosanitaryApp, "reference", data.get("reference"), "reference", cid)
    obj = DeclPhytosanitaryApp(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/decl-phytosanitary-applications/{ident}", response_model=DeclPhytosanitaryAppOut)
def update_phytosanitary_app(
    ident: int,
    payload: DeclPhytosanitaryAppUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.phytosanitary_app.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, DeclPhytosanitaryApp, ident, "Demandes phytosanitaires")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/decl-phytosanitary-applications/{ident}", response_model=DeclPhytosanitaryAppOut)
def delete_phytosanitary_app(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.phytosanitary_app.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, DeclPhytosanitaryApp, ident, "Demandes phytosanitaires")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Paiements douaniers ─────────────────────────────────────────────────

@router.get("/decl-customs-payments", response_model=List[DeclCustomsPaymentOut])
def list_customs_payment(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.customs_payment.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, DeclCustomsPayment, cid, {"statut": statut})


@router.post("/decl-customs-payments", response_model=DeclCustomsPaymentOut, status_code=201)
def create_customs_payment(
    payload: DeclCustomsPaymentCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.customs_payment.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, DeclCustomsPayment, "reference", data.get("reference"), "reference", cid)
    obj = DeclCustomsPayment(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/decl-customs-payments/{ident}", response_model=DeclCustomsPaymentOut)
def update_customs_payment(
    ident: int,
    payload: DeclCustomsPaymentUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.customs_payment.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, DeclCustomsPayment, ident, "Paiements douaniers")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/decl-customs-payments/{ident}", response_model=DeclCustomsPaymentOut)
def delete_customs_payment(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.customs_payment.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, DeclCustomsPayment, ident, "Paiements douaniers")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Documents de transit (T1/T2) ─────────────────────────────────────────────────

@router.get("/decl-transit-documents", response_model=List[DeclTransitDocumentOut])
def list_transit_document(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.transit_document.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, DeclTransitDocument, cid, {"statut": statut})


@router.post("/decl-transit-documents", response_model=DeclTransitDocumentOut, status_code=201)
def create_transit_document(
    payload: DeclTransitDocumentCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.transit_document.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, DeclTransitDocument, "reference", data.get("reference"), "reference", cid)
    obj = DeclTransitDocument(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/decl-transit-documents/{ident}", response_model=DeclTransitDocumentOut)
def update_transit_document(
    ident: int,
    payload: DeclTransitDocumentUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.transit_document.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, DeclTransitDocument, ident, "Documents de transit (T1/T2)")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/decl-transit-documents/{ident}", response_model=DeclTransitDocumentOut)
def delete_transit_document(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.transit_document.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, DeclTransitDocument, ident, "Documents de transit (T1/T2)")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Declarations marchandises dangereuses ─────────────────────────────────────────────────

@router.get("/decl-dangerous-goods-decls", response_model=List[DeclDangerousGoodsOut])
def list_dangerous_goods_decl(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.dangerous_goods_decl.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, DeclDangerousGoods, cid, {"statut": statut})


@router.post("/decl-dangerous-goods-decls", response_model=DeclDangerousGoodsOut, status_code=201)
def create_dangerous_goods_decl(
    payload: DeclDangerousGoodsCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.dangerous_goods_decl.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, DeclDangerousGoods, "reference", data.get("reference"), "reference", cid)
    obj = DeclDangerousGoods(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/decl-dangerous-goods-decls/{ident}", response_model=DeclDangerousGoodsOut)
def update_dangerous_goods_decl(
    ident: int,
    payload: DeclDangerousGoodsUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.dangerous_goods_decl.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, DeclDangerousGoods, ident, "Declarations marchandises dangereuses")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/decl-dangerous-goods-decls/{ident}", response_model=DeclDangerousGoodsOut)
def delete_dangerous_goods_decl(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.dangerous_goods_decl.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, DeclDangerousGoods, ident, "Declarations marchandises dangereuses")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Entrees en entrepot sous douane ─────────────────────────────────────────────────

@router.get("/decl-bonded-warehouse-entries", response_model=List[DeclBondedWarehouseEntryOut])
def list_bonded_warehouse_entry(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.bonded_warehouse_entry.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, DeclBondedWarehouseEntry, cid, {"statut": statut})


@router.post("/decl-bonded-warehouse-entries", response_model=DeclBondedWarehouseEntryOut, status_code=201)
def create_bonded_warehouse_entry(
    payload: DeclBondedWarehouseEntryCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.bonded_warehouse_entry.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, DeclBondedWarehouseEntry, "reference", data.get("reference"), "reference", cid)
    obj = DeclBondedWarehouseEntry(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/decl-bonded-warehouse-entries/{ident}", response_model=DeclBondedWarehouseEntryOut)
def update_bonded_warehouse_entry(
    ident: int,
    payload: DeclBondedWarehouseEntryUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.bonded_warehouse_entry.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, DeclBondedWarehouseEntry, ident, "Entrees en entrepot sous douane")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/decl-bonded-warehouse-entries/{ident}", response_model=DeclBondedWarehouseEntryOut)
def delete_bonded_warehouse_entry(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.bonded_warehouse_entry.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, DeclBondedWarehouseEntry, ident, "Entrees en entrepot sous douane")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Demandes de franchise de droits ─────────────────────────────────────────────────

@router.get("/decl-duty-relief-claims", response_model=List[DeclDutyReliefClaimOut])
def list_duty_relief_claim(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.duty_relief_claim.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, DeclDutyReliefClaim, cid, {"statut": statut})


@router.post("/decl-duty-relief-claims", response_model=DeclDutyReliefClaimOut, status_code=201)
def create_duty_relief_claim(
    payload: DeclDutyReliefClaimCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.duty_relief_claim.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, DeclDutyReliefClaim, "reference", data.get("reference"), "reference", cid)
    obj = DeclDutyReliefClaim(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/decl-duty-relief-claims/{ident}", response_model=DeclDutyReliefClaimOut)
def update_duty_relief_claim(
    ident: int,
    payload: DeclDutyReliefClaimUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.duty_relief_claim.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, DeclDutyReliefClaim, ident, "Demandes de franchise de droits")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/decl-duty-relief-claims/{ident}", response_model=DeclDutyReliefClaimOut)
def delete_duty_relief_claim(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.duty_relief_claim.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, DeclDutyReliefClaim, ident, "Demandes de franchise de droits")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Rectifications de manifeste ─────────────────────────────────────────────────

@router.get("/decl-manifest-corrections", response_model=List[DeclManifestCorrectionOut])
def list_manifest_correction(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.manifest_correction.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, DeclManifestCorrection, cid, {"statut": statut})


@router.post("/decl-manifest-corrections", response_model=DeclManifestCorrectionOut, status_code=201)
def create_manifest_correction(
    payload: DeclManifestCorrectionCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.manifest_correction.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, DeclManifestCorrection, "reference", data.get("reference"), "reference", cid)
    obj = DeclManifestCorrection(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/decl-manifest-corrections/{ident}", response_model=DeclManifestCorrectionOut)
def update_manifest_correction(
    ident: int,
    payload: DeclManifestCorrectionUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.manifest_correction.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, DeclManifestCorrection, ident, "Rectifications de manifeste")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/decl-manifest-corrections/{ident}", response_model=DeclManifestCorrectionOut)
def delete_manifest_correction(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.manifest_correction.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, DeclManifestCorrection, ident, "Rectifications de manifeste")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Support controle douanier ─────────────────────────────────────────────────

@router.get("/decl-customs-audit-support", response_model=List[DeclCustomsAuditSupportOut])
def list_customs_audit_support(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.customs_audit_support.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, DeclCustomsAuditSupport, cid, {"statut": statut})


@router.post("/decl-customs-audit-support", response_model=DeclCustomsAuditSupportOut, status_code=201)
def create_customs_audit_support(
    payload: DeclCustomsAuditSupportCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.customs_audit_support.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, DeclCustomsAuditSupport, "reference", data.get("reference"), "reference", cid)
    obj = DeclCustomsAuditSupport(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/decl-customs-audit-support/{ident}", response_model=DeclCustomsAuditSupportOut)
def update_customs_audit_support(
    ident: int,
    payload: DeclCustomsAuditSupportUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.customs_audit_support.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, DeclCustomsAuditSupport, ident, "Support controle douanier")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/decl-customs-audit-support/{ident}", response_model=DeclCustomsAuditSupportOut)
def delete_customs_audit_support(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transit.customs_audit_support.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, DeclCustomsAuditSupport, ident, "Support controle douanier")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj

