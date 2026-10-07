"""Routeur CRUD genere pour portail-commercial (expansion)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List

from app.core.database import get_db
from app.core.permissions import require_perm
from app.models.user import User
from app.models.commercial_d_deep import (
    CommLead,
    CommOpportunity,
    CommQuote,
    CommSalesOrder,
    CommCustomerVisit,
    CommSampleRequest,
    CommTender,
    CommContractRenewal,
    CommPriceRequest,
    CommCreditRequest,
    CommOrderModification,
    CommCustomerComplaint,
    CommUpsellRecord,
    CommCommissionStatement,
    CommPipelineReview,
)
from app.schemas.commercial_d_deep import (
    CommLeadCreate, CommLeadUpdate, CommLeadOut,
    CommOpportunityCreate, CommOpportunityUpdate, CommOpportunityOut,
    CommQuoteCreate, CommQuoteUpdate, CommQuoteOut,
    CommSalesOrderCreate, CommSalesOrderUpdate, CommSalesOrderOut,
    CommCustomerVisitCreate, CommCustomerVisitUpdate, CommCustomerVisitOut,
    CommSampleRequestCreate, CommSampleRequestUpdate, CommSampleRequestOut,
    CommTenderCreate, CommTenderUpdate, CommTenderOut,
    CommContractRenewalCreate, CommContractRenewalUpdate, CommContractRenewalOut,
    CommPriceRequestCreate, CommPriceRequestUpdate, CommPriceRequestOut,
    CommCreditRequestCreate, CommCreditRequestUpdate, CommCreditRequestOut,
    CommOrderModificationCreate, CommOrderModificationUpdate, CommOrderModificationOut,
    CommCustomerComplaintCreate, CommCustomerComplaintUpdate, CommCustomerComplaintOut,
    CommUpsellRecordCreate, CommUpsellRecordUpdate, CommUpsellRecordOut,
    CommCommissionStatementCreate, CommCommissionStatementUpdate, CommCommissionStatementOut,
    CommPipelineReviewCreate, CommPipelineReviewUpdate, CommPipelineReviewOut,
)

router = APIRouter(tags=["portail-commercial (expansion)"])


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

@router.get("/nomenclatures", summary="Vocabulaire metier portail-commercial")
def nomenclatures(user: User = Depends(require_perm("b2b.nomenclature.read"))):
    from app.models import commercial_d_deep as _md
    import enum as _pyenum
    out = {}
    for name in dir(_md):
        obj = getattr(_md, name)
        if isinstance(obj, type) and issubclass(obj, _pyenum.Enum) and obj is not _pyenum.Enum:
            out[name.lower()] = [{"code": m.name, "valeur": m.value} for m in obj]
    return out


# ─── Pistes commerciales ─────────────────────────────────────────────────

@router.get("/comm-leads", response_model=List[CommLeadOut])
def list_lead(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.lead.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, CommLead, cid, {"statut": statut})


@router.post("/comm-leads", response_model=CommLeadOut, status_code=201)
def create_lead(
    payload: CommLeadCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.lead.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, CommLead, "reference", data.get("reference"), "reference", cid)
    obj = CommLead(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/comm-leads/{ident}", response_model=CommLeadOut)
def update_lead(
    ident: int,
    payload: CommLeadUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.lead.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CommLead, ident, "Pistes commerciales")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/comm-leads/{ident}", response_model=CommLeadOut)
def delete_lead(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.lead.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CommLead, ident, "Pistes commerciales")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ───  opportunites ─────────────────────────────────────────────────

@router.get("/comm-opportunities", response_model=List[CommOpportunityOut])
def list_opportunity(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.opportunity.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, CommOpportunity, cid, {"statut": statut})


@router.post("/comm-opportunities", response_model=CommOpportunityOut, status_code=201)
def create_opportunity(
    payload: CommOpportunityCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.opportunity.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, CommOpportunity, "reference", data.get("reference"), "reference", cid)
    obj = CommOpportunity(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/comm-opportunities/{ident}", response_model=CommOpportunityOut)
def update_opportunity(
    ident: int,
    payload: CommOpportunityUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.opportunity.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CommOpportunity, ident, " opportunites")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/comm-opportunities/{ident}", response_model=CommOpportunityOut)
def delete_opportunity(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.opportunity.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CommOpportunity, ident, " opportunites")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Devis ─────────────────────────────────────────────────

@router.get("/comm-quotes", response_model=List[CommQuoteOut])
def list_quote(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.quote.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, CommQuote, cid, {"statut": statut})


@router.post("/comm-quotes", response_model=CommQuoteOut, status_code=201)
def create_quote(
    payload: CommQuoteCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.quote.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, CommQuote, "reference", data.get("reference"), "reference", cid)
    obj = CommQuote(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/comm-quotes/{ident}", response_model=CommQuoteOut)
def update_quote(
    ident: int,
    payload: CommQuoteUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.quote.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CommQuote, ident, "Devis")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/comm-quotes/{ident}", response_model=CommQuoteOut)
def delete_quote(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.quote.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CommQuote, ident, "Devis")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Commandes clients ─────────────────────────────────────────────────

@router.get("/comm-sales-orders", response_model=List[CommSalesOrderOut])
def list_sales_order(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.sales_order.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, CommSalesOrder, cid, {"statut": statut})


@router.post("/comm-sales-orders", response_model=CommSalesOrderOut, status_code=201)
def create_sales_order(
    payload: CommSalesOrderCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.sales_order.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, CommSalesOrder, "reference", data.get("reference"), "reference", cid)
    obj = CommSalesOrder(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/comm-sales-orders/{ident}", response_model=CommSalesOrderOut)
def update_sales_order(
    ident: int,
    payload: CommSalesOrderUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.sales_order.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CommSalesOrder, ident, "Commandes clients")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/comm-sales-orders/{ident}", response_model=CommSalesOrderOut)
def delete_sales_order(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.sales_order.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CommSalesOrder, ident, "Commandes clients")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Visites clients ─────────────────────────────────────────────────

@router.get("/comm-customer-visits", response_model=List[CommCustomerVisitOut])
def list_customer_visit(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.customer_visit.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, CommCustomerVisit, cid, {"statut": statut})


@router.post("/comm-customer-visits", response_model=CommCustomerVisitOut, status_code=201)
def create_customer_visit(
    payload: CommCustomerVisitCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.customer_visit.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, CommCustomerVisit, "reference", data.get("reference"), "reference", cid)
    obj = CommCustomerVisit(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/comm-customer-visits/{ident}", response_model=CommCustomerVisitOut)
def update_customer_visit(
    ident: int,
    payload: CommCustomerVisitUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.customer_visit.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CommCustomerVisit, ident, "Visites clients")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/comm-customer-visits/{ident}", response_model=CommCustomerVisitOut)
def delete_customer_visit(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.customer_visit.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CommCustomerVisit, ident, "Visites clients")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Demandes d' echantillons ─────────────────────────────────────────────────

@router.get("/comm-samples-requests", response_model=List[CommSampleRequestOut])
def list_sample_request(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.sample_request.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, CommSampleRequest, cid, {"statut": statut})


@router.post("/comm-samples-requests", response_model=CommSampleRequestOut, status_code=201)
def create_sample_request(
    payload: CommSampleRequestCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.sample_request.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, CommSampleRequest, "reference", data.get("reference"), "reference", cid)
    obj = CommSampleRequest(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/comm-samples-requests/{ident}", response_model=CommSampleRequestOut)
def update_sample_request(
    ident: int,
    payload: CommSampleRequestUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.sample_request.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CommSampleRequest, ident, "Demandes d' echantillons")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/comm-samples-requests/{ident}", response_model=CommSampleRequestOut)
def delete_sample_request(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.sample_request.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CommSampleRequest, ident, "Demandes d' echantillons")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Appels d' offres ─────────────────────────────────────────────────

@router.get("/comm-tenders", response_model=List[CommTenderOut])
def list_tender(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.tender.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, CommTender, cid, {"statut": statut})


@router.post("/comm-tenders", response_model=CommTenderOut, status_code=201)
def create_tender(
    payload: CommTenderCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.tender.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, CommTender, "reference", data.get("reference"), "reference", cid)
    obj = CommTender(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/comm-tenders/{ident}", response_model=CommTenderOut)
def update_tender(
    ident: int,
    payload: CommTenderUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.tender.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CommTender, ident, "Appels d' offres")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/comm-tenders/{ident}", response_model=CommTenderOut)
def delete_tender(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.tender.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CommTender, ident, "Appels d' offres")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Renouvellements de contrat ─────────────────────────────────────────────────

@router.get("/comm-contract-renewals", response_model=List[CommContractRenewalOut])
def list_contract_renewal(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.contract_renewal.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, CommContractRenewal, cid, {"statut": statut})


@router.post("/comm-contract-renewals", response_model=CommContractRenewalOut, status_code=201)
def create_contract_renewal(
    payload: CommContractRenewalCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.contract_renewal.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, CommContractRenewal, "reference", data.get("reference"), "reference", cid)
    obj = CommContractRenewal(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/comm-contract-renewals/{ident}", response_model=CommContractRenewalOut)
def update_contract_renewal(
    ident: int,
    payload: CommContractRenewalUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.contract_renewal.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CommContractRenewal, ident, "Renouvellements de contrat")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/comm-contract-renewals/{ident}", response_model=CommContractRenewalOut)
def delete_contract_renewal(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.contract_renewal.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CommContractRenewal, ident, "Renouvellements de contrat")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Demandes de prix ─────────────────────────────────────────────────

@router.get("/comm-price-requests", response_model=List[CommPriceRequestOut])
def list_price_request(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.price_request.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, CommPriceRequest, cid, {"statut": statut})


@router.post("/comm-price-requests", response_model=CommPriceRequestOut, status_code=201)
def create_price_request(
    payload: CommPriceRequestCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.price_request.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, CommPriceRequest, "reference", data.get("reference"), "reference", cid)
    obj = CommPriceRequest(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/comm-price-requests/{ident}", response_model=CommPriceRequestOut)
def update_price_request(
    ident: int,
    payload: CommPriceRequestUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.price_request.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CommPriceRequest, ident, "Demandes de prix")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/comm-price-requests/{ident}", response_model=CommPriceRequestOut)
def delete_price_request(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.price_request.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CommPriceRequest, ident, "Demandes de prix")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Demandes d' encours client ─────────────────────────────────────────────────

@router.get("/comm-credit-requests", response_model=List[CommCreditRequestOut])
def list_credit_request(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.credit_request.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, CommCreditRequest, cid, {"statut": statut})


@router.post("/comm-credit-requests", response_model=CommCreditRequestOut, status_code=201)
def create_credit_request(
    payload: CommCreditRequestCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.credit_request.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, CommCreditRequest, "reference", data.get("reference"), "reference", cid)
    obj = CommCreditRequest(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/comm-credit-requests/{ident}", response_model=CommCreditRequestOut)
def update_credit_request(
    ident: int,
    payload: CommCreditRequestUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.credit_request.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CommCreditRequest, ident, "Demandes d' encours client")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/comm-credit-requests/{ident}", response_model=CommCreditRequestOut)
def delete_credit_request(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.credit_request.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CommCreditRequest, ident, "Demandes d' encours client")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Modifications de commande ─────────────────────────────────────────────────

@router.get("/comm-order-modifications", response_model=List[CommOrderModificationOut])
def list_order_modification(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.order_modification.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, CommOrderModification, cid, {"statut": statut})


@router.post("/comm-order-modifications", response_model=CommOrderModificationOut, status_code=201)
def create_order_modification(
    payload: CommOrderModificationCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.order_modification.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, CommOrderModification, "reference", data.get("reference"), "reference", cid)
    obj = CommOrderModification(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/comm-order-modifications/{ident}", response_model=CommOrderModificationOut)
def update_order_modification(
    ident: int,
    payload: CommOrderModificationUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.order_modification.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CommOrderModification, ident, "Modifications de commande")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/comm-order-modifications/{ident}", response_model=CommOrderModificationOut)
def delete_order_modification(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.order_modification.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CommOrderModification, ident, "Modifications de commande")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Reclamations clients ─────────────────────────────────────────────────

@router.get("/comm-customer-complaints", response_model=List[CommCustomerComplaintOut])
def list_customer_complaint(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.customer_complaint.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, CommCustomerComplaint, cid, {"statut": statut})


@router.post("/comm-customer-complaints", response_model=CommCustomerComplaintOut, status_code=201)
def create_customer_complaint(
    payload: CommCustomerComplaintCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.customer_complaint.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, CommCustomerComplaint, "reference", data.get("reference"), "reference", cid)
    obj = CommCustomerComplaint(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/comm-customer-complaints/{ident}", response_model=CommCustomerComplaintOut)
def update_customer_complaint(
    ident: int,
    payload: CommCustomerComplaintUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.customer_complaint.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CommCustomerComplaint, ident, "Reclamations clients")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/comm-customer-complaints/{ident}", response_model=CommCustomerComplaintOut)
def delete_customer_complaint(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.customer_complaint.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CommCustomerComplaint, ident, "Reclamations clients")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Actions de vente additionnelle ─────────────────────────────────────────────────

@router.get("/comm-upsell-records", response_model=List[CommUpsellRecordOut])
def list_upsell_record(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.upsell_record.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, CommUpsellRecord, cid, {"statut": statut})


@router.post("/comm-upsell-records", response_model=CommUpsellRecordOut, status_code=201)
def create_upsell_record(
    payload: CommUpsellRecordCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.upsell_record.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, CommUpsellRecord, "reference", data.get("reference"), "reference", cid)
    obj = CommUpsellRecord(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/comm-upsell-records/{ident}", response_model=CommUpsellRecordOut)
def update_upsell_record(
    ident: int,
    payload: CommUpsellRecordUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.upsell_record.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CommUpsellRecord, ident, "Actions de vente additionnelle")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/comm-upsell-records/{ident}", response_model=CommUpsellRecordOut)
def delete_upsell_record(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.upsell_record.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CommUpsellRecord, ident, "Actions de vente additionnelle")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Etats de commission ─────────────────────────────────────────────────

@router.get("/comm-commission-statements", response_model=List[CommCommissionStatementOut])
def list_commission_statement(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.commission_statement.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, CommCommissionStatement, cid, {"statut": statut})


@router.post("/comm-commission-statements", response_model=CommCommissionStatementOut, status_code=201)
def create_commission_statement(
    payload: CommCommissionStatementCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.commission_statement.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, CommCommissionStatement, "reference", data.get("reference"), "reference", cid)
    obj = CommCommissionStatement(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/comm-commission-statements/{ident}", response_model=CommCommissionStatementOut)
def update_commission_statement(
    ident: int,
    payload: CommCommissionStatementUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.commission_statement.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CommCommissionStatement, ident, "Etats de commission")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/comm-commission-statements/{ident}", response_model=CommCommissionStatementOut)
def delete_commission_statement(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.commission_statement.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CommCommissionStatement, ident, "Etats de commission")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Revues de pipeline ─────────────────────────────────────────────────

@router.get("/comm-pipeline-reviews", response_model=List[CommPipelineReviewOut])
def list_pipeline_review(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.pipeline_review.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, CommPipelineReview, cid, {"statut": statut})


@router.post("/comm-pipeline-reviews", response_model=CommPipelineReviewOut, status_code=201)
def create_pipeline_review(
    payload: CommPipelineReviewCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.pipeline_review.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, CommPipelineReview, "reference", data.get("reference"), "reference", cid)
    obj = CommPipelineReview(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/comm-pipeline-reviews/{ident}", response_model=CommPipelineReviewOut)
def update_pipeline_review(
    ident: int,
    payload: CommPipelineReviewUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.pipeline_review.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CommPipelineReview, ident, "Revues de pipeline")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/comm-pipeline-reviews/{ident}", response_model=CommPipelineReviewOut)
def delete_pipeline_review(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.pipeline_review.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CommPipelineReview, ident, "Revues de pipeline")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj

