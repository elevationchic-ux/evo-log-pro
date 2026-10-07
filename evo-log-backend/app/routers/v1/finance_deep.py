"""Routeur CRUD genere pour finance-ohada (expansion)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List

from app.core.database import get_db
from app.core.permissions import require_perm
from app.models.user import User
from app.models.finance_deep import (
    MultiyearBudget,
    CreditFacility,
    CashPool,
    FinancialInvestment,
    FxExposure,
    PaymentSchedule,
    ExpenseReport,
    PettyCashBox,
    BankGuarantee,
    LeaseContract,
    CashForecast,
    TreasuryAlert,
)
from app.schemas.finance_deep import (
    MultiyearBudgetCreate, MultiyearBudgetUpdate, MultiyearBudgetOut,
    CreditFacilityCreate, CreditFacilityUpdate, CreditFacilityOut,
    CashPoolCreate, CashPoolUpdate, CashPoolOut,
    FinancialInvestmentCreate, FinancialInvestmentUpdate, FinancialInvestmentOut,
    FxExposureCreate, FxExposureUpdate, FxExposureOut,
    PaymentScheduleCreate, PaymentScheduleUpdate, PaymentScheduleOut,
    ExpenseReportCreate, ExpenseReportUpdate, ExpenseReportOut,
    PettyCashBoxCreate, PettyCashBoxUpdate, PettyCashBoxOut,
    BankGuaranteeCreate, BankGuaranteeUpdate, BankGuaranteeOut,
    LeaseContractCreate, LeaseContractUpdate, LeaseContractOut,
    CashForecastCreate, CashForecastUpdate, CashForecastOut,
    TreasuryAlertCreate, TreasuryAlertUpdate, TreasuryAlertOut,
)

router = APIRouter(tags=["finance-ohada (expansion)"])


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

@router.get("/nomenclatures", summary="Vocabulaire metier finance-ohada")
def nomenclatures(user: User = Depends(require_perm("tresorerie.nomenclature.read"))):
    from app.models import finance_deep as _md
    import enum as _pyenum
    out = {}
    for name in dir(_md):
        obj = getattr(_md, name)
        if isinstance(obj, type) and issubclass(obj, _pyenum.Enum) and obj is not _pyenum.Enum:
            out[name.lower()] = [{"code": m.name, "valeur": m.value} for m in obj]
    return out


# ─── Budget pluriannuel ─────────────────────────────────────────────────

@router.get("/multiyear-budgets", response_model=List[MultiyearBudgetOut])
def list_budget_management(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.budget_management.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, MultiyearBudget, cid, {"statut": statut})


@router.post("/multiyear-budgets", response_model=MultiyearBudgetOut, status_code=201)
def create_budget_management(
    payload: MultiyearBudgetCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.budget_management.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, MultiyearBudget, "reference", data.get("reference"), "reference", cid)
    obj = MultiyearBudget(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/multiyear-budgets/{ident}", response_model=MultiyearBudgetOut)
def update_budget_management(
    ident: int,
    payload: MultiyearBudgetUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.budget_management.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, MultiyearBudget, ident, "Budget pluriannuel")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/multiyear-budgets/{ident}", response_model=MultiyearBudgetOut)
def delete_budget_management(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.budget_management.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, MultiyearBudget, ident, "Budget pluriannuel")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Facilites de caisse et credits ─────────────────────────────────────────────────

@router.get("/credit-facilities", response_model=List[CreditFacilityOut])
def list_credit_facility(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.credit_facility.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, CreditFacility, cid, {"statut": statut})


@router.post("/credit-facilities", response_model=CreditFacilityOut, status_code=201)
def create_credit_facility(
    payload: CreditFacilityCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.credit_facility.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, CreditFacility, "reference", data.get("reference"), "reference", cid)
    obj = CreditFacility(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/credit-facilities/{ident}", response_model=CreditFacilityOut)
def update_credit_facility(
    ident: int,
    payload: CreditFacilityUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.credit_facility.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CreditFacility, ident, "Facilites de caisse et credits")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/credit-facilities/{ident}", response_model=CreditFacilityOut)
def delete_credit_facility(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.credit_facility.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CreditFacility, ident, "Facilites de caisse et credits")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Centralisation de tresorerie ─────────────────────────────────────────────────

@router.get("/cash-pools", response_model=List[CashPoolOut])
def list_cash_pooling(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.cash_pooling.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, CashPool, cid, {"statut": statut})


@router.post("/cash-pools", response_model=CashPoolOut, status_code=201)
def create_cash_pooling(
    payload: CashPoolCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.cash_pooling.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, CashPool, "reference", data.get("reference"), "reference", cid)
    obj = CashPool(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/cash-pools/{ident}", response_model=CashPoolOut)
def update_cash_pooling(
    ident: int,
    payload: CashPoolUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.cash_pooling.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CashPool, ident, "Centralisation de tresorerie")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/cash-pools/{ident}", response_model=CashPoolOut)
def delete_cash_pooling(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.cash_pooling.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CashPool, ident, "Centralisation de tresorerie")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Investissements financiers ─────────────────────────────────────────────────

@router.get("/financial-investments", response_model=List[FinancialInvestmentOut])
def list_investment_tracking(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.investment_tracking.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, FinancialInvestment, cid, {"statut": statut})


@router.post("/financial-investments", response_model=FinancialInvestmentOut, status_code=201)
def create_investment_tracking(
    payload: FinancialInvestmentCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.investment_tracking.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, FinancialInvestment, "reference", data.get("reference"), "reference", cid)
    obj = FinancialInvestment(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/financial-investments/{ident}", response_model=FinancialInvestmentOut)
def update_investment_tracking(
    ident: int,
    payload: FinancialInvestmentUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.investment_tracking.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, FinancialInvestment, ident, "Investissements financiers")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/financial-investments/{ident}", response_model=FinancialInvestmentOut)
def delete_investment_tracking(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.investment_tracking.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, FinancialInvestment, ident, "Investissements financiers")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Risque de change XAF/EUR/USD ─────────────────────────────────────────────────

@router.get("/fx-exposures", response_model=List[FxExposureOut])
def list_fx_management(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.fx_management.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, FxExposure, cid, {"statut": statut})


@router.post("/fx-exposures", response_model=FxExposureOut, status_code=201)
def create_fx_management(
    payload: FxExposureCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.fx_management.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, FxExposure, "reference", data.get("reference"), "reference", cid)
    obj = FxExposure(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/fx-exposures/{ident}", response_model=FxExposureOut)
def update_fx_management(
    ident: int,
    payload: FxExposureUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.fx_management.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, FxExposure, ident, "Risque de change XAF/EUR/USD")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/fx-exposures/{ident}", response_model=FxExposureOut)
def delete_fx_management(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.fx_management.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, FxExposure, ident, "Risque de change XAF/EUR/USD")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Echeancier reglements fournisseurs ─────────────────────────────────────────────────

@router.get("/payment-schedules", response_model=List[PaymentScheduleOut])
def list_payment_scheduling(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.payment_scheduling.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, PaymentSchedule, cid, {"statut": statut})


@router.post("/payment-schedules", response_model=PaymentScheduleOut, status_code=201)
def create_payment_scheduling(
    payload: PaymentScheduleCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.payment_scheduling.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, PaymentSchedule, "reference", data.get("reference"), "reference", cid)
    obj = PaymentSchedule(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/payment-schedules/{ident}", response_model=PaymentScheduleOut)
def update_payment_scheduling(
    ident: int,
    payload: PaymentScheduleUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.payment_scheduling.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, PaymentSchedule, ident, "Echeancier reglements fournisseurs")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/payment-schedules/{ident}", response_model=PaymentScheduleOut)
def delete_payment_scheduling(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.payment_scheduling.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, PaymentSchedule, ident, "Echeancier reglements fournisseurs")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Notes de frais ─────────────────────────────────────────────────

@router.get("/expense-reports", response_model=List[ExpenseReportOut])
def list_expense_report(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.expense_report.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, ExpenseReport, cid, {"statut": statut})


@router.post("/expense-reports", response_model=ExpenseReportOut, status_code=201)
def create_expense_report(
    payload: ExpenseReportCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.expense_report.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, ExpenseReport, "numero_note_frais", data.get("numero_note_frais"), "numero_note_frais", cid)
    obj = ExpenseReport(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/expense-reports/{ident}", response_model=ExpenseReportOut)
def update_expense_report(
    ident: int,
    payload: ExpenseReportUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.expense_report.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ExpenseReport, ident, "Notes de frais")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/expense-reports/{ident}", response_model=ExpenseReportOut)
def delete_expense_report(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.expense_report.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ExpenseReport, ident, "Notes de frais")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Regies d'avance ─────────────────────────────────────────────────

@router.get("/petty-cash-boxes", response_model=List[PettyCashBoxOut])
def list_petty_cash(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.petty_cash.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, PettyCashBox, cid, {"statut": statut})


@router.post("/petty-cash-boxes", response_model=PettyCashBoxOut, status_code=201)
def create_petty_cash(
    payload: PettyCashBoxCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.petty_cash.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, PettyCashBox, "code_regie", data.get("code_regie"), "code_regie", cid)
    obj = PettyCashBox(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/petty-cash-boxes/{ident}", response_model=PettyCashBoxOut)
def update_petty_cash(
    ident: int,
    payload: PettyCashBoxUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.petty_cash.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, PettyCashBox, ident, "Regies d'avance")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/petty-cash-boxes/{ident}", response_model=PettyCashBoxOut)
def delete_petty_cash(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.petty_cash.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, PettyCashBox, ident, "Regies d'avance")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Garanties bancaires ─────────────────────────────────────────────────

@router.get("/bank-guarantees", response_model=List[BankGuaranteeOut])
def list_bank_guarantee(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.bank_guarantee.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, BankGuarantee, cid, {"statut": statut})


@router.post("/bank-guarantees", response_model=BankGuaranteeOut, status_code=201)
def create_bank_guarantee(
    payload: BankGuaranteeCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.bank_guarantee.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, BankGuarantee, "reference", data.get("reference"), "reference", cid)
    obj = BankGuarantee(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/bank-guarantees/{ident}", response_model=BankGuaranteeOut)
def update_bank_guarantee(
    ident: int,
    payload: BankGuaranteeUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.bank_guarantee.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, BankGuarantee, ident, "Garanties bancaires")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/bank-guarantees/{ident}", response_model=BankGuaranteeOut)
def delete_bank_guarantee(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.bank_guarantee.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, BankGuarantee, ident, "Garanties bancaires")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Credit-leasing / contrats location ─────────────────────────────────────────────────

@router.get("/lease-contracts", response_model=List[LeaseContractOut])
def list_lease_accounting(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.lease_accounting.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, LeaseContract, cid, {"statut": statut})


@router.post("/lease-contracts", response_model=LeaseContractOut, status_code=201)
def create_lease_accounting(
    payload: LeaseContractCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.lease_accounting.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, LeaseContract, "reference", data.get("reference"), "reference", cid)
    obj = LeaseContract(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/lease-contracts/{ident}", response_model=LeaseContractOut)
def update_lease_accounting(
    ident: int,
    payload: LeaseContractUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.lease_accounting.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, LeaseContract, ident, "Credit-leasing / contrats location")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/lease-contracts/{ident}", response_model=LeaseContractOut)
def delete_lease_accounting(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.lease_accounting.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, LeaseContract, ident, "Credit-leasing / contrats location")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Previsions de tresorerie ─────────────────────────────────────────────────

@router.get("/cash-forecasts", response_model=List[CashForecastOut])
def list_financial_forecast(db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.financial_forecast.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, CashForecast, cid)


@router.post("/cash-forecasts", response_model=CashForecastOut, status_code=201)
def create_financial_forecast(
    payload: CashForecastCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.financial_forecast.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, CashForecast, "reference", data.get("reference"), "reference", cid)
    obj = CashForecast(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/cash-forecasts/{ident}", response_model=CashForecastOut)
def update_financial_forecast(
    ident: int,
    payload: CashForecastUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.financial_forecast.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CashForecast, ident, "Previsions de tresorerie")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/cash-forecasts/{ident}", response_model=CashForecastOut)
def delete_financial_forecast(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.financial_forecast.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CashForecast, ident, "Previsions de tresorerie")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Alertes tresorerie ─────────────────────────────────────────────────

@router.get("/treasury-alerts", response_model=List[TreasuryAlertOut])
def list_treasury_alerts(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.treasury_alerts.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, TreasuryAlert, cid, {"statut": statut})


@router.post("/treasury-alerts", response_model=TreasuryAlertOut, status_code=201)
def create_treasury_alerts(
    payload: TreasuryAlertCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.treasury_alerts.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, TreasuryAlert, "reference", data.get("reference"), "reference", cid)
    obj = TreasuryAlert(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/treasury-alerts/{ident}", response_model=TreasuryAlertOut)
def update_treasury_alerts(
    ident: int,
    payload: TreasuryAlertUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.treasury_alerts.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TreasuryAlert, ident, "Alertes tresorerie")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/treasury-alerts/{ident}", response_model=TreasuryAlertOut)
def delete_treasury_alerts(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.treasury_alerts.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TreasuryAlert, ident, "Alertes tresorerie")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj

