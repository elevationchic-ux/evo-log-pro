"""Schemas Pydantic pour dashboard (genere)."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date


class ModuleHealthCreate(BaseModel):
    code_module: str
    etat: Optional[str] = None
    nombre_requetes_jour: Optional[int] = None
    taux_erreur_pct: Optional[float] = None
    latence_p95_ms: Optional[int] = None
    dernier_incident: Optional[datetime] = None


class ModuleHealthUpdate(BaseModel):
    code_module: Optional[str] = None
    etat: Optional[str] = None
    nombre_requetes_jour: Optional[int] = None
    taux_erreur_pct: Optional[float] = None
    latence_p95_ms: Optional[int] = None
    dernier_incident: Optional[datetime] = None
    is_active: Optional[bool] = None


class ModuleHealthOut(BaseModel):
    id: int
    company_id: int
    code_module: str
    etat: Optional[str] = None
    nombre_requetes_jour: Optional[int] = None
    taux_erreur_pct: Optional[float] = None
    latence_p95_ms: Optional[int] = None
    dernier_incident: Optional[datetime] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class ActivityRecordCreate(BaseModel):
    reference: str
    module_source: Optional[str] = None
    type_action: Optional[str] = None
    utilisateur: Optional[str] = None
    entite: Optional[str] = None
    horodatage: Optional[datetime] = None
    resume: Optional[str] = None


class ActivityRecordUpdate(BaseModel):
    reference: Optional[str] = None
    module_source: Optional[str] = None
    type_action: Optional[str] = None
    utilisateur: Optional[str] = None
    entite: Optional[str] = None
    horodatage: Optional[datetime] = None
    resume: Optional[str] = None
    is_active: Optional[bool] = None


class ActivityRecordOut(BaseModel):
    id: int
    company_id: int
    reference: str
    module_source: Optional[str] = None
    type_action: Optional[str] = None
    utilisateur: Optional[str] = None
    entite: Optional[str] = None
    horodatage: Optional[datetime] = None
    resume: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class UnifiedTaskCreate(BaseModel):
    reference: str
    titre: Optional[str] = None
    module_source: Optional[str] = None
    entite_id: Optional[int] = None
    assigne_a: Optional[int] = None
    date_echeance: Optional[datetime] = None
    priorite: Optional[str] = None
    statut: Optional[str] = None


class UnifiedTaskUpdate(BaseModel):
    reference: Optional[str] = None
    titre: Optional[str] = None
    module_source: Optional[str] = None
    entite_id: Optional[int] = None
    assigne_a: Optional[int] = None
    date_echeance: Optional[datetime] = None
    priorite: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class UnifiedTaskOut(BaseModel):
    id: int
    company_id: int
    reference: str
    titre: Optional[str] = None
    module_source: Optional[str] = None
    entite_id: Optional[int] = None
    assigne_a: Optional[int] = None
    date_echeance: Optional[datetime] = None
    priorite: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class QuickActionCreate(BaseModel):
    reference: str
    libelle: Optional[str] = None
    module_source: Optional[str] = None
    url_action: Optional[str] = None
    utilisateur_id: Optional[int] = None
    ordre: Optional[int] = None
    actif: Optional[bool] = None


class QuickActionUpdate(BaseModel):
    reference: Optional[str] = None
    libelle: Optional[str] = None
    module_source: Optional[str] = None
    url_action: Optional[str] = None
    utilisateur_id: Optional[int] = None
    ordre: Optional[int] = None
    actif: Optional[bool] = None
    is_active: Optional[bool] = None


class QuickActionOut(BaseModel):
    id: int
    company_id: int
    reference: str
    libelle: Optional[str] = None
    module_source: Optional[str] = None
    url_action: Optional[str] = None
    utilisateur_id: Optional[int] = None
    ordre: Optional[int] = None
    actif: Optional[bool] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class TeamPerformanceCreate(BaseModel):
    reference: str
    equipe: Optional[str] = None
    periode: Optional[str] = None
    objectifs_atteints_pct: Optional[float] = None
    volume_traite: Optional[float] = None
    qualite_score: Optional[float] = None


class TeamPerformanceUpdate(BaseModel):
    reference: Optional[str] = None
    equipe: Optional[str] = None
    periode: Optional[str] = None
    objectifs_atteints_pct: Optional[float] = None
    volume_traite: Optional[float] = None
    qualite_score: Optional[float] = None
    is_active: Optional[bool] = None


class TeamPerformanceOut(BaseModel):
    id: int
    company_id: int
    reference: str
    equipe: Optional[str] = None
    periode: Optional[str] = None
    objectifs_atteints_pct: Optional[float] = None
    volume_traite: Optional[float] = None
    qualite_score: Optional[float] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class FinancialSummaryCreate(BaseModel):
    reference: str
    periode: Optional[str] = None
    ca_consolide_xaf: Optional[float] = None
    marge_brute_xaf: Optional[float] = None
    ebitda_xaf: Optional[float] = None
    bfr_xaf: Optional[float] = None
    tresorerie_xaf: Optional[float] = None


class FinancialSummaryUpdate(BaseModel):
    reference: Optional[str] = None
    periode: Optional[str] = None
    ca_consolide_xaf: Optional[float] = None
    marge_brute_xaf: Optional[float] = None
    ebitda_xaf: Optional[float] = None
    bfr_xaf: Optional[float] = None
    tresorerie_xaf: Optional[float] = None
    is_active: Optional[bool] = None


class FinancialSummaryOut(BaseModel):
    id: int
    company_id: int
    reference: str
    periode: Optional[str] = None
    ca_consolide_xaf: Optional[float] = None
    marge_brute_xaf: Optional[float] = None
    ebitda_xaf: Optional[float] = None
    bfr_xaf: Optional[float] = None
    tresorerie_xaf: Optional[float] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class OperationalAlertCreate(BaseModel):
    reference: str
    module_source: Optional[str] = None
    niveau: Optional[str] = None
    description: Optional[str] = None
    date_alerte: Optional[datetime] = None
    destinataire: Optional[str] = None
    statut: Optional[str] = None


class OperationalAlertUpdate(BaseModel):
    reference: Optional[str] = None
    module_source: Optional[str] = None
    niveau: Optional[str] = None
    description: Optional[str] = None
    date_alerte: Optional[datetime] = None
    destinataire: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class OperationalAlertOut(BaseModel):
    id: int
    company_id: int
    reference: str
    module_source: Optional[str] = None
    niveau: Optional[str] = None
    description: Optional[str] = None
    date_alerte: Optional[datetime] = None
    destinataire: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class RecentDocumentCreate(BaseModel):
    reference: str
    titre: Optional[str] = None
    module_source: Optional[str] = None
    entite_id: Optional[int] = None
    url: Optional[str] = None
    date_creation: Optional[datetime] = None
    partage: Optional[str] = None


class RecentDocumentUpdate(BaseModel):
    reference: Optional[str] = None
    titre: Optional[str] = None
    module_source: Optional[str] = None
    entite_id: Optional[int] = None
    url: Optional[str] = None
    date_creation: Optional[datetime] = None
    partage: Optional[str] = None
    is_active: Optional[bool] = None


class RecentDocumentOut(BaseModel):
    id: int
    company_id: int
    reference: str
    titre: Optional[str] = None
    module_source: Optional[str] = None
    entite_id: Optional[int] = None
    url: Optional[str] = None
    date_creation: Optional[datetime] = None
    partage: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class UnifiedAgendaCreate(BaseModel):
    reference: str
    titre: Optional[str] = None
    module_source: Optional[str] = None
    entite_id: Optional[int] = None
    date_debut: Optional[datetime] = None
    date_fin: Optional[datetime] = None
    invite_par: Optional[str] = None


class UnifiedAgendaUpdate(BaseModel):
    reference: Optional[str] = None
    titre: Optional[str] = None
    module_source: Optional[str] = None
    entite_id: Optional[int] = None
    date_debut: Optional[datetime] = None
    date_fin: Optional[datetime] = None
    invite_par: Optional[str] = None
    is_active: Optional[bool] = None


class UnifiedAgendaOut(BaseModel):
    id: int
    company_id: int
    reference: str
    titre: Optional[str] = None
    module_source: Optional[str] = None
    entite_id: Optional[int] = None
    date_debut: Optional[datetime] = None
    date_fin: Optional[datetime] = None
    invite_par: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class IntegrationStatusCreate(BaseModel):
    reference: str
    nom_integration: Optional[str] = None
    url_testee: Optional[str] = None
    date_dernier_test: Optional[datetime] = None
    succes: Optional[bool] = None
    latence_ms: Optional[int] = None
    message_erreur: Optional[str] = None


class IntegrationStatusUpdate(BaseModel):
    reference: Optional[str] = None
    nom_integration: Optional[str] = None
    url_testee: Optional[str] = None
    date_dernier_test: Optional[datetime] = None
    succes: Optional[bool] = None
    latence_ms: Optional[int] = None
    message_erreur: Optional[str] = None
    is_active: Optional[bool] = None


class IntegrationStatusOut(BaseModel):
    id: int
    company_id: int
    reference: str
    nom_integration: Optional[str] = None
    url_testee: Optional[str] = None
    date_dernier_test: Optional[datetime] = None
    succes: Optional[bool] = None
    latence_ms: Optional[int] = None
    message_erreur: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}

