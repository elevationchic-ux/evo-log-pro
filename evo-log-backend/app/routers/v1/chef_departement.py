"""Espace departement (Phase 3/4 — niveau 2, Chef de departement).

Perimetre strict : un chef de departement (role_level 2) ne voit et ne pilote
QUE les collaborateurs de SON departement. L'Admin Entreprise (1) et le CADC (0)
peuvent cibler n'importe quel departement, mais toujours a l'interieur de leur
entreprise (403 cross-tenant), ce que verifie ``_scoped_department``.

Garde (invisibilite double, cf. plan) :
- ``require_department_head`` (utils/rbac.py) : niveau <= 2 ; un niveau 2 doit
  porter un ``department_id`` ; niveau 3 -> 403.
- ``_scoped_department`` : epingle un chef a son departement ; un admin/CADC
  doit passer un ``department_id`` explicite et l'appartenance d'entreprise est
  controlee.

Tranche A (lecture) : roster humain + fiche du departement. Tranche B (ecriture) :
- un chef (2) AFFECTE / RETIRE des COLLABORATEURS (niveau 3) de SON departement ;
  il ne touche jamais un niveau 1/2, ni un compte d'une autre entreprise, ni un
  Super Admin ;
- l'ALLOCATION des modules d'un departement releve de l'Admin Entreprise (1) /
  CADC (0) UNIQUEMENT (un chef ne se auto-grantit pas ; cf. PUT /modules 403) et reste STRICTEMENT
  bornee par ``Company.modules_actives`` (un departement ne peut pas depasser son
  entreprise).
Phase 4 (Tranche A, lecture) : PLANNING + PRESENCE du departement scopes par le
MEME ``_scoped_department`` (modeles chef_personnel PlanningGarde / PointageVacation).
Phase 4 (Tranche B, ecriture) : un chef peut CREER / MODIFIER / SUPPRIMER les tours
de garde (PlanningGarde) de SES collaborateurs, sous la contrainte de publication
"au mercredi de la semaine precedente" ; il peut aussi VALIDER un emargement
(PointageVacation) d'un membre. L'ecriture ne sort jamais du perimetre departement.
"""
import json
from datetime import date as _date, timedelta
from typing import Any, Dict, List, Optional, Tuple

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.chef_personnel import PlanningGarde, PointageVacation
from app.models.tenant import Company, Department
from app.models.user import User
from app.utils.rbac import _is_superadmin, require_department_head

router = APIRouter(dependencies=[Depends(require_department_head)])


def _loads(raw: Optional[str], default: Any) -> Any:
    if not raw:
        return default
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return default


def _week_bounds(semaine: Optional[str]) -> Tuple[_date, _date]:
    """Borne [lundi, dimanche] d'une semaine ISO ``AAAA-WNN`` (defaut : semaine courante).

    ``date.fromisocalendar`` evite le piege du format ``%W`` (semaine non-ISO) :
    une semaine invalide ou un format inattendu renvoient un 400 explicite plutot
    qu'une plage silencieusement faussée.
    """
    if not semaine:
        today = _date.today()
        iso = today.isocalendar()
        start = _date.fromisocalendar(iso[0], iso[1], 1)
        end = _date.fromisocalendar(iso[0], iso[1], 7)
        return start, end
    try:
        year_s, week_s = semaine.upper().split("-W", 1)
        year = int(year_s)
        week = int(week_s)
        start = _date.fromisocalendar(year, week, 1)
        end = _date.fromisocalendar(year, week, 7)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=400,
            detail="Format de semaine invalide (attendu AAAA-WNN, ex. 2026-W40)",
        )
    return start, end


def _parse_date(value: Optional[str]) -> _date:
    """Date ``AAAA-MM-JJ`` (defaut : aujourd'hui). Refuse un format invalide (400)."""
    if not value:
        return _date.today()
    try:
        return _date.fromisoformat(value.strip())
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=400,
            detail="Format de date invalide (attendu AAAA-MM-JJ)",
        )


