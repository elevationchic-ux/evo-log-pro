"""Routeur CRUD genere pour comptabilite-ohada (expansion)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List

from app.core.database import get_db
from app.core.permissions import require_perm
from app.models.user import User
from app.models.comptabilite_deep import (
    AssetRegistration,
    DepreciationSchedule,
    Provision,
    BankReconciliation,
    IntercompanyEntry,
    BudgetControl,
    AuditPaf,
    TaxDeclaration,
    PayrollEntry,
    TreasuryAccount,
    AnalyticalSection,
)
from app.schemas.comptabilite_deep import (
    AssetRegistrationCreate, AssetRegistrationUpdate, AssetRegistrationOut,
    DepreciationScheduleCreate, DepreciationScheduleUpdate, DepreciationScheduleOut,
    ProvisionCreate, ProvisionUpdate, ProvisionOut,
    BankReconciliationCreate, BankReconciliationUpdate, BankReconciliationOut,
    IntercompanyEntryCreate, IntercompanyEntryUpdate, IntercompanyEntryOut,
    BudgetControlCreate, BudgetControlUpdate, BudgetControlOut,
    AuditPafCreate, AuditPafUpdate, AuditPafOut,
    TaxDeclarationCreate, TaxDeclarationUpdate, TaxDeclarationOut,
    PayrollEntryCreate, PayrollEntryUpdate, PayrollEntryOut,
    TreasuryAccountCreate, TreasuryAccountUpdate, TreasuryAccountOut,
    AnalyticalSectionCreate, AnalyticalSectionUpdate, AnalyticalSectionOut,
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
def nomenclatures(user: User = Depends(require_perm("compta.nomenclature.read"))):
    from app.models import comptabilite_deep as _md
    import enum as _pyenum
    out = {}
    for name in dir(_md):
        obj = getattr(_md, name)
        if isinstance(obj, type) and issubclass(obj, _pyenum.Enum) and obj is not _pyenum.Enum:
            out[name.lower()] = [{"code": m.name, "valeur": m.value} for m in obj]
    return out


# ─── Registre immobilisations ─────────────────────────────────────────────────

@router.get("/asset-registrations", response_model=List[AssetRegistrationOut])
def list_fixed_asset(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("compta.fixed_asset.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, AssetRegistration, cid, {"statut": statut})


@router.post("/asset-registrations", response_model=AssetRegistrationOut, status_code=201)
def create_fixed_asset(
    payload: AssetRegistrationCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("compta.fixed_asset.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, AssetRegistration, "numero_inventaire", data.get("numero_inventaire"), "numero_inventaire", cid)
    obj = AssetRegistration(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/asset-registrations/{ident}", response_model=AssetRegistrationOut)
def update_fixed_asset(
    ident: int,
    payload: AssetRegistrationUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("compta.fixed_asset.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, AssetRegistration, ident, "Registre immobilisations")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/asset-registrations/{ident}", response_model=AssetRegistrationOut)
def delete_fixed_asset(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("compta.fixed_asset.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, AssetRegistration, ident, "Registre immobilisations")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Plans d'amortissement ─────────────────────────────────────────────────

@router.get("/depreciation-schedules", response_model=List[DepreciationScheduleOut])
def list_depreciation(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("compta.depreciation.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, DepreciationSchedule, cid, {"statut": statut})


@router.post("/depreciation-schedules", response_model=DepreciationScheduleOut, status_code=201)
def create_depreciation(
    payload: DepreciationScheduleCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("compta.depreciation.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, DepreciationSchedule, "reference", data.get("reference"), "reference", cid)
    obj = DepreciationSchedule(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/depreciation-schedules/{ident}", response_model=DepreciationScheduleOut)
def update_depreciation(
    ident: int,
    payload: DepreciationScheduleUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("compta.depreciation.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, DepreciationSchedule, ident, "Plans d'amortissement")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/depreciation-schedules/{ident}", response_model=DepreciationScheduleOut)
def delete_depreciation(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("compta.depreciation.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, DepreciationSchedule, ident, "Plans d'amortissement")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Dotations et reprises ─────────────────────────────────────────────────

@router.get("/provisions", response_model=List[ProvisionOut])
def list_provision(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("compta.provision.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, Provision, cid, {"statut": statut})


@router.post("/provisions", response_model=ProvisionOut, status_code=201)
def create_provision(
    payload: ProvisionCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("compta.provision.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, Provision, "reference", data.get("reference"), "reference", cid)
    obj = Provision(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/provisions/{ident}", response_model=ProvisionOut)
def update_provision(
    ident: int,
    payload: ProvisionUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("compta.provision.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, Provision, ident, "Dotations et reprises")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/provisions/{ident}", response_model=ProvisionOut)
def delete_provision(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("compta.provision.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, Provision, ident, "Dotations et reprises")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Rapprochement bancaire ─────────────────────────────────────────────────

@router.get("/bank-reconciliations", response_model=List[BankReconciliationOut])
def list_bank_reconciliation(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("compta.bank_reconciliation.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, BankReconciliation, cid, {"statut": statut})


@router.post("/bank-reconciliations", response_model=BankReconciliationOut, status_code=201)
def create_bank_reconciliation(
    payload: BankReconciliationCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("compta.bank_reconciliation.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, BankReconciliation, "reference", data.get("reference"), "reference", cid)
    obj = BankReconciliation(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/bank-reconciliations/{ident}", response_model=BankReconciliationOut)
def update_bank_reconciliation(
    ident: int,
    payload: BankReconciliationUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("compta.bank_reconciliation.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, BankReconciliation, ident, "Rapprochement bancaire")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/bank-reconciliations/{ident}", response_model=BankReconciliationOut)
def delete_bank_reconciliation(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("compta.bank_reconciliation.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, BankReconciliation, ident, "Rapprochement bancaire")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Comptes inter-societes ─────────────────────────────────────────────────

@router.get("/intercompany-entries", response_model=List[IntercompanyEntryOut])
def list_intercompany(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("compta.intercompany.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, IntercompanyEntry, cid, {"statut": statut})


@router.post("/intercompany-entries", response_model=IntercompanyEntryOut, status_code=201)
def create_intercompany(
    payload: IntercompanyEntryCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("compta.intercompany.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, IntercompanyEntry, "reference", data.get("reference"), "reference", cid)
    obj = IntercompanyEntry(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/intercompany-entries/{ident}", response_model=IntercompanyEntryOut)
def update_intercompany(
    ident: int,
    payload: IntercompanyEntryUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("compta.intercompany.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, IntercompanyEntry, ident, "Comptes inter-societes")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/intercompany-entries/{ident}", response_model=IntercompanyEntryOut)
def delete_intercompany(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("compta.intercompany.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, IntercompanyEntry, ident, "Comptes inter-societes")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Budget et controle budgetaire ─────────────────────────────────────────────────

@router.get("/budget-controls", response_model=List[BudgetControlOut])
def list_budget_control(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("compta.budget_control.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, BudgetControl, cid, {"statut": statut})


@router.post("/budget-controls", response_model=BudgetControlOut, status_code=201)
def create_budget_control(
    payload: BudgetControlCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("compta.budget_control.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, BudgetControl, "reference", data.get("reference"), "reference", cid)
    obj = BudgetControl(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/budget-controls/{ident}", response_model=BudgetControlOut)
def update_budget_control(
    ident: int,
    payload: BudgetControlUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("compta.budget_control.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, BudgetControl, ident, "Budget et controle budgetaire")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/budget-controls/{ident}", response_model=BudgetControlOut)
def delete_budget_control(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("compta.budget_control.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, BudgetControl, ident, "Budget et controle budgetaire")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Piste d'audit fiable ─────────────────────────────────────────────────

@router.get("/audit-pafs", response_model=List[AuditPafOut])
def list_audit_trail(db: Session = Depends(get_db),
    user: User = Depends(require_perm("compta.audit_trail.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, AuditPaf, cid)


@router.post("/audit-pafs", response_model=AuditPafOut, status_code=201)
def create_audit_trail(
    payload: AuditPafCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("compta.audit_trail.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, AuditPaf, "hash_ligne", data.get("hash_ligne"), "hash_ligne", cid)
    obj = AuditPaf(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/audit-pafs/{ident}", response_model=AuditPafOut)
def update_audit_trail(
    ident: int,
    payload: AuditPafUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("compta.audit_trail.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, AuditPaf, ident, "Piste d'audit fiable")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/audit-pafs/{ident}", response_model=AuditPafOut)
def delete_audit_trail(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("compta.audit_trail.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, AuditPaf, ident, "Piste d'audit fiable")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Declarations fiscales periodiques ─────────────────────────────────────────────────

@router.get("/tax-declarations", response_model=List[TaxDeclarationOut])
def list_tax_declaration(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("compta.tax_declaration.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, TaxDeclaration, cid, {"statut": statut})


@router.post("/tax-declarations", response_model=TaxDeclarationOut, status_code=201)
def create_tax_declaration(
    payload: TaxDeclarationCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("compta.tax_declaration.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, TaxDeclaration, "reference", data.get("reference"), "reference", cid)
    obj = TaxDeclaration(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/tax-declarations/{ident}", response_model=TaxDeclarationOut)
def update_tax_declaration(
    ident: int,
    payload: TaxDeclarationUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("compta.tax_declaration.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TaxDeclaration, ident, "Declarations fiscales periodiques")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/tax-declarations/{ident}", response_model=TaxDeclarationOut)
def delete_tax_declaration(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("compta.tax_declaration.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TaxDeclaration, ident, "Declarations fiscales periodiques")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Ecritures de paie ─────────────────────────────────────────────────

@router.get("/payroll-entries", response_model=List[PayrollEntryOut])
def list_payroll_accounts(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("compta.payroll_accounts.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, PayrollEntry, cid, {"statut": statut})


@router.post("/payroll-entries", response_model=PayrollEntryOut, status_code=201)
def create_payroll_accounts(
    payload: PayrollEntryCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("compta.payroll_accounts.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, PayrollEntry, "reference", data.get("reference"), "reference", cid)
    obj = PayrollEntry(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/payroll-entries/{ident}", response_model=PayrollEntryOut)
def update_payroll_accounts(
    ident: int,
    payload: PayrollEntryUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("compta.payroll_accounts.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, PayrollEntry, ident, "Ecritures de paie")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/payroll-entries/{ident}", response_model=PayrollEntryOut)
def delete_payroll_accounts(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("compta.payroll_accounts.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, PayrollEntry, ident, "Ecritures de paie")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Comptes de tresorerie ─────────────────────────────────────────────────

@router.get("/treasury-accounts", response_model=List[TreasuryAccountOut])
def list_treasury_accounts(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("compta.treasury_accounts.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, TreasuryAccount, cid, {"statut": statut})


@router.post("/treasury-accounts", response_model=TreasuryAccountOut, status_code=201)
def create_treasury_accounts(
    payload: TreasuryAccountCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("compta.treasury_accounts.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, TreasuryAccount, "code_compte", data.get("code_compte"), "code_compte", cid)
    obj = TreasuryAccount(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/treasury-accounts/{ident}", response_model=TreasuryAccountOut)
def update_treasury_accounts(
    ident: int,
    payload: TreasuryAccountUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("compta.treasury_accounts.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TreasuryAccount, ident, "Comptes de tresorerie")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/treasury-accounts/{ident}", response_model=TreasuryAccountOut)
def delete_treasury_accounts(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("compta.treasury_accounts.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TreasuryAccount, ident, "Comptes de tresorerie")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Comptabilite analytique ─────────────────────────────────────────────────

@router.get("/analytical-sections", response_model=List[AnalyticalSectionOut])
def list_analytical_accounting(db: Session = Depends(get_db),
    user: User = Depends(require_perm("compta.analytical_accounting.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, AnalyticalSection, cid)


@router.post("/analytical-sections", response_model=AnalyticalSectionOut, status_code=201)
def create_analytical_accounting(
    payload: AnalyticalSectionCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("compta.analytical_accounting.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, AnalyticalSection, "code_section", data.get("code_section"), "code_section", cid)
    obj = AnalyticalSection(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/analytical-sections/{ident}", response_model=AnalyticalSectionOut)
def update_analytical_accounting(
    ident: int,
    payload: AnalyticalSectionUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("compta.analytical_accounting.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, AnalyticalSection, ident, "Comptabilite analytique")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/analytical-sections/{ident}", response_model=AnalyticalSectionOut)
def delete_analytical_accounting(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("compta.analytical_accounting.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, AnalyticalSection, ident, "Comptabilite analytique")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj

