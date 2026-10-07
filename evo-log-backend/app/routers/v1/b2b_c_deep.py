"""Routeur CRUD genere pour client-b2b (expansion)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List

from app.core.database import get_db
from app.core.permissions import require_perm
from app.models.user import User
from app.models.b2b_c_deep import (
    B2bCContractAgreement,
    B2bCPriceList,
    B2bCSalesOrder,
    B2bCCreditAccount,
    B2bCSupportTicket,
)
from app.schemas.b2b_c_deep import (
    B2bCContractAgreementCreate, B2bCContractAgreementUpdate, B2bCContractAgreementOut,
    B2bCPriceListCreate, B2bCPriceListUpdate, B2bCPriceListOut,
    B2bCSalesOrderCreate, B2bCSalesOrderUpdate, B2bCSalesOrderOut,
    B2bCCreditAccountCreate, B2bCCreditAccountUpdate, B2bCCreditAccountOut,
    B2bCSupportTicketCreate, B2bCSupportTicketUpdate, B2bCSupportTicketOut,
)

router = APIRouter(tags=["client-b2b (expansion)"])


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

@router.get("/nomenclatures", summary="Vocabulaire metier client-b2b")
def nomenclatures(user: User = Depends(require_perm("b2b.nomenclature.read"))):
    from app.models import b2b_c_deep as _md
    import enum as _pyenum
    out = {}
    for name in dir(_md):
        obj = getattr(_md, name)
        if isinstance(obj, type) and issubclass(obj, _pyenum.Enum) and obj is not _pyenum.Enum:
            out[name.lower()] = [{"code": m.name, "valeur": m.value} for m in obj]
    return out


# ─── Contrats-cadres clients ─────────────────────────────────────────────────

@router.get("/b2bc-contracts", response_model=List[B2bCContractAgreementOut])
def list_contract_agreement(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.contract_agreement.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, B2bCContractAgreement, cid, {"statut": statut})


@router.post("/b2bc-contracts", response_model=B2bCContractAgreementOut, status_code=201)
def create_contract_agreement(
    payload: B2bCContractAgreementCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.contract_agreement.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, B2bCContractAgreement, "reference", data.get("reference"), "reference", cid)
    obj = B2bCContractAgreement(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/b2bc-contracts/{ident}", response_model=B2bCContractAgreementOut)
def update_contract_agreement(
    ident: int,
    payload: B2bCContractAgreementUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.contract_agreement.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, B2bCContractAgreement, ident, "Contrats-cadres clients")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/b2bc-contracts/{ident}", response_model=B2bCContractAgreementOut)
def delete_contract_agreement(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.contract_agreement.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, B2bCContractAgreement, ident, "Contrats-cadres clients")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Grilles tarifaires client ─────────────────────────────────────────────────

@router.get("/b2bc-price-lists", response_model=List[B2bCPriceListOut])
def list_price_list(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.price_list.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, B2bCPriceList, cid, {"statut": statut})


@router.post("/b2bc-price-lists", response_model=B2bCPriceListOut, status_code=201)
def create_price_list(
    payload: B2bCPriceListCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.price_list.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, B2bCPriceList, "reference", data.get("reference"), "reference", cid)
    obj = B2bCPriceList(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/b2bc-price-lists/{ident}", response_model=B2bCPriceListOut)
def update_price_list(
    ident: int,
    payload: B2bCPriceListUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.price_list.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, B2bCPriceList, ident, "Grilles tarifaires client")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/b2bc-price-lists/{ident}", response_model=B2bCPriceListOut)
def delete_price_list(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.price_list.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, B2bCPriceList, ident, "Grilles tarifaires client")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Commandes clients ─────────────────────────────────────────────────

@router.get("/b2bc-sales-orders", response_model=List[B2bCSalesOrderOut])
def list_sales_order(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.sales_order.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, B2bCSalesOrder, cid, {"statut": statut})


@router.post("/b2bc-sales-orders", response_model=B2bCSalesOrderOut, status_code=201)
def create_sales_order(
    payload: B2bCSalesOrderCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.sales_order.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, B2bCSalesOrder, "reference", data.get("reference"), "reference", cid)
    obj = B2bCSalesOrder(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/b2bc-sales-orders/{ident}", response_model=B2bCSalesOrderOut)
def update_sales_order(
    ident: int,
    payload: B2bCSalesOrderUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.sales_order.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, B2bCSalesOrder, ident, "Commandes clients")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/b2bc-sales-orders/{ident}", response_model=B2bCSalesOrderOut)
def delete_sales_order(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.sales_order.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, B2bCSalesOrder, ident, "Commandes clients")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Encours clients ─────────────────────────────────────────────────

@router.get("/b2bc-credit-accounts", response_model=List[B2bCCreditAccountOut])
def list_credit_account(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.credit_account.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, B2bCCreditAccount, cid, {"statut": statut})


@router.post("/b2bc-credit-accounts", response_model=B2bCCreditAccountOut, status_code=201)
def create_credit_account(
    payload: B2bCCreditAccountCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.credit_account.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, B2bCCreditAccount, "reference", data.get("reference"), "reference", cid)
    obj = B2bCCreditAccount(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/b2bc-credit-accounts/{ident}", response_model=B2bCCreditAccountOut)
def update_credit_account(
    ident: int,
    payload: B2bCCreditAccountUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.credit_account.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, B2bCCreditAccount, ident, "Encours clients")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/b2bc-credit-accounts/{ident}", response_model=B2bCCreditAccountOut)
def delete_credit_account(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.credit_account.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, B2bCCreditAccount, ident, "Encours clients")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Tickets support client ─────────────────────────────────────────────────

@router.get("/b2bc-support-tickets", response_model=List[B2bCSupportTicketOut])
def list_support_ticket(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.support_ticket.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, B2bCSupportTicket, cid, {"statut": statut})


@router.post("/b2bc-support-tickets", response_model=B2bCSupportTicketOut, status_code=201)
def create_support_ticket(
    payload: B2bCSupportTicketCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.support_ticket.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, B2bCSupportTicket, "reference", data.get("reference"), "reference", cid)
    obj = B2bCSupportTicket(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/b2bc-support-tickets/{ident}", response_model=B2bCSupportTicketOut)
def update_support_ticket(
    ident: int,
    payload: B2bCSupportTicketUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.support_ticket.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, B2bCSupportTicket, ident, "Tickets support client")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/b2bc-support-tickets/{ident}", response_model=B2bCSupportTicketOut)
def delete_support_ticket(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.support_ticket.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, B2bCSupportTicket, ident, "Tickets support client")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj

