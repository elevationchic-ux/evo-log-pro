"""Schemas Pydantic pour client-b2b (genere)."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date


class B2bCContractAgreementCreate(BaseModel):
    reference: str
    client: Optional[str] = None
    type_contrat: Optional[str] = None
    date_debut: Optional[date] = None
    date_fin: Optional[date] = None
    valeur_annuelle: Optional[float] = None
    contact: Optional[str] = None
    statut: Optional[str] = None


class B2bCContractAgreementUpdate(BaseModel):
    reference: Optional[str] = None
    client: Optional[str] = None
    type_contrat: Optional[str] = None
    date_debut: Optional[date] = None
    date_fin: Optional[date] = None
    valeur_annuelle: Optional[float] = None
    contact: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class B2bCContractAgreementOut(BaseModel):
    id: int
    company_id: int
    reference: str
    client: Optional[str] = None
    type_contrat: Optional[str] = None
    date_debut: Optional[date] = None
    date_fin: Optional[date] = None
    valeur_annuelle: Optional[float] = None
    contact: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class B2bCPriceListCreate(BaseModel):
    reference: str
    client: Optional[str] = None
    version: Optional[str] = None
    devise: Optional[str] = None
    date_debut_validite: Optional[date] = None
    date_fin_validite: Optional[date] = None
    remise_globale_pct: Optional[int] = None
    statut: Optional[str] = None


class B2bCPriceListUpdate(BaseModel):
    reference: Optional[str] = None
    client: Optional[str] = None
    version: Optional[str] = None
    devise: Optional[str] = None
    date_debut_validite: Optional[date] = None
    date_fin_validite: Optional[date] = None
    remise_globale_pct: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class B2bCPriceListOut(BaseModel):
    id: int
    company_id: int
    reference: str
    client: Optional[str] = None
    version: Optional[str] = None
    devise: Optional[str] = None
    date_debut_validite: Optional[date] = None
    date_fin_validite: Optional[date] = None
    remise_globale_pct: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class B2bCSalesOrderCreate(BaseModel):
    reference: str
    client: Optional[str] = None
    date_commande: Optional[date] = None
    nb_lignes: Optional[int] = None
    montant_total: Optional[float] = None
    date_livraison_souhaitee: Optional[date] = None
    contrat_ref: Optional[str] = None
    statut: Optional[str] = None


class B2bCSalesOrderUpdate(BaseModel):
    reference: Optional[str] = None
    client: Optional[str] = None
    date_commande: Optional[date] = None
    nb_lignes: Optional[int] = None
    montant_total: Optional[float] = None
    date_livraison_souhaitee: Optional[date] = None
    contrat_ref: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class B2bCSalesOrderOut(BaseModel):
    id: int
    company_id: int
    reference: str
    client: Optional[str] = None
    date_commande: Optional[date] = None
    nb_lignes: Optional[int] = None
    montant_total: Optional[float] = None
    date_livraison_souhaitee: Optional[date] = None
    contrat_ref: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class B2bCCreditAccountCreate(BaseModel):
    reference: str
    client: Optional[str] = None
    limite_credit: Optional[float] = None
    encours: Optional[float] = None
    delai_paiement_jours: Optional[int] = None
    date_dernier_paiement: Optional[date] = None
    statut: Optional[str] = None


class B2bCCreditAccountUpdate(BaseModel):
    reference: Optional[str] = None
    client: Optional[str] = None
    limite_credit: Optional[float] = None
    encours: Optional[float] = None
    delai_paiement_jours: Optional[int] = None
    date_dernier_paiement: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class B2bCCreditAccountOut(BaseModel):
    id: int
    company_id: int
    reference: str
    client: Optional[str] = None
    limite_credit: Optional[float] = None
    encours: Optional[float] = None
    delai_paiement_jours: Optional[int] = None
    date_dernier_paiement: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class B2bCSupportTicketCreate(BaseModel):
    reference: str
    client: Optional[str] = None
    sujet: Optional[str] = None
    categorie: Optional[str] = None
    priorite: Optional[str] = None
    date_ouverture: Optional[datetime] = None
    date_resolution: Optional[datetime] = None
    statut: Optional[str] = None


class B2bCSupportTicketUpdate(BaseModel):
    reference: Optional[str] = None
    client: Optional[str] = None
    sujet: Optional[str] = None
    categorie: Optional[str] = None
    priorite: Optional[str] = None
    date_ouverture: Optional[datetime] = None
    date_resolution: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class B2bCSupportTicketOut(BaseModel):
    id: int
    company_id: int
    reference: str
    client: Optional[str] = None
    sujet: Optional[str] = None
    categorie: Optional[str] = None
    priorite: Optional[str] = None
    date_ouverture: Optional[datetime] = None
    date_resolution: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}

