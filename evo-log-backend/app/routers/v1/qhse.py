"""QHSE router - Quality, Health, Safety, Environment management"""
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy import desc
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, date
import random
import string

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.qhse import (
    AnalyseRisqueCreate, AnalyseRisqueUpdate, AnalyseRisqueResponse,
    ActionPreventionCreate, ActionPreventionUpdate, ActionPreventionResponse,
    PlanPreventionCreate, PlanPreventionUpdate, PlanPreventionResponse,
    EPIRequisCreate, EPIRequisUpdate, EPIRequisResponse,
    AccidentTravailCreate, AccidentTravailUpdate, AccidentTravailResponse,
    InvestigationAccidentCreate, InvestigationAccidentUpdate, InvestigationAccidentResponse,
    NormeCertificationCreate, NormeCertificationUpdate, NormeCertificationResponse,
    AuditQualiteCreate, AuditQualiteUpdate, AuditQualiteResponse,
    HACCPPlanCreate, HACCPPlanUpdate, HACCPPlanResponse,
    PointCritiqueCCPCreate, PointCritiqueCCPUpdate, PointCritiqueCCPResponse,
    EnregistrementHACCPCreate, EnregistrementHACCPUpdate, EnregistrementHACCPResponse,
    FormationQHSECreate, FormationQHSEUpdate, FormationQHSEResponse,
    IndicateurQHSECreate, IndicateurQHSEUpdate, IndicateurQHSEResponse,
    RapportSecuriteResponse
)
from app.services.qhse_service import (
    AnalyseRisqueService, ActionPreventionService, PlanPreventionService, EPIRequisService,
    AccidentTravailService, InvestigationAccidentService, NormeCertificationService,
    AuditQualiteService, HACCPPlanService, PointCritiqueCCPService, EnregistrementHACCPService,
    FormationQHSEService, IndicateurQHSEService, QHSEReportingService
)
from app.models.qhse import (
    AnalyseRisque, PlanPrevention, AccidentTravail, NormeCertification, HACCPPlan,
    AuditQualite, InvestigationAccident, FormationQHSE,
)
from app.models.gap_bridge import RegistreEntry

router = APIRouter(tags=["QHSE"])  # monte sur /api/v1/qhse par main.py (pas de double prefix)


def _gen_numero(prefix: str) -> str:
    return f"{prefix}-{datetime.now().strftime('%Y%m%d')}-{''.join(random.choices(string.ascii_uppercase + string.digits, k=4))}"


def _registre_dict(e: RegistreEntry) -> dict:
    base = {
        "id": e.id,
        "reference": e.reference,
        "statut": e.statut,
        "created_by": e.created_by,
        "created_at": e.created_at.isoformat() if e.created_at else None,
    }
    if isinstance(e.payload, dict):
        base.update(e.payload)
    return base


