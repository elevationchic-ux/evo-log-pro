"""Schemas Pydantic pour portail-frais (genere)."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date


class FraExpenseReportCreate(BaseModel):
    reference: str
    collaborateur: Optional[str] = None
    periode: Optional[str] = None
    total: Optional[float] = None
    nb_justificatifs: Optional[int] = None
    statut: Optional[str] = None


class FraExpenseReportUpdate(BaseModel):
    reference: Optional[str] = None
    collaborateur: Optional[str] = None
    periode: Optional[str] = None
    total: Optional[float] = None
    nb_justificatifs: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class FraExpenseReportOut(BaseModel):
    id: int
    company_id: int
    reference: str
    collaborateur: Optional[str] = None
    periode: Optional[str] = None
    total: Optional[float] = None
    nb_justificatifs: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class FraExpenseReceiptCreate(BaseModel):
    reference: str
    note_frais: Optional[str] = None
    fournisseur: Optional[str] = None
    montant: Optional[float] = None
    date: Optional[date] = None
    statut: Optional[str] = None


class FraExpenseReceiptUpdate(BaseModel):
    reference: Optional[str] = None
    note_frais: Optional[str] = None
    fournisseur: Optional[str] = None
    montant: Optional[float] = None
    date: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class FraExpenseReceiptOut(BaseModel):
    id: int
    company_id: int
    reference: str
    note_frais: Optional[str] = None
    fournisseur: Optional[str] = None
    montant: Optional[float] = None
    date: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class FraExpenseAdvanceCreate(BaseModel):
    reference: str
    collaborateur: Optional[str] = None
    montant: Optional[float] = None
    motif: Optional[str] = None
    date: Optional[date] = None
    statut: Optional[str] = None


class FraExpenseAdvanceUpdate(BaseModel):
    reference: Optional[str] = None
    collaborateur: Optional[str] = None
    montant: Optional[float] = None
    motif: Optional[str] = None
    date: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class FraExpenseAdvanceOut(BaseModel):
    id: int
    company_id: int
    reference: str
    collaborateur: Optional[str] = None
    montant: Optional[float] = None
    motif: Optional[str] = None
    date: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class FraPerDiemClaimCreate(BaseModel):
    reference: str
    collaborateur: Optional[str] = None
    jours: Optional[int] = None
    taux_journalier: Optional[float] = None
    statut: Optional[str] = None


class FraPerDiemClaimUpdate(BaseModel):
    reference: Optional[str] = None
    collaborateur: Optional[str] = None
    jours: Optional[int] = None
    taux_journalier: Optional[float] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class FraPerDiemClaimOut(BaseModel):
    id: int
    company_id: int
    reference: str
    collaborateur: Optional[str] = None
    jours: Optional[int] = None
    taux_journalier: Optional[float] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class FraMileageClaimCreate(BaseModel):
    reference: str
    collaborateur: Optional[str] = None
    km: Optional[int] = None
    trajet: Optional[str] = None
    montant: Optional[float] = None
    statut: Optional[str] = None


class FraMileageClaimUpdate(BaseModel):
    reference: Optional[str] = None
    collaborateur: Optional[str] = None
    km: Optional[int] = None
    trajet: Optional[str] = None
    montant: Optional[float] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class FraMileageClaimOut(BaseModel):
    id: int
    company_id: int
    reference: str
    collaborateur: Optional[str] = None
    km: Optional[int] = None
    trajet: Optional[str] = None
    montant: Optional[float] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class FraMealExpenseCreate(BaseModel):
    reference: str
    collaborateur: Optional[str] = None
    montant: Optional[float] = None
    nb_personnes: Optional[int] = None
    date: Optional[date] = None
    statut: Optional[str] = None


class FraMealExpenseUpdate(BaseModel):
    reference: Optional[str] = None
    collaborateur: Optional[str] = None
    montant: Optional[float] = None
    nb_personnes: Optional[int] = None
    date: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class FraMealExpenseOut(BaseModel):
    id: int
    company_id: int
    reference: str
    collaborateur: Optional[str] = None
    montant: Optional[float] = None
    nb_personnes: Optional[int] = None
    date: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class FraTravelBookingCreate(BaseModel):
    reference: str
    collaborateur: Optional[str] = None
    mode: Optional[str] = None
    destination: Optional[str] = None
    date_depart: Optional[date] = None
    statut: Optional[str] = None


class FraTravelBookingUpdate(BaseModel):
    reference: Optional[str] = None
    collaborateur: Optional[str] = None
    mode: Optional[str] = None
    destination: Optional[str] = None
    date_depart: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class FraTravelBookingOut(BaseModel):
    id: int
    company_id: int
    reference: str
    collaborateur: Optional[str] = None
    mode: Optional[str] = None
    destination: Optional[str] = None
    date_depart: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class FraHotelStayCreate(BaseModel):
    reference: str
    collaborateur: Optional[str] = None
    hotel: Optional[str] = None
    nuits: Optional[int] = None
    montant: Optional[float] = None
    statut: Optional[str] = None


class FraHotelStayUpdate(BaseModel):
    reference: Optional[str] = None
    collaborateur: Optional[str] = None
    hotel: Optional[str] = None
    nuits: Optional[int] = None
    montant: Optional[float] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class FraHotelStayOut(BaseModel):
    id: int
    company_id: int
    reference: str
    collaborateur: Optional[str] = None
    hotel: Optional[str] = None
    nuits: Optional[int] = None
    montant: Optional[float] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class FraTransportExpenseCreate(BaseModel):
    reference: str
    collaborateur: Optional[str] = None
    type: Optional[str] = None
    montant: Optional[float] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None


class FraTransportExpenseUpdate(BaseModel):
    reference: Optional[str] = None
    collaborateur: Optional[str] = None
    type: Optional[str] = None
    montant: Optional[float] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class FraTransportExpenseOut(BaseModel):
    id: int
    company_id: int
    reference: str
    collaborateur: Optional[str] = None
    type: Optional[str] = None
    montant: Optional[float] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class FraClientEntertainmentCreate(BaseModel):
    reference: str
    collaborateur: Optional[str] = None
    client: Optional[str] = None
    montant: Optional[float] = None
    nb_invites: Optional[int] = None
    statut: Optional[str] = None


class FraClientEntertainmentUpdate(BaseModel):
    reference: Optional[str] = None
    collaborateur: Optional[str] = None
    client: Optional[str] = None
    montant: Optional[float] = None
    nb_invites: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class FraClientEntertainmentOut(BaseModel):
    id: int
    company_id: int
    reference: str
    collaborateur: Optional[str] = None
    client: Optional[str] = None
    montant: Optional[float] = None
    nb_invites: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class FraConferenceFeeCreate(BaseModel):
    reference: str
    collaborateur: Optional[str] = None
    evenement: Optional[str] = None
    montant: Optional[float] = None
    date: Optional[date] = None
    statut: Optional[str] = None


class FraConferenceFeeUpdate(BaseModel):
    reference: Optional[str] = None
    collaborateur: Optional[str] = None
    evenement: Optional[str] = None
    montant: Optional[float] = None
    date: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class FraConferenceFeeOut(BaseModel):
    id: int
    company_id: int
    reference: str
    collaborateur: Optional[str] = None
    evenement: Optional[str] = None
    montant: Optional[float] = None
    date: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class FraOfficeSupplyCreate(BaseModel):
    reference: str
    demandeur: Optional[str] = None
    article: Optional[str] = None
    montant: Optional[float] = None
    centre_cout: Optional[str] = None
    statut: Optional[str] = None


class FraOfficeSupplyUpdate(BaseModel):
    reference: Optional[str] = None
    demandeur: Optional[str] = None
    article: Optional[str] = None
    montant: Optional[float] = None
    centre_cout: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class FraOfficeSupplyOut(BaseModel):
    id: int
    company_id: int
    reference: str
    demandeur: Optional[str] = None
    article: Optional[str] = None
    montant: Optional[float] = None
    centre_cout: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class FraCardTransactionCreate(BaseModel):
    reference: str
    titulaire: Optional[str] = None
    marchand: Optional[str] = None
    montant: Optional[float] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None


class FraCardTransactionUpdate(BaseModel):
    reference: Optional[str] = None
    titulaire: Optional[str] = None
    marchand: Optional[str] = None
    montant: Optional[float] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class FraCardTransactionOut(BaseModel):
    id: int
    company_id: int
    reference: str
    titulaire: Optional[str] = None
    marchand: Optional[str] = None
    montant: Optional[float] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class FraCurrencyConversionCreate(BaseModel):
    reference: str
    frais: Optional[str] = None
    devise_source: Optional[str] = None
    montant_source: Optional[float] = None
    taux: Optional[float] = None
    statut: Optional[str] = None


class FraCurrencyConversionUpdate(BaseModel):
    reference: Optional[str] = None
    frais: Optional[str] = None
    devise_source: Optional[str] = None
    montant_source: Optional[float] = None
    taux: Optional[float] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class FraCurrencyConversionOut(BaseModel):
    id: int
    company_id: int
    reference: str
    frais: Optional[str] = None
    devise_source: Optional[str] = None
    montant_source: Optional[float] = None
    taux: Optional[float] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class FraExpenseApprovalCreate(BaseModel):
    reference: str
    note_frais: Optional[str] = None
    valideur: Optional[str] = None
    commentaire: Optional[str] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None


class FraExpenseApprovalUpdate(BaseModel):
    reference: Optional[str] = None
    note_frais: Optional[str] = None
    valideur: Optional[str] = None
    commentaire: Optional[str] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class FraExpenseApprovalOut(BaseModel):
    id: int
    company_id: int
    reference: str
    note_frais: Optional[str] = None
    valideur: Optional[str] = None
    commentaire: Optional[str] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class FraExpenseDisputeCreate(BaseModel):
    reference: str
    note_frais: Optional[str] = None
    motif: Optional[str] = None
    montant_conteste: Optional[float] = None
    statut: Optional[str] = None


class FraExpenseDisputeUpdate(BaseModel):
    reference: Optional[str] = None
    note_frais: Optional[str] = None
    motif: Optional[str] = None
    montant_conteste: Optional[float] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class FraExpenseDisputeOut(BaseModel):
    id: int
    company_id: int
    reference: str
    note_frais: Optional[str] = None
    motif: Optional[str] = None
    montant_conteste: Optional[float] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class FraVatRecoveryCreate(BaseModel):
    reference: str
    frais: Optional[str] = None
    montant_ht: Optional[float] = None
    tva: Optional[float] = None
    statut: Optional[str] = None


class FraVatRecoveryUpdate(BaseModel):
    reference: Optional[str] = None
    frais: Optional[str] = None
    montant_ht: Optional[float] = None
    tva: Optional[float] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class FraVatRecoveryOut(BaseModel):
    id: int
    company_id: int
    reference: str
    frais: Optional[str] = None
    montant_ht: Optional[float] = None
    tva: Optional[float] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class FraExpenseBudgetTrackingCreate(BaseModel):
    reference: str
    centre_cout: Optional[str] = None
    periode: Optional[str] = None
    budget: Optional[float] = None
    engage: Optional[float] = None
    statut: Optional[str] = None


class FraExpenseBudgetTrackingUpdate(BaseModel):
    reference: Optional[str] = None
    centre_cout: Optional[str] = None
    periode: Optional[str] = None
    budget: Optional[float] = None
    engage: Optional[float] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class FraExpenseBudgetTrackingOut(BaseModel):
    id: int
    company_id: int
    reference: str
    centre_cout: Optional[str] = None
    periode: Optional[str] = None
    budget: Optional[float] = None
    engage: Optional[float] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class FraExpenseCategoryCreate(BaseModel):
    reference: str
    libelle: Optional[str] = None
    plafond: Optional[float] = None
    justificatif_requis: Optional[bool] = None
    statut: Optional[str] = None


class FraExpenseCategoryUpdate(BaseModel):
    reference: Optional[str] = None
    libelle: Optional[str] = None
    plafond: Optional[float] = None
    justificatif_requis: Optional[bool] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class FraExpenseCategoryOut(BaseModel):
    id: int
    company_id: int
    reference: str
    libelle: Optional[str] = None
    plafond: Optional[float] = None
    justificatif_requis: Optional[bool] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}

