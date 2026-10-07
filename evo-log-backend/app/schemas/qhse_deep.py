"""Schemas Pydantic pour qhse-securite (genere)."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date


class EnvironmentalMeasurementCreate(BaseModel):
    reference: str
    type_relevé: Optional[str] = None
    polluant: Optional[str] = None
    valeur: Optional[float] = None
    unite: Optional[str] = None
    norme_max: Optional[float] = None
    station: Optional[str] = None
    date_relevé: Optional[datetime] = None
    conformite: Optional[str] = None


class EnvironmentalMeasurementUpdate(BaseModel):
    reference: Optional[str] = None
    type_relevé: Optional[str] = None
    polluant: Optional[str] = None
    valeur: Optional[float] = None
    unite: Optional[str] = None
    norme_max: Optional[float] = None
    station: Optional[str] = None
    date_relevé: Optional[datetime] = None
    conformite: Optional[str] = None
    is_active: Optional[bool] = None


class EnvironmentalMeasurementOut(BaseModel):
    id: int
    company_id: int
    reference: str
    type_relevé: Optional[str] = None
    polluant: Optional[str] = None
    valeur: Optional[float] = None
    unite: Optional[str] = None
    norme_max: Optional[float] = None
    station: Optional[str] = None
    date_relevé: Optional[datetime] = None
    conformite: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class WasteRecordCreate(BaseModel):
    numero_bsd: str
    type_dechet: Optional[str] = None
    quantite_kg: Optional[float] = None
    date_production: Optional[date] = None
    transporteur: Optional[str] = None
    destination: Optional[str] = None
    statut: Optional[str] = None


class WasteRecordUpdate(BaseModel):
    numero_bsd: Optional[str] = None
    type_dechet: Optional[str] = None
    quantite_kg: Optional[float] = None
    date_production: Optional[date] = None
    transporteur: Optional[str] = None
    destination: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class WasteRecordOut(BaseModel):
    id: int
    company_id: int
    numero_bsd: str
    type_dechet: Optional[str] = None
    quantite_kg: Optional[float] = None
    date_production: Optional[date] = None
    transporteur: Optional[str] = None
    destination: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class SafetyDataSheetCreate(BaseModel):
    reference: str
    nom_produit: Optional[str] = None
    numero_ce: Optional[str] = None
    fournisseur: Optional[str] = None
    phrase_risque: Optional[str] = None
    version_fds: Optional[str] = None
    date_revision: Optional[date] = None
    classification: Optional[str] = None


class SafetyDataSheetUpdate(BaseModel):
    reference: Optional[str] = None
    nom_produit: Optional[str] = None
    numero_ce: Optional[str] = None
    fournisseur: Optional[str] = None
    phrase_risque: Optional[str] = None
    version_fds: Optional[str] = None
    date_revision: Optional[date] = None
    classification: Optional[str] = None
    is_active: Optional[bool] = None


class SafetyDataSheetOut(BaseModel):
    id: int
    company_id: int
    reference: str
    nom_produit: Optional[str] = None
    numero_ce: Optional[str] = None
    fournisseur: Optional[str] = None
    phrase_risque: Optional[str] = None
    version_fds: Optional[str] = None
    date_revision: Optional[date] = None
    classification: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class EmergencyPlanCreate(BaseModel):
    reference: str
    type_plan: Optional[str] = None
    zone_concernee: Optional[str] = None
    date_elaboration: Optional[date] = None
    date_dernier_exercice: Optional[date] = None
    frequence_exercice_mois: Optional[int] = None


class EmergencyPlanUpdate(BaseModel):
    reference: Optional[str] = None
    type_plan: Optional[str] = None
    zone_concernee: Optional[str] = None
    date_elaboration: Optional[date] = None
    date_dernier_exercice: Optional[date] = None
    frequence_exercice_mois: Optional[int] = None
    is_active: Optional[bool] = None


class EmergencyPlanOut(BaseModel):
    id: int
    company_id: int
    reference: str
    type_plan: Optional[str] = None
    zone_concernee: Optional[str] = None
    date_elaboration: Optional[date] = None
    date_dernier_exercice: Optional[date] = None
    frequence_exercice_mois: Optional[int] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class PpeItemCreate(BaseModel):
    reference: str
    employe_id: Optional[int] = None
    type_epi: Optional[str] = None
    taille: Optional[str] = None
    date_attribution: Optional[date] = None
    date_expiration: Optional[date] = None
    quantite: Optional[int] = None
    statut: Optional[str] = None


class PpeItemUpdate(BaseModel):
    reference: Optional[str] = None
    employe_id: Optional[int] = None
    type_epi: Optional[str] = None
    taille: Optional[str] = None
    date_attribution: Optional[date] = None
    date_expiration: Optional[date] = None
    quantite: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class PpeItemOut(BaseModel):
    id: int
    company_id: int
    reference: str
    employe_id: Optional[int] = None
    type_epi: Optional[str] = None
    taille: Optional[str] = None
    date_attribution: Optional[date] = None
    date_expiration: Optional[date] = None
    quantite: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class HealthVisitCreate(BaseModel):
    reference: str
    employe_id: Optional[int] = None
    type_visite: Optional[str] = None
    date_visite: Optional[date] = None
    medecin: Optional[str] = None
    resultat: Optional[str] = None
    prochaine_visite: Optional[date] = None


class HealthVisitUpdate(BaseModel):
    reference: Optional[str] = None
    employe_id: Optional[int] = None
    type_visite: Optional[str] = None
    date_visite: Optional[date] = None
    medecin: Optional[str] = None
    resultat: Optional[str] = None
    prochaine_visite: Optional[date] = None
    is_active: Optional[bool] = None


class HealthVisitOut(BaseModel):
    id: int
    company_id: int
    reference: str
    employe_id: Optional[int] = None
    type_visite: Optional[str] = None
    date_visite: Optional[date] = None
    medecin: Optional[str] = None
    resultat: Optional[str] = None
    prochaine_visite: Optional[date] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class RiskAssessmentCreate(BaseModel):
    reference: str
    unite_travail: Optional[str] = None
    description_risque: Optional[str] = None
    cotation: Optional[str] = None
    mesure_prevention: Optional[str] = None
    date_evaluation: Optional[date] = None
    responsable: Optional[str] = None


class RiskAssessmentUpdate(BaseModel):
    reference: Optional[str] = None
    unite_travail: Optional[str] = None
    description_risque: Optional[str] = None
    cotation: Optional[str] = None
    mesure_prevention: Optional[str] = None
    date_evaluation: Optional[date] = None
    responsable: Optional[str] = None
    is_active: Optional[bool] = None


class RiskAssessmentOut(BaseModel):
    id: int
    company_id: int
    reference: str
    unite_travail: Optional[str] = None
    description_risque: Optional[str] = None
    cotation: Optional[str] = None
    mesure_prevention: Optional[str] = None
    date_evaluation: Optional[date] = None
    responsable: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class CorrectiveActionCreate(BaseModel):
    reference: str
    source_ecart: Optional[str] = None
    description_probleme: Optional[str] = None
    cause_racine: Optional[str] = None
    action_corrective: Optional[str] = None
    responsable: Optional[str] = None
    date_prevue_cloture: Optional[date] = None
    statut: Optional[str] = None


class CorrectiveActionUpdate(BaseModel):
    reference: Optional[str] = None
    source_ecart: Optional[str] = None
    description_probleme: Optional[str] = None
    cause_racine: Optional[str] = None
    action_corrective: Optional[str] = None
    responsable: Optional[str] = None
    date_prevue_cloture: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class CorrectiveActionOut(BaseModel):
    id: int
    company_id: int
    reference: str
    source_ecart: Optional[str] = None
    description_probleme: Optional[str] = None
    cause_racine: Optional[str] = None
    action_corrective: Optional[str] = None
    responsable: Optional[str] = None
    date_prevue_cloture: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class ManagementReviewCreate(BaseModel):
    reference: str
    date_revue: Optional[date] = None
    participants: Optional[str] = None
    sujets: Optional[str] = None
    decisions: Optional[str] = None
    statut: Optional[str] = None


class ManagementReviewUpdate(BaseModel):
    reference: Optional[str] = None
    date_revue: Optional[date] = None
    participants: Optional[str] = None
    sujets: Optional[str] = None
    decisions: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class ManagementReviewOut(BaseModel):
    id: int
    company_id: int
    reference: str
    date_revue: Optional[date] = None
    participants: Optional[str] = None
    sujets: Optional[str] = None
    decisions: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class ComplianceRecordCreate(BaseModel):
    reference: str
    regulation: Optional[str] = None
    domaine: Optional[str] = None
    obligation: Optional[str] = None
    preuve: Optional[str] = None
    date_constat: Optional[date] = None
    prochaine_echeance: Optional[date] = None
    statut: Optional[str] = None


class ComplianceRecordUpdate(BaseModel):
    reference: Optional[str] = None
    regulation: Optional[str] = None
    domaine: Optional[str] = None
    obligation: Optional[str] = None
    preuve: Optional[str] = None
    date_constat: Optional[date] = None
    prochaine_echeance: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class ComplianceRecordOut(BaseModel):
    id: int
    company_id: int
    reference: str
    regulation: Optional[str] = None
    domaine: Optional[str] = None
    obligation: Optional[str] = None
    preuve: Optional[str] = None
    date_constat: Optional[date] = None
    prochaine_echeance: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class QualityAuditCreate(BaseModel):
    reference: str
    type_audit: Optional[str] = None
    perimetre: Optional[str] = None
    auditeur: Optional[str] = None
    date_debut: Optional[date] = None
    date_fin: Optional[date] = None
    nb_ecarts: Optional[int] = None
    statut: Optional[str] = None


class QualityAuditUpdate(BaseModel):
    reference: Optional[str] = None
    type_audit: Optional[str] = None
    perimetre: Optional[str] = None
    auditeur: Optional[str] = None
    date_debut: Optional[date] = None
    date_fin: Optional[date] = None
    nb_ecarts: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class QualityAuditOut(BaseModel):
    id: int
    company_id: int
    reference: str
    type_audit: Optional[str] = None
    perimetre: Optional[str] = None
    auditeur: Optional[str] = None
    date_debut: Optional[date] = None
    date_fin: Optional[date] = None
    nb_ecarts: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}

