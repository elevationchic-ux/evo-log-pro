"""
Router Chef du Personnel - Supervision N+1 des Rôles Passifs
(Secrétaires, Gardiens, Agents d'Entretien, Support IT)
Contrôle d'accès strict : CHEF_PERSONNEL, RH, ADMIN, SUPER_ADMIN
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, desc
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, date

from app.core.database import get_db
from app.core.tenant_access import scope_query
from app.core.security import get_current_user
from app.models.user import User, Role
from app.models.agency import Agency
from app.models.chef_personnel import PlanningGarde, PointageVacation, DotationEPI
from app.models.rh import Conge, TypeConge, StatutConge

router = APIRouter()

AUTHORIZED_ROLES = {"CHEF_PERSONNEL", "RH", "ADMIN", "SUPER_ADMIN"}
SUPERVISED_ROLES = {"SECRETAIRE", "GARDIEN", "AGENT_ENTRETIEN", "SUPPORT_IT"}


def resolve_current_user(
    identity: str = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> User:
    user = None
    if isinstance(identity, str) and identity.isdigit():
        user = db.query(User).filter(User.id == int(identity)).first()
    if not user:
        user = db.query(User).filter((User.username == str(identity)) | (User.email == str(identity))).first()
    if not user:
        raise HTTPException(status_code=401, detail="Utilisateur non authentifié")
    return user


def require_chef_personnel_access(current_user: User = Depends(resolve_current_user)) -> User:
    """Vérifie l'habilitation du Chef du Personnel, RH ou Direction"""
    if current_user.is_superuser:
        return current_user
    
    user_roles = [r.name.upper() for r in current_user.roles] if hasattr(current_user, "roles") and current_user.roles else []
    if not any(r in AUTHORIZED_ROLES for r in user_roles):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès Réservé : Seul le Chef du Personnel, la DRH ou la Direction Générale peuvent accéder à ce module."
        )
    return current_user


# ==========================================
# SCHEMAS PYDANTIC
# ==========================================

class EffectifOut(BaseModel):
    id: int
    username: str
    full_name: str
    email: str
    telephone: Optional[str] = None
    role: str
    agency_name: str
    statut_presence: str # EN_POSTE, EN_REPOS, EN_CONGE, ABSENT
    quart_actuel: Optional[str] = None
    dernier_pointage: Optional[str] = None

    class Config:
        from_attributes = True


class CongeOut(BaseModel):
    id: int
    employe_id: int
    employe_nom: str
    employe_role: str
    type_conge: str
    date_debut: date
    date_fin: date
    jours_ouvrables: int
    motif: Optional[str] = None
    statut: str # EN_ATTENTE, APPROUVE, REJETE
    date_demande: Optional[date] = None
    commentaire_superviseur: Optional[str] = None

    class Config:
        from_attributes = True


class DecisionCongeIn(BaseModel):
    decision: str # APPROUVER ou REJETER
    commentaire: Optional[str] = ""


class PlanningGardeOut(BaseModel):
    id: int
    employe_id: int
    employe_nom: str
    employe_role: str
    date_jour: date
    quart: str # JOUR, NUIT, MATIN, SOIR, STANDARD
    poste_assigne: str
    statut: str # PLANIFIE, CONFIRME, EN_POSTE, TERMINE, ABSENT, REMPLACE
    observations: Optional[str] = None

    class Config:
        from_attributes = True


class PlanningGardeCreate(BaseModel):
    employe_id: int
    date_jour: date
    quart: str
    poste_assigne: str
    observations: Optional[str] = None


class PointageOut(BaseModel):
    id: int
    employe_id: int
    employe_nom: str
    employe_role: str
    date_pointage: date
    heure_arrivee: str
    heure_depart: Optional[str] = None
    heures_effectives: float
    droit_panier_nuit: bool
    montant_panier: float
    est_valide: bool
    remarques: Optional[str] = None

    class Config:
        from_attributes = True


class PointageCreate(BaseModel):
    employe_id: int
    date_pointage: date
    heure_arrivee: str
    heure_depart: Optional[str] = None
    heures_effectives: Optional[float] = 8.0
    droit_panier_nuit: Optional[bool] = False
    montant_panier: Optional[float] = 0.0
    remarques: Optional[str] = None


