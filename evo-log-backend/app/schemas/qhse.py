"""Pydantic schemas for QHSE module - Quality, Health, Safety, Environment management"""
from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel


# Analyse Risque schemas
class AnalyseRisqueBase(BaseModel):
    numero_analyse: str
    zone: str
    processus: str
    type_risque: str
    description_danger: str
    causes_potentielles: str
    consequences: str
    population_exposee: int
    frequence: str
    gravite: str
    probabilite: int


class AnalyseRisqueCreate(AnalyseRisqueBase):
    pass


class AnalyseRisqueUpdate(BaseModel):
    mesures_existantes: Optional[str] = None
    mesures_recommandees: Optional[str] = None
    responsable: Optional[str] = None
    date_revision: Optional[date] = None
    statut: Optional[str] = None


class AnalyseRisqueResponse(AnalyseRisqueBase):
    id: int
    date_analyse: date
    risque_calcule: int
    niveau_risque: str
    mesures_existantes: Optional[str] = None
    mesures_recommandees: Optional[str] = None
    responsable: Optional[str] = None
    date_revision: Optional[date] = None
    statut: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Action Prevention schemas
class ActionPreventionBase(BaseModel):
    numero_action: str
    analyse_risque_id: int
    type_action: str
    description: str
    priorite: str
    responsable: str
    date_prevue: date


class ActionPreventionCreate(ActionPreventionBase):
    cout_estime: float = 0.0


class ActionPreventionUpdate(BaseModel):
    date_realisation: Optional[date] = None
    statut: Optional[str] = None
    cout_estime: Optional[float] = None
    verification: Optional[str] = None
    efficacite: Optional[str] = None


class ActionPreventionResponse(ActionPreventionBase):
    id: int
    date_realisation: Optional[date] = None
    statut: str
    cout_estime: Optional[float] = None
    devise: str
    verification: Optional[str] = None
    efficacite: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Plan Prevention schemas
class PlanPreventionBase(BaseModel):
    numero_plan: str
    type_activite: str
    zone: str
    date_debut: date
    date_fin: date
    responsable: str


class PlanPreventionCreate(PlanPreventionBase):
    description: str = ""
    risques_identifies: str = ""
    mesures_prevention: str = ""
    equipements_protection: str = ""
    procedures_urgence: str = ""
    formation_requise: str = ""


class PlanPreventionUpdate(BaseModel):
    description: Optional[str] = None
    risques_identifies: Optional[str] = None
    mesures_prevention: Optional[str] = None
    equipements_protection: Optional[str] = None
    procedures_urgence: Optional[str] = None
    formation_requise: Optional[str] = None
    statut: Optional[str] = None
    date_validation: Optional[date] = None
    valide_par: Optional[str] = None


class PlanPreventionResponse(PlanPreventionBase):
    id: int
    description: Optional[str] = None
    risques_identifies: Optional[str] = None
    mesures_prevention: Optional[str] = None
    equipements_protection: Optional[str] = None
    procedures_urgence: Optional[str] = None
    formation_requise: Optional[str] = None
    statut: str
    date_validation: Optional[date] = None
    valide_par: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# EPI Requis schemas
class EPIRequisBase(BaseModel):
    plan_prevention_id: int
    type_epi: str
    designation: str
    quantite: int


class EPIRequisCreate(EPIRequisBase):
    marque: str = ""
    modele: str = ""
    norme: str = ""
    date_expiration: date = None


class EPIRequisUpdate(BaseModel):
    marque: Optional[str] = None
    modele: Optional[str] = None
    norme: Optional[str] = None
    date_expiration: Optional[date] = None
    statut: Optional[str] = None


class EPIRequisResponse(EPIRequisBase):
    id: int
    marque: Optional[str] = None
    modele: Optional[str] = None
    norme: Optional[str] = None
    date_expiration: Optional[date] = None
    statut: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Accident Travail schemas
class AccidentTravailBase(BaseModel):
    numero_accident: str
    employe_id: int
    date_accident: datetime
    lieu: str
    type_accident: str
    description: str
    gravite: str


class AccidentTravailCreate(AccidentTravailBase):
    partie_corps: str = ""
    temoin1: str = ""
    temoin2: str = ""
    premier_secours: str = ""
    hospitalisation: bool = False
    duree_hospitalisation: int = 0
    arret_travail: int = 0
    photos: str = ""


class AccidentTravailUpdate(BaseModel):
    partie_corps: Optional[str] = None
    temoin1: Optional[str] = None
    temoin2: Optional[str] = None
    premier_secours: Optional[str] = None
    hospitalisation: Optional[bool] = None
    duree_hospitalisation: Optional[int] = None
    arret_travail: Optional[int] = None
    statut: Optional[str] = None
    rapport_medical: Optional[str] = None
    photos: Optional[str] = None


