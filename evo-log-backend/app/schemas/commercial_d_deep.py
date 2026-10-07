"""Schemas Pydantic pour portail-commercial (genere)."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date


class CommLeadCreate(BaseModel):
    reference: str
    prospect: Optional[str] = None
    source: Optional[str] = None
    segment: Optional[str] = None
    date: Optional[date] = None
    statut: Optional[str] = None


class CommLeadUpdate(BaseModel):
    reference: Optional[str] = None
    prospect: Optional[str] = None
    source: Optional[str] = None
    segment: Optional[str] = None
    date: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class CommLeadOut(BaseModel):
    id: int
    company_id: int
    reference: str
    prospect: Optional[str] = None
    source: Optional[str] = None
    segment: Optional[str] = None
    date: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class CommOpportunityCreate(BaseModel):
    reference: str
    client: Optional[str] = None
    libelle: Optional[str] = None
    montant_estime: Optional[float] = None
    cloture_prevue: Optional[date] = None
    statut: Optional[str] = None


class CommOpportunityUpdate(BaseModel):
    reference: Optional[str] = None
    client: Optional[str] = None
    libelle: Optional[str] = None
    montant_estime: Optional[float] = None
    cloture_prevue: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class CommOpportunityOut(BaseModel):
    id: int
    company_id: int
    reference: str
    client: Optional[str] = None
    libelle: Optional[str] = None
    montant_estime: Optional[float] = None
    cloture_prevue: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class CommQuoteCreate(BaseModel):
    reference: str
    client: Optional[str] = None
    montant: Optional[float] = None
    validite: Optional[date] = None
    date_emission: Optional[date] = None
    statut: Optional[str] = None


class CommQuoteUpdate(BaseModel):
    reference: Optional[str] = None
    client: Optional[str] = None
    montant: Optional[float] = None
    validite: Optional[date] = None
    date_emission: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class CommQuoteOut(BaseModel):
    id: int
    company_id: int
    reference: str
    client: Optional[str] = None
    montant: Optional[float] = None
    validite: Optional[date] = None
    date_emission: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class CommSalesOrderCreate(BaseModel):
    reference: str
    client: Optional[str] = None
    devis: Optional[str] = None
    montant: Optional[float] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None


class CommSalesOrderUpdate(BaseModel):
    reference: Optional[str] = None
    client: Optional[str] = None
    devis: Optional[str] = None
    montant: Optional[float] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class CommSalesOrderOut(BaseModel):
    id: int
    company_id: int
    reference: str
    client: Optional[str] = None
    devis: Optional[str] = None
    montant: Optional[float] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class CommCustomerVisitCreate(BaseModel):
    reference: str
    client: Optional[str] = None
    date: Optional[datetime] = None
    interlocuteur: Optional[str] = None
    compte_rendu: Optional[str] = None
    statut: Optional[str] = None


class CommCustomerVisitUpdate(BaseModel):
    reference: Optional[str] = None
    client: Optional[str] = None
    date: Optional[datetime] = None
    interlocuteur: Optional[str] = None
    compte_rendu: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class CommCustomerVisitOut(BaseModel):
    id: int
    company_id: int
    reference: str
    client: Optional[str] = None
    date: Optional[datetime] = None
    interlocuteur: Optional[str] = None
    compte_rendu: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class CommSampleRequestCreate(BaseModel):
    reference: str
    client: Optional[str] = None
    produit: Optional[str] = None
    quantite: Optional[int] = None
    date: Optional[date] = None
    statut: Optional[str] = None


class CommSampleRequestUpdate(BaseModel):
    reference: Optional[str] = None
    client: Optional[str] = None
    produit: Optional[str] = None
    quantite: Optional[int] = None
    date: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class CommSampleRequestOut(BaseModel):
    id: int
    company_id: int
    reference: str
    client: Optional[str] = None
    produit: Optional[str] = None
    quantite: Optional[int] = None
    date: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class CommTenderCreate(BaseModel):
    reference: str
    acheteur: Optional[str] = None
    objet: Optional[str] = None
    date_limite: Optional[date] = None
    montant_offre: Optional[float] = None
    statut: Optional[str] = None


class CommTenderUpdate(BaseModel):
    reference: Optional[str] = None
    acheteur: Optional[str] = None
    objet: Optional[str] = None
    date_limite: Optional[date] = None
    montant_offre: Optional[float] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class CommTenderOut(BaseModel):
    id: int
    company_id: int
    reference: str
    acheteur: Optional[str] = None
    objet: Optional[str] = None
    date_limite: Optional[date] = None
    montant_offre: Optional[float] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class CommContractRenewalCreate(BaseModel):
    reference: str
    client: Optional[str] = None
    contrat: Optional[str] = None
    echeance: Optional[date] = None
    valeur: Optional[float] = None
    statut: Optional[str] = None


class CommContractRenewalUpdate(BaseModel):
    reference: Optional[str] = None
    client: Optional[str] = None
    contrat: Optional[str] = None
    echeance: Optional[date] = None
    valeur: Optional[float] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class CommContractRenewalOut(BaseModel):
    id: int
    company_id: int
    reference: str
    client: Optional[str] = None
    contrat: Optional[str] = None
    echeance: Optional[date] = None
    valeur: Optional[float] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class CommPriceRequestCreate(BaseModel):
    reference: str
    client: Optional[str] = None
    produit: Optional[str] = None
    remise: Optional[float] = None
    date: Optional[date] = None
    statut: Optional[str] = None


class CommPriceRequestUpdate(BaseModel):
    reference: Optional[str] = None
    client: Optional[str] = None
    produit: Optional[str] = None
    remise: Optional[float] = None
    date: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class CommPriceRequestOut(BaseModel):
    id: int
    company_id: int
    reference: str
    client: Optional[str] = None
    produit: Optional[str] = None
    remise: Optional[float] = None
    date: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class CommCreditRequestCreate(BaseModel):
    reference: str
    client: Optional[str] = None
    encours_actuel: Optional[float] = None
    montant_souhaite: Optional[float] = None
    date: Optional[date] = None
    statut: Optional[str] = None


class CommCreditRequestUpdate(BaseModel):
    reference: Optional[str] = None
    client: Optional[str] = None
    encours_actuel: Optional[float] = None
    montant_souhaite: Optional[float] = None
    date: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class CommCreditRequestOut(BaseModel):
    id: int
    company_id: int
    reference: str
    client: Optional[str] = None
    encours_actuel: Optional[float] = None
    montant_souhaite: Optional[float] = None
    date: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class CommOrderModificationCreate(BaseModel):
    reference: str
    commande: Optional[str] = None
    changement: Optional[str] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None


class CommOrderModificationUpdate(BaseModel):
    reference: Optional[str] = None
    commande: Optional[str] = None
    changement: Optional[str] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class CommOrderModificationOut(BaseModel):
    id: int
    company_id: int
    reference: str
    commande: Optional[str] = None
    changement: Optional[str] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class CommCustomerComplaintCreate(BaseModel):
    reference: str
    client: Optional[str] = None
    objet: Optional[str] = None
    canal: Optional[str] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None


class CommCustomerComplaintUpdate(BaseModel):
    reference: Optional[str] = None
    client: Optional[str] = None
    objet: Optional[str] = None
    canal: Optional[str] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class CommCustomerComplaintOut(BaseModel):
    id: int
    company_id: int
    reference: str
    client: Optional[str] = None
    objet: Optional[str] = None
    canal: Optional[str] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class CommUpsellRecordCreate(BaseModel):
    reference: str
    client: Optional[str] = None
    offre: Optional[str] = None
    montant_potentiel: Optional[float] = None
    date: Optional[date] = None
    statut: Optional[str] = None


class CommUpsellRecordUpdate(BaseModel):
    reference: Optional[str] = None
    client: Optional[str] = None
    offre: Optional[str] = None
    montant_potentiel: Optional[float] = None
    date: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class CommUpsellRecordOut(BaseModel):
    id: int
    company_id: int
    reference: str
    client: Optional[str] = None
    offre: Optional[str] = None
    montant_potentiel: Optional[float] = None
    date: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class CommCommissionStatementCreate(BaseModel):
    reference: str
    commercial: Optional[str] = None
    periode: Optional[str] = None
    base_vente: Optional[float] = None
    taux: Optional[float] = None
    statut: Optional[str] = None


class CommCommissionStatementUpdate(BaseModel):
    reference: Optional[str] = None
    commercial: Optional[str] = None
    periode: Optional[str] = None
    base_vente: Optional[float] = None
    taux: Optional[float] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class CommCommissionStatementOut(BaseModel):
    id: int
    company_id: int
    reference: str
    commercial: Optional[str] = None
    periode: Optional[str] = None
    base_vente: Optional[float] = None
    taux: Optional[float] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class CommPipelineReviewCreate(BaseModel):
    reference: str
    commercial: Optional[str] = None
    nb_opportunites: Optional[int] = None
    valeur_ponderee: Optional[float] = None
    date: Optional[date] = None
    statut: Optional[str] = None


class CommPipelineReviewUpdate(BaseModel):
    reference: Optional[str] = None
    commercial: Optional[str] = None
    nb_opportunites: Optional[int] = None
    valeur_ponderee: Optional[float] = None
    date: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class CommPipelineReviewOut(BaseModel):
    id: int
    company_id: int
    reference: str
    commercial: Optional[str] = None
    nb_opportunites: Optional[int] = None
    valeur_ponderee: Optional[float] = None
    date: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}