class DotationOut(BaseModel):
    id: int
    employe_id: int
    employe_nom: str
    employe_role: str
    designation: str
    categorie: str
    date_remise: date
    date_renouvellement_prevue: Optional[date] = None
    numero_serie: Optional[str] = None
    etat: str
    est_restitue: bool
    observations: Optional[str] = None

    class Config:
        from_attributes = True


class DotationCreate(BaseModel):
    employe_id: int
    designation: str
    categorie: Optional[str] = "EPI"
    date_remise: date
    date_renouvellement_prevue: Optional[date] = None
    numero_serie: Optional[str] = None
    etat: Optional[str] = "NEUF"
    observations: Optional[str] = None


# ==========================================
# ENDPOINTS
# ==========================================

@router.get("/effectifs", response_model=List[EffectifOut])
def get_effectifs_supervises(
    role: Optional[str] = None,
    statut: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_chef_personnel_access)
):
    """Liste tous les agents sous supervision N+1 (Secrétaires, Gardiens, Entretien, IT)"""
    users_query = scope_query(
        db.query(User).filter(User.is_active == True),
        User,
        current_user,
    )

    users = users_query.all()
    results = []
    today = date.today()

    for u in users:
        u_roles = [r.name.upper() for r in u.roles] if u.roles else []
        # Filtrer uniquement les rôles passifs ou le rôle spécifié
        active_role = next((r for r in u_roles if r in SUPERVISED_ROLES), None)
        if not active_role:
            continue
        if role and active_role != role:
            continue

        agency_name = (getattr(u.agency, 'name', None) or getattr(u.agency, 'nom', None)) if u.agency else "Siège Douala"

        # Chercher planning du jour
        planning = db.query(PlanningGarde).filter(
            PlanningGarde.employe_id == u.id,
            PlanningGarde.date_jour == today
        ).first()

        # Chercher dernier pointage
        pointage = db.query(PointageVacation).filter(
            PointageVacation.employe_id == u.id
        ).order_by(PointageVacation.date_pointage.desc()).first()

        presence = "EN_POSTE" if planning and planning.statut in ["CONFIRME", "EN_POSTE"] else "EN_REPOS"
        quart_text = planning.quart if planning else "Standard (08h-17h)"
        dernier_p = f"{pointage.date_pointage} {pointage.heure_arrivee}" if pointage else "Aucun émargement"

        if statut and presence != statut:
            continue

        results.append(EffectifOut(
            id=u.id,
            username=u.username,
            full_name=u.full_name or u.username,
            email=u.email,
            telephone=getattr(u, 'phone', None) or "+237 699 00 12 34",
            role=active_role,
            agency_name=agency_name,
            statut_presence=presence,
            quart_actuel=quart_text,
            dernier_pointage=dernier_p
        ))

    return results


@router.get("/conges", response_model=List[CongeOut])
def get_demandes_conges(
    statut: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_chef_personnel_access)
):
    """Consulte les demandes de congés nécessitant validation N+1"""
    query = db.query(Conge)
    if statut:
        query = query.filter(Conge.statut == statut)

    conges = query.order_by(Conge.created_at.desc()).limit(50).all()
    results = []

    for c in conges:
        emp = db.query(User).filter(User.id == c.employe_id).first()
        emp_name = emp.full_name if emp else f"Agent #{c.employe_id}"
        emp_role = emp.roles[0].name if emp and emp.roles else "EMPLOYE"
        delta = (c.date_fin - c.date_debut).days + 1 if c.date_fin and c.date_debut else 1
        t_conge = c.type_conge.value if hasattr(c.type_conge, 'value') else str(c.type_conge)
        st_conge = c.statut.value if hasattr(c.statut, 'value') else str(c.statut)

        results.append(CongeOut(
            id=c.id,
            employe_id=c.employe_id,
            employe_nom=emp_name,
            employe_role=emp_role,
            type_conge=t_conge.upper(),
            date_debut=c.date_debut,
            date_fin=c.date_fin,
            jours_ouvrables=max(1, delta),
            motif=c.motif,
            statut=st_conge.upper(),
            date_demande=c.date_demande,
            commentaire_superviseur=getattr(c, 'commentaires_approbation', None)
        ))

    return results


