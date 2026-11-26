"""Schemas Pydantic pour comptabilite-ohada (genere)."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date


class CmptcJournalReversalCreate(BaseModel):
    reference: str
    ecriture_origine: Optional[str] = None
    date_reversal: Optional[date] = None
    compte_debit: Optional[str] = None
    compte_credit: Optional[str] = None
    montant: Optional[float] = None
    motif: Optional[str] = None
    statut: Optional[str] = None


class CmptcJournalReversalUpdate(BaseModel):
    reference: Optional[str] = None
    ecriture_origine: Optional[str] = None
    date_reversal: Optional[date] = None
    compte_debit: Optional[str] = None
    compte_credit: Optional[str] = None
    montant: Optional[float] = None
    motif: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class CmptcJournalReversalOut(BaseModel):
    id: int
    company_id: int
    reference: str
    ecriture_origine: Optional[str] = None
    date_reversal: Optional[date] = None
    compte_debit: Optional[str] = None
    compte_credit: Optional[str] = None
    montant: Optional[float] = None
    motif: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class CmptcBankReconciliationCreate(BaseModel):
    reference: str
    compte_banque: Optional[str] = None
    date_releve: Optional[date] = None
    solde_comptable: Optional[float] = None
    solde_bancaire: Optional[float] = None
    ecart: Optional[float] = None
    date_rapprochement: Optional[date] = None
    statut: Optional[str] = None


class CmptcBankReconciliationUpdate(BaseModel):
    reference: Optional[str] = None
    compte_banque: Optional[str] = None
    date_releve: Optional[date] = None
    solde_comptable: Optional[float] = None
    solde_bancaire: Optional[float] = None
    ecart: Optional[float] = None
    date_rapprochement: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class CmptcBankReconciliationOut(BaseModel):
    id: int
    company_id: int
    reference: str
    compte_banque: Optional[str] = None
    date_releve: Optional[date] = None
    solde_comptable: Optional[float] = None
    solde_bancaire: Optional[float] = None
    ecart: Optional[float] = None
    date_rapprochement: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}

