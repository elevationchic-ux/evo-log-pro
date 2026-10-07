"""Schemas Pydantic pour client-b2b (genere)."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date


class ClientOnboardingCreate(BaseModel):
    reference: str
    raison_sociale: Optional[str] = None
    niu: Optional[str] = None
    rc: Optional[str] = None
    contact_principal: Optional[str] = None
    email: Optional[str] = None
    telephone: Optional[str] = None
    date_demande: Optional[date] = None
    statut: Optional[str] = None


class ClientOnboardingUpdate(BaseModel):
    reference: Optional[str] = None
    raison_sociale: Optional[str] = None
    niu: Optional[str] = None
    rc: Optional[str] = None
    contact_principal: Optional[str] = None
    email: Optional[str] = None
    telephone: Optional[str] = None
    date_demande: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class ClientOnboardingOut(BaseModel):
    id: int
    company_id: int
    reference: str
    raison_sociale: Optional[str] = None
    niu: Optional[str] = None
    rc: Optional[str] = None
    contact_principal: Optional[str] = None
    email: Optional[str] = None
    telephone: Optional[str] = None
    date_demande: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class SlaContractCreate(BaseModel):
    reference: str
    client_id: Optional[int] = None
    type_prestation: Optional[str] = None
    engagement_valeur: Optional[float] = None
    taux_atteint_pct: Optional[float] = None
    penalite_xaf: Optional[float] = None
    periode: Optional[str] = None
    statut: Optional[str] = None


class SlaContractUpdate(BaseModel):
    reference: Optional[str] = None
    client_id: Optional[int] = None
    type_prestation: Optional[str] = None
    engagement_valeur: Optional[float] = None
    taux_atteint_pct: Optional[float] = None
    penalite_xaf: Optional[float] = None
    periode: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class SlaContractOut(BaseModel):
    id: int
    company_id: int
    reference: str
    client_id: Optional[int] = None
    type_prestation: Optional[str] = None
    engagement_valeur: Optional[float] = None
    taux_atteint_pct: Optional[float] = None
    penalite_xaf: Optional[float] = None
    periode: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class B2bContractCreate(BaseModel):
    numero_contrat: str
    client_id: Optional[int] = None
    type_contrat: Optional[str] = None
    date_debut: Optional[date] = None
    date_fin: Optional[date] = None
    montant_engage_xaf: Optional[float] = None
    nb_avenants: Optional[int] = None
    statut: Optional[str] = None


class B2bContractUpdate(BaseModel):
    numero_contrat: Optional[str] = None
    client_id: Optional[int] = None
    type_contrat: Optional[str] = None
    date_debut: Optional[date] = None
    date_fin: Optional[date] = None
    montant_engage_xaf: Optional[float] = None
    nb_avenants: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class B2bContractOut(BaseModel):
    id: int
    company_id: int
    numero_contrat: str
    client_id: Optional[int] = None
    type_contrat: Optional[str] = None
    date_debut: Optional[date] = None
    date_fin: Optional[date] = None
    montant_engage_xaf: Optional[float] = None
    nb_avenants: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class SatisfactionSurveyCreate(BaseModel):
    reference: str
    client_id: Optional[int] = None
    date_enquete: Optional[date] = None
    note_global: Optional[float] = None
    score_nps: Optional[int] = None
    commentaires: Optional[str] = None


class SatisfactionSurveyUpdate(BaseModel):
    reference: Optional[str] = None
    client_id: Optional[int] = None
    date_enquete: Optional[date] = None
    note_global: Optional[float] = None
    score_nps: Optional[int] = None
    commentaires: Optional[str] = None
    is_active: Optional[bool] = None


class SatisfactionSurveyOut(BaseModel):
    id: int
    company_id: int
    reference: str
    client_id: Optional[int] = None
    date_enquete: Optional[date] = None
    note_global: Optional[float] = None
    score_nps: Optional[int] = None
    commentaires: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class ClientCreditLimitCreate(BaseModel):
    reference: str
    client_id: Optional[int] = None
    plafond_xaf: Optional[float] = None
    encours_actuel_xaf: Optional[float] = None
    delai_paiement_jours: Optional[int] = None
    date_revision: Optional[date] = None
    statut: Optional[str] = None


class ClientCreditLimitUpdate(BaseModel):
    reference: Optional[str] = None
    client_id: Optional[int] = None
    plafond_xaf: Optional[float] = None
    encours_actuel_xaf: Optional[float] = None
    delai_paiement_jours: Optional[int] = None
    date_revision: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class ClientCreditLimitOut(BaseModel):
    id: int
    company_id: int
    reference: str
    client_id: Optional[int] = None
    plafond_xaf: Optional[float] = None
    encours_actuel_xaf: Optional[float] = None
    delai_paiement_jours: Optional[int] = None
    date_revision: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class B2bDocumentCreate(BaseModel):
    reference: str
    client_id: Optional[int] = None
    type_document: Optional[str] = None
    nom_fichier: Optional[str] = None
    date_envoi: Optional[datetime] = None
    date_reception: Optional[datetime] = None
    statut: Optional[str] = None


class B2bDocumentUpdate(BaseModel):
    reference: Optional[str] = None
    client_id: Optional[int] = None
    type_document: Optional[str] = None
    nom_fichier: Optional[str] = None
    date_envoi: Optional[datetime] = None
    date_reception: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class B2bDocumentOut(BaseModel):
    id: int
    company_id: int
    reference: str
    client_id: Optional[int] = None
    type_document: Optional[str] = None
    nom_fichier: Optional[str] = None
    date_envoi: Optional[datetime] = None
    date_reception: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class ServiceRequestCreate(BaseModel):
    reference: str
    client_id: Optional[int] = None
    type_demande: Optional[str] = None
    description: Optional[str] = None
    date_creation: Optional[datetime] = None
    date_echeance: Optional[datetime] = None
    priorite: Optional[str] = None
    statut: Optional[str] = None


class ServiceRequestUpdate(BaseModel):
    reference: Optional[str] = None
    client_id: Optional[int] = None
    type_demande: Optional[str] = None
    description: Optional[str] = None
    date_creation: Optional[datetime] = None
    date_echeance: Optional[datetime] = None
    priorite: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class ServiceRequestOut(BaseModel):
    id: int
    company_id: int
    reference: str
    client_id: Optional[int] = None
    type_demande: Optional[str] = None
    description: Optional[str] = None
    date_creation: Optional[datetime] = None
    date_echeance: Optional[datetime] = None
    priorite: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class PricingAgreementCreate(BaseModel):
    reference: str
    client_id: Optional[int] = None
    type_prestation: Optional[str] = None
    remise_pct: Optional[float] = None
    palier_volume: Optional[str] = None
    date_debut: Optional[date] = None
    date_fin: Optional[date] = None
    statut: Optional[str] = None


class PricingAgreementUpdate(BaseModel):
    reference: Optional[str] = None
    client_id: Optional[int] = None
    type_prestation: Optional[str] = None
    remise_pct: Optional[float] = None
    palier_volume: Optional[str] = None
    date_debut: Optional[date] = None
    date_fin: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class PricingAgreementOut(BaseModel):
    id: int
    company_id: int
    reference: str
    client_id: Optional[int] = None
    type_prestation: Optional[str] = None
    remise_pct: Optional[float] = None
    palier_volume: Optional[str] = None
    date_debut: Optional[date] = None
    date_fin: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class ShipmentBookingCreate(BaseModel):
    reference: str
    client_id: Optional[int] = None
    escale_id: Optional[int] = None
    type_expedition: Optional[str] = None
    date_reservation: Optional[datetime] = None
    date_prevue: Optional[datetime] = None
    conteneurs_prevus: Optional[int] = None
    statut: Optional[str] = None


class ShipmentBookingUpdate(BaseModel):
    reference: Optional[str] = None
    client_id: Optional[int] = None
    escale_id: Optional[int] = None
    type_expedition: Optional[str] = None
    date_reservation: Optional[datetime] = None
    date_prevue: Optional[datetime] = None
    conteneurs_prevus: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class ShipmentBookingOut(BaseModel):
    id: int
    company_id: int
    reference: str
    client_id: Optional[int] = None
    escale_id: Optional[int] = None
    type_expedition: Optional[str] = None
    date_reservation: Optional[datetime] = None
    date_prevue: Optional[datetime] = None
    conteneurs_prevus: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class ClientClaimCreate(BaseModel):
    reference: str
    client_id: Optional[int] = None
    objet: Optional[str] = None
    description: Optional[str] = None
    date_reclamation: Optional[date] = None
    montant_reclame_xaf: Optional[float] = None
    statut: Optional[str] = None


class ClientClaimUpdate(BaseModel):
    reference: Optional[str] = None
    client_id: Optional[int] = None
    objet: Optional[str] = None
    description: Optional[str] = None
    date_reclamation: Optional[date] = None
    montant_reclame_xaf: Optional[float] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class ClientClaimOut(BaseModel):
    id: int
    company_id: int
    reference: str
    client_id: Optional[int] = None
    objet: Optional[str] = None
    description: Optional[str] = None
    date_reclamation: Optional[date] = None
    montant_reclame_xaf: Optional[float] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class AccountReportCreate(BaseModel):
    reference: str
    client_id: Optional[int] = None
    periode_debut: Optional[date] = None
    periode_fin: Optional[date] = None
    factures_emises_xaf: Optional[float] = None
    reglements_recus_xaf: Optional[float] = None
    solde_a_payer_xaf: Optional[float] = None


class AccountReportUpdate(BaseModel):
    reference: Optional[str] = None
    client_id: Optional[int] = None
    periode_debut: Optional[date] = None
    periode_fin: Optional[date] = None
    factures_emises_xaf: Optional[float] = None
    reglements_recus_xaf: Optional[float] = None
    solde_a_payer_xaf: Optional[float] = None
    is_active: Optional[bool] = None


class AccountReportOut(BaseModel):
    id: int
    company_id: int
    reference: str
    client_id: Optional[int] = None
    periode_debut: Optional[date] = None
    periode_fin: Optional[date] = None
    factures_emises_xaf: Optional[float] = None
    reglements_recus_xaf: Optional[float] = None
    solde_a_payer_xaf: Optional[float] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}

