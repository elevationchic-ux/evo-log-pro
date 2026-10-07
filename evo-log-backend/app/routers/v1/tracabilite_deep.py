"""Routeur CRUD genere pour tracabilite-bout-en-bout (expansion wave 6)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List

from app.core.database import get_db
from app.core.permissions import require_perm
from app.models.user import User
from app.models.tracabilite_deep import (
    TraceabilityEvent,
    ChainOfCustodyTransfer,
    BatchGenealogy,
    SerialGenealogy,
    DocumentHash,
    GeolocationTrace,
    ColdChainTrace,
    IncidentChainOfCommand,
    RegulatoryTraceExport,
    ImmutableAuditLog,
    TimestampAuthority,
    WitnessSignature,
    IntegrityMerkleProof,
    ContainerSeal,
    CargoHandoff,
    AccessSecurityLog,
    ConsentGrant,
    AntiTamperingEvent,
    RetentionPolicy,
)
from app.schemas.tracabilite_deep import (
    TraceabilityEventCreate, TraceabilityEventUpdate, TraceabilityEventOut,
    ChainOfCustodyTransferCreate, ChainOfCustodyTransferUpdate, ChainOfCustodyTransferOut,
    BatchGenealogyCreate, BatchGenealogyUpdate, BatchGenealogyOut,
    SerialGenealogyCreate, SerialGenealogyUpdate, SerialGenealogyOut,
    DocumentHashCreate, DocumentHashUpdate, DocumentHashOut,
    GeolocationTraceCreate, GeolocationTraceUpdate, GeolocationTraceOut,
    ColdChainTraceCreate, ColdChainTraceUpdate, ColdChainTraceOut,
    IncidentChainOfCommandCreate, IncidentChainOfCommandUpdate, IncidentChainOfCommandOut,
    RegulatoryTraceExportCreate, RegulatoryTraceExportUpdate, RegulatoryTraceExportOut,
    ImmutableAuditLogCreate, ImmutableAuditLogUpdate, ImmutableAuditLogOut,
    TimestampAuthorityCreate, TimestampAuthorityUpdate, TimestampAuthorityOut,
    WitnessSignatureCreate, WitnessSignatureUpdate, WitnessSignatureOut,
    IntegrityMerkleProofCreate, IntegrityMerkleProofUpdate, IntegrityMerkleProofOut,
    ContainerSealCreate, ContainerSealUpdate, ContainerSealOut,
    CargoHandoffCreate, CargoHandoffUpdate, CargoHandoffOut,
    AccessSecurityLogCreate, AccessSecurityLogUpdate, AccessSecurityLogOut,
    ConsentGrantCreate, ConsentGrantUpdate, ConsentGrantOut,
    AntiTamperingEventCreate, AntiTamperingEventUpdate, AntiTamperingEventOut,
    RetentionPolicyCreate, RetentionPolicyUpdate, RetentionPolicyOut,
)

router = APIRouter(tags=["tracabilite-bout-en-bout (expansion)"])


# --- Helpers generiques ---------------------------------------------------

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
            detail=f"{label} {value} existe deja dans votre organisation.",
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


# --- Nomenclatures ---------------------------------------------------------

@router.get("/nomenclatures", summary="Vocabulaire metier tracabilite-bout-en-bout")
def nomenclatures(user: User = Depends(require_perm("tracabilite.nomenclature.read"))):
    from app.models import tracabilite_deep as _md
    import enum as _pyenum
    out = {}
    for name in dir(_md):
        obj = getattr(_md, name)
        if isinstance(obj, type) and issubclass(obj, _pyenum.Enum) and obj is not _pyenum.Enum:
            out[name.lower()] = [{"code": m.name, "valeur": m.value} for m in obj]
    return out


# --- Evenement tracabilite ---------------------------------------------------------

@router.get("/events", response_model=List[TraceabilityEventOut])
def list_events(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("tracabilite.events.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, TraceabilityEvent, cid, {'statut': statut})


@router.post("/events", response_model=TraceabilityEventOut, status_code=201)
def create_events(
    payload: TraceabilityEventCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tracabilite.events.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, TraceabilityEvent, "event_uid", data.get("event_uid"), "event_uid", cid)
    obj = TraceabilityEvent(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/events/{ident}", response_model=TraceabilityEventOut)
def update_events(
    ident: int,
    payload: TraceabilityEventUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tracabilite.events.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TraceabilityEvent, ident, "Evenement tracabilite")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/events/{ident}", response_model=TraceabilityEventOut)
def delete_events(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tracabilite.events.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TraceabilityEvent, ident, "Evenement tracabilite")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# --- Chaine de custody ---------------------------------------------------------

@router.get("/custody-transfers", response_model=List[ChainOfCustodyTransferOut])
def list_custody_transfers(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("tracabilite.custody_transfers.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, ChainOfCustodyTransfer, cid, {'statut': statut})


@router.post("/custody-transfers", response_model=ChainOfCustodyTransferOut, status_code=201)
def create_custody_transfers(
    payload: ChainOfCustodyTransferCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tracabilite.custody_transfers.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, ChainOfCustodyTransfer, "reference_transfert", data.get("reference_transfert"), "reference_transfert", cid)
    obj = ChainOfCustodyTransfer(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/custody-transfers/{ident}", response_model=ChainOfCustodyTransferOut)
def update_custody_transfers(
    ident: int,
    payload: ChainOfCustodyTransferUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tracabilite.custody_transfers.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ChainOfCustodyTransfer, ident, "Chaine de custody")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/custody-transfers/{ident}", response_model=ChainOfCustodyTransferOut)
def delete_custody_transfers(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tracabilite.custody_transfers.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ChainOfCustodyTransfer, ident, "Chaine de custody")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# --- Genealogie lot ---------------------------------------------------------

@router.get("/batch-genealogy", response_model=List[BatchGenealogyOut])
def list_batch_genealogy(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("tracabilite.batch_genealogy.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, BatchGenealogy, cid, {'statut': statut})


@router.post("/batch-genealogy", response_model=BatchGenealogyOut, status_code=201)
def create_batch_genealogy(
    payload: BatchGenealogyCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tracabilite.batch_genealogy.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, BatchGenealogy, "child_lot", data.get("child_lot"), "child_lot", cid)
    obj = BatchGenealogy(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/batch-genealogy/{ident}", response_model=BatchGenealogyOut)
def update_batch_genealogy(
    ident: int,
    payload: BatchGenealogyUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tracabilite.batch_genealogy.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, BatchGenealogy, ident, "Genealogie lot")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/batch-genealogy/{ident}", response_model=BatchGenealogyOut)
def delete_batch_genealogy(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tracabilite.batch_genealogy.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, BatchGenealogy, ident, "Genealogie lot")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# --- Genealogie numero serial ---------------------------------------------------------

@router.get("/serial-genealogy", response_model=List[SerialGenealogyOut])
def list_serial_genealogy(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("tracabilite.serial_genealogy.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, SerialGenealogy, cid, {'statut': statut})


@router.post("/serial-genealogy", response_model=SerialGenealogyOut, status_code=201)
def create_serial_genealogy(
    payload: SerialGenealogyCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tracabilite.serial_genealogy.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, SerialGenealogy, "child_serial", data.get("child_serial"), "child_serial", cid)
    obj = SerialGenealogy(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/serial-genealogy/{ident}", response_model=SerialGenealogyOut)
def update_serial_genealogy(
    ident: int,
    payload: SerialGenealogyUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tracabilite.serial_genealogy.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, SerialGenealogy, ident, "Genealogie numero serial")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/serial-genealogy/{ident}", response_model=SerialGenealogyOut)
def delete_serial_genealogy(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tracabilite.serial_genealogy.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, SerialGenealogy, ident, "Genealogie numero serial")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# --- Empreinte document ---------------------------------------------------------

@router.get("/document-hashes", response_model=List[DocumentHashOut])
def list_document_hashes(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("tracabilite.document_hashes.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, DocumentHash, cid, {'statut': statut})


@router.post("/document-hashes", response_model=DocumentHashOut, status_code=201)
def create_document_hashes(
    payload: DocumentHashCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tracabilite.document_hashes.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, DocumentHash, "document_ref", data.get("document_ref"), "document_ref", cid)
    obj = DocumentHash(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/document-hashes/{ident}", response_model=DocumentHashOut)
def update_document_hashes(
    ident: int,
    payload: DocumentHashUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tracabilite.document_hashes.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, DocumentHash, ident, "Empreinte document")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/document-hashes/{ident}", response_model=DocumentHashOut)
def delete_document_hashes(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tracabilite.document_hashes.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, DocumentHash, ident, "Empreinte document")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# --- Trace geolocalisation ---------------------------------------------------------

@router.get("/geolocations", response_model=List[GeolocationTraceOut])
def list_geolocations(db: Session = Depends(get_db),
    user: User = Depends(require_perm("tracabilite.geolocations.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, GeolocationTrace, cid)


@router.post("/geolocations", response_model=GeolocationTraceOut, status_code=201)
def create_geolocations(
    payload: GeolocationTraceCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tracabilite.geolocations.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    obj = GeolocationTrace(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/geolocations/{ident}", response_model=GeolocationTraceOut)
def update_geolocations(
    ident: int,
    payload: GeolocationTraceUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tracabilite.geolocations.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, GeolocationTrace, ident, "Trace geolocalisation")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/geolocations/{ident}", response_model=GeolocationTraceOut)
def delete_geolocations(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tracabilite.geolocations.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, GeolocationTrace, ident, "Trace geolocalisation")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# --- Chaine du froid ---------------------------------------------------------

@router.get("/cold-chain", response_model=List[ColdChainTraceOut])
def list_cold_chain(db: Session = Depends(get_db),
    user: User = Depends(require_perm("tracabilite.cold_chain.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, ColdChainTrace, cid)


@router.post("/cold-chain", response_model=ColdChainTraceOut, status_code=201)
def create_cold_chain(
    payload: ColdChainTraceCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tracabilite.cold_chain.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    obj = ColdChainTrace(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/cold-chain/{ident}", response_model=ColdChainTraceOut)
def update_cold_chain(
    ident: int,
    payload: ColdChainTraceUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tracabilite.cold_chain.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ColdChainTrace, ident, "Chaine du froid")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/cold-chain/{ident}", response_model=ColdChainTraceOut)
def delete_cold_chain(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tracabilite.cold_chain.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ColdChainTrace, ident, "Chaine du froid")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# --- Post commandement incident ---------------------------------------------------------

@router.get("/incidents", response_model=List[IncidentChainOfCommandOut])
def list_incidents(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("tracabilite.incidents.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, IncidentChainOfCommand, cid, {'statut': statut})


@router.post("/incidents", response_model=IncidentChainOfCommandOut, status_code=201)
def create_incidents(
    payload: IncidentChainOfCommandCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tracabilite.incidents.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, IncidentChainOfCommand, "reference_incident", data.get("reference_incident"), "reference_incident", cid)
    obj = IncidentChainOfCommand(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/incidents/{ident}", response_model=IncidentChainOfCommandOut)
def update_incidents(
    ident: int,
    payload: IncidentChainOfCommandUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tracabilite.incidents.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, IncidentChainOfCommand, ident, "Post commandement incident")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/incidents/{ident}", response_model=IncidentChainOfCommandOut)
def delete_incidents(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tracabilite.incidents.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, IncidentChainOfCommand, ident, "Post commandement incident")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# --- Export reglementaire ---------------------------------------------------------

@router.get("/regulatory-exports", response_model=List[RegulatoryTraceExportOut])
def list_regulatory_exports(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("tracabilite.regulatory_exports.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, RegulatoryTraceExport, cid, {'statut': statut})


@router.post("/regulatory-exports", response_model=RegulatoryTraceExportOut, status_code=201)
def create_regulatory_exports(
    payload: RegulatoryTraceExportCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tracabilite.regulatory_exports.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, RegulatoryTraceExport, "numero_expedition", data.get("numero_expedition"), "numero_expedition", cid)
    obj = RegulatoryTraceExport(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/regulatory-exports/{ident}", response_model=RegulatoryTraceExportOut)
def update_regulatory_exports(
    ident: int,
    payload: RegulatoryTraceExportUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tracabilite.regulatory_exports.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, RegulatoryTraceExport, ident, "Export reglementaire")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/regulatory-exports/{ident}", response_model=RegulatoryTraceExportOut)
def delete_regulatory_exports(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tracabilite.regulatory_exports.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, RegulatoryTraceExport, ident, "Export reglementaire")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# --- Journal audit inalterable ---------------------------------------------------------

@router.get("/audit-logs", response_model=List[ImmutableAuditLogOut])
def list_audit_logs(db: Session = Depends(get_db),
    user: User = Depends(require_perm("tracabilite.audit_logs.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, ImmutableAuditLog, cid)


@router.post("/audit-logs", response_model=ImmutableAuditLogOut, status_code=201)
def create_audit_logs(
    payload: ImmutableAuditLogCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tracabilite.audit_logs.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    obj = ImmutableAuditLog(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/audit-logs/{ident}", response_model=ImmutableAuditLogOut)
def update_audit_logs(
    ident: int,
    payload: ImmutableAuditLogUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tracabilite.audit_logs.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ImmutableAuditLog, ident, "Journal audit inalterable")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/audit-logs/{ident}", response_model=ImmutableAuditLogOut)
def delete_audit_logs(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tracabilite.audit_logs.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ImmutableAuditLog, ident, "Journal audit inalterable")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# --- Horodatage qualifie ---------------------------------------------------------

@router.get("/timestamps", response_model=List[TimestampAuthorityOut])
def list_timestamps(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("tracabilite.timestamps.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, TimestampAuthority, cid, {'statut': statut})


@router.post("/timestamps", response_model=TimestampAuthorityOut, status_code=201)
def create_timestamps(
    payload: TimestampAuthorityCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tracabilite.timestamps.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, TimestampAuthority, "token_tsa", data.get("token_tsa"), "token_tsa", cid)
    obj = TimestampAuthority(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/timestamps/{ident}", response_model=TimestampAuthorityOut)
def update_timestamps(
    ident: int,
    payload: TimestampAuthorityUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tracabilite.timestamps.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TimestampAuthority, ident, "Horodatage qualifie")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/timestamps/{ident}", response_model=TimestampAuthorityOut)
def delete_timestamps(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tracabilite.timestamps.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TimestampAuthority, ident, "Horodatage qualifie")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# --- Signature / temoin ---------------------------------------------------------

@router.get("/signatures", response_model=List[WitnessSignatureOut])
def list_signatures(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("tracabilite.signatures.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, WitnessSignature, cid, {'statut': statut})


@router.post("/signatures", response_model=WitnessSignatureOut, status_code=201)
def create_signatures(
    payload: WitnessSignatureCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tracabilite.signatures.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, WitnessSignature, "reference_signature", data.get("reference_signature"), "reference_signature", cid)
    obj = WitnessSignature(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/signatures/{ident}", response_model=WitnessSignatureOut)
def update_signatures(
    ident: int,
    payload: WitnessSignatureUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tracabilite.signatures.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, WitnessSignature, ident, "Signature / temoin")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/signatures/{ident}", response_model=WitnessSignatureOut)
def delete_signatures(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tracabilite.signatures.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, WitnessSignature, ident, "Signature / temoin")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# --- Preuve Merkle ---------------------------------------------------------

@router.get("/merkle-proofs", response_model=List[IntegrityMerkleProofOut])
def list_merkle_proofs(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("tracabilite.merkle_proofs.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, IntegrityMerkleProof, cid, {'statut': statut})


@router.post("/merkle-proofs", response_model=IntegrityMerkleProofOut, status_code=201)
def create_merkle_proofs(
    payload: IntegrityMerkleProofCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tracabilite.merkle_proofs.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, IntegrityMerkleProof, "periode", data.get("periode"), "periode", cid)
    obj = IntegrityMerkleProof(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/merkle-proofs/{ident}", response_model=IntegrityMerkleProofOut)
def update_merkle_proofs(
    ident: int,
    payload: IntegrityMerkleProofUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tracabilite.merkle_proofs.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, IntegrityMerkleProof, ident, "Preuve Merkle")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/merkle-proofs/{ident}", response_model=IntegrityMerkleProofOut)
def delete_merkle_proofs(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tracabilite.merkle_proofs.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, IntegrityMerkleProof, ident, "Preuve Merkle")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# --- Sceau conteneur ISO 17712 ---------------------------------------------------------

@router.get("/seals", response_model=List[ContainerSealOut])
def list_seals(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("tracabilite.seals.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, ContainerSeal, cid, {'statut': statut})


@router.post("/seals", response_model=ContainerSealOut, status_code=201)
def create_seals(
    payload: ContainerSealCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tracabilite.seals.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, ContainerSeal, "numero_sceau", data.get("numero_sceau"), "numero_sceau", cid)
    obj = ContainerSeal(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/seals/{ident}", response_model=ContainerSealOut)
def update_seals(
    ident: int,
    payload: ContainerSealUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tracabilite.seals.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ContainerSeal, ident, "Sceau conteneur ISO 17712")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/seals/{ident}", response_model=ContainerSealOut)
def delete_seals(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tracabilite.seals.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ContainerSeal, ident, "Sceau conteneur ISO 17712")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# --- Transfert cargo multimodal ---------------------------------------------------------

@router.get("/cargo-handoffs", response_model=List[CargoHandoffOut])
def list_cargo_handoffs(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("tracabilite.cargo_handoffs.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, CargoHandoff, cid, {'statut': statut})


@router.post("/cargo-handoffs", response_model=CargoHandoffOut, status_code=201)
def create_cargo_handoffs(
    payload: CargoHandoffCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tracabilite.cargo_handoffs.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, CargoHandoff, "reference_handoff", data.get("reference_handoff"), "reference_handoff", cid)
    obj = CargoHandoff(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/cargo-handoffs/{ident}", response_model=CargoHandoffOut)
def update_cargo_handoffs(
    ident: int,
    payload: CargoHandoffUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tracabilite.cargo_handoffs.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CargoHandoff, ident, "Transfert cargo multimodal")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/cargo-handoffs/{ident}", response_model=CargoHandoffOut)
def delete_cargo_handoffs(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tracabilite.cargo_handoffs.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CargoHandoff, ident, "Transfert cargo multimodal")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# --- Journal securite acces ---------------------------------------------------------

@router.get("/access-logs", response_model=List[AccessSecurityLogOut])
def list_access_logs(db: Session = Depends(get_db),
    user: User = Depends(require_perm("tracabilite.access_logs.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, AccessSecurityLog, cid)


@router.post("/access-logs", response_model=AccessSecurityLogOut, status_code=201)
def create_access_logs(
    payload: AccessSecurityLogCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tracabilite.access_logs.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    obj = AccessSecurityLog(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/access-logs/{ident}", response_model=AccessSecurityLogOut)
def update_access_logs(
    ident: int,
    payload: AccessSecurityLogUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tracabilite.access_logs.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, AccessSecurityLog, ident, "Journal securite acces")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/access-logs/{ident}", response_model=AccessSecurityLogOut)
def delete_access_logs(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tracabilite.access_logs.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, AccessSecurityLog, ident, "Journal securite acces")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# --- Consentement RGPD / loi Cameroun ---------------------------------------------------------

@router.get("/consents", response_model=List[ConsentGrantOut])
def list_consents(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("tracabilite.consents.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, ConsentGrant, cid, {'statut': statut})


@router.post("/consents", response_model=ConsentGrantOut, status_code=201)
def create_consents(
    payload: ConsentGrantCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tracabilite.consents.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, ConsentGrant, "reference_consentement", data.get("reference_consentement"), "reference_consentement", cid)
    obj = ConsentGrant(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/consents/{ident}", response_model=ConsentGrantOut)
def update_consents(
    ident: int,
    payload: ConsentGrantUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tracabilite.consents.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ConsentGrant, ident, "Consentement RGPD / loi Cameroun")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/consents/{ident}", response_model=ConsentGrantOut)
def delete_consents(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tracabilite.consents.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ConsentGrant, ident, "Consentement RGPD / loi Cameroun")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# --- Evenement anti-falsification ---------------------------------------------------------

@router.get("/anti-tampering", response_model=List[AntiTamperingEventOut])
def list_anti_tampering(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("tracabilite.anti_tampering.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, AntiTamperingEvent, cid, {'statut': statut})


@router.post("/anti-tampering", response_model=AntiTamperingEventOut, status_code=201)
def create_anti_tampering(
    payload: AntiTamperingEventCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tracabilite.anti_tampering.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, AntiTamperingEvent, "reference_alerte", data.get("reference_alerte"), "reference_alerte", cid)
    obj = AntiTamperingEvent(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/anti-tampering/{ident}", response_model=AntiTamperingEventOut)
def update_anti_tampering(
    ident: int,
    payload: AntiTamperingEventUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tracabilite.anti_tampering.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, AntiTamperingEvent, ident, "Evenement anti-falsification")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/anti-tampering/{ident}", response_model=AntiTamperingEventOut)
def delete_anti_tampering(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tracabilite.anti_tampering.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, AntiTamperingEvent, ident, "Evenement anti-falsification")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# --- Politique conservation ---------------------------------------------------------

@router.get("/retention-policies", response_model=List[RetentionPolicyOut])
def list_retention_policies(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("tracabilite.retention_policies.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, RetentionPolicy, cid, {'statut': statut})


@router.post("/retention-policies", response_model=RetentionPolicyOut, status_code=201)
def create_retention_policies(
    payload: RetentionPolicyCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tracabilite.retention_policies.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, RetentionPolicy, "code_politique", data.get("code_politique"), "code_politique", cid)
    obj = RetentionPolicy(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/retention-policies/{ident}", response_model=RetentionPolicyOut)
def update_retention_policies(
    ident: int,
    payload: RetentionPolicyUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tracabilite.retention_policies.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, RetentionPolicy, ident, "Politique conservation")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/retention-policies/{ident}", response_model=RetentionPolicyOut)
def delete_retention_policies(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tracabilite.retention_policies.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, RetentionPolicy, ident, "Politique conservation")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj

