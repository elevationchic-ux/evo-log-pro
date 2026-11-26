"""Schemas Pydantic pour annuaire-prestataires (genere)."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date


class ProvProfileCreate(BaseModel):
    reference: str
    raison_sociale: Optional[str] = None
    type_prestation: Optional[str] = None
    zone: Optional[str] = None
    contact: Optional[str] = None
    statut: Optional[str] = None


class ProvProfileUpdate(BaseModel):
    reference: Optional[str] = None
    raison_sociale: Optional[str] = None
    type_prestation: Optional[str] = None
    zone: Optional[str] = None
    contact: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class ProvProfileOut(BaseModel):
    id: int
    company_id: int
    reference: str
    raison_sociale: Optional[str] = None
    type_prestation: Optional[str] = None
    zone: Optional[str] = None
    contact: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class ProvCategoryCreate(BaseModel):
    reference: str
    libelle: Optional[str] = None
    exigence_documentaire: Optional[bool] = None
    nb_prestataires: Optional[int] = None
    statut: Optional[str] = None


class ProvCategoryUpdate(BaseModel):
    reference: Optional[str] = None
    libelle: Optional[str] = None
    exigence_documentaire: Optional[bool] = None
    nb_prestataires: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class ProvCategoryOut(BaseModel):
    id: int
    company_id: int
    reference: str
    libelle: Optional[str] = None
    exigence_documentaire: Optional[bool] = None
    nb_prestataires: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class ProvCertificationCreate(BaseModel):
    reference: str
    prestataire: Optional[str] = None
    intitule: Optional[str] = None
    emetteur: Optional[str] = None
    expire_le: Optional[date] = None
    statut: Optional[str] = None


class ProvCertificationUpdate(BaseModel):
    reference: Optional[str] = None
    prestataire: Optional[str] = None
    intitule: Optional[str] = None
    emetteur: Optional[str] = None
    expire_le: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class ProvCertificationOut(BaseModel):
    id: int
    company_id: int
    reference: str
    prestataire: Optional[str] = None
    intitule: Optional[str] = None
    emetteur: Optional[str] = None
    expire_le: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class ProvInsuranceAttestationCreate(BaseModel):
    reference: str
    prestataire: Optional[str] = None
    type_assurance: Optional[str] = None
    montant_couvert: Optional[float] = None
    expire_le: Optional[date] = None
    statut: Optional[str] = None


class ProvInsuranceAttestationUpdate(BaseModel):
    reference: Optional[str] = None
    prestataire: Optional[str] = None
    type_assurance: Optional[str] = None
    montant_couvert: Optional[float] = None
    expire_le: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class ProvInsuranceAttestationOut(BaseModel):
    id: int
    company_id: int
    reference: str
    prestataire: Optional[str] = None
    type_assurance: Optional[str] = None
    montant_couvert: Optional[float] = None
    expire_le: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class ProvServiceContractCreate(BaseModel):
    reference: str
    prestataire: Optional[str] = None
    objet: Optional[str] = None
    montant: Optional[float] = None
    echeance: Optional[date] = None
    statut: Optional[str] = None


class ProvServiceContractUpdate(BaseModel):
    reference: Optional[str] = None
    prestataire: Optional[str] = None
    objet: Optional[str] = None
    montant: Optional[float] = None
    echeance: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class ProvServiceContractOut(BaseModel):
    id: int
    company_id: int
    reference: str
    prestataire: Optional[str] = None
    objet: Optional[str] = None
    montant: Optional[float] = None
    echeance: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class ProvEvaluationCreate(BaseModel):
    reference: str
    prestataire: Optional[str] = None
    periode: Optional[str] = None
    score: Optional[int] = None
    evalueur: Optional[str] = None
    statut: Optional[str] = None


class ProvEvaluationUpdate(BaseModel):
    reference: Optional[str] = None
    prestataire: Optional[str] = None
    periode: Optional[str] = None
    score: Optional[int] = None
    evalueur: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class ProvEvaluationOut(BaseModel):
    id: int
    company_id: int
    reference: str
    prestataire: Optional[str] = None
    periode: Optional[str] = None
    score: Optional[int] = None
    evalueur: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class ProvIncidentCreate(BaseModel):
    reference: str
    prestataire: Optional[str] = None
    description: Optional[str] = None
    gravite: Optional[str] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None


class ProvIncidentUpdate(BaseModel):
    reference: Optional[str] = None
    prestataire: Optional[str] = None
    description: Optional[str] = None
    gravite: Optional[str] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class ProvIncidentOut(BaseModel):
    id: int
    company_id: int
    reference: str
    prestataire: Optional[str] = None
    description: Optional[str] = None
    gravite: Optional[str] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class ProvAvailabilityCalendarCreate(BaseModel):
    reference: str
    prestataire: Optional[str] = None
    semaine: Optional[str] = None
    creneaux_libres: Optional[int] = None
    statut: Optional[str] = None


class ProvAvailabilityCalendarUpdate(BaseModel):
    reference: Optional[str] = None
    prestataire: Optional[str] = None
    semaine: Optional[str] = None
    creneaux_libres: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class ProvAvailabilityCalendarOut(BaseModel):
    id: int
    company_id: int
    reference: str
    prestataire: Optional[str] = None
    semaine: Optional[str] = None
    creneaux_libres: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class ProvPriceListCreate(BaseModel):
    reference: str
    prestataire: Optional[str] = None
    unite_prix: Optional[float] = None
    validite: Optional[date] = None
    statut: Optional[str] = None


class ProvPriceListUpdate(BaseModel):
    reference: Optional[str] = None
    prestataire: Optional[str] = None
    unite_prix: Optional[float] = None
    validite: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class ProvPriceListOut(BaseModel):
    id: int
    company_id: int
    reference: str
    prestataire: Optional[str] = None
    unite_prix: Optional[float] = None
    validite: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class ProvContactCreate(BaseModel):
    reference: str
    prestataire: Optional[str] = None
    nom: Optional[str] = None
    role: Optional[str] = None
    telephone: Optional[str] = None
    statut: Optional[str] = None


class ProvContactUpdate(BaseModel):
    reference: Optional[str] = None
    prestataire: Optional[str] = None
    nom: Optional[str] = None
    role: Optional[str] = None
    telephone: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class ProvContactOut(BaseModel):
    id: int
    company_id: int
    reference: str
    prestataire: Optional[str] = None
    nom: Optional[str] = None
    role: Optional[str] = None
    telephone: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class ProvOnboardingCreate(BaseModel):
    reference: str
    prestataire: Optional[str] = None
    etapes_faites: Optional[int] = None
    etapes_total: Optional[int] = None
    date: Optional[date] = None
    statut: Optional[str] = None


class ProvOnboardingUpdate(BaseModel):
    reference: Optional[str] = None
    prestataire: Optional[str] = None
    etapes_faites: Optional[int] = None
    etapes_total: Optional[int] = None
    date: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class ProvOnboardingOut(BaseModel):
    id: int
    company_id: int
    reference: str
    prestataire: Optional[str] = None
    etapes_faites: Optional[int] = None
    etapes_total: Optional[int] = None
    date: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class ProvReviewCreate(BaseModel):
    reference: str
    prestataire: Optional[str] = None
    commentaire: Optional[str] = None
    nb_etoiles: Optional[int] = None
    date: Optional[date] = None
    statut: Optional[str] = None


class ProvReviewUpdate(BaseModel):
    reference: Optional[str] = None
    prestataire: Optional[str] = None
    commentaire: Optional[str] = None
    nb_etoiles: Optional[int] = None
    date: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class ProvReviewOut(BaseModel):
    id: int
    company_id: int
    reference: str
    prestataire: Optional[str] = None
    commentaire: Optional[str] = None
    nb_etoiles: Optional[int] = None
    date: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class ProvRfqRequestCreate(BaseModel):
    reference: str
    objet: Optional[str] = None
    nb_offres: Optional[int] = None
    date_limite: Optional[date] = None
    statut: Optional[str] = None


class ProvRfqRequestUpdate(BaseModel):
    reference: Optional[str] = None
    objet: Optional[str] = None
    nb_offres: Optional[int] = None
    date_limite: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class ProvRfqRequestOut(BaseModel):
    id: int
    company_id: int
    reference: str
    objet: Optional[str] = None
    nb_offres: Optional[int] = None
    date_limite: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class ProvInterventionCreate(BaseModel):
    reference: str
    prestataire: Optional[str] = None
    site: Optional[str] = None
    date: Optional[datetime] = None
    compte_rendu: Optional[str] = None
    statut: Optional[str] = None


class ProvInterventionUpdate(BaseModel):
    reference: Optional[str] = None
    prestataire: Optional[str] = None
    site: Optional[str] = None
    date: Optional[datetime] = None
    compte_rendu: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class ProvInterventionOut(BaseModel):
    id: int
    company_id: int
    reference: str
    prestataire: Optional[str] = None
    site: Optional[str] = None
    date: Optional[datetime] = None
    compte_rendu: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class ProvComplianceDocCreate(BaseModel):
    reference: str
    prestataire: Optional[str] = None
    type_piece: Optional[str] = None
    expire_le: Optional[date] = None
    statut: Optional[str] = None


class ProvComplianceDocUpdate(BaseModel):
    reference: Optional[str] = None
    prestataire: Optional[str] = None
    type_piece: Optional[str] = None
    expire_le: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class ProvComplianceDocOut(BaseModel):
    id: int
    company_id: int
    reference: str
    prestataire: Optional[str] = None
    type_piece: Optional[str] = None
    expire_le: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class ProvBankDetailCreate(BaseModel):
    reference: str
    prestataire: Optional[str] = None
    banque: Optional[str] = None
    iban_verifie: Optional[bool] = None
    date: Optional[date] = None
    statut: Optional[str] = None


class ProvBankDetailUpdate(BaseModel):
    reference: Optional[str] = None
    prestataire: Optional[str] = None
    banque: Optional[str] = None
    iban_verifie: Optional[bool] = None
    date: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class ProvBankDetailOut(BaseModel):
    id: int
    company_id: int
    reference: str
    prestataire: Optional[str] = None
    banque: Optional[str] = None
    iban_verifie: Optional[bool] = None
    date: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class ProvBlacklistCreate(BaseModel):
    reference: str
    prestataire: Optional[str] = None
    motif: Optional[str] = None
    debut: Optional[date] = None
    fin_prevue: Optional[date] = None
    statut: Optional[str] = None


class ProvBlacklistUpdate(BaseModel):
    reference: Optional[str] = None
    prestataire: Optional[str] = None
    motif: Optional[str] = None
    debut: Optional[date] = None
    fin_prevue: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class ProvBlacklistOut(BaseModel):
    id: int
    company_id: int
    reference: str
    prestataire: Optional[str] = None
    motif: Optional[str] = None
    debut: Optional[date] = None
    fin_prevue: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}