def _scoped_department(db: Session, current: User, requested: Optional[int]) -> Department:
    """Resout le departement cible selon le niveau de l'appelant.

    - Chef (2) : epingle a ``current.department_id`` ; un ``requested`` divergent
      -> 403 (il ne peut pas telecharger un autre departement).
    - Admin entreprise (1) : ``department_id`` requis ; le departement doit
      appartenir a SON entreprise, sinon 403.
    - CADC (0) : ``department_id`` explicite requis (un super-admin ne porte
      aucune entreprise/departement par defaut).
    """
    own_level = getattr(current, "role_level", 99)

    if _is_superadmin(current):
        if not requested:
            raise HTTPException(
                status_code=400,
                detail="department_id requis pour un Super Admin",
            )
        dept = db.query(Department).filter(Department.id == requested).first()
        if not dept:
            raise HTTPException(status_code=404, detail="Departement introuvable")
        return dept

    if own_level == 2:
        own_dept_id = getattr(current, "department_id", None)
        if requested and requested != own_dept_id:
            raise HTTPException(
                status_code=403,
                detail="Hors de votre departement",
            )
        dept = db.query(Department).filter(Department.id == own_dept_id).first()
        if not dept:
            raise HTTPException(status_code=403, detail="Departement introuvable pour ce compte")
        return dept

    # Admin entreprise (1) : gere n'importe quel departement de SON entreprise.
    if not requested:
        raise HTTPException(
            status_code=400,
            detail="department_id requis (choisissez un departement de votre entreprise)",
        )
    dept = db.query(Department).filter(Department.id == requested).first()
    if not dept:
        raise HTTPException(status_code=404, detail="Departement introuvable")
    if dept.company_id != getattr(current, "company_id", None):
        raise HTTPException(
            status_code=403,
            detail="Departement d'une autre entreprise",
        )
    return dept


def _member_dict(u: User) -> Dict[str, Any]:
    return {
        "id": u.id,
        "username": u.username,
        "email": u.email,
        "full_name": u.full_name,
        "matricule": u.matricule,
        "job_title": u.job_title,
        "phone": u.phone,
        "role_level": u.role_level,
        "is_active": u.is_active,
        "department_id": u.department_id,
        "roles": [r.name for r in (u.roles or [])],
    }


def _guard_target(db: Session, current: User, dept: Department, member_id: int) -> User:
    """Cible d'une ecriture membre : existe, meme entreprise que le departement,
    et jamais un compte Super Admin.

    Un chef de departement (niveau 2) ne pilote QUE des collaborateurs (niveau 3) :
    il ne peut ni deplacer un pair/superieur (niveau 1 ou 2), ni toucher un autre
    tenant. L'admin entreprise (1) et le CADC (0) gerent tout compte non-superieur
    de leur perimetre (regle alignee sur company_admin).
    """
    target = db.query(User).filter(User.id == member_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="Utilisateur non trouve")
    if getattr(target, "company_id", None) != dept.company_id:
        raise HTTPException(
            status_code=403,
            detail="Collaborateur hors de l'entreprise de ce departement",
        )
    if getattr(target, "role_level", 99) == 0:
        raise HTTPException(status_code=403, detail="Compte Super Admin non modifiable ici")
    if getattr(current, "role_level", 99) == 2 and getattr(target, "role_level", 99) != 3:
        raise HTTPException(
            status_code=403,
            detail="Un chef de departement ne pilote que des collaborateurs (niveau 3)",
        )
    return target


@router.get("/overview", summary="Fiche de mon departement (nom, modules, effectif)")
def department_overview(
    department_id: Optional[int] = Query(None, description="Reserve admin/CADC ; ignore pour un chef"),
    db: Session = Depends(get_db),
    current: User = Depends(require_department_head),
):
    dept = _scoped_department(db, current, department_id)
    members = (
        db.query(User)
        .filter(User.department_id == dept.id, User.company_id == dept.company_id)
        .all()
    )
    manager = None
    if dept.manager_id:
        mgr = db.query(User).filter(User.id == dept.manager_id).first()
        if mgr:
            manager = {"id": mgr.id, "username": mgr.username, "full_name": mgr.full_name}
    return {
        "id": dept.id,
        "company_id": dept.company_id,
        "code": dept.code,
        "nom": dept.nom,
        "description": dept.description,
        "modules_allowed": _loads(dept.modules_allowed, []),
        "effectif": len(members),
        "manager": manager,
        "is_active": dept.is_active,
        "role_level_callant": current.role_level,
    }