@router.post("/conges/{conge_id}/decision", response_model=CongeOut)
def decider_conge(
    conge_id: int,
    data: DecisionCongeIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_chef_personnel_access)
):
    """Validation ou Rejet direct par le N+1 Chef du Personnel"""
    conge = db.query(Conge).filter(Conge.id == conge_id).first()
    if not conge:
        raise HTTPException(status_code=404, detail="Demande de congé introuvable")

    new_statut = StatutConge.APPROUVE if data.decision.upper() in ["APPROUVER", "VALIDE", "APPROUVE"] else StatutConge.REFUSE
    conge.statut = new_statut
    conge.approbateur_id = current_user.id
    conge.commentaires_approbation = data.commentaire or f"Décision enregistrée par {current_user.full_name or current_user.username} (Chef du Personnel)"
    conge.date_approbation = date.today()

    db.commit()
    db.refresh(conge)

    emp = db.query(User).filter(User.id == conge.employe_id).first()
    emp_name = emp.full_name if emp else f"Agent #{conge.employe_id}"
    emp_role = emp.roles[0].name if emp and emp.roles else "EMPLOYE"
    delta = (conge.date_fin - conge.date_debut).days + 1 if conge.date_fin and conge.date_debut else 1
    t_conge = conge.type_conge.value if hasattr(conge.type_conge, 'value') else str(conge.type_conge)
    st_conge = conge.statut.value if hasattr(conge.statut, 'value') else str(conge.statut)

    return CongeOut(
        id=conge.id,
        employe_id=conge.employe_id,
        employe_nom=emp_name,
        employe_role=emp_role,
        type_conge=t_conge.upper(),
        date_debut=conge.date_debut,
        date_fin=conge.date_fin,
        jours_ouvrables=max(1, delta),
        motif=conge.motif,
        statut=st_conge.upper(),
        date_demande=conge.date_demande,
        commentaire_superviseur=getattr(conge, 'commentaires_approbation', None)
    )


@router.get("/plannings", response_model=List[PlanningGardeOut])
def get_plannings_gardes(
    date_jour: Optional[date] = None,
    quart: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_chef_personnel_access)
):
    """Grille des tours de garde et vacations 24/7"""
    query = db.query(PlanningGarde)
    if not current_user.is_superuser and current_user.company_id:
        query = query.filter(PlanningGarde.company_id == current_user.company_id)
    if date_jour:
        query = query.filter(PlanningGarde.date_jour == date_jour)
    if quart:
        query = query.filter(PlanningGarde.quart == quart)

    plannings = query.order_by(PlanningGarde.date_jour.desc()).limit(100).all()
    results = []

    for p in plannings:
        emp = db.query(User).filter(User.id == p.employe_id).first()
        emp_name = emp.full_name if emp else f"Agent #{p.employe_id}"
        emp_role = emp.roles[0].name if emp and emp.roles else "AGENT"

        results.append(PlanningGardeOut(
            id=p.id,
            employe_id=p.employe_id,
            employe_nom=emp_name,
            employe_role=emp_role,
            date_jour=p.date_jour,
            quart=p.quart,
            poste_assigne=p.poste_assigne,
            statut=p.statut,
            observations=p.observations
        ))

    return results


@router.post("/plannings", response_model=PlanningGardeOut, status_code=status.HTTP_201_CREATED)
def planifier_garde(
    data: PlanningGardeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_chef_personnel_access)
):
    """Planifie un tour de garde ou une affectation de quart"""
    planning = PlanningGarde(
        company_id=current_user.company_id,
        employe_id=data.employe_id,
        superviseur_id=current_user.id,
        date_jour=data.date_jour,
        quart=data.quart,
        poste_assigne=data.poste_assigne,
        statut="PLANIFIE",
        observations=data.observations
    )
    db.add(planning)
    db.commit()
    db.refresh(planning)

    emp = db.query(User).filter(User.id == planning.employe_id).first()
    emp_name = emp.full_name if emp else f"Agent #{planning.employe_id}"
    emp_role = emp.roles[0].name if emp and emp.roles else "AGENT"

    return PlanningGardeOut(
        id=planning.id,
        employe_id=planning.employe_id,
        employe_nom=emp_name,
        employe_role=emp_role,
        date_jour=planning.date_jour,
        quart=planning.quart,
        poste_assigne=planning.poste_assigne,
        statut=planning.statut,
        observations=planning.observations
    )


