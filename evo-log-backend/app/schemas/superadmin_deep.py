"""Schemas Pydantic pour superadmin-cadc (genere)."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date


class PlatformAuditCreate(BaseModel):
    reference: str
    periode_debut: Optional[date] = None
    periode_fin: Optional[date] = None
    nb_tenants_audites: Optional[int] = None
    constats: Optional[str] = None
    recommandations: Optional[str] = None
    statut: Optional[str] = None


class PlatformAuditUpdate(BaseModel):
    reference: Optional[str] = None
    periode_debut: Optional[date] = None
    periode_fin: Optional[date] = None
    nb_tenants_audites: Optional[int] = None
    constats: Optional[str] = None
    recommandations: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class PlatformAuditOut(BaseModel):
    id: int
    company_id: int
    reference: str
    periode_debut: Optional[date] = None
    periode_fin: Optional[date] = None
    nb_tenants_audites: Optional[int] = None
    constats: Optional[str] = None
    recommandations: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class ComplianceDashboardCreate(BaseModel):
    reference: str
    domaine: Optional[str] = None
    nb_tenants_conformes: Optional[int] = None
    nb_tenants_hors: Optional[int] = None
    score_global_pct: Optional[float] = None
    date_revue: Optional[date] = None


class ComplianceDashboardUpdate(BaseModel):
    reference: Optional[str] = None
    domaine: Optional[str] = None
    nb_tenants_conformes: Optional[int] = None
    nb_tenants_hors: Optional[int] = None
    score_global_pct: Optional[float] = None
    date_revue: Optional[date] = None
    is_active: Optional[bool] = None


class ComplianceDashboardOut(BaseModel):
    id: int
    company_id: int
    reference: str
    domaine: Optional[str] = None
    nb_tenants_conformes: Optional[int] = None
    nb_tenants_hors: Optional[int] = None
    score_global_pct: Optional[float] = None
    date_revue: Optional[date] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class RetentionPolicyCreate(BaseModel):
    reference: str
    categorie: Optional[str] = None
    duree_conservation_jours: Optional[int] = None
    methode_purge: Optional[str] = None
    base_legale: Optional[str] = None
    actif: Optional[bool] = None


class RetentionPolicyUpdate(BaseModel):
    reference: Optional[str] = None
    categorie: Optional[str] = None
    duree_conservation_jours: Optional[int] = None
    methode_purge: Optional[str] = None
    base_legale: Optional[str] = None
    actif: Optional[bool] = None
    is_active: Optional[bool] = None


class RetentionPolicyOut(BaseModel):
    id: int
    company_id: int
    reference: str
    categorie: Optional[str] = None
    duree_conservation_jours: Optional[int] = None
    methode_purge: Optional[str] = None
    base_legale: Optional[str] = None
    actif: Optional[bool] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class PlatformIncidentCreate(BaseModel):
    reference: str
    titre: Optional[str] = None
    priorite: Optional[str] = None
    date_debut: Optional[datetime] = None
    date_resolution: Optional[datetime] = None
    impact_tenants: Optional[str] = None
    cause_racine: Optional[str] = None
    statut: Optional[str] = None


class PlatformIncidentUpdate(BaseModel):
    reference: Optional[str] = None
    titre: Optional[str] = None
    priorite: Optional[str] = None
    date_debut: Optional[datetime] = None
    date_resolution: Optional[datetime] = None
    impact_tenants: Optional[str] = None
    cause_racine: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class PlatformIncidentOut(BaseModel):
    id: int
    company_id: int
    reference: str
    titre: Optional[str] = None
    priorite: Optional[str] = None
    date_debut: Optional[datetime] = None
    date_resolution: Optional[datetime] = None
    impact_tenants: Optional[str] = None
    cause_racine: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class AccessReviewCreate(BaseModel):
    reference: str
    tenant_id: Optional[int] = None
    date_revue: Optional[date] = None
    nb_utilisateurs_revus: Optional[int] = None
    nb_droits_retires: Optional[int] = None
    revue_par: Optional[str] = None
    statut: Optional[str] = None


class AccessReviewUpdate(BaseModel):
    reference: Optional[str] = None
    tenant_id: Optional[int] = None
    date_revue: Optional[date] = None
    nb_utilisateurs_revus: Optional[int] = None
    nb_droits_retires: Optional[int] = None
    revue_par: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class AccessReviewOut(BaseModel):
    id: int
    company_id: int
    reference: str
    tenant_id: Optional[int] = None
    date_revue: Optional[date] = None
    nb_utilisateurs_revus: Optional[int] = None
    nb_droits_retires: Optional[int] = None
    revue_par: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class SoftwareLicenseCreate(BaseModel):
    reference: str
    module: Optional[str] = None
    editeur: Optional[str] = None
    nb_sieges: Optional[int] = None
    date_debut: Optional[date] = None
    date_fin: Optional[date] = None
    cotisation_xaf: Optional[float] = None
    statut: Optional[str] = None


class SoftwareLicenseUpdate(BaseModel):
    reference: Optional[str] = None
    module: Optional[str] = None
    editeur: Optional[str] = None
    nb_sieges: Optional[int] = None
    date_debut: Optional[date] = None
    date_fin: Optional[date] = None
    cotisation_xaf: Optional[float] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class SoftwareLicenseOut(BaseModel):
    id: int
    company_id: int
    reference: str
    module: Optional[str] = None
    editeur: Optional[str] = None
    nb_sieges: Optional[int] = None
    date_debut: Optional[date] = None
    date_fin: Optional[date] = None
    cotisation_xaf: Optional[float] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class TechnologyPartnerCreate(BaseModel):
    reference: str
    nom: Optional[str] = None
    type_partenaire: Optional[str] = None
    produit_associe: Optional[str] = None
    contrat: Optional[str] = None
    date_debut: Optional[date] = None
    statut: Optional[str] = None


class TechnologyPartnerUpdate(BaseModel):
    reference: Optional[str] = None
    nom: Optional[str] = None
    type_partenaire: Optional[str] = None
    produit_associe: Optional[str] = None
    contrat: Optional[str] = None
    date_debut: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class TechnologyPartnerOut(BaseModel):
    id: int
    company_id: int
    reference: str
    nom: Optional[str] = None
    type_partenaire: Optional[str] = None
    produit_associe: Optional[str] = None
    contrat: Optional[str] = None
    date_debut: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class SaasRevenueRecordCreate(BaseModel):
    reference: str
    mois: Optional[str] = None
    mrr_xaf: Optional[float] = None
    churn_mrr_xaf: Optional[float] = None
    expansion_mrr_xaf: Optional[float] = None
    arpu_xaf: Optional[float] = None
    nb_customers: Optional[int] = None


class SaasRevenueRecordUpdate(BaseModel):
    reference: Optional[str] = None
    mois: Optional[str] = None
    mrr_xaf: Optional[float] = None
    churn_mrr_xaf: Optional[float] = None
    expansion_mrr_xaf: Optional[float] = None
    arpu_xaf: Optional[float] = None
    nb_customers: Optional[int] = None
    is_active: Optional[bool] = None


class SaasRevenueRecordOut(BaseModel):
    id: int
    company_id: int
    reference: str
    mois: Optional[str] = None
    mrr_xaf: Optional[float] = None
    churn_mrr_xaf: Optional[float] = None
    expansion_mrr_xaf: Optional[float] = None
    arpu_xaf: Optional[float] = None
    nb_customers: Optional[int] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class GlobalConfigSettingCreate(BaseModel):
    code_setting: str
    valeur: Optional[str] = None
    categorie: Optional[str] = None
    description: Optional[str] = None
    modifie_par: Optional[str] = None
    date_modif: Optional[datetime] = None
    statut: Optional[str] = None


class GlobalConfigSettingUpdate(BaseModel):
    code_setting: Optional[str] = None
    valeur: Optional[str] = None
    categorie: Optional[str] = None
    description: Optional[str] = None
    modifie_par: Optional[str] = None
    date_modif: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class GlobalConfigSettingOut(BaseModel):
    id: int
    company_id: int
    code_setting: str
    valeur: Optional[str] = None
    categorie: Optional[str] = None
    description: Optional[str] = None
    modifie_par: Optional[str] = None
    date_modif: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class DrPlanCreate(BaseModel):
    reference: str
    scenario: Optional[str] = None
    rto_heures: Optional[float] = None
    rpo_minutes: Optional[float] = None
    solution_secours: Optional[str] = None
    date_dernier_test: Optional[date] = None
    resultat_test: Optional[str] = None


class DrPlanUpdate(BaseModel):
    reference: Optional[str] = None
    scenario: Optional[str] = None
    rto_heures: Optional[float] = None
    rpo_minutes: Optional[float] = None
    solution_secours: Optional[str] = None
    date_dernier_test: Optional[date] = None
    resultat_test: Optional[str] = None
    is_active: Optional[bool] = None


class DrPlanOut(BaseModel):
    id: int
    company_id: int
    reference: str
    scenario: Optional[str] = None
    rto_heures: Optional[float] = None
    rpo_minutes: Optional[float] = None
    solution_secours: Optional[str] = None
    date_dernier_test: Optional[date] = None
    resultat_test: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}