@router.get("/membres", summary="Lister les collaborateurs de mon departement")
def list_members(
    department_id: Optional[int] = Query(None, description="Reserve admin/CADC ; ignore pour un chef"),
    search: Optional[str] = Query(None),
    include_inactive: bool = Query(True, description="Inclure les comptes desactives"),
    db: Session = Depends(get_db),
    current: User = Depends(require_department_head),
):
    """Roster humain du departement, scope par ``department_id`` ET ``company_id``.

    Le chef de departement (2) ne peut jamais telecharger un autre departement :
    ``_scoped_department`` l'y epingle. On filtre aussi sur ``company_id`` pour
    qu'un identifiant de departement devine ne fuite jamais une autre entreprise.
    """
    dept = _scoped_department(db, current, department_id)
    q = db.query(User).filter(
        User.department_id == dept.id,
        User.company_id == dept.company_id,
    )
    if not include_inactive:
        q = q.filter(User.is_active.is_(True))
    if search:
        like = f"%{search.strip()}%"
        q = q.filter(
            (User.username.ilike(like))
            | (User.email.ilike(like))
            | (User.full_name.ilike(like))
            | (User.matricule.ilike(like))
        )
    return [_member_dict(u) for u in q.order_by(User.id.asc()).all()]


@router.get("/candidats", summary="Collaborateurs mobilisables pour mon departement")
def list_candidates(
    department_id: Optional[int] = Query(None, description="Reserve admin/CADC ; ignore pour un chef"),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current: User = Depends(require_department_head),
):
    """Niveaux 3 de l'entreprise pas encore rattaches au departement resolu.

    Lit le MEME perimetre que l'action d'affectation : uniquement des
    collaborateurs (niveau 3) de la propre entreprise du departement, jamais un
    niveau 1/2/Super Admin, et jamais deja dans ce departement. Le chef ne fait
    que remonter la liste vers laquelle sa propre competence d'affectation
    l'autorise a ecrire.
    """
    dept = _scoped_department(db, current, department_id)
    q = db.query(User).filter(
        User.company_id == dept.company_id,
        User.role_level == 3,
        User.is_active.is_(True),
        or_(User.department_id.is_(None), User.department_id != dept.id),
    )
    if search:
        like = f"%{search.strip()}%"
        q = q.filter(
            (User.username.ilike(like))
            | (User.email.ilike(like))
            | (User.full_name.ilike(like))
            | (User.matricule.ilike(like))
        )
    return [_member_dict(u) for u in q.order_by(User.username.asc()).all()]


# ── Tranche B : ecritures (affectation / retrait de membres, allocation modules) ──
class DepartmentModulesPayload(BaseModel):
    modules: List[str] = Field(default_factory=list, description="Cles de modules autorisees pour ce departement")


@router.post(
    "/membres/{member_id}/affecter",
    summary="Affecter un collaborateur a mon departement",
)
def affect_member(
    member_id: int,
    department_id: Optional[int] = Query(None, description="Reserve admin/CADC ; ignore pour un chef"),
    db: Session = Depends(get_db),
    current: User = Depends(require_department_head),
):
    """Rattache ``member_id`` au departement resolu (epingle au dept du chef).

    Un chef ne peut que faire ENTRER un collaborateur (niveau 3) de SON entreprise
    dans SON departement ; un admin/CADC peut placer un niveau 2/3 dans n'importe
    quel departement de son entreprise.
    """
    dept = _scoped_department(db, current, department_id)
    target = _guard_target(db, current, dept, member_id)
    previous = target.department_id
    target.department_id = dept.id
    db.commit()
    db.refresh(target)
    return {
        "id": target.id,
        "department_id": target.department_id,
        "previous_department_id": previous,
        "member": _member_dict(target),
    }


@router.post(
    "/membres/{member_id}/retirer",
    summary="Retirer un collaborateur de mon departement",
)
def remove_member(
    member_id: int,
    department_id: Optional[int] = Query(None, description="Reserve admin/CADC ; ignore pour un chef"),
    db: Session = Depends(get_db),
    current: User = Depends(require_department_head),
):
    """Decroche ``member_id`` du departement resolu (``department_id`` -> None).

    Le collaborateur doit ACTUELLEMENT appartenir a ce departement ; on ne retire
    jamais quelqu'un d'un departement qui n'est pas le sien, et jamais de soi-meme.
    """
    dept = _scoped_department(db, current, department_id)
    target = _guard_target(db, current, dept, member_id)
    if target.id == current.id:
        raise HTTPException(status_code=400, detail="Impossible de vous retirer vous-meme")
    if target.department_id != dept.id:
        raise HTTPException(
            status_code=400,
            detail="Ce collaborateur n'appartient pas a ce departement",
        )
    target.department_id = None
    db.commit()
    db.refresh(target)
    return {"id": target.id, "department_id": None, "member": _member_dict(target)}


