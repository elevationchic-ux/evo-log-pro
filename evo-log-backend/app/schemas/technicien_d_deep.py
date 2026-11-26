"""Schemas Pydantic pour portail-technicien (genere)."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date


class TechWorkOrderCreate(BaseModel):
    reference: str
    vehicule: Optional[str] = None
    type_travaux: Optional[str] = None
    description: Optional[str] = None
    ouverture: Optional[datetime] = None
    cloture: Optional[datetime] = None
    statut: Optional[str] = None


class TechWorkOrderUpdate(BaseModel):
    reference: Optional[str] = None
    vehicule: Optional[str] = None
    type_travaux: Optional[str] = None
    description: Optional[str] = None
    ouverture: Optional[datetime] = None
    cloture: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class TechWorkOrderOut(BaseModel):
    id: int
    company_id: int
    reference: str
    vehicule: Optional[str] = None
    type_travaux: Optional[str] = None
    description: Optional[str] = None
    ouverture: Optional[datetime] = None
    cloture: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class TechInterventionSheetCreate(BaseModel):
    reference: str
    ordre_travail: Optional[str] = None
    technicien: Optional[str] = None
    duree_min: Optional[int] = None
    main_oeuvre: Optional[float] = None
    statut: Optional[str] = None


class TechInterventionSheetUpdate(BaseModel):
    reference: Optional[str] = None
    ordre_travail: Optional[str] = None
    technicien: Optional[str] = None
    duree_min: Optional[int] = None
    main_oeuvre: Optional[float] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class TechInterventionSheetOut(BaseModel):
    id: int
    company_id: int
    reference: str
    ordre_travail: Optional[str] = None
    technicien: Optional[str] = None
    duree_min: Optional[int] = None
    main_oeuvre: Optional[float] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class TechDiagnosisCreate(BaseModel):
    reference: str
    vehicule: Optional[str] = None
    symptome: Optional[str] = None
    cause_racine: Optional[str] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None


class TechDiagnosisUpdate(BaseModel):
    reference: Optional[str] = None
    vehicule: Optional[str] = None
    symptome: Optional[str] = None
    cause_racine: Optional[str] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class TechDiagnosisOut(BaseModel):
    id: int
    company_id: int
    reference: str
    vehicule: Optional[str] = None
    symptome: Optional[str] = None
    cause_racine: Optional[str] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class TechPartConsumptionCreate(BaseModel):
    reference: str
    ordre_travail: Optional[str] = None
    piece: Optional[str] = None
    quantite: Optional[int] = None
    cout_unitaire: Optional[float] = None
    statut: Optional[str] = None


class TechPartConsumptionUpdate(BaseModel):
    reference: Optional[str] = None
    ordre_travail: Optional[str] = None
    piece: Optional[str] = None
    quantite: Optional[int] = None
    cout_unitaire: Optional[float] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class TechPartConsumptionOut(BaseModel):
    id: int
    company_id: int
    reference: str
    ordre_travail: Optional[str] = None
    piece: Optional[str] = None
    quantite: Optional[int] = None
    cout_unitaire: Optional[float] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class TechPreventivePlanCreate(BaseModel):
    reference: str
    vehicule: Optional[str] = None
    operation: Optional[str] = None
    intervalle_km: Optional[int] = None
    derniere_realisation: Optional[date] = None
    statut: Optional[str] = None


class TechPreventivePlanUpdate(BaseModel):
    reference: Optional[str] = None
    vehicule: Optional[str] = None
    operation: Optional[str] = None
    intervalle_km: Optional[int] = None
    derniere_realisation: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class TechPreventivePlanOut(BaseModel):
    id: int
    company_id: int
    reference: str
    vehicule: Optional[str] = None
    operation: Optional[str] = None
    intervalle_km: Optional[int] = None
    derniere_realisation: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class TechBreakdownTicketCreate(BaseModel):
    reference: str
    vehicule: Optional[str] = None
    lieu: Optional[str] = None
    severite: Optional[str] = None
    recu: Optional[datetime] = None
    statut: Optional[str] = None


class TechBreakdownTicketUpdate(BaseModel):
    reference: Optional[str] = None
    vehicule: Optional[str] = None
    lieu: Optional[str] = None
    severite: Optional[str] = None
    recu: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class TechBreakdownTicketOut(BaseModel):
    id: int
    company_id: int
    reference: str
    vehicule: Optional[str] = None
    lieu: Optional[str] = None
    severite: Optional[str] = None
    recu: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class TechRepairReportCreate(BaseModel):
    reference: str
    ordre_travail: Optional[str] = None
    travaux_realises: Optional[str] = None
    test_sortie_ok: Optional[bool] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None


class TechRepairReportUpdate(BaseModel):
    reference: Optional[str] = None
    ordre_travail: Optional[str] = None
    travaux_realises: Optional[str] = None
    test_sortie_ok: Optional[bool] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class TechRepairReportOut(BaseModel):
    id: int
    company_id: int
    reference: str
    ordre_travail: Optional[str] = None
    travaux_realises: Optional[str] = None
    test_sortie_ok: Optional[bool] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class TechCalibrationRecordCreate(BaseModel):
    reference: str
    instrument: Optional[str] = None
    tolerance: Optional[str] = None
    date_etalonnage: Optional[date] = None
    prochaine_date: Optional[date] = None
    statut: Optional[str] = None


class TechCalibrationRecordUpdate(BaseModel):
    reference: Optional[str] = None
    instrument: Optional[str] = None
    tolerance: Optional[str] = None
    date_etalonnage: Optional[date] = None
    prochaine_date: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class TechCalibrationRecordOut(BaseModel):
    id: int
    company_id: int
    reference: str
    instrument: Optional[str] = None
    tolerance: Optional[str] = None
    date_etalonnage: Optional[date] = None
    prochaine_date: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class TechEquipmentChecklistCreate(BaseModel):
    reference: str
    equipement: Optional[str] = None
    points_controles: Optional[int] = None
    anomalies: Optional[int] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None


class TechEquipmentChecklistUpdate(BaseModel):
    reference: Optional[str] = None
    equipement: Optional[str] = None
    points_controles: Optional[int] = None
    anomalies: Optional[int] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class TechEquipmentChecklistOut(BaseModel):
    id: int
    company_id: int
    reference: str
    equipement: Optional[str] = None
    points_controles: Optional[int] = None
    anomalies: Optional[int] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class TechToolLoanCreate(BaseModel):
    reference: str
    outil: Optional[str] = None
    technicien: Optional[str] = None
    sortie: Optional[datetime] = None
    retour: Optional[datetime] = None
    statut: Optional[str] = None


class TechToolLoanUpdate(BaseModel):
    reference: Optional[str] = None
    outil: Optional[str] = None
    technicien: Optional[str] = None
    sortie: Optional[datetime] = None
    retour: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class TechToolLoanOut(BaseModel):
    id: int
    company_id: int
    reference: str
    outil: Optional[str] = None
    technicien: Optional[str] = None
    sortie: Optional[datetime] = None
    retour: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class TechSafetyLockoutCreate(BaseModel):
    reference: str
    installation: Optional[str] = None
    motif: Optional[str] = None
    pose: Optional[datetime] = None
    levee: Optional[datetime] = None
    statut: Optional[str] = None


class TechSafetyLockoutUpdate(BaseModel):
    reference: Optional[str] = None
    installation: Optional[str] = None
    motif: Optional[str] = None
    pose: Optional[datetime] = None
    levee: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class TechSafetyLockoutOut(BaseModel):
    id: int
    company_id: int
    reference: str
    installation: Optional[str] = None
    motif: Optional[str] = None
    pose: Optional[datetime] = None
    levee: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class TechWarrantyClaimCreate(BaseModel):
    reference: str
    piece: Optional[str] = None
    fournisseur: Optional[str] = None
    date_achat: Optional[date] = None
    montant: Optional[float] = None
    statut: Optional[str] = None


class TechWarrantyClaimUpdate(BaseModel):
    reference: Optional[str] = None
    piece: Optional[str] = None
    fournisseur: Optional[str] = None
    date_achat: Optional[date] = None
    montant: Optional[float] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class TechWarrantyClaimOut(BaseModel):
    id: int
    company_id: int
    reference: str
    piece: Optional[str] = None
    fournisseur: Optional[str] = None
    date_achat: Optional[date] = None
    montant: Optional[float] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class TechServiceAppointmentCreate(BaseModel):
    reference: str
    vehicule: Optional[str] = None
    creneau: Optional[datetime] = None
    atelier: Optional[str] = None
    duree_min: Optional[int] = None
    statut: Optional[str] = None


class TechServiceAppointmentUpdate(BaseModel):
    reference: Optional[str] = None
    vehicule: Optional[str] = None
    creneau: Optional[datetime] = None
    atelier: Optional[str] = None
    duree_min: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class TechServiceAppointmentOut(BaseModel):
    id: int
    company_id: int
    reference: str
    vehicule: Optional[str] = None
    creneau: Optional[datetime] = None
    atelier: Optional[str] = None
    duree_min: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class TechLaborTimesheetCreate(BaseModel):
    reference: str
    ordre_travail: Optional[str] = None
    technicien: Optional[str] = None
    minutes: Optional[int] = None
    date: Optional[date] = None
    statut: Optional[str] = None


class TechLaborTimesheetUpdate(BaseModel):
    reference: Optional[str] = None
    ordre_travail: Optional[str] = None
    technicien: Optional[str] = None
    minutes: Optional[int] = None
    date: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class TechLaborTimesheetOut(BaseModel):
    id: int
    company_id: int
    reference: str
    ordre_travail: Optional[str] = None
    technicien: Optional[str] = None
    minutes: Optional[int] = None
    date: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class TechUpgradeRequestCreate(BaseModel):
    reference: str
    cible: Optional[str] = None
    objet: Optional[str] = None
    gain_attendu: Optional[str] = None
    cout_estime: Optional[float] = None
    statut: Optional[str] = None


class TechUpgradeRequestUpdate(BaseModel):
    reference: Optional[str] = None
    cible: Optional[str] = None
    objet: Optional[str] = None
    gain_attendu: Optional[str] = None
    cout_estime: Optional[float] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class TechUpgradeRequestOut(BaseModel):
    id: int
    company_id: int
    reference: str
    cible: Optional[str] = None
    objet: Optional[str] = None
    gain_attendu: Optional[str] = None
    cout_estime: Optional[float] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class TechFailureAnalysisCreate(BaseModel):
    reference: str
    vehicule: Optional[str] = None
    mode_defaillance: Optional[str] = None
    frequence: Optional[int] = None
    date: Optional[date] = None
    statut: Optional[str] = None


class TechFailureAnalysisUpdate(BaseModel):
    reference: Optional[str] = None
    vehicule: Optional[str] = None
    mode_defaillance: Optional[str] = None
    frequence: Optional[int] = None
    date: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class TechFailureAnalysisOut(BaseModel):
    id: int
    company_id: int
    reference: str
    vehicule: Optional[str] = None
    mode_defaillance: Optional[str] = None
    frequence: Optional[int] = None
    date: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class TechSpareRequestCreate(BaseModel):
    reference: str
    piece: Optional[str] = None
    quantite: Optional[int] = None
    demandeur: Optional[str] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None


class TechSpareRequestUpdate(BaseModel):
    reference: Optional[str] = None
    piece: Optional[str] = None
    quantite: Optional[int] = None
    demandeur: Optional[str] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class TechSpareRequestOut(BaseModel):
    id: int
    company_id: int
    reference: str
    piece: Optional[str] = None
    quantite: Optional[int] = None
    demandeur: Optional[str] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class TechInspectionRecordCreate(BaseModel):
    reference: str
    vehicule: Optional[str] = None
    type_controle: Optional[str] = None
    date_controle: Optional[date] = None
    validite: Optional[date] = None
    statut: Optional[str] = None


class TechInspectionRecordUpdate(BaseModel):
    reference: Optional[str] = None
    vehicule: Optional[str] = None
    type_controle: Optional[str] = None
    date_controle: Optional[date] = None
    validite: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class TechInspectionRecordOut(BaseModel):
    id: int
    company_id: int
    reference: str
    vehicule: Optional[str] = None
    type_controle: Optional[str] = None
    date_controle: Optional[date] = None
    validite: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class TechWorkOrderCostCreate(BaseModel):
    reference: str
    ordre_travail: Optional[str] = None
    cout_pieces: Optional[float] = None
    cout_mo: Optional[float] = None
    date: Optional[date] = None
    statut: Optional[str] = None


class TechWorkOrderCostUpdate(BaseModel):
    reference: Optional[str] = None
    ordre_travail: Optional[str] = None
    cout_pieces: Optional[float] = None
    cout_mo: Optional[float] = None
    date: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class TechWorkOrderCostOut(BaseModel):
    id: int
    company_id: int
    reference: str
    ordre_travail: Optional[str] = None
    cout_pieces: Optional[float] = None
    cout_mo: Optional[float] = None
    date: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}