# ============ ANALYSES RISQUES ============
@router.post("/analyses-risques", response_model=AnalyseRisqueResponse, status_code=status.HTTP_201_CREATED)
def creer_analyse_risque(
    analyse: AnalyseRisqueCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create risk analysis"""
    return AnalyseRisqueService.creer_analyse_risque(
        db, analyse.numero_analyse, analyse.zone, analyse.processus,
        analyse.type_risque, analyse.description_danger, analyse.causes_potentielles,
        analyse.consequences, analyse.population_exposee, analyse.frequence,
        analyse.gravite, analyse.probabilite
    )


@router.put("/analyses-risques/{analyse_id}", response_model=AnalyseRisqueResponse)
def mettre_a_jour_analyse(
    analyse_id: int,
    analyse: AnalyseRisqueUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update risk analysis"""
    a = db.query(AnalyseRisque).filter(AnalyseRisque.id == analyse_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Analyse de risque non trouvée")
    
    for field, value in analyse.model_dump(exclude_unset=True).items():
        setattr(a, field, value)
    
    db.commit()
    db.refresh(a)
    return a


# ============ ACTIONS PREVENTION ============
@router.post("/actions-prevention", response_model=ActionPreventionResponse, status_code=status.HTTP_201_CREATED)
def creer_action_prevention(
    action: ActionPreventionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create prevention action"""
    return ActionPreventionService.creer_action_prevention(
        db, action.numero_action, action.analyse_risque_id, action.type_action,
        action.description, action.priorite, action.responsable, action.date_prevue
    )


@router.put("/actions-prevention/{action_id}", response_model=ActionPreventionResponse)
def mettre_a_jour_action(
    action_id: int,
    action: ActionPreventionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update prevention action"""
    a = db.query(ActionPrevention).filter(ActionPrevention.id == action_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Action de prévention non trouvée")
    
    for field, value in action.model_dump(exclude_unset=True).items():
        setattr(a, field, value)
    
    db.commit()
    db.refresh(a)
    return a


# ============ PLANS PREVENTION ============
@router.post("/plans-prevention", response_model=PlanPreventionResponse, status_code=status.HTTP_201_CREATED)
def creer_plan_prevention(
    plan: PlanPreventionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create prevention plan"""
    return PlanPreventionService.creer_plan_prevention(
        db, plan.numero_plan, plan.type_activite, plan.zone,
        plan.date_debut, plan.date_fin, plan.responsable, plan.description
    )


@router.put("/plans-prevention/{plan_id}", response_model=PlanPreventionResponse)
def mettre_a_jour_plan(
    plan_id: int,
    plan: PlanPreventionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update prevention plan"""
    p = db.query(PlanPrevention).filter(PlanPrevention.id == plan_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Plan de prévention non trouvé")
    
    for field, value in plan.model_dump(exclude_unset=True).items():
        setattr(p, field, value)
    
    db.commit()
    db.refresh(p)
    return p


# ============ EPI REQUIS ============
@router.post("/epi-requis", response_model=EPIRequisResponse, status_code=status.HTTP_201_CREATED)
def ajouter_epi(
    epi: EPIRequisCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add required PPE"""
    return EPIRequisService.ajouter_epi(
        db, epi.plan_prevention_id, epi.type_epi, epi.designation,
        epi.quantite, epi.norme
    )


@router.put("/epi-requis/{epi_id}", response_model=EPIRequisResponse)
def mettre_a_jour_epi(
    epi_id: int,
    epi: EPIRequisUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update required PPE"""
    e = db.query(EPIRequis).filter(EPIRequis.id == epi_id).first()
    if not e:
        raise HTTPException(status_code=404, detail="EPI non trouvé")
    
    for field, value in epi.model_dump(exclude_unset=True).items():
        setattr(e, field, value)
    
    db.commit()
    db.refresh(e)
    return e


# ============ ACCIDENTS TRAVAIL ============
@router.get("/accidents")
def lister_accidents(
    skip: int = 0, limit: int = 200,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Registre reel des accidents du travail declares (persistance SQLAlchemy)."""
    rows = db.query(AccidentTravail).order_by(desc(AccidentTravail.id)).offset(skip).limit(limit).all()
    data = [
        {
            "id": a.id, "numero_accident": a.numero_accident,
            "employe_id": a.employe_id,
            "date_accident": a.date_accident.isoformat() if a.date_accident else None,
            "lieu": a.lieu, "type_accident": a.type_accident,
            "description": a.description, "gravite": a.gravite,
            "arret_travail": a.arret_travail or 0,
            "hospitalisation": bool(a.hospitalisation),
            "statut": a.statut.value if hasattr(a.statut, "value") else str(a.statut),
            "declarant": a.declarant,
            "created_at": a.created_at.isoformat() if a.created_at else None,
        } for a in rows
    ]
    return {"data": data, "items": data, "total": len(data)}


@router.post("/accidents", response_model=AccidentTravailResponse, status_code=status.HTTP_201_CREATED)
def declarer_accident(
    accident: AccidentTravailCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Declare work accident"""
    created = AccidentTravailService.declarer_accident(
        db, accident.numero_accident or _gen_numero("ACC"), accident.employe_id,
        accident.date_accident, accident.lieu, accident.type_accident,
        accident.description, accident.gravite
    )
    # Persistance complete du formulaire reel (sinon ces champs resteraient nuls)
    for field in ("partie_corps", "temoin1", "temoin2", "premier_secours",
                  "hospitalisation", "duree_hospitalisation", "arret_travail", "photos"):
        value = getattr(accident, field, None)
        if value not in (None, "", 0, False):
            setattr(created, field, value)
    if not created.declarant:
        created.declarant = getattr(current_user, "full_name", None) or getattr(current_user, "username", None)
    if not created.date_declaration:
        created.date_declaration = date.today()
    db.commit()
    db.refresh(created)
    return created


@router.put("/accidents/{accident_id}", response_model=AccidentTravailResponse)
def mettre_a_jour_accident(
    accident_id: int,
    accident: AccidentTravailUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update work accident"""
    a = db.query(AccidentTravail).filter(AccidentTravail.id == accident_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Accident non trouvé")
    
    for field, value in accident.model_dump(exclude_unset=True).items():
        setattr(a, field, value)
    
    db.commit()
    db.refresh(a)
    return a


# ============ INVESTIGATIONS ACCIDENTS ============
@router.get("/investigations")
def lister_investigations(
    skip: int = 0, limit: int = 200,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Registre reel des enquetes / plans d'actions correctives (CAPA)."""
    rows = db.query(InvestigationAccident).order_by(desc(InvestigationAccident.id)).offset(skip).limit(limit).all()
    data = [
        {
            "id": i.id, "accident_id": i.accident_id,
            "numero_investigation": i.numero_investigation,
            "date_investigation": i.date_investigation.isoformat() if i.date_investigation else None,
            "investigateur": i.investigateur,
            "causes_directes": i.causes_directes, "causes_indirectes": i.causes_indirectes,
            "causes_racines": i.causes_racines,
            "mesures_correctives": i.mesures_correctives, "mesures_preventives": i.mesures_preventives,
            "delai_mise_oeuvre": i.delai_mise_oeuvre, "responsable_suivi": i.responsable_suivi,
            "statut": i.statut, "conclusions": i.conclusions,
            "created_at": i.created_at.isoformat() if i.created_at else None,
        } for i in rows
    ]
    return {"data": data, "items": data, "total": len(data)}


@router.post("/investigations", response_model=InvestigationAccidentResponse, status_code=status.HTTP_201_CREATED)
def creer_investigation(
    investigation: InvestigationAccidentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create accident investigation"""
    created = InvestigationAccidentService.creer_investigation(
        db, investigation.accident_id,
        investigation.numero_investigation or _gen_numero("INV"),
        investigation.date_investigation, investigation.investigateur
    )
    for field in ("temoins", "causes_directes", "causes_indirectes", "causes_racines",
                  "mesures_correctives", "mesures_preventives", "delai_mise_oeuvre",
                  "responsable_suivi"):
        value = getattr(investigation, field, None)
        if value not in (None, "", 0):
            setattr(created, field, value)
    db.commit()
    db.refresh(created)
    return created


@router.put("/investigations/{investigation_id}", response_model=InvestigationAccidentResponse)
def mettre_a_jour_investigation(
    investigation_id: int,
    investigation: InvestigationAccidentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update accident investigation"""
    i = db.query(InvestigationAccident).filter(InvestigationAccident.id == investigation_id).first()
    if not i:
        raise HTTPException(status_code=404, detail="Investigation non trouvée")
    
    for field, value in investigation.model_dump(exclude_unset=True).items():
        setattr(i, field, value)
    
    db.commit()
    db.refresh(i)
    return i


# ============ NORMES CERTIFICATIONS ============
@router.post("/certifications", response_model=NormeCertificationResponse, status_code=status.HTTP_201_CREATED)
def creer_certification(
    certification: NormeCertificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create ISO certification"""
    return NormeCertificationService.creer_certification(
        db, certification.numero_certificat, certification.norme,
        certification.organisme, certification.date_obtention,
        certification.date_expiration, certification.scope
    )


@router.put("/certifications/{certification_id}", response_model=NormeCertificationResponse)
def mettre_a_jour_certification(
    certification_id: int,
    certification: NormeCertificationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update ISO certification"""
    c = db.query(NormeCertification).filter(NormeCertification.id == certification_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Certification non trouvée")
    
    for field, value in certification.model_dump(exclude_unset=True).items():
        setattr(c, field, value)
    
    db.commit()
    db.refresh(c)
    return c


# ============ AUDITS QUALITE ============
@router.post("/audits", response_model=AuditQualiteResponse, status_code=status.HTTP_201_CREATED)
def creer_audit(
    audit: AuditQualiteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create quality audit"""
    return AuditQualiteService.creer_audit(
        db, audit.numero_audit, audit.certification_id, audit.type_audit,
        audit.date_debut, audit.date_fin, audit.auditeur
    )


@router.put("/audits/{audit_id}", response_model=AuditQualiteResponse)
def mettre_a_jour_audit(
    audit_id: int,
    audit: AuditQualiteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update quality audit"""
    a = db.query(AuditQualite).filter(AuditQualite.id == audit_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Audit non trouvé")
    
    for field, value in audit.model_dump(exclude_unset=True).items():
        setattr(a, field, value)
    
    db.commit()
    db.refresh(a)
    return a


# ============ PLANS HACCP ============
@router.post("/plans-haccp", response_model=HACCPPlanResponse, status_code=status.HTTP_201_CREATED)
def creer_plan_haccp(
    plan: HACCPPlanCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create HACCP plan"""
    return HACCPPlanService.creer_plan_haccp(
        db, plan.numero_plan, plan.produit, plan.processus, plan.responsable
    )


@router.put("/plans-haccp/{plan_id}", response_model=HACCPPlanResponse)
def mettre_a_jour_plan_haccp(
    plan_id: int,
    plan: HACCPPlanUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update HACCP plan"""
    p = db.query(HACCPPlan).filter(HACCPPlan.id == plan_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Plan HACCP non trouvé")
    
    for field, value in plan.model_dump(exclude_unset=True).items():
        setattr(p, field, value)
    
    db.commit()
    db.refresh(p)
    return p


# ============ POINTS CRITIQUES CCP ============
@router.post("/points-critiques", response_model=PointCritiqueCCPResponse, status_code=status.HTTP_201_CREATED)
def ajouter_ccp(
    ccp: PointCritiqueCCPCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add critical control point"""
    return PointCritiqueCCPService.ajouter_ccp(
        db, ccp.haccp_plan_id, ccp.numero_ccp, ccp.etape,
        ccp.danger, ccp.limites_critiques, ccp.surveillance
    )


@router.put("/points-critiques/{ccp_id}", response_model=PointCritiqueCCPResponse)
def mettre_a_jour_ccp(
    ccp_id: int,
    ccp: PointCritiqueCCPUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update critical control point"""
    c = db.query(PointCritiqueCCP).filter(PointCritiqueCCP.id == ccp_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Point critique non trouvé")
    
    for field, value in ccp.model_dump(exclude_unset=True).items():
        setattr(c, field, value)
    
    db.commit()
    db.refresh(c)
    return c


# ============ ENREGISTREMENTS HACCP ============
@router.post("/enregistrements-haccp", response_model=EnregistrementHACCPResponse, status_code=status.HTTP_201_CREATED)
def enregistrer_controle(
    enregistrement: EnregistrementHACCPCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Record HACCP control"""
    return EnregistrementHACCPService.enregistrer_controle(
        db, enregistrement.point_critique_id, enregistrement.valeur_mesuree,
        enregistrement.unite, enregistrement.operateur
    )


@router.put("/enregistrements-haccp/{enregistrement_id}", response_model=EnregistrementHACCPResponse)
def mettre_a_jour_enregistrement(
    enregistrement_id: int,
    enregistrement: EnregistrementHACCPUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update HACCP record"""
    e = db.query(EnregistrementHACCP).filter(EnregistrementHACCP.id == enregistrement_id).first()
    if not e:
        raise HTTPException(status_code=404, detail="Enregistrement non trouvé")
    
    for field, value in enregistrement.model_dump(exclude_unset=True).items():
        setattr(e, field, value)
    
    db.commit()
    db.refresh(e)
    return e


# ============ FORMATIONS QHSE ============
@router.post("/formations", response_model=FormationQHSEResponse, status_code=status.HTTP_201_CREATED)
def creer_formation(
    formation: FormationQHSECreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create QHSE training"""
    return FormationQHSEService.creer_formation(
        db, formation.numero_formation, formation.type_formation, formation.titre,
        formation.formateur, formation.date_debut, formation.date_fin, formation.duree_heures
    )


@router.put("/formations/{formation_id}", response_model=FormationQHSEResponse)
def mettre_a_jour_formation(
    formation_id: int,
    formation: FormationQHSEUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update QHSE training"""
    f = db.query(FormationQHSE).filter(FormationQHSE.id == formation_id).first()
    if not f:
        raise HTTPException(status_code=404, detail="Formation non trouvée")
    
    for field, value in formation.model_dump(exclude_unset=True).items():
        setattr(f, field, value)
    
    db.commit()
    db.refresh(f)
    return f


# ============ INDICATEURS QHSE ============
@router.post("/indicateurs", response_model=IndicateurQHSEResponse, status_code=status.HTTP_201_CREATED)
def creer_indicateur(
    indicateur: IndicateurQHSECreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create QHSE indicator"""
    return IndicateurQHSEService.creer_indicateur(
        db, indicateur.code, indicateur.nom, indicateur.type_indicateur,
        indicateur.unite, indicateur.objectif
    )


@router.put("/indicateurs/{indicateur_id}/valeur", response_model=IndicateurQHSEResponse)
def mettre_a_jour_valeur(
    indicateur_id: int,
    valeur_actuelle: float,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update indicator value"""
    return IndicateurQHSEService.mettre_a_jour_valeur(db, indicateur_id, valeur_actuelle)


@router.put("/indicateurs/{indicateur_id}", response_model=IndicateurQHSEResponse)
def mettre_a_jour_indicateur(
    indicateur_id: int,
    indicateur: IndicateurQHSEUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update QHSE indicator"""
    i = db.query(IndicateurQHSE).filter(IndicateurQHSE.id == indicateur_id).first()
    if not i:
        raise HTTPException(status_code=404, detail="Indicateur non trouvé")
    
    for field, value in indicateur.model_dump(exclude_unset=True).items():
        setattr(i, field, value)
    
    db.commit()
    db.refresh(i)
    return i


@router.get("/rapports/securite/{annee}", response_model=RapportSecuriteResponse)
def rapport_securite(
    annee: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate safety report"""
    return QHSEReportingService.rapport_securite(db, annee)


# ============ LISTES REELLES (formations, audits, certifications) ============
@router.get("/formations")
def lister_formations_qhse(
    skip: int = 0, limit: int = 200,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    rows = db.query(FormationQHSE).order_by(desc(FormationQHSE.id)).offset(skip).limit(limit).all()
    data = [
        {
            "id": f.id, "numero_formation": f.numero_formation,
            "type_formation": f.type_formation, "titre": f.titre,
            "formateur": f.formateur, "lieu": f.lieu,
            "date_debut": f.date_debut.isoformat() if f.date_debut else None,
            "date_fin": f.date_fin.isoformat() if f.date_fin else None,
            "duree_heures": f.duree_heures, "statut": f.statut,
            "description": f.description,
        } for f in rows
    ]
    return {"data": data, "items": data, "total": len(data)}


@router.get("/audits")
def lister_audits_qhse(
    skip: int = 0, limit: int = 200,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    rows = db.query(AuditQualite).order_by(desc(AuditQualite.id)).offset(skip).limit(limit).all()
    data = [
        {
            "id": a.id, "numero_audit": a.numero_audit,
            "certification_id": a.certification_id, "type_audit": a.type_audit,
            "auditeur": a.auditeur,
            "date_debut": a.date_debut.isoformat() if a.date_debut else None,
            "date_fin": a.date_fin.isoformat() if a.date_fin else None,
            "statut": a.statut, "scope": a.scope,
            "non_conformites": a.non_conformites, "conclusion": a.conclusion,
        } for a in rows
    ]
    return {"data": data, "items": data, "total": len(data)}


@router.get("/certifications")
def lister_certifications_qhse(
    skip: int = 0, limit: int = 200,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    rows = db.query(NormeCertification).order_by(desc(NormeCertification.id)).offset(skip).limit(limit).all()
    data = [
        {
            "id": c.id, "numero_certificat": c.numero_certificat,
            "norme": c.norme.value if hasattr(c.norme, "value") else str(c.norme),
            "organisme": c.organisme,
            "date_obtention": c.date_obtention.isoformat() if c.date_obtention else None,
            "date_expiration": c.date_expiration.isoformat() if c.date_expiration else None,
            "statut": c.statut, "scope": c.scope,
            "resultat_audit": c.resultat_audit,
        } for c in rows
    ]
    return {"data": data, "items": data, "total": len(data)}


# ============ REGISTRE INSPECTIONS QHSE (persistance reelle) ============
QHSE_REGISTRY = "qhse-inspections"


@router.get("")
@router.get("/")
def lister_enregistrements_qhse_root(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Liste des rapports d'inspection QHSE reellement enregistres par la structure."""
    q = db.query(RegistreEntry).filter(RegistreEntry.registry == QHSE_REGISTRY)
    cid = getattr(current_user, "company_id", None)
    if cid is not None:
        q = q.filter(RegistreEntry.company_id.in_([cid, None]))
    rows = q.order_by(desc(RegistreEntry.id)).limit(300).all()
    return [_registre_dict(e) for e in rows]


@router.post("", status_code=status.HTTP_201_CREATED)
@router.post("/", status_code=status.HTTP_201_CREATED)
def creer_enregistrement_qhse_root(
    payload: dict = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Enregistre un rapport d'inspection / signalement QHSE (donnees reelles du formulaire)."""
    entry = RegistreEntry(
        company_id=getattr(current_user, "company_id", None),
        registry=QHSE_REGISTRY,
        reference=payload.pop("reference", None) or _gen_numero("QHS"),
        statut=payload.pop("statut", None) or "ENREISTRE",
        payload=payload,
        created_by=getattr(current_user, "username", None),
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return _registre_dict(entry)


@router.get("/{record_id}")
def lire_enregistrement_qhse(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    e = db.query(RegistreEntry).filter(
        RegistreEntry.id == record_id, RegistreEntry.registry == QHSE_REGISTRY
    ).first()
    if not e:
        raise HTTPException(status_code=404, detail="Enregistrement QHSE introuvable")
    return _registre_dict(e)


@router.put("/{record_id}")
def modifier_enregistrement_qhse(
    record_id: int,
    payload: dict = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    e = db.query(RegistreEntry).filter(
        RegistreEntry.id == record_id, RegistreEntry.registry == QHSE_REGISTRY
    ).first()
    if not e:
        raise HTTPException(status_code=404, detail="Enregistrement QHSE introuvable")
    if "reference" in payload:
        e.reference = payload.pop("reference")
    if "statut" in payload:
        e.statut = payload.pop("statut")
    merged = dict(e.payload or {})
    merged.update(payload)
    e.payload = merged
    db.commit()
    db.refresh(e)
    return _registre_dict(e)


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
def supprimer_enregistrement_qhse(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    e = db.query(RegistreEntry).filter(
        RegistreEntry.id == record_id, RegistreEntry.registry == QHSE_REGISTRY
    ).first()
    if not e:
        raise HTTPException(status_code=404, detail="Enregistrement QHSE introuvable")
    db.delete(e)
    db.commit()


# ============ PERMIS DE TRAVAIL DÉMATÉRIALISÉS ============
@router.post("/permis-travail")
def creer_permis_travail_api(payload: dict):
    """Generate electronic work permit (Hot work, height, confined space) with tripartite validation"""
    from app.services.qhse_service import WorkPermitsIMDGService
    return WorkPermitsIMDGService.creer_permis_travail(payload)


# ============ MATRICE SÉGRÉGATION PRODUITS CHIMIQUES IMDG ============
@router.post("/imdg/segregation")
def verifier_compatibilite_imdg_api(payload: dict):
    """Check dangerous goods segregation compatibility per IMDG Code 41-22"""
    from app.services.qhse_service import WorkPermitsIMDGService
    classes = payload.get("classes_imdg", ["3", "8"])
    return WorkPermitsIMDGService.verifier_segregation_imdg(classes)


# ============ BILAN ANNUEL OFFICIEL CSST & CNPS CAMEROUN ============
@router.get("/csst-cnps/bilan")
def obtenir_bilan_csst_cnps(annee: int = 2026):
    """Generate official CSST / CNPS safety statistics (Frequency Rate TF and Severity Rate TG)"""
    from app.services.qhse_service import WorkPermitsIMDGService
    return WorkPermitsIMDGService.bilan_annuel_csst_cnps(annee)