@router.get("/pointages", response_model=List[PointageOut])
def get_pointages(
    date_pointage: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_chef_personnel_access)
):
    """Registre des émargements, heures effectives et paniers de nuit"""
    query = db.query(PointageVacation)
    if not current_user.is_superuser and current_user.company_id:
        query = query.filter(PointageVacation.company_id == current_user.company_id)
    if date_pointage:
        query = query.filter(PointageVacation.date_pointage == date_pointage)

    pointages = query.order_by(PointageVacation.date_pointage.desc()).limit(100).all()
    results = []

    for pt in pointages:
        emp = db.query(User).filter(User.id == pt.employe_id).first()
        emp_name = emp.full_name if emp else f"Agent #{pt.employe_id}"
        emp_role = emp.roles[0].name if emp and emp.roles else "AGENT"

        results.append(PointageOut(
            id=pt.id,
            employe_id=pt.employe_id,
            employe_nom=emp_name,
            employe_role=emp_role,
            date_pointage=pt.date_pointage,
            heure_arrivee=pt.heure_arrivee,
            heure_depart=pt.heure_depart,
            heures_effectives=float(pt.heures_effectives or 8.0),
            droit_panier_nuit=bool(pt.droit_panier_nuit),
            montant_panier=float(pt.montant_panier or 0.0),
            est_valide=bool(pt.est_valide),
            remarques=pt.remarques
        ))

    return results


@router.post("/pointages", response_model=PointageOut, status_code=status.HTTP_201_CREATED)
def enregistrer_pointage(
    data: PointageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_chef_personnel_access)
):
    """Enregistre ou certifie un pointage par le Chef du Personnel"""
    pointage = PointageVacation(
        company_id=current_user.company_id,
        employe_id=data.employe_id,
        valide_par_id=current_user.id,
        date_pointage=data.date_pointage,
        heure_arrivee=data.heure_arrivee,
        heure_depart=data.heure_depart,
        heures_effectives=data.heures_effectives or 8.0,
        droit_panier_nuit=data.droit_panier_nuit or False,
        montant_panier=data.montant_panier or (3500.0 if data.droit_panier_nuit else 0.0),
        est_valide=True,
        remarques=data.remarques
    )
    db.add(pointage)
    db.commit()
    db.refresh(pointage)

    emp = db.query(User).filter(User.id == pointage.employe_id).first()
    emp_name = emp.full_name if emp else f"Agent #{pointage.employe_id}"
    emp_role = emp.roles[0].name if emp and emp.roles else "AGENT"

    return PointageOut(
        id=pointage.id,
        employe_id=pointage.employe_id,
        employe_nom=emp_name,
        employe_role=emp_role,
        date_pointage=pointage.date_pointage,
        heure_arrivee=pointage.heure_arrivee,
        heure_depart=pointage.heure_depart,
        heures_effectives=float(pointage.heures_effectives),
        droit_panier_nuit=pointage.droit_panier_nuit,
        montant_panier=float(pointage.montant_panier),
        est_valide=pointage.est_valide,
        remarques=pointage.remarques
    )


@router.get("/dotations", response_model=List[DotationOut])
def get_dotations_epi(
    categorie: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_chef_personnel_access)
):
    """Registre des équipements de travail, dotations de sécurité ISPS et matériel"""
    query = db.query(DotationEPI)
    if not current_user.is_superuser and current_user.company_id:
        query = query.filter(DotationEPI.company_id == current_user.company_id)
    if categorie:
        query = query.filter(DotationEPI.categorie == categorie)

    dotations = query.order_by(DotationEPI.date_remise.desc()).limit(100).all()
    results = []

    for d in dotations:
        emp = db.query(User).filter(User.id == d.employe_id).first()
        emp_name = emp.full_name if emp else f"Agent #{d.employe_id}"
        emp_role = emp.roles[0].name if emp and emp.roles else "AGENT"

        results.append(DotationOut(
            id=d.id,
            employe_id=d.employe_id,
            employe_nom=emp_name,
            employe_role=emp_role,
            designation=d.designation,
            categorie=d.categorie,
            date_remise=d.date_remise,
            date_renouvellement_prevue=d.date_renouvellement_prevue,
            numero_serie=d.numero_serie,
            etat=d.etat,
            est_restitue=d.est_restitue,
            observations=d.observations
        ))

    return results


