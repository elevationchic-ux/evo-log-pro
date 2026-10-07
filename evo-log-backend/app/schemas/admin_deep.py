"""Schemas Pydantic pour admin-saas (genere)."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date


class FeatureFlagCreate(BaseModel):
    code_flag: str
    description: Optional[str] = None
    actif: Optional[bool] = None
    tenants_concernes: Optional[str] = None
    date_debut_rollout: Optional[date] = None
    statut: Optional[str] = None


class FeatureFlagUpdate(BaseModel):
    code_flag: Optional[str] = None
    description: Optional[str] = None
    actif: Optional[bool] = None
    tenants_concernes: Optional[str] = None
    date_debut_rollout: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class FeatureFlagOut(BaseModel):
    id: int
    company_id: int
    code_flag: str
    description: Optional[str] = None
    actif: Optional[bool] = None
    tenants_concernes: Optional[str] = None
    date_debut_rollout: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class ApiQuotaCreate(BaseModel):
    reference: str
    tenant_id: Optional[int] = None
    api_group: Optional[str] = None
    limite_minute: Optional[int] = None
    limite_jour: Optional[int] = None
    consommation_actuelle: Optional[int] = None
    statut: Optional[str] = None


class ApiQuotaUpdate(BaseModel):
    reference: Optional[str] = None
    tenant_id: Optional[int] = None
    api_group: Optional[str] = None
    limite_minute: Optional[int] = None
    limite_jour: Optional[int] = None
    consommation_actuelle: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class ApiQuotaOut(BaseModel):
    id: int
    company_id: int
    reference: str
    tenant_id: Optional[int] = None
    api_group: Optional[str] = None
    limite_minute: Optional[int] = None
    limite_jour: Optional[int] = None
    consommation_actuelle: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class WhiteLabelCreate(BaseModel):
    reference: str
    tenant_id: Optional[int] = None
    nom_marque: Optional[str] = None
    domaine_personnalise: Optional[str] = None
    logo_url: Optional[str] = None
    couleur_primaire: Optional[str] = None
    couleur_secondaire: Optional[str] = None
    actif: Optional[bool] = None


class WhiteLabelUpdate(BaseModel):
    reference: Optional[str] = None
    tenant_id: Optional[int] = None
    nom_marque: Optional[str] = None
    domaine_personnalise: Optional[str] = None
    logo_url: Optional[str] = None
    couleur_primaire: Optional[str] = None
    couleur_secondaire: Optional[str] = None
    actif: Optional[bool] = None
    is_active: Optional[bool] = None


class WhiteLabelOut(BaseModel):
    id: int
    company_id: int
    reference: str
    tenant_id: Optional[int] = None
    nom_marque: Optional[str] = None
    domaine_personnalise: Optional[str] = None
    logo_url: Optional[str] = None
    couleur_primaire: Optional[str] = None
    couleur_secondaire: Optional[str] = None
    actif: Optional[bool] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class TenantOnboardingCreate(BaseModel):
    reference: str
    tenant_id: Optional[int] = None
    date_debut: Optional[date] = None
    date_activation: Optional[date] = None
    nb_etapes_completes: Optional[int] = None
    responsable_succeed: Optional[str] = None
    statut: Optional[str] = None


class TenantOnboardingUpdate(BaseModel):
    reference: Optional[str] = None
    tenant_id: Optional[int] = None
    date_debut: Optional[date] = None
    date_activation: Optional[date] = None
    nb_etapes_completes: Optional[int] = None
    responsable_succeed: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class TenantOnboardingOut(BaseModel):
    id: int
    company_id: int
    reference: str
    tenant_id: Optional[int] = None
    date_debut: Optional[date] = None
    date_activation: Optional[date] = None
    nb_etapes_completes: Optional[int] = None
    responsable_succeed: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class TenantApiKeyCreate(BaseModel):
    reference: str
    tenant_id: Optional[int] = None
    label: Optional[str] = None
    scopes: Optional[str] = None
    date_creation: Optional[date] = None
    date_expiration: Optional[date] = None
    derniere_utilisation: Optional[datetime] = None
    statut: Optional[str] = None


class TenantApiKeyUpdate(BaseModel):
    reference: Optional[str] = None
    tenant_id: Optional[int] = None
    label: Optional[str] = None
    scopes: Optional[str] = None
    date_creation: Optional[date] = None
    date_expiration: Optional[date] = None
    derniere_utilisation: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class TenantApiKeyOut(BaseModel):
    id: int
    company_id: int
    reference: str
    tenant_id: Optional[int] = None
    label: Optional[str] = None
    scopes: Optional[str] = None
    date_creation: Optional[date] = None
    date_expiration: Optional[date] = None
    derniere_utilisation: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class TenantWebhookCreate(BaseModel):
    reference: str
    tenant_id: Optional[int] = None
    url_destination: Optional[str] = None
    evenements_abonnes: Optional[str] = None
    secret_hmac: Optional[str] = None
    dernier_succes: Optional[datetime] = None
    statut: Optional[str] = None


class TenantWebhookUpdate(BaseModel):
    reference: Optional[str] = None
    tenant_id: Optional[int] = None
    url_destination: Optional[str] = None
    evenements_abonnes: Optional[str] = None
    secret_hmac: Optional[str] = None
    dernier_succes: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class TenantWebhookOut(BaseModel):
    id: int
    company_id: int
    reference: str
    tenant_id: Optional[int] = None
    url_destination: Optional[str] = None
    evenements_abonnes: Optional[str] = None
    secret_hmac: Optional[str] = None
    dernier_succes: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class DataMigrationCreate(BaseModel):
    reference: str
    tenant_id: Optional[int] = None
    type_migration: Optional[str] = None
    source: Optional[str] = None
    nb_lignes_prevues: Optional[int] = None
    nb_lignes_importees: Optional[int] = None
    nb_lignes_rejetees: Optional[int] = None
    date_debut: Optional[datetime] = None
    date_fin: Optional[datetime] = None
    statut: Optional[str] = None


class DataMigrationUpdate(BaseModel):
    reference: Optional[str] = None
    tenant_id: Optional[int] = None
    type_migration: Optional[str] = None
    source: Optional[str] = None
    nb_lignes_prevues: Optional[int] = None
    nb_lignes_importees: Optional[int] = None
    nb_lignes_rejetees: Optional[int] = None
    date_debut: Optional[datetime] = None
    date_fin: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class DataMigrationOut(BaseModel):
    id: int
    company_id: int
    reference: str
    tenant_id: Optional[int] = None
    type_migration: Optional[str] = None
    source: Optional[str] = None
    nb_lignes_prevues: Optional[int] = None
    nb_lignes_importees: Optional[int] = None
    nb_lignes_rejetees: Optional[int] = None
    date_debut: Optional[datetime] = None
    date_fin: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class PlatformTicketCreate(BaseModel):
    reference: str
    tenant_id: Optional[int] = None
    titre: Optional[str] = None
    description: Optional[str] = None
    priorite: Optional[str] = None
    assigne_a: Optional[str] = None
    date_creation: Optional[datetime] = None
    statut: Optional[str] = None


class PlatformTicketUpdate(BaseModel):
    reference: Optional[str] = None
    tenant_id: Optional[int] = None
    titre: Optional[str] = None
    description: Optional[str] = None
    priorite: Optional[str] = None
    assigne_a: Optional[str] = None
    date_creation: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class PlatformTicketOut(BaseModel):
    id: int
    company_id: int
    reference: str
    tenant_id: Optional[int] = None
    titre: Optional[str] = None
    description: Optional[str] = None
    priorite: Optional[str] = None
    assigne_a: Optional[str] = None
    date_creation: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class BillingEntryCreate(BaseModel):
    reference: str
    tenant_id: Optional[int] = None
    periode: Optional[str] = None
    type_facture: Optional[str] = None
    montant_ht_xaf: Optional[float] = None
    tva_xaf: Optional[float] = None
    total_ttc_xaf: Optional[float] = None
    statut: Optional[str] = None


class BillingEntryUpdate(BaseModel):
    reference: Optional[str] = None
    tenant_id: Optional[int] = None
    periode: Optional[str] = None
    type_facture: Optional[str] = None
    montant_ht_xaf: Optional[float] = None
    tva_xaf: Optional[float] = None
    total_ttc_xaf: Optional[float] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class BillingEntryOut(BaseModel):
    id: int
    company_id: int
    reference: str
    tenant_id: Optional[int] = None
    periode: Optional[str] = None
    type_facture: Optional[str] = None
    montant_ht_xaf: Optional[float] = None
    tva_xaf: Optional[float] = None
    total_ttc_xaf: Optional[float] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class UsageAnalyticsCreate(BaseModel):
    reference: str
    tenant_id: Optional[int] = None
    periode: Optional[str] = None
    utilisateurs_actifs: Optional[int] = None
    utilisateurs_seats: Optional[int] = None
    taux_adoption_pct: Optional[float] = None
    score_sante: Optional[float] = None


class UsageAnalyticsUpdate(BaseModel):
    reference: Optional[str] = None
    tenant_id: Optional[int] = None
    periode: Optional[str] = None
    utilisateurs_actifs: Optional[int] = None
    utilisateurs_seats: Optional[int] = None
    taux_adoption_pct: Optional[float] = None
    score_sante: Optional[float] = None
    is_active: Optional[bool] = None


class UsageAnalyticsOut(BaseModel):
    id: int
    company_id: int
    reference: str
    tenant_id: Optional[int] = None
    periode: Optional[str] = None
    utilisateurs_actifs: Optional[int] = None
    utilisateurs_seats: Optional[int] = None
    taux_adoption_pct: Optional[float] = None
    score_sante: Optional[float] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class UptimeRecordCreate(BaseModel):
    reference: str
    service: Optional[str] = None
    region: Optional[str] = None
    statut: Optional[str] = None
    latence_ms: Optional[int] = None
    disponibilite_pct: Optional[float] = None
    date_mesure: Optional[datetime] = None


class UptimeRecordUpdate(BaseModel):
    reference: Optional[str] = None
    service: Optional[str] = None
    region: Optional[str] = None
    statut: Optional[str] = None
    latence_ms: Optional[int] = None
    disponibilite_pct: Optional[float] = None
    date_mesure: Optional[datetime] = None
    is_active: Optional[bool] = None


class UptimeRecordOut(BaseModel):
    id: int
    company_id: int
    reference: str
    service: Optional[str] = None
    region: Optional[str] = None
    statut: Optional[str] = None
    latence_ms: Optional[int] = None
    disponibilite_pct: Optional[float] = None
    date_mesure: Optional[datetime] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}

