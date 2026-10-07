"""Schemas Pydantic pour portail-collaborateur (genere)."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date


class CollAssignmentCreate(BaseModel):
    reference: str
    collaborateur: Optional[str] = None
    mission: Optional[str] = None
    site: Optional[str] = None
    debut: Optional[date] = None
    statut: Optional[str] = None


class CollAssignmentUpdate(BaseModel):
    reference: Optional[str] = None
    collaborateur: Optional[str] = None
    mission: Optional[str] = None
    site: Optional[str] = None
    debut: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class CollAssignmentOut(BaseModel):
    id: int
    company_id: int
    reference: str
    collaborateur: Optional[str] = None
    mission: Optional[str] = None
    site: Optional[str] = None
    debut: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class CollActivityLogCreate(BaseModel):
    reference: str
    collaborateur: Optional[str] = None
    date: Optional[date] = None
    heures: Optional[float] = None
    activite: Optional[str] = None
    statut: Optional[str] = None


class CollActivityLogUpdate(BaseModel):
    reference: Optional[str] = None
    collaborateur: Optional[str] = None
    date: Optional[date] = None
    heures: Optional[float] = None
    activite: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class CollActivityLogOut(BaseModel):
    id: int
    company_id: int
    reference: str
    collaborateur: Optional[str] = None
    date: Optional[date] = None
    heures: Optional[float] = None
    activite: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class CollDeliverableCreate(BaseModel):
    reference: str
    collaborateur: Optional[str] = None
    livrable: Optional[str] = None
    mission: Optional[str] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None


class CollDeliverableUpdate(BaseModel):
    reference: Optional[str] = None
    collaborateur: Optional[str] = None
    livrable: Optional[str] = None
    mission: Optional[str] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class CollDeliverableOut(BaseModel):
    id: int
    company_id: int
    reference: str
    collaborateur: Optional[str] = None
    livrable: Optional[str] = None
    mission: Optional[str] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class CollTimesheetCreate(BaseModel):
    reference: str
    collaborateur: Optional[str] = None
    mission: Optional[str] = None
    heures: Optional[float] = None
    semaine: Optional[str] = None
    statut: Optional[str] = None


class CollTimesheetUpdate(BaseModel):
    reference: Optional[str] = None
    collaborateur: Optional[str] = None
    mission: Optional[str] = None
    heures: Optional[float] = None
    semaine: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class CollTimesheetOut(BaseModel):
    id: int
    company_id: int
    reference: str
    collaborateur: Optional[str] = None
    mission: Optional[str] = None
    heures: Optional[float] = None
    semaine: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class CollSiteAccessLogCreate(BaseModel):
    reference: str
    collaborateur: Optional[str] = None
    site: Optional[str] = None
    entree: Optional[datetime] = None
    sortie: Optional[datetime] = None
    statut: Optional[str] = None


class CollSiteAccessLogUpdate(BaseModel):
    reference: Optional[str] = None
    collaborateur: Optional[str] = None
    site: Optional[str] = None
    entree: Optional[datetime] = None
    sortie: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class CollSiteAccessLogOut(BaseModel):
    id: int
    company_id: int
    reference: str
    collaborateur: Optional[str] = None
    site: Optional[str] = None
    entree: Optional[datetime] = None
    sortie: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class CollWorkInstructionReceiptCreate(BaseModel):
    reference: str
    collaborateur: Optional[str] = None
    consigne: Optional[str] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None


class CollWorkInstructionReceiptUpdate(BaseModel):
    reference: Optional[str] = None
    collaborateur: Optional[str] = None
    consigne: Optional[str] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class CollWorkInstructionReceiptOut(BaseModel):
    id: int
    company_id: int
    reference: str
    collaborateur: Optional[str] = None
    consigne: Optional[str] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class CollIncidentReportCreate(BaseModel):
    reference: str
    collaborateur: Optional[str] = None
    lieu: Optional[str] = None
    description: Optional[str] = None
    gravite: Optional[str] = None
    statut: Optional[str] = None


class CollIncidentReportUpdate(BaseModel):
    reference: Optional[str] = None
    collaborateur: Optional[str] = None
    lieu: Optional[str] = None
    description: Optional[str] = None
    gravite: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class CollIncidentReportOut(BaseModel):
    id: int
    company_id: int
    reference: str
    collaborateur: Optional[str] = None
    lieu: Optional[str] = None
    description: Optional[str] = None
    gravite: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class CollQualityCheckCreate(BaseModel):
    reference: str
    collaborateur: Optional[str] = None
    controle: Optional[str] = None
    point_testes: Optional[int] = None
    anomalies: Optional[int] = None
    statut: Optional[str] = None


class CollQualityCheckUpdate(BaseModel):
    reference: Optional[str] = None
    collaborateur: Optional[str] = None
    controle: Optional[str] = None
    point_testes: Optional[int] = None
    anomalies: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class CollQualityCheckOut(BaseModel):
    id: int
    company_id: int
    reference: str
    collaborateur: Optional[str] = None
    controle: Optional[str] = None
    point_testes: Optional[int] = None
    anomalies: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class CollTrainingCompletionCreate(BaseModel):
    reference: str
    collaborateur: Optional[str] = None
    formation: Optional[str] = None
    date: Optional[date] = None
    score: Optional[int] = None
    statut: Optional[str] = None


class CollTrainingCompletionUpdate(BaseModel):
    reference: Optional[str] = None
    collaborateur: Optional[str] = None
    formation: Optional[str] = None
    date: Optional[date] = None
    score: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class CollTrainingCompletionOut(BaseModel):
    id: int
    company_id: int
    reference: str
    collaborateur: Optional[str] = None
    formation: Optional[str] = None
    date: Optional[date] = None
    score: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class CollEquipmentIssueCreate(BaseModel):
    reference: str
    collaborateur: Optional[str] = None
    equipement: Optional[str] = None
    probleme: Optional[str] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None


class CollEquipmentIssueUpdate(BaseModel):
    reference: Optional[str] = None
    collaborateur: Optional[str] = None
    equipement: Optional[str] = None
    probleme: Optional[str] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class CollEquipmentIssueOut(BaseModel):
    id: int
    company_id: int
    reference: str
    collaborateur: Optional[str] = None
    equipement: Optional[str] = None
    probleme: Optional[str] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class CollShiftAttendanceCreate(BaseModel):
    reference: str
    collaborateur: Optional[str] = None
    poste: Optional[str] = None
    date: Optional[date] = None
    arrivee: Optional[datetime] = None
    statut: Optional[str] = None


class CollShiftAttendanceUpdate(BaseModel):
    reference: Optional[str] = None
    collaborateur: Optional[str] = None
    poste: Optional[str] = None
    date: Optional[date] = None
    arrivee: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class CollShiftAttendanceOut(BaseModel):
    id: int
    company_id: int
    reference: str
    collaborateur: Optional[str] = None
    poste: Optional[str] = None
    date: Optional[date] = None
    arrivee: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class CollTravelOrderCreate(BaseModel):
    reference: str
    collaborateur: Optional[str] = None
    destination: Optional[str] = None
    debut: Optional[date] = None
    fin: Optional[date] = None
    statut: Optional[str] = None


class CollTravelOrderUpdate(BaseModel):
    reference: Optional[str] = None
    collaborateur: Optional[str] = None
    destination: Optional[str] = None
    debut: Optional[date] = None
    fin: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class CollTravelOrderOut(BaseModel):
    id: int
    company_id: int
    reference: str
    collaborateur: Optional[str] = None
    destination: Optional[str] = None
    debut: Optional[date] = None
    fin: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class CollExpenseDeclarationCreate(BaseModel):
    reference: str
    collaborateur: Optional[str] = None
    mission: Optional[str] = None
    montant: Optional[float] = None
    date: Optional[date] = None
    statut: Optional[str] = None


class CollExpenseDeclarationUpdate(BaseModel):
    reference: Optional[str] = None
    collaborateur: Optional[str] = None
    mission: Optional[str] = None
    montant: Optional[float] = None
    date: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class CollExpenseDeclarationOut(BaseModel):
    id: int
    company_id: int
    reference: str
    collaborateur: Optional[str] = None
    mission: Optional[str] = None
    montant: Optional[float] = None
    date: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class CollCertificationUploadCreate(BaseModel):
    reference: str
    collaborateur: Optional[str] = None
    certification: Optional[str] = None
    expire_le: Optional[date] = None
    statut: Optional[str] = None


class CollCertificationUploadUpdate(BaseModel):
    reference: Optional[str] = None
    collaborateur: Optional[str] = None
    certification: Optional[str] = None
    expire_le: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class CollCertificationUploadOut(BaseModel):
    id: int
    company_id: int
    reference: str
    collaborateur: Optional[str] = None
    certification: Optional[str] = None
    expire_le: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class CollTaskCompletionCreate(BaseModel):
    reference: str
    collaborateur: Optional[str] = None
    tache: Optional[str] = None
    acheve_le: Optional[datetime] = None
    statut: Optional[str] = None


class CollTaskCompletionUpdate(BaseModel):
    reference: Optional[str] = None
    collaborateur: Optional[str] = None
    tache: Optional[str] = None
    acheve_le: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class CollTaskCompletionOut(BaseModel):
    id: int
    company_id: int
    reference: str
    collaborateur: Optional[str] = None
    tache: Optional[str] = None
    acheve_le: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class CollFeedbackCreate(BaseModel):
    reference: str
    collaborateur: Optional[str] = None
    sujet: Optional[str] = None
    contenu: Optional[str] = None
    date: Optional[date] = None
    statut: Optional[str] = None


class CollFeedbackUpdate(BaseModel):
    reference: Optional[str] = None
    collaborateur: Optional[str] = None
    sujet: Optional[str] = None
    contenu: Optional[str] = None
    date: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class CollFeedbackOut(BaseModel):
    id: int
    company_id: int
    reference: str
    collaborateur: Optional[str] = None
    sujet: Optional[str] = None
    contenu: Optional[str] = None
    date: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class CollAvailabilityCreate(BaseModel):
    reference: str
    collaborateur: Optional[str] = None
    periode: Optional[str] = None
    statut: Optional[str] = None


class CollAvailabilityUpdate(BaseModel):
    reference: Optional[str] = None
    collaborateur: Optional[str] = None
    periode: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class CollAvailabilityOut(BaseModel):
    id: int
    company_id: int
    reference: str
    collaborateur: Optional[str] = None
    periode: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class CollContractRenewalRequestCreate(BaseModel):
    reference: str
    collaborateur: Optional[str] = None
    echeance: Optional[date] = None
    type: Optional[str] = None
    statut: Optional[str] = None


class CollContractRenewalRequestUpdate(BaseModel):
    reference: Optional[str] = None
    collaborateur: Optional[str] = None
    echeance: Optional[date] = None
    type: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class CollContractRenewalRequestOut(BaseModel):
    id: int
    company_id: int
    reference: str
    collaborateur: Optional[str] = None
    echeance: Optional[date] = None
    type: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class CollDocumentRequestCreate(BaseModel):
    reference: str
    collaborateur: Optional[str] = None
    document: Optional[str] = None
    delai: Optional[date] = None
    statut: Optional[str] = None


class CollDocumentRequestUpdate(BaseModel):
    reference: Optional[str] = None
    collaborateur: Optional[str] = None
    document: Optional[str] = None
    delai: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class CollDocumentRequestOut(BaseModel):
    id: int
    company_id: int
    reference: str
    collaborateur: Optional[str] = None
    document: Optional[str] = None
    delai: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}