@router.put(
    "/modules",
    summary="Definir les modules autorises d'un departement (admin entreprise / CADC)",
)
def set_department_modules(
    payload: DepartmentModulesPayload,
    department_id: Optional[int] = Query(None, description="Reserve admin/CADC ; ignore pour un chef"),
    db: Session = Depends(get_db),
    current: User = Depends(require_department_head),
):
    """Allocation des modules d'un departement — GARELEE aux niveaux <= 1.

    Un chef (niveau 2) ne peut pas se auto-grantir un module : toute ecriture ici
    est refusee 403. Les modules demandes doivent etre SOUS-ENSEMBLE des modules
    alloues a l'entreprise (``Company.modules_actives``) : un departement ne peut
    jamais depasser son tenant.
    """
    if getattr(current, "role_level", 99) == 2 and not _is_superadmin(current):
        raise HTTPException(
            status_code=403,
            detail="Allocation des modules reservee a l'Admin Entreprise / CADC",
        )
    dept = _scoped_department(db, current, department_id)
    company = db.query(Company).filter(Company.id == dept.company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Entreprise du departement introuvable")

    allocated = {str(m).lower() for m in _loads(company.modules_actives, [])}
    # Dedoupage conservant l'ordre, normalise en minuscules.
    requested: List[str] = []
    for raw in payload.modules:
        mod = str(raw).strip().lower()
        if mod and mod not in requested:
            requested.append(mod)
    for mod in requested:
        if mod not in allocated:
            raise HTTPException(
                status_code=400,
                detail=f"Module non alloue a l'entreprise : {mod}",
            )
    dept.modules_allowed = json.dumps(requested, ensure_ascii=False)
    db.commit()
    db.refresh(dept)
    return {"id": dept.id, "modules_allowed": requested}


# ── Phase 4 (Tranche A, lecture) : planning + presence du departement, scopes ──
def _department_member_ids(db: Session, dept: Department) -> List[int]:
    """Identifiants des collaborateurs rattaches au departement (meme entreprise).

    La liste des MEMBRES est la source de verite du perimetre : PlanningGarde /
    PointageVacation sont filtres sur ces ids, ce qui cloisonne automatiquement un
    autre departement (et une autre entreprise) hors du champ.
    """
    return [
        uid for (uid,) in db.query(User.id).filter(
            User.department_id == dept.id,
            User.company_id == dept.company_id,
        ).all()
    ]


@router.get(
    "/planning",
    summary="Planning (tours de garde) des collaborateurs de mon departement",
)
def department_planning(
    semaine: Optional[str] = Query(None, description="Semaine ISO AAAA-WNN ; defaut : semaine courante"),
    department_id: Optional[int] = Query(None, description="Reserve admin/CADC ; ignore pour un chef"),
    db: Session = Depends(get_db),
    current: User = Depends(require_department_head),
):
    """Tours de garde (``PlanningGarde``) des membres du departement sur la semaine.

    Scope identique au reste de l'espace : un chef est epingle a SON departement ;
    un admin/CADC cible un departement de son entreprise. Aucun employe hors du
    departement n'apparait (filtre sur les identifiants des membres).
    """
    dept = _scoped_department(db, current, department_id)
    start, end = _week_bounds(semaine)
    member_ids = _department_member_ids(db, dept)

    lignes: List[Dict[str, Any]] = []
    if member_ids:
        rows = (
            db.query(PlanningGarde, User)
            .join(User, User.id == PlanningGarde.employe_id)
            .filter(
                PlanningGarde.employe_id.in_(member_ids),
                PlanningGarde.date_jour >= start,
                PlanningGarde.date_jour <= end,
            )
            .order_by(PlanningGarde.date_jour.asc(), User.username.asc())
            .all()
        )
        for pg, emp in rows:
            lignes.append({
                "id": pg.id,
                "employe_id": emp.id,
                "employe_username": emp.username,
                "employe_nom": emp.full_name or emp.username,
                "date_jour": pg.date_jour.isoformat() if pg.date_jour else None,
                "quart": pg.quart,
                "poste_assigne": pg.poste_assigne,
                "statut": pg.statut,
                "observations": pg.observations,
            })

    iso = start.isocalendar()
    return {
        "departement_id": dept.id,
        "departement_nom": dept.nom,
        "semaine": semaine or f"{iso[0]}-W{iso[1]:02d}",
        "du": start.isoformat(),
        "au": end.isoformat(),
        "lignes": lignes,
    }


@router.get(
    "/presence",
    summary="Presence / pointage du jour des collaborateurs de mon departement",
)
def department_presence(
    date: Optional[str] = Query(None, description="Date AAAA-MM-JJ ; defaut : aujourd'hui"),
    department_id: Optional[int] = Query(None, description="Reserve admin/CADC ; ignore pour un chef"),
    db: Session = Depends(get_db),
    current: User = Depends(require_department_head),
):
    """Etat de presence par collaborateur du departement, pour une journee donnee.

    Le statut est DEDUIT des lignes reelles, jamais invente :
      - ``PRESENT``      : une pointe (``PointageVacation``) existe ce jour ;
      - ``ATTENDU``      : un tour de garde est planifie mais pas encore pointe ;
      - ``NON_PLANIFIE`` : ni pointe ni planification ce jour.
    Perimetre = membres du departement resolu uniquement (cloisonnement departement
    et entreprise garanti par le filtre sur les identifiants des membres).
    """
    dept = _scoped_department(db, current, department_id)
    day = _parse_date(date)
    members = (
        db.query(User)
        .filter(User.department_id == dept.id, User.company_id == dept.company_id)
        .order_by(User.username.asc())
        .all()
    )
    ids = [u.id for u in members]

    plan_map: Dict[int, PlanningGarde] = {}
    point_map: Dict[int, PointageVacation] = {}
    if ids:
        for pg in db.query(PlanningGarde).filter(
            PlanningGarde.employe_id.in_(ids), PlanningGarde.date_jour == day
        ).all():
            plan_map.setdefault(pg.employe_id, pg)
        for pv in db.query(PointageVacation).filter(
            PointageVacation.employe_id.in_(ids), PointageVacation.date_pointage == day
        ).all():
            point_map.setdefault(pv.employe_id, pv)

    collaborateurs: List[Dict[str, Any]] = []
    synthese = {"effectif": len(members), "presents": 0, "attendus": 0, "non_planifies": 0}
    for u in members:
        pg = plan_map.get(u.id)
        pv = point_map.get(u.id)
        if pv is not None:
            presence = "PRESENT"
            synthese["presents"] += 1
        elif pg is not None:
            presence = "ATTENDU"
            synthese["attendus"] += 1
        else:
            presence = "NON_PLANIFIE"
            synthese["non_planifies"] += 1
        collaborateurs.append({
            "employe_id": u.id,
            "username": u.username,
            "full_name": u.full_name or u.username,
            "planifie": pg is not None,
            "quart": pg.quart if pg is not None else None,
            "poste_assigne": pg.poste_assigne if pg is not None else None,
            "pointe": pv is not None,
            "heure_arrivee": pv.heure_arrivee if pv is not None else None,
            "heure_depart": pv.heure_depart if pv is not None else None,
            "heures_effectives": float(pv.heures_effectives) if (pv is not None and pv.heures_effectives is not None) else None,
            "est_valide": bool(pv.est_valide) if pv is not None else None,
            "presence": presence,
        })

    return {
        "departement_id": dept.id,
        "departement_nom": dept.nom,
        "date": day.isoformat(),
        "collaborateurs": collaborateurs,
        "synthese": synthese,
    }


# ── Phase 4 (Tranche B, ecriture) : planning + presence ──────────────────────
_VALID_QUARTS = frozenset({"JOUR", "NUIT", "MATIN", "SOIR", "STANDARD"})
_VALID_STATUTS = frozenset({"PLANIFIE", "CONFIRME", "EN_POSTE", "TERMINE", "ABSENT", "REMPLACE"})


class PlanningCreatePayload(BaseModel):
    employe_id: int = Field(..., description="Collaborateur du departement")
    date_jour: str = Field(..., description="Date AAAA-MM-JJ")
    quart: str = Field(..., description="JOUR | NUIT | MATIN | SOIR | STANDARD")
    poste_assigne: str = Field(..., max_length=100)
    statut: Optional[str] = Field("PLANIFIE", description="Defaut PLANIFIE ; CONFIRME est soumis au delai du mercredi")
    observations: Optional[str] = None


class PlanningUpdatePayload(BaseModel):
    quart: Optional[str] = None
    poste_assigne: Optional[str] = None
    statut: Optional[str] = None
    observations: Optional[str] = None


def _check_publication_deadline(date_jour: _date, new_statut: Optional[str]) -> None:
    """Contrainte "au mercredi de la semaine precedente".

    Un tour de garde dont la date_jour tombe dans une semaine ISO FUTURE ne peut
    passer en statut CONFIRME (publication) que si l'on est au plus mercredi de
    la semaine ISO precedente. Au-dela, la fenetre de publication est fermée ;
    le tour reste en PLANIFIE (brouillon) — modification libre, mais pas validation.
    """
    if (new_statut or "").upper() != "CONFIRME":
        return  # Seule la publication est concernee.
    today = _date.today()
    iso_target = date_jour.isocalendar()  # (year, week, weekday)
    iso_today = today.isocalendar()
    # Si la date est dans la semaine courante ou passee, pas de contrainte.
    target_key = (iso_target[0], iso_target[1])
    today_key = (iso_today[0], iso_today[1])
    if target_key <= today_key:
        return
    # Deadline : mercredi de la semaine PRECEDANT celle du target.
    prev_week = iso_target[1] - 1
    prev_year = iso_target[0]
    if prev_week < 1:
        prev_year -= 1
        prev_week = 52  # Approximation sure ; un calendrier reel max 53.
        # Verifier si l'annee precedente a 53 semaines.
        try:
            _date.fromisocalendar(prev_year, 53, 1)
            prev_week = 53
        except ValueError:
            pass
    try:
        deadline = _date.fromisocalendar(prev_year, prev_week, 3)  # Mercredi
    except ValueError:
        raise HTTPException(status_code=400, detail="Semaine cible invalide")
    if today > deadline:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Publication fermee : le planning de la semaine "
                f"{iso_target[0]}-W{iso_target[1]:02d} devait etre confirme "
                f"au plus tard le {deadline.isoformat()} (mercredi precedent). "
                "Le tour reste en statut PLANIFIE."
            ),
        )