class AccidentTravailResponse(AccidentTravailBase):
    id: int
    partie_corps: Optional[str] = None
    temoin1: Optional[str] = None
    temoin2: Optional[str] = None
    premier_secours: Optional[str] = None
    hospitalisation: bool
    duree_hospitalisation: int
    arret_travail: int
    statut: str
    declarant: str
    date_declaration: date
    rapport_medical: Optional[str] = None
    photos: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Investigation Accident schemas
class InvestigationAccidentBase(BaseModel):
    accident_id: int
    numero_investigation: str
    date_investigation: date
    investigateur: str


class InvestigationAccidentCreate(InvestigationAccidentBase):
    temoins: str = ""
    causes_directes: str = ""
    causes_indirectes: str = ""
    causes_racines: str = ""
    mesures_correctives: str = ""
    mesures_preventives: str = ""
    delai_mise_oeuvre: int = 0
    responsable_suivi: str = ""


class InvestigationAccidentUpdate(BaseModel):
    temoins: Optional[str] = None
    causes_directes: Optional[str] = None
    causes_indirectes: Optional[str] = None
    causes_racines: Optional[str] = None
    mesures_correctives: Optional[str] = None
    mesures_preventives: Optional[str] = None
    delai_mise_oeuvre: Optional[int] = None
    responsable_suivi: Optional[str] = None
    statut: Optional[str] = None
    conclusions: Optional[str] = None


class InvestigationAccidentResponse(InvestigationAccidentBase):
    id: int
    temoins: Optional[str] = None
    causes_directes: Optional[str] = None
    causes_indirectes: Optional[str] = None
    causes_racines: Optional[str] = None
    mesures_correctives: Optional[str] = None
    mesures_preventives: Optional[str] = None
    delai_mise_oeuvre: int
    responsable_suivi: Optional[str] = None
    statut: str
    conclusions: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Norme Certification schemas
class NormeCertificationBase(BaseModel):
    numero_certificat: str
    norme: str
    organisme: str
    date_obtention: date
    date_expiration: date
    scope: str


class NormeCertificationCreate(NormeCertificationBase):
    pass


class NormeCertificationUpdate(BaseModel):
    statut: Optional[str] = None
    numero_audit: Optional[str] = None
    date_dernier_audit: Optional[date] = None
    resultat_audit: Optional[str] = None
    non_conformites: Optional[str] = None


class NormeCertificationResponse(NormeCertificationBase):
    id: int
    statut: str
    numero_audit: Optional[str] = None
    date_dernier_audit: Optional[date] = None
    resultat_audit: Optional[str] = None
    non_conformites: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Audit Qualite schemas
class AuditQualiteBase(BaseModel):
    numero_audit: str
    certification_id: int
    type_audit: str
    date_debut: date
    date_fin: date
    auditeur: str


class AuditQualiteCreate(AuditQualiteBase):
    equipe_audit: str = ""
    scope: str = ""
    criteres: str = ""
    delai_correction: int = 0


class AuditQualiteUpdate(BaseModel):
    equipe_audit: Optional[str] = None
    scope: Optional[str] = None
    criteres: Optional[str] = None
    resultats: Optional[str] = None
    non_conformites: Optional[str] = None
    actions_correctives: Optional[str] = None
    delai_correction: Optional[int] = None
    statut: Optional[str] = None
    conclusion: Optional[str] = None


class AuditQualiteResponse(AuditQualiteBase):
    id: int
    equipe_audit: Optional[str] = None
    scope: Optional[str] = None
    criteres: Optional[str] = None
    resultats: Optional[str] = None
    non_conformites: Optional[str] = None
    actions_correctives: Optional[str] = None
    delai_correction: int
    statut: str
    conclusion: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# HACCP Plan schemas
class HACCPPlanBase(BaseModel):
    numero_plan: str
    produit: str
    processus: str
    responsable: str


class HACCPPlanCreate(HACCPPlanBase):
    equipe_haccp: str = ""
    diagramme_flux: str = ""


class HACCPPlanUpdate(BaseModel):
    date_revision: Optional[date] = None
    equipe_haccp: Optional[str] = None
    diagramme_flux: Optional[str] = None
    statut: Optional[str] = None


class HACCPPlanResponse(HACCPPlanBase):
    id: int
    date_creation: date
    date_revision: Optional[date] = None
    equipe_haccp: Optional[str] = None
    diagramme_flux: Optional[str] = None
    statut: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Point Critique CCP schemas
class PointCritiqueCCPBase(BaseModel):
    haccp_plan_id: int
    numero_ccp: str
    etape: str
    danger: str
    limites_critiques: str
    surveillance: str


class PointCritiqueCCPCreate(PointCritiqueCCPBase):
    mesures_prevention: str = ""
    frequence_controle: str = ""
    actions_correctives: str = ""
    responsable: str = ""
    enregistrements: str = ""