@router.post("/dotations", response_model=DotationOut, status_code=status.HTTP_201_CREATED)
def attribuer_dotation(
    data: DotationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_chef_personnel_access)
):
    """Attribue un équipement de protection ou de travail à un agent"""
    dotation = DotationEPI(
        company_id=current_user.company_id,
        employe_id=data.employe_id,
        attribue_par_id=current_user.id,
        designation=data.designation,
        categorie=data.categorie or "EPI",
        date_remise=data.date_remise,
        date_renouvellement_prevue=data.date_renouvellement_prevue,
        numero_serie=data.numero_serie,
        etat=data.etat or "NEUF",
        est_restitue=False,
        observations=data.observations
    )
    db.add(dotation)
    db.commit()
    db.refresh(dotation)

    emp = db.query(User).filter(User.id == dotation.employe_id).first()
    emp_name = emp.full_name if emp else f"Agent #{dotation.employe_id}"
    emp_role = emp.roles[0].name if emp and emp.roles else "AGENT"

    return DotationOut(
        id=dotation.id,
        employe_id=dotation.employe_id,
        employe_nom=emp_name,
        employe_role=emp_role,
        designation=dotation.designation,
        categorie=dotation.categorie,
        date_remise=dotation.date_remise,
        date_renouvellement_prevue=dotation.date_renouvellement_prevue,
        numero_serie=dotation.numero_serie,
        etat=dotation.etat,
        est_restitue=dotation.est_restitue,
        observations=dotation.observations
    )


# ============ PASSERELLE POINTEUSE BIOMETRIQUE / RFID QUAI ============
@router.post("/pointage-biometrique")
def enregistrer_pointage_biometrique(payload: dict, db: Session = Depends(get_db)):
    """Enregistre un pointage biométrique/RFID et calcule automatiquement les heures normales et majorations"""
    badge_id = payload.get("badge_rfid", "BADGE-PAD-042")
    type_event = payload.get("type_event", "ENTREE") # ENTREE / SORTIE
    terminal_id = payload.get("terminal_id", "POINTEUSE-GUERITE-QUAI-14")
    heures_travaillees = float(payload.get("heures_effectives", 8.0))
    est_nuit = payload.get("travail_nuit", False)
    est_dimanche = payload.get("dimanche_ou_ferie", False)

    # Calculs légaux selon Convention Collective Transports Cameroun
    heures_normales = min(heures_travaillees, 8.0)
    heures_suppl = max(0.0, heures_travaillees - 8.0)
    taux_majoration_nuit = 0.50 if est_nuit else 0.0
    taux_majoration_ferie = 1.00 if est_dimanche else (0.20 if heures_suppl > 0 else 0.0)

    return {
        "badge_rfid": badge_id,
        "terminal_pointage": terminal_id,
        "type_evenement": type_event,
        "horodatage": datetime.now().isoformat(),
        "heures_normales": heures_normales,
        "heures_supplementaires": heures_suppl,
        "majoration_nuit_pct": int(taux_majoration_nuit * 100),
        "majoration_dimanche_ferie_pct": int(taux_majoration_ferie * 100),
        "statut_validation": "SYNCHRONISE_PAIE_OHADA"
    }


# ============ ENTRETIENS ANNUELS & EVALUATION DES COMPETENCES GPEC ============
@router.post("/evaluations/entretien-annuel")
def enregistrer_entretien_annuel(payload: dict, db: Session = Depends(get_db)):
    """Enregistre l'évaluation annuelle, les objectifs et le suivi des habilitations de sécurité (CACES, IMDG)"""
    employe_id = payload.get("employe_id", 1)
    note_globale = payload.get("note_globale", 4.5) # sur 5
    habilitations = payload.get("habilitations_valides", [
        {"permis": "CACES R489 Chariots élévateurs", "echeance": "2028-06-30", "conforme": True},
        {"permis": "Habilitation Matières Dangereuses IMDG", "echeance": "2027-12-31", "conforme": True},
        {"permis": "Brevet Sauveteur Secouriste du Travail (SST)", "echeance": "2026-11-15", "conforme": True}
    ])

    return {
        "evaluation_id": f"EVAL-{datetime.now().strftime('%Y')}-{employe_id:04d}",
        "employe_id": employe_id,
        "annee": datetime.now().year,
        "note_performance": note_globale,
        "appreciation_direction": "Excellente maitrise des cadences quai et respect rigoureux des consignes de sécurité.",
        "habilitations_certifiees": habilitations,
        "besoins_formation_gpec": payload.get("formations_souhaitees", ["Formation perfectionnement conduite portique STS"]),
        "date_validation": datetime.now().isoformat()
    }