def _guard_planning_in_dept(db: Session, planning_id: int, dept: Department) -> PlanningGarde:
    """Le PlanningGarde existe ET son employe est membre du departement resolu."""
    pg = db.query(PlanningGarde).filter(PlanningGarde.id == planning_id).first()
    if not pg:
        raise HTTPException(status_code=404, detail="Tour de garde introuvable")
    member_ids = _department_member_ids(db, dept)
    if pg.employe_id not in member_ids:
        raise HTTPException(
            status_code=403,
            detail="Ce tour de garde ne concerne pas un collaborateur de votre departement",
        )
    return pg


@router.post(
    "/planning",
    summary="Creer un tour de garde pour un collaborateur du departement",
    status_code=status.HTTP_201_CREATED,
)
def create_planning(
    payload: PlanningCreatePayload,
    department_id: Optional[int] = Query(None, description="Reserve admin/CADC ; ignore pour un chef"),
    db: Session = Depends(get_db),
    current: User = Depends(require_department_head),
):
    """Le chef planifie un tour de garde (PlanningGarde) pour un membre de SON departement.

    Contrainte : statut CONFIRME est soumis au delai "au mercredi de la semaine
    precedente" (_check_publication_deadline). Quart et statut valides contre
    les enumerations du modele.
    """
    dept = _scoped_department(db, current, department_id)
    member_ids = _department_member_ids(db, dept)
    if payload.employe_id not in member_ids:
        raise HTTPException(
            status_code=403,
            detail="Collaborateur hors de votre departement",
        )
    quart = payload.quart.upper().strip()
    if quart not in _VALID_QUARTS:
        raise HTTPException(
            status_code=400,
            detail=f"Quart invalide (attendu : {', '.join(sorted(_VALID_QUARTS))})",
        )
    statut = (payload.statut or "PLANIFIE").upper().strip()
    if statut not in _VALID_STATUTS:
        raise HTTPException(
            status_code=400,
            detail=f"Statut invalide (attendu : {', '.join(sorted(_VALID_STATUTS))})",
        )
    date_jour = _parse_date(payload.date_jour)
    _check_publication_deadline(date_jour, statut)

    pg = PlanningGarde(
        company_id=dept.company_id,
        employe_id=payload.employe_id,
        superviseur_id=current.id,
        date_jour=date_jour,
        quart=quart,
        poste_assigne=payload.poste_assigne.strip(),
        statut=statut,
        observations=payload.observations,
    )
    db.add(pg)
    db.commit()
    db.refresh(pg)
    return {
        "id": pg.id,
        "employe_id": pg.employe_id,
        "date_jour": pg.date_jour.isoformat(),
        "quart": pg.quart,
        "poste_assigne": pg.poste_assigne,
        "statut": pg.statut,
        "observations": pg.observations,
    }