class PointCritiqueCCPUpdate(BaseModel):
    mesures_prevention: Optional[str] = None
    frequence_controle: Optional[str] = None
    actions_correctives: Optional[str] = None
    responsable: Optional[str] = None
    enregistrements: Optional[str] = None
    statut: Optional[str] = None


class PointCritiqueCCPResponse(PointCritiqueCCPBase):
    id: int
    mesures_prevention: Optional[str] = None
    frequence_controle: Optional[str] = None
    actions_correctives: Optional[str] = None
    responsable: Optional[str] = None
    enregistrements: Optional[str] = None
    statut: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Enregistrement HACCP schemas
class EnregistrementHACCPBase(BaseModel):
    point_critique_id: int
    valeur_mesuree: float
    unite: str
    operateur: str


class EnregistrementHACCPCreate(EnregistrementHACCPBase):
    conforme: bool = True
    observations: str = ""
    action_prise: str = ""


class EnregistrementHACCPUpdate(BaseModel):
    conforme: Optional[bool] = None
    observations: Optional[str] = None
    action_prise: Optional[str] = None


class EnregistrementHACCPResponse(EnregistrementHACCPBase):
    id: int
    date_enregistrement: datetime
    conforme: bool
    observations: Optional[str] = None
    action_prise: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# Formation QHSE schemas
class FormationQHSEBase(BaseModel):
    numero_formation: str
    type_formation: str
    titre: str
    formateur: str
    date_debut: date
    date_fin: date
    duree_heures: int


class FormationQHSECreate(FormationQHSEBase):
    description: str = ""
    lieu: str = ""
    participants: str = ""
    objectifs: str = ""
    contenu: str = ""
    evaluation: str = ""
    cout: float = 0.0


class FormationQHSEUpdate(BaseModel):
    description: Optional[str] = None
    lieu: Optional[str] = None
    participants: Optional[str] = None
    objectifs: Optional[str] = None
    contenu: Optional[str] = None
    evaluation: Optional[str] = None
    statut: Optional[str] = None
    cout: Optional[float] = None


class FormationQHSEResponse(FormationQHSEBase):
    id: int
    description: Optional[str] = None
    lieu: Optional[str] = None
    participants: Optional[str] = None
    objectifs: Optional[str] = None
    contenu: Optional[str] = None
    evaluation: Optional[str] = None
    statut: str
    cout: Optional[float] = None
    devise: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Indicateur QHSE schemas
class IndicateurQHSEBase(BaseModel):
    code: str
    nom: str
    type_indicateur: str
    unite: str
    objectif: float


class IndicateurQHSECreate(IndicateurQHSEBase):
    pass


class IndicateurQHSEUpdate(BaseModel):
    valeur_actuelle: Optional[float] = None
    periode: Optional[str] = None
    statut: Optional[str] = None


class IndicateurQHSEResponse(IndicateurQHSEBase):
    id: int
    periode: Optional[str] = None
    valeur_actuelle: Optional[float] = None
    valeur_previous: Optional[float] = None
    variation: Optional[float] = None
    tendance: Optional[str] = None
    date_mesure: Optional[date] = None
    statut: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Rapport Securite
class RapportSecuriteResponse(BaseModel):
    annee: int
    accidents: dict
    risques: dict


# Incident schemas
class IncidentCreate(BaseModel):
    numero_incident: str
    type_incident: str
    date_incident: datetime
    lieu: str
    description: str
    gravite: str = "mineur"
    personnes_impliquees: Optional[str] = None
    actions_immediates: Optional[str] = None
    statut: str = "declare"


class IncidentUpdate(BaseModel):
    gravite: Optional[str] = None
    description: Optional[str] = None
    actions_correctives: Optional[str] = None
    statut: Optional[str] = None
    date_cloture: Optional[datetime] = None


class IncidentResponse(BaseModel):
    id: int
    numero_incident: str
    type_incident: str
    date_incident: datetime
    lieu: str
    description: str
    gravite: str
    personnes_impliquees: Optional[str] = None
    actions_immediates: Optional[str] = None
    actions_correctives: Optional[str] = None
    statut: str
    date_cloture: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Rapport QHSE
class RapportQHSEResponse(BaseModel):
    id: int
    periode: str
    nb_incidents: int = 0
    nb_accidents: int = 0
    nb_inspections: int = 0
    nb_actions_correctives: int = 0
    taux_frequence: Optional[float] = None
    taux_gravite: Optional[float] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Procedure Securite schemas
class ProcedureSecuriteCreate(BaseModel):
    numero_procedure: str
    titre: str
    type_procedure: str
    description: str
    frequence: Optional[str] = None
    responsable: Optional[str] = None
    statut: str = "active"


class ProcedureSecuriteResponse(BaseModel):
    id: int
    numero_procedure: str
    titre: str
    type_procedure: str
    description: str
    frequence: Optional[str] = None
    responsable: Optional[str] = None
    statut: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
