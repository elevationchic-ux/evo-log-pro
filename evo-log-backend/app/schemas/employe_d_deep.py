"""Schemas Pydantic pour portail-employe (genere)."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date


class EmpLeaveRequestCreate(BaseModel):
    reference: str
    collaborateur: Optional[str] = None
    type_conge: Optional[str] = None
    debut: Optional[date] = None
    fin: Optional[date] = None
    jours: Optional[int] = None
    statut: Optional[str] = None


class EmpLeaveRequestUpdate(BaseModel):
    reference: Optional[str] = None
    collaborateur: Optional[str] = None
    type_conge: Optional[str] = None
    debut: Optional[date] = None
    fin: Optional[date] = None
    jours: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class EmpLeaveRequestOut(BaseModel):
    id: int
    company_id: int
    reference: str
    collaborateur: Optional[str] = None
    type_conge: Optional[str] = None
    debut: Optional[date] = None
    fin: Optional[date] = None
    jours: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class EmpTimesheetEntryCreate(BaseModel):
    reference: str
    collaborateur: Optional[str] = None
    date: Optional[date] = None
    heures: Optional[float] = None
    projet: Optional[str] = None
    statut: Optional[str] = None


class EmpTimesheetEntryUpdate(BaseModel):
    reference: Optional[str] = None
    collaborateur: Optional[str] = None
    date: Optional[date] = None
    heures: Optional[float] = None
    projet: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class EmpTimesheetEntryOut(BaseModel):
    id: int
    company_id: int
    reference: str
    collaborateur: Optional[str] = None
    date: Optional[date] = None
    heures: Optional[float] = None
    projet: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class EmpOvertimeRequestCreate(BaseModel):
    reference: str
    collaborateur: Optional[str] = None
    minutes: Optional[int] = None
    motif: Optional[str] = None
    date: Optional[date] = None
    statut: Optional[str] = None


class EmpOvertimeRequestUpdate(BaseModel):
    reference: Optional[str] = None
    collaborateur: Optional[str] = None
    minutes: Optional[int] = None
    motif: Optional[str] = None
    date: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class EmpOvertimeRequestOut(BaseModel):
    id: int
    company_id: int
    reference: str
    collaborateur: Optional[str] = None
    minutes: Optional[int] = None
    motif: Optional[str] = None
    date: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class EmpAttendanceCorrectionCreate(BaseModel):
    reference: str
    collaborateur: Optional[str] = None
    date_concernee: Optional[date] = None
    motif: Optional[str] = None
    statut: Optional[str] = None


class EmpAttendanceCorrectionUpdate(BaseModel):
    reference: Optional[str] = None
    collaborateur: Optional[str] = None
    date_concernee: Optional[date] = None
    motif: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class EmpAttendanceCorrectionOut(BaseModel):
    id: int
    company_id: int
    reference: str
    collaborateur: Optional[str] = None
    date_concernee: Optional[date] = None
    motif: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class EmpShiftSwapCreate(BaseModel):
    reference: str
    demandeur: Optional[str] = None
    partenaire: Optional[str] = None
    date_poste: Optional[datetime] = None
    statut: Optional[str] = None


class EmpShiftSwapUpdate(BaseModel):
    reference: Optional[str] = None
    demandeur: Optional[str] = None
    partenaire: Optional[str] = None
    date_poste: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class EmpShiftSwapOut(BaseModel):
    id: int
    company_id: int
    reference: str
    demandeur: Optional[str] = None
    partenaire: Optional[str] = None
    date_poste: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class EmpTrainingEnrollmentCreate(BaseModel):
    reference: str
    collaborateur: Optional[str] = None
    formation: Optional[str] = None
    date_debut: Optional[date] = None
    organism: Optional[str] = None
    statut: Optional[str] = None


class EmpTrainingEnrollmentUpdate(BaseModel):
    reference: Optional[str] = None
    collaborateur: Optional[str] = None
    formation: Optional[str] = None
    date_debut: Optional[date] = None
    organism: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class EmpTrainingEnrollmentOut(BaseModel):
    id: int
    company_id: int
    reference: str
    collaborateur: Optional[str] = None
    formation: Optional[str] = None
    date_debut: Optional[date] = None
    organism: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class EmpSkillDeclarationCreate(BaseModel):
    reference: str
    collaborateur: Optional[str] = None
    competence: Optional[str] = None
    niveau: Optional[str] = None
    date: Optional[date] = None
    statut: Optional[str] = None


class EmpSkillDeclarationUpdate(BaseModel):
    reference: Optional[str] = None
    collaborateur: Optional[str] = None
    competence: Optional[str] = None
    niveau: Optional[str] = None
    date: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class EmpSkillDeclarationOut(BaseModel):
    id: int
    company_id: int
    reference: str
    collaborateur: Optional[str] = None
    competence: Optional[str] = None
    niveau: Optional[str] = None
    date: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class EmpCertificationRenewalCreate(BaseModel):
    reference: str
    collaborateur: Optional[str] = None
    certification: Optional[str] = None
    expire_le: Optional[date] = None
    statut: Optional[str] = None


class EmpCertificationRenewalUpdate(BaseModel):
    reference: Optional[str] = None
    collaborateur: Optional[str] = None
    certification: Optional[str] = None
    expire_le: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class EmpCertificationRenewalOut(BaseModel):
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


class EmpPersonalInfoChangeCreate(BaseModel):
    reference: str
    collaborateur: Optional[str] = None
    champ: Optional[str] = None
    nouvelle_valeur: Optional[str] = None
    date: Optional[date] = None
    statut: Optional[str] = None


class EmpPersonalInfoChangeUpdate(BaseModel):
    reference: Optional[str] = None
    collaborateur: Optional[str] = None
    champ: Optional[str] = None
    nouvelle_valeur: Optional[str] = None
    date: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class EmpPersonalInfoChangeOut(BaseModel):
    id: int
    company_id: int
    reference: str
    collaborateur: Optional[str] = None
    champ: Optional[str] = None
    nouvelle_valeur: Optional[str] = None
    date: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class EmpBankDetailsUpdateCreate(BaseModel):
    reference: str
    collaborateur: Optional[str] = None
    banque: Optional[str] = None
    date_effet: Optional[date] = None
    statut: Optional[str] = None


class EmpBankDetailsUpdateUpdate(BaseModel):
    reference: Optional[str] = None
    collaborateur: Optional[str] = None
    banque: Optional[str] = None
    date_effet: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class EmpBankDetailsUpdateOut(BaseModel):
    id: int
    company_id: int
    reference: str
    collaborateur: Optional[str] = None
    banque: Optional[str] = None
    date_effet: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class EmpEmergencyContactCreate(BaseModel):
    reference: str
    collaborateur: Optional[str] = None
    nom: Optional[str] = None
    lien: Optional[str] = None
    telephone: Optional[str] = None
    statut: Optional[str] = None


class EmpEmergencyContactUpdate(BaseModel):
    reference: Optional[str] = None
    collaborateur: Optional[str] = None
    nom: Optional[str] = None
    lien: Optional[str] = None
    telephone: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class EmpEmergencyContactOut(BaseModel):
    id: int
    company_id: int
    reference: str
    collaborateur: Optional[str] = None
    nom: Optional[str] = None
    lien: Optional[str] = None
    telephone: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class EmpBadgeRequestCreate(BaseModel):
    reference: str
    collaborateur: Optional[str] = None
    motif: Optional[str] = None
    date: Optional[date] = None
    statut: Optional[str] = None


class EmpBadgeRequestUpdate(BaseModel):
    reference: Optional[str] = None
    collaborateur: Optional[str] = None
    motif: Optional[str] = None
    date: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class EmpBadgeRequestOut(BaseModel):
    id: int
    company_id: int
    reference: str
    collaborateur: Optional[str] = None
    motif: Optional[str] = None
    date: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class EmpAccessRequestCreate(BaseModel):
    reference: str
    collaborateur: Optional[str] = None
    ressource: Optional[str] = None
    type_acces: Optional[str] = None
    date: Optional[date] = None
    statut: Optional[str] = None


class EmpAccessRequestUpdate(BaseModel):
    reference: Optional[str] = None
    collaborateur: Optional[str] = None
    ressource: Optional[str] = None
    type_acces: Optional[str] = None
    date: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class EmpAccessRequestOut(BaseModel):
    id: int
    company_id: int
    reference: str
    collaborateur: Optional[str] = None
    ressource: Optional[str] = None
    type_acces: Optional[str] = None
    date: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class EmpDocumentUploadCreate(BaseModel):
    reference: str
    collaborateur: Optional[str] = None
    type_piece: Optional[str] = None
    fichier: Optional[str] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None


class EmpDocumentUploadUpdate(BaseModel):
    reference: Optional[str] = None
    collaborateur: Optional[str] = None
    type_piece: Optional[str] = None
    fichier: Optional[str] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class EmpDocumentUploadOut(BaseModel):
    id: int
    company_id: int
    reference: str
    collaborateur: Optional[str] = None
    type_piece: Optional[str] = None
    fichier: Optional[str] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class EmpSelfReviewCreate(BaseModel):
    reference: str
    collaborateur: Optional[str] = None
    periode: Optional[str] = None
    accomplissements: Optional[str] = None
    date: Optional[date] = None
    statut: Optional[str] = None


class EmpSelfReviewUpdate(BaseModel):
    reference: Optional[str] = None
    collaborateur: Optional[str] = None
    periode: Optional[str] = None
    accomplissements: Optional[str] = None
    date: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class EmpSelfReviewOut(BaseModel):
    id: int
    company_id: int
    reference: str
    collaborateur: Optional[str] = None
    periode: Optional[str] = None
    accomplissements: Optional[str] = None
    date: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class EmpMobilityApplicationCreate(BaseModel):
    reference: str
    collaborateur: Optional[str] = None
    poste_cible: Optional[str] = None
    motivation: Optional[str] = None
    date: Optional[date] = None
    statut: Optional[str] = None


class EmpMobilityApplicationUpdate(BaseModel):
    reference: Optional[str] = None
    collaborateur: Optional[str] = None
    poste_cible: Optional[str] = None
    motivation: Optional[str] = None
    date: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class EmpMobilityApplicationOut(BaseModel):
    id: int
    company_id: int
    reference: str
    collaborateur: Optional[str] = None
    poste_cible: Optional[str] = None
    motivation: Optional[str] = None
    date: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class EmpSicknessDeclarationCreate(BaseModel):
    reference: str
    collaborateur: Optional[str] = None
    debut: Optional[date] = None
    duree_jours: Optional[int] = None
    justificatif: Optional[bool] = None
    statut: Optional[str] = None


class EmpSicknessDeclarationUpdate(BaseModel):
    reference: Optional[str] = None
    collaborateur: Optional[str] = None
    debut: Optional[date] = None
    duree_jours: Optional[int] = None
    justificatif: Optional[bool] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class EmpSicknessDeclarationOut(BaseModel):
    id: int
    company_id: int
    reference: str
    collaborateur: Optional[str] = None
    debut: Optional[date] = None
    duree_jours: Optional[int] = None
    justificatif: Optional[bool] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}