@router.put(
    "/planning/{planning_id}",
    summary="Modifier un tour de garde du departement",
)
def update_planning(
    planning_id: int,
    payload: PlanningUpdatePayload,
    department_id: Optional[int] = Query(None, description="Reserve admin/CADC ; ignore pour un chef"),
    db: Session = Depends(get_db),
    current: User = Depends(require_department_head),
):
    """Met a jour les champs fournis (quart, poste, statut, observations).

    Le tour doit appartenir a un membre du departement resolu. La contrainte
    "au mercredi" s'applique si le nouveau statut est CONFIRME.
    """
    dept = _scoped_department(db, current, department_id)
    pg = _guard_planning_in_dept(db, planning_id, dept)

    if payload.quart is not None:
        q = payload.quart.upper().strip()
        if q not in _VALID_QUARTS:
            raise HTTPException(
                status_code=400,
                detail=f"Quart invalide (attendu : {', '.join(sorted(_VALID_QUARTS))})",
            )
        pg.quart = q
    if payload.poste_assigne is not None:
        pg.poste_assigne = payload.poste_assigne.strip()
    if payload.statut is not None:
        s = payload.statut.upper().strip()
        if s not in _VALID_STATUTS:
            raise HTTPException(
                status_code=400,
                detail=f"Statut invalide (attendu : {', '.join(sorted(_VALID_STATUTS))})",
            )
        _check_publication_deadline(pg.date_jour, s)
        pg.statut = s
    if payload.observations is not None:
        pg.observations = payload.observations

    db.commit()
    db.refresh(pg)
    return {
        "id": pg.id,
        "employe_id": pg.employe_id,
        "date_jour": pg.date_jour.isoformat(),
        "quart": pg.quart,
        "poste_assigne": pg.poste_assigne,
        "statut": pg.statut,
        "observations": pg.observations,
    }


@router.delete(
    "/planning/{planning_id}",
    summary="Supprimer un tour de garde du departement",
)
def delete_planning(
    planning_id: int,
    department_id: Optional[int] = Query(None, description="Reserve admin/CADC ; ignore pour un chef"),
    db: Session = Depends(get_db),
    current: User = Depends(require_department_head),
):
    """Supprime definitivement un tour de garde appartenant a un membre du departement."""
    dept = _scoped_department(db, current, department_id)
    pg = _guard_planning_in_dept(db, planning_id, dept)
    db.delete(pg)
    db.commit()
    return {"deleted": pg.id}


@router.post(
    "/presence/{pointage_id}/valider",
    summary="Valider un emargement (pointage) d'un collaborateur du departement",
)
def validate_presence(
    pointage_id: int,
    department_id: Optional[int] = Query(None, description="Reserve admin/CADC ; ignore pour un chef"),
    db: Session = Depends(get_db),
    current: User = Depends(require_department_head),
):
    """Le chef confirme qu'un emargement (PointageVacation) est correct.

    Seuls les pointages des membres de SON departement sont validables. L'appel
    met est_valide=True et renseigne valide_par_id (chef). Si le pointage est
    deja valide, la reponse reste 200 (idempotent).
    """
    dept = _scoped_department(db, current, department_id)
    pv = db.query(PointageVacation).filter(PointageVacation.id == pointage_id).first()
    if not pv:
        raise HTTPException(status_code=404, detail="Emargement introuvable")
    member_ids = _department_member_ids(db, dept)
    if pv.employe_id not in member_ids:
        raise HTTPException(
            status_code=403,
            detail="Cet emargement ne concerne pas un collaborateur de votre departement",
        )
    pv.est_valide = True
    pv.valide_par_id = current.id
    db.commit()
    db.refresh(pv)
    return {
        "id": pv.id,
        "employe_id": pv.employe_id,
        "date_pointage": pv.date_pointage.isoformat() if pv.date_pointage else None,
        "heure_arrivee": pv.heure_arrivee,
        "heure_depart": pv.heure_depart,
        "est_valide": pv.est_valide,
        "valide_par_id": pv.valide_par_id,
    }
