"""Routeur CRUD genere pour comptabilite-ohada (expansion)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List

from app.core.database import get_db
from app.core.permissions import require_perm
from app.models.user import User
from app.models.compta_c_deep import (
    CmptcJournalReversal,
    CmptcBankReconciliation,
)
from app.schemas.compta_c_deep import (
    CmptcJournalReversalCreate, CmptcJournalReversalUpdate, CmptcJournalReversalOut,
    CmptcBankReconciliationCreate, CmptcBankReconciliationUpdate, CmptcBankReconciliationOut,
)

router = APIRouter(tags=["comptabilite-ohada (expansion)"])


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

@router.get("/nomenclatures", summary="Vocabulaire metier comptabilite-ohada")
def nomenclatures(user: User = Depends(require_perm("comptabilite.nomenclature.read"))):
    from app.models import compta_c_deep as _md
    import enum as _pyenum
    out = {}
    for name in dir(_md):
        obj = getattr(_md, name)
        if isinstance(obj, type) and issubclass(obj, _pyenum.Enum) and obj is not _pyenum.Enum:
            out[name.lower()] = [{"code": m.name, "valeur": m.value} for m in obj]
    return out


# ─── Contre-passations d'ecritures ─────────────────────────────────────────────────

@router.get("/cmptc-journal-reversals", response_model=List[CmptcJournalReversalOut])
def list_journal_reversal(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("comptabilite.journal_reversal.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, CmptcJournalReversal, cid, {"statut": statut})


@router.post("/cmptc-journal-reversals", response_model=CmptcJournalReversalOut, status_code=201)
def create_journal_reversal(
    payload: CmptcJournalReversalCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("comptabilite.journal_reversal.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, CmptcJournalReversal, "reference", data.get("reference"), "reference", cid)
    obj = CmptcJournalReversal(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/cmptc-journal-reversals/{ident}", response_model=CmptcJournalReversalOut)
def update_journal_reversal(
    ident: int,
    payload: CmptcJournalReversalUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("comptabilite.journal_reversal.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CmptcJournalReversal, ident, "Contre-passations d'ecritures")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/cmptc-journal-reversals/{ident}", response_model=CmptcJournalReversalOut)
def delete_journal_reversal(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("comptabilite.journal_reversal.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CmptcJournalReversal, ident, "Contre-passations d'ecritures")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Rapprochements bancaires ─────────────────────────────────────────────────

@router.get("/cmptc-bank-reconciliations", response_model=List[CmptcBankReconciliationOut])
def list_bank_reconciliation(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("comptabilite.bank_reconciliation.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, CmptcBankReconciliation, cid, {"statut": statut})


@router.post("/cmptc-bank-reconciliations", response_model=CmptcBankReconciliationOut, status_code=201)
def create_bank_reconciliation(
    payload: CmptcBankReconciliationCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("comptabilite.bank_reconciliation.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, CmptcBankReconciliation, "reference", data.get("reference"), "reference", cid)
    obj = CmptcBankReconciliation(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/cmptc-bank-reconciliations/{ident}", response_model=CmptcBankReconciliationOut)
def update_bank_reconciliation(
    ident: int,
    payload: CmptcBankReconciliationUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("comptabilite.bank_reconciliation.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CmptcBankReconciliation, ident, "Rapprochements bancaires")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/cmptc-bank-reconciliations/{ident}", response_model=CmptcBankReconciliationOut)
def delete_bank_reconciliation(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("comptabilite.bank_reconciliation.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CmptcBankReconciliation, ident, "Rapprochements bancaires")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj

