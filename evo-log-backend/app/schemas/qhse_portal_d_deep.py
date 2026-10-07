"""Schemas Pydantic pour portail-qhse (genere)."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date


class QspHazardReportCreate(BaseModel):
    reference: str
    lieu: Optional[str] = None
    description: Optional[str] = None
    gravite: Optional[str] = None
    signale_le: Optional[datetime] = None
    statut: Optional[str] = None


class QspHazardReportUpdate(BaseModel):
    reference: Optional[str] = None
    lieu: Optional[str] = None
    description: Optional[str] = None
    gravite: Optional[str] = None
    signale_le: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class QspHazardReportOut(BaseModel):
    id: int
    company_id: int
    reference: str
    lieu: Optional[str] = None
    description: Optional[str] = None
    gravite: Optional[str] = None
    signale_le: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class QspNearMissCreate(BaseModel):
    reference: str
    lieu: Optional[str] = None
    situation: Optional[str] = None
    date: Optional[datetime] = None
    témoin: Optional[str] = None
    statut: Optional[str] = None


class QspNearMissUpdate(BaseModel):
    reference: Optional[str] = None
    lieu: Optional[str] = None
    situation: Optional[str] = None
    date: Optional[datetime] = None
    témoin: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class QspNearMissOut(BaseModel):
    id: int
    company_id: int
    reference: str
    lieu: Optional[str] = None
    situation: Optional[str] = None
    date: Optional[datetime] = None
    témoin: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class QspSafetyObservationCreate(BaseModel):
    reference: str
    zone: Optional[str] = None
    observation: Optional[str] = None
    nature: Optional[str] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None


class QspSafetyObservationUpdate(BaseModel):
    reference: Optional[str] = None
    zone: Optional[str] = None
    observation: Optional[str] = None
    nature: Optional[str] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class QspSafetyObservationOut(BaseModel):
    id: int
    company_id: int
    reference: str
    zone: Optional[str] = None
    observation: Optional[str] = None
    nature: Optional[str] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class QspPpeAttestationCreate(BaseModel):
    reference: str
    operateur: Optional[str] = None
    epi_controles: Optional[int] = None
    conforme: Optional[bool] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None


class QspPpeAttestationUpdate(BaseModel):
    reference: Optional[str] = None
    operateur: Optional[str] = None
    epi_controles: Optional[int] = None
    conforme: Optional[bool] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class QspPpeAttestationOut(BaseModel):
    id: int
    company_id: int
    reference: str
    operateur: Optional[str] = None
    epi_controles: Optional[int] = None
    conforme: Optional[bool] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class QspToolboxTalkCreate(BaseModel):
    reference: str
    sujet: Optional[str] = None
    anime_par: Optional[str] = None
    nb_participants: Optional[int] = None
    date: Optional[date] = None
    statut: Optional[str] = None


class QspToolboxTalkUpdate(BaseModel):
    reference: Optional[str] = None
    sujet: Optional[str] = None
    anime_par: Optional[str] = None
    nb_participants: Optional[int] = None
    date: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class QspToolboxTalkOut(BaseModel):
    id: int
    company_id: int
    reference: str
    sujet: Optional[str] = None
    anime_par: Optional[str] = None
    nb_participants: Optional[int] = None
    date: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class QspWorkPermitRequestCreate(BaseModel):
    reference: str
    type: Optional[str] = None
    lieu: Optional[str] = None
    demandeur: Optional[str] = None
    debut: Optional[datetime] = None
    statut: Optional[str] = None


class QspWorkPermitRequestUpdate(BaseModel):
    reference: Optional[str] = None
    type: Optional[str] = None
    lieu: Optional[str] = None
    demandeur: Optional[str] = None
    debut: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class QspWorkPermitRequestOut(BaseModel):
    id: int
    company_id: int
    reference: str
    type: Optional[str] = None
    lieu: Optional[str] = None
    demandeur: Optional[str] = None
    debut: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class QspSafetyTrainingLogCreate(BaseModel):
    reference: str
    operateur: Optional[str] = None
    formation: Optional[str] = None
    date: Optional[date] = None
    validite: Optional[date] = None
    statut: Optional[str] = None


class QspSafetyTrainingLogUpdate(BaseModel):
    reference: Optional[str] = None
    operateur: Optional[str] = None
    formation: Optional[str] = None
    date: Optional[date] = None
    validite: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class QspSafetyTrainingLogOut(BaseModel):
    id: int
    company_id: int
    reference: str
    operateur: Optional[str] = None
    formation: Optional[str] = None
    date: Optional[date] = None
    validite: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class QspExposureRecordCreate(BaseModel):
    reference: str
    operateur: Optional[str] = None
    agent: Optional[str] = None
    valeur: Optional[float] = None
    date: Optional[date] = None
    statut: Optional[str] = None


class QspExposureRecordUpdate(BaseModel):
    reference: Optional[str] = None
    operateur: Optional[str] = None
    agent: Optional[str] = None
    valeur: Optional[float] = None
    date: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class QspExposureRecordOut(BaseModel):
    id: int
    company_id: int
    reference: str
    operateur: Optional[str] = None
    agent: Optional[str] = None
    valeur: Optional[float] = None
    date: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class QspFirstAidLogCreate(BaseModel):
    reference: str
    personne: Optional[str] = None
    nature_blessure: Optional[str] = None
    date: Optional[datetime] = None
    secouriste: Optional[str] = None
    statut: Optional[str] = None


class QspFirstAidLogUpdate(BaseModel):
    reference: Optional[str] = None
    personne: Optional[str] = None
    nature_blessure: Optional[str] = None
    date: Optional[datetime] = None
    secouriste: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class QspFirstAidLogOut(BaseModel):
    id: int
    company_id: int
    reference: str
    personne: Optional[str] = None
    nature_blessure: Optional[str] = None
    date: Optional[datetime] = None
    secouriste: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class QspSafetySuggestionCreate(BaseModel):
    reference: str
    auteur: Optional[str] = None
    idee: Optional[str] = None
    date: Optional[date] = None
    statut: Optional[str] = None


class QspSafetySuggestionUpdate(BaseModel):
    reference: Optional[str] = None
    auteur: Optional[str] = None
    idee: Optional[str] = None
    date: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class QspSafetySuggestionOut(BaseModel):
    id: int
    company_id: int
    reference: str
    auteur: Optional[str] = None
    idee: Optional[str] = None
    date: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class QspStopWorkAuthorityCreate(BaseModel):
    reference: str
    motif: Optional[str] = None
    declenche_le: Optional[datetime] = None
    reprise_le: Optional[datetime] = None
    statut: Optional[str] = None


class QspStopWorkAuthorityUpdate(BaseModel):
    reference: Optional[str] = None
    motif: Optional[str] = None
    declenche_le: Optional[datetime] = None
    reprise_le: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class QspStopWorkAuthorityOut(BaseModel):
    id: int
    company_id: int
    reference: str
    motif: Optional[str] = None
    declenche_le: Optional[datetime] = None
    reprise_le: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class QspSpillReportCreate(BaseModel):
    reference: str
    produit: Optional[str] = None
    volume: Optional[float] = None
    lieu: Optional[str] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None


class QspSpillReportUpdate(BaseModel):
    reference: Optional[str] = None
    produit: Optional[str] = None
    volume: Optional[float] = None
    lieu: Optional[str] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class QspSpillReportOut(BaseModel):
    id: int
    company_id: int
    reference: str
    produit: Optional[str] = None
    volume: Optional[float] = None
    lieu: Optional[str] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class QspMsdsAckCreate(BaseModel):
    reference: str
    produit: Optional[str] = None
    operateur: Optional[str] = None
    date: Optional[date] = None
    version_fds: Optional[str] = None
    statut: Optional[str] = None


class QspMsdsAckUpdate(BaseModel):
    reference: Optional[str] = None
    produit: Optional[str] = None
    operateur: Optional[str] = None
    date: Optional[date] = None
    version_fds: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class QspMsdsAckOut(BaseModel):
    id: int
    company_id: int
    reference: str
    produit: Optional[str] = None
    operateur: Optional[str] = None
    date: Optional[date] = None
    version_fds: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class QspErgonomicsAssessmentCreate(BaseModel):
    reference: str
    poste: Optional[str] = None
    contrainte: Optional[str] = None
    score: Optional[int] = None
    date: Optional[date] = None
    statut: Optional[str] = None


class QspErgonomicsAssessmentUpdate(BaseModel):
    reference: Optional[str] = None
    poste: Optional[str] = None
    contrainte: Optional[str] = None
    score: Optional[int] = None
    date: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class QspErgonomicsAssessmentOut(BaseModel):
    id: int
    company_id: int
    reference: str
    poste: Optional[str] = None
    contrainte: Optional[str] = None
    score: Optional[int] = None
    date: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class QspHygieneCheckCreate(BaseModel):
    reference: str
    local: Optional[str] = None
    point_controle: Optional[str] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None


class QspHygieneCheckUpdate(BaseModel):
    reference: Optional[str] = None
    local: Optional[str] = None
    point_controle: Optional[str] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class QspHygieneCheckOut(BaseModel):
    id: int
    company_id: int
    reference: str
    local: Optional[str] = None
    point_controle: Optional[str] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class QspInspectionFindingCreate(BaseModel):
    reference: str
    inspection: Optional[str] = None
    constat: Optional[str] = None
    criticite: Optional[str] = None
    date: Optional[date] = None
    statut: Optional[str] = None


class QspInspectionFindingUpdate(BaseModel):
    reference: Optional[str] = None
    inspection: Optional[str] = None
    constat: Optional[str] = None
    criticite: Optional[str] = None
    date: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class QspInspectionFindingOut(BaseModel):
    id: int
    company_id: int
    reference: str
    inspection: Optional[str] = None
    constat: Optional[str] = None
    criticite: Optional[str] = None
    date: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class QspCapaReplyCreate(BaseModel):
    reference: str
    action_corrective: Optional[str] = None
    reponse: Optional[str] = None
    operateur: Optional[str] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None


class QspCapaReplyUpdate(BaseModel):
    reference: Optional[str] = None
    action_corrective: Optional[str] = None
    reponse: Optional[str] = None
    operateur: Optional[str] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class QspCapaReplyOut(BaseModel):
    id: int
    company_id: int
    reference: str
    action_corrective: Optional[str] = None
    reponse: Optional[str] = None
    operateur: Optional[str] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class QspRiskAssessmentInputCreate(BaseModel):
    reference: str
    activite: Optional[str] = None
    risque_identifie: Optional[str] = None
    cotation: Optional[int] = None
    date: Optional[date] = None
    statut: Optional[str] = None


class QspRiskAssessmentInputUpdate(BaseModel):
    reference: Optional[str] = None
    activite: Optional[str] = None
    risque_identifie: Optional[str] = None
    cotation: Optional[int] = None
    date: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class QspRiskAssessmentInputOut(BaseModel):
    id: int
    company_id: int
    reference: str
    activite: Optional[str] = None
    risque_identifie: Optional[str] = None
    cotation: Optional[int] = None
    date: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class QspEvacuationDrillCreate(BaseModel):
    reference: str
    site: Optional[str] = None
    date: Optional[datetime] = None
    duree_sec: Optional[int] = None
    nb_evacues: Optional[int] = None
    statut: Optional[str] = None


class QspEvacuationDrillUpdate(BaseModel):
    reference: Optional[str] = None
    site: Optional[str] = None
    date: Optional[datetime] = None
    duree_sec: Optional[int] = None
    nb_evacues: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class QspEvacuationDrillOut(BaseModel):
    id: int
    company_id: int
    reference: str
    site: Optional[str] = None
    date: Optional[datetime] = None
    duree_sec: Optional[int] = None
    nb_evacues: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}

