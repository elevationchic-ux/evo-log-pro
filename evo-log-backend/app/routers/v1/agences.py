"""
Module Agences & succursales — réseau territorial multi-sites.

Couvre le cycle complet d'une agence/extension/bureau :

- Referentiel : liste, detail, creation, mise a jour, suppression
  (desactivation douce si des utilisateurs y sont rattaches).
- Contexte : ``GET /moi`` (agence active + agences accessibles) et
  ``POST /{id}/activer`` (bascule de l'agence de session — tout le perimetre
  ORM est alors scope par ``app.core.agency_enforcement``).
- Pilotage : ``GET /comparatif`` et ``GET /{id}/tableau-de-bord`` — KPI reels
  par agence (effectifs, tiers, missions, vehicules, escales, conteneurs,
  facturation) calcules depuis les tables, jamais estimes.
- Effectifs : liste et affectation des utilisateurs par agence.

Regle de perimetre : les donnees portent ``agency_id`` ; NULL = partage /
non rattache (visible par toutes les agences). Les ecritures realisees
tandis qu'une agence est active sont marquees automatiquement.
"""
from datetime import date, datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.core.agency_context import bypass_agency_filter
from app.core.database import get_db
from app.core.permissions import can, require_perm
from app.core.security import get_current_user
from app.models.user import User
from app.models.agency import Agency

router = APIRouter(tags=["Agences & succursales"])

TYPES_AGENCE = {"SIEGE", "AGENCE", "EXTENSION", "BUREAU"}


# ─── Schemas ────────────────────────────────────────────────────────────────

class AgencyCreate(BaseModel):
    code: str
    name: str
    type_agence: Optional[str] = "AGENCE"
    parent_id: Optional[int] = None
    address: Optional[str] = None
    city: Optional[str] = "Douala"
    country: Optional[str] = "Cameroun"
    phone: Optional[str] = None
    email: Optional[str] = None
    is_active: Optional[bool] = True
    is_headquarters: Optional[bool] = False
    organization_id: Optional[int] = None


class AgencyUpdate(BaseModel):
    name: Optional[str] = None
    type_agence: Optional[str] = None
    parent_id: Optional[int] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    is_active: Optional[bool] = None
    is_headquarters: Optional[bool] = None


# ─── Helpers ────────────────────────────────────────────────────────────────

def _agence_visible(agency: Agency, user: User) -> bool:
    """Une agence est visible si elle appartient a l'organisation/cie de
    l'utilisateur ; les agences sans rattachement (NULL) sont heritees
    (compatibilite legacy mono-tenant)."""
    if user.is_superuser:
        return True
    org = getattr(user, "organization_id", None)
    if org is not None and agency.organization_id is not None:
        return agency.organization_id == org
    company = getattr(user, "company_id", None)
    if company is not None and agency.company_id is not None:
        return agency.company_id == company
    return True


def _get_agence_or_404(db: Session, agency_id: int, user: User) -> Agency:
    agency = db.query(Agency).filter(Agency.id == agency_id).first()
    if not agency or not _agence_visible(agency, user):
        raise HTTPException(status_code=404, detail=f"Agence #{agency_id} non trouvee")
    return agency


def _kpis_agence(db: Session, agency_id: int) -> dict:
    """KPI reels d'une agence — compteurs depuis les tables metier.

    Execute sous ``bypass_agency_filter`` : le comparatif doit voir TOUTES
    les agences meme quand l'utilisateur en a une active.
    """
    with bypass_agency_filter():
        from app.models.user import User as U
        from app.models.tiers import Tiers
        from app.models.transport import Mission, Camion, Conducteur
        from app.models.parc import Vehicule
        from app.models.acconage import Navire, Escale, Conteneur
        from app.models.finance import Facture, FactureStatus
        from app.models.transport_avance import Tournée, Livraison

        def count(model, *conds):
            q = db.query(func.count(model.id)).filter(model.agency_id == agency_id)
            for c in conds:
                q = q.filter(c)
            return q.scalar() or 0

        users_rattaches = db.query(func.count(U.id)).filter(U.agency_id == agency_id).scalar() or 0
        users_actifs = db.query(func.count(U.id)).filter(U.current_agency_id == agency_id).scalar() or 0

        factures = db.query(
            func.count(Facture.id),
            func.coalesce(func.sum(Facture.montant_ttc), 0),
        ).filter(Facture.agency_id == agency_id).one()
        ca_encaisse = db.query(func.coalesce(func.sum(Facture.montant_ttc), 0)).filter(
            Facture.agency_id == agency_id,
            Facture.statut == FactureStatus.PAYEE,
        ).scalar() or 0

        return {
            "agence_id": agency_id,
            "utilisateurs": {
                "rattaches": users_rattaches,
                "session_active": users_actifs,
            },
            "tiers": {"clients_fournisseurs": count(Tiers)},
            "transport": {
                "missions": count(Mission),
                "camions": count(Camion),
                "conducteurs": count(Conducteur),
                "tournees": count(Tournée),
                "livraisons": count(Livraison),
            },
            "parc": {"vehicules": count(Vehicule)},
            "acconage": {
                "navires": count(Navire),
                "escales": count(Escale),
                "conteneurs": count(Conteneur),
            },
            "finance": {
                "factures": factures[0] or 0,
                "ca_facture_ttc": float(factures[1] or 0),
                "ca_encaisse_ttc": float(ca_encaisse),
            },
        }


# ─── Contexte de session ───────────────────────────────────────────────────

@router.get("/moi")
def mon_contexte_agence(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Agence active de l'utilisateur + agences accessibles au reseau."""
    from app.core.agency_context import get_current_agency, is_agency_enforcement_active

    agences = db.query(Agency).filter(Agency.is_active.is_(True)).all()
    accessibles = [a for a in agences if _agence_visible(a, current_user)]

    active = db.query(Agency).filter(Agency.id == current_user.current_agency_id).first() \
        if current_user.current_agency_id else None

    return {
        "agence_active": _serialize(active) if active else None,
        "filtrage_actif": is_agency_enforcement_active() and get_current_agency() is not None,
        "agences": [_serialize(a) for a in accessibles],
        "peut_gerer_reseau": can(current_user, "agences.agences.create"),
        "peut_voir_pilotage": can(current_user, "agences.pilotage.read"),
        "peut_voir_comptes": can(current_user, "agences.comptes.read"),
        "peut_gerer_comptes": can(current_user, "agences.comptes.modify"),
    }


def _serialize(a: Agency) -> dict:
    return {
        "id": a.id,
        "code": a.code,
        "name": a.name,
        "type_agence": a.type_agence,
        "parent_id": a.parent_id,
        "address": a.address,
        "city": a.city,
        "country": a.country,
        "phone": a.phone,
        "email": a.email,
        "is_active": a.is_active,
        "is_headquarters": a.is_headquarters,
        "is_current": False,  # renseigne par l'appelant si besoin
    }


@router.post("/{agency_id}/activer")
def activer_agence(
    agency_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Bascule l'agence active de l'utilisateur (Limbe -> Kribi, national ou
    international). A partir de la requete suivante, le perimetre ORM est
    scope : seules les donnees de cette agence + les donnees partagees
    (agency_id NULL) restent visibles."""
    agency = _get_agence_or_404(db, agency_id, current_user)
    if not agency.is_active:
        raise HTTPException(status_code=400, detail="Cette agence est desactivee")

    current_user.current_agency_id = agency.id
    db.commit()

    return {
        "message": f"Agence active : {agency.name} ({agency.code})",
        "agence": _serialize(agency),
        "perimetre": "donnees de l'agence + donnees partagees (non rattachees)",
    }


@router.post("/reinitialiser")
def reinitialiser_agence(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Revenir a la vue consolidée (toutes les agences + partagees)."""
    current_user.current_agency_id = None
    db.commit()
    return {"message": "Vue consolidée active : toutes les agences visibles", "agence": None}


# ─── Referentiel ────────────────────────────────────────────────────────────

@router.get("/")
def lister_agences(
    city: Optional[str] = Query(None),
    country: Optional[str] = Query(None),
    type_agence: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Agences accessibles a l'utilisateur, avec effectifs et indicateur courant."""
    query = db.query(Agency)
    if city:
        query = query.filter(Agency.city.ilike(f"%{city}%"))
    if country:
        query = query.filter(Agency.country.ilike(f"%{country}%"))
    if type_agence:
        query = query.filter(Agency.type_agence == type_agence.upper())
    if is_active is not None:
        query = query.filter(Agency.is_active == is_active)
    if search:
        query = query.filter(or_(
            Agency.code.ilike(f"%{search}%"),
            Agency.name.ilike(f"%{search}%"),
            Agency.city.ilike(f"%{search}%"),
        ))

    items = query.order_by(Agency.is_headquarters.desc(), Agency.name.asc()).all()
    items = [a for a in items if _agence_visible(a, current_user)]

    with bypass_agency_filter():
        counts = dict(
            db.query(User.agency_id, func.count(User.id))
            .filter(User.agency_id.isnot(None))
            .group_by(User.agency_id).all()
        )

    current = current_user.current_agency_id
    return {
        "total": len(items),
        "items": [
            {**_serialize(a), "users_count": counts.get(a.id, 0), "is_current": a.id == current}
            for a in items
        ],
    }


@router.post("/", status_code=status.HTTP_201_CREATED)
def creer_agence(
    payload: AgencyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_perm("agences.agences.create")),
):
    """Cree une agence, succursale, extension ou bureau (national ou international)."""
    existing = db.query(Agency).filter(Agency.code == payload.code.upper()).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Le code '{payload.code}' existe deja")

    if payload.parent_id is not None:
        parent = db.query(Agency).filter(Agency.id == payload.parent_id).first()
        if not parent:
            raise HTTPException(status_code=400, detail="Agence parente introuvable")

    type_agence = (payload.type_agence or "AGENCE").upper()
    if type_agence not in TYPES_AGENCE:
        raise HTTPException(status_code=400, detail=f"type_agence doit etre parmi {sorted(TYPES_AGENCE)}")

    agency = Agency(
        code=payload.code.upper(),
        name=payload.name,
        type_agence=type_agence,
        parent_id=payload.parent_id,
        address=payload.address,
        city=payload.city or "Douala",
        country=payload.country or "Cameroun",
        phone=payload.phone,
        email=payload.email,
        is_active=payload.is_active if payload.is_active is not None else True,
        is_headquarters=payload.is_headquarters or False,
        organization_id=payload.organization_id or getattr(current_user, "organization_id", None),
        company_id=getattr(current_user, "company_id", None),
    )
    if agency.is_headquarters:
        # Un seul siege par perimetre : retrograder les autres.
        q = db.query(Agency).filter(Agency.is_headquarters.is_(True))
        if agency.organization_id is not None:
            q = q.filter(or_(Agency.organization_id == agency.organization_id,
                             Agency.organization_id.is_(None)))
        for other in q.all():
            if other.id != agency.id:
                other.is_headquarters = False

    db.add(agency)
    db.commit()
    db.refresh(agency)
    return {"message": "Agence creee", "id": agency.id, "code": agency.code, "name": agency.name}


@router.get("/{agency_id}")
def detail_agence(
    agency_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Detail d'une agence : fiche, effectif, extensions rattachees, KPI."""
    agency = _get_agence_or_404(db, agency_id, current_user)

    with bypass_agency_filter():
        collaborateurs = db.query(User).filter(User.agency_id == agency_id).all()
        enfants = db.query(Agency).filter(Agency.parent_id == agency_id).all()

    return {
        **_serialize(agency),
        "is_current": agency.id == current_user.current_agency_id,
        "created_at": agency.created_at.isoformat() if agency.created_at else None,
        "collaborateurs": [
            {
                "id": u.id,
                "email": u.email,
                "full_name": u.full_name,
                "role_level": u.role_level,
                "is_active": u.is_active,
            }
            for u in collaborateurs
        ],
        "extensions": [_serialize(e) for e in enfants],
        "kpis": _kpis_agence(db, agency_id),
    }


@router.put("/{agency_id}")
def maj_agence(
    agency_id: int,
    payload: AgencyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_perm("agences.agences.modify")),
):
    agency = _get_agence_or_404(db, agency_id, current_user)

    data = payload.model_dump(exclude_unset=True)
    if "type_agence" in data and data["type_agence"]:
        t = data["type_agence"].upper()
        if t not in TYPES_AGENCE:
            raise HTTPException(status_code=400, detail=f"type_agence doit etre parmi {sorted(TYPES_AGENCE)}")
        data["type_agence"] = t
    if payload.parent_id is not None and payload.parent_id == agency_id:
        raise HTTPException(status_code=400, detail="Une agence ne peut pas etre sa propre parente")

    for field, value in data.items():
        setattr(agency, field, value)
    agency.updated_at = datetime.utcnow()

    if agency.is_headquarters:
        q = db.query(Agency).filter(Agency.is_headquarters.is_(True), Agency.id != agency.id)
        for other in q.all():
            other.is_headquarters = False

    db.commit()
    db.refresh(agency)
    return {"message": "Agence mise a jour", "id": agency.id}


@router.delete("/{agency_id}")
def supprimer_agence(
    agency_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_perm("agences.agences.delete")),
):
    agency = _get_agence_or_404(db, agency_id, current_user)

    with bypass_agency_filter():
        users_count = db.query(func.count(User.id)).filter(User.agency_id == agency_id).scalar() or 0

    if users_count > 0:
        agency.is_active = False
        # Les utilisateurs dont l'agence ACTIVE etait celle-ci perdent leur
        # perimetre restreint : on les rebascule sur leur agence d'appartenance.
        db.query(User).filter(User.current_agency_id == agency_id).update(
            {"current_agency_id": None}, synchronize_session=False)
        db.commit()
        return {"message": f"Agence #{agency_id} desactivee ({users_count} utilisateur(s) rattache(s))"}

    enfants = db.query(Agency).filter(Agency.parent_id == agency_id).count()
    if enfants:
        raise HTTPException(status_code=400, detail="Des extensions sont rattachees a cette agence")

    db.delete(agency)
    db.commit()
    return {"message": f"Agence #{agency_id} supprimee"}


# ─── Pilotage : comparatif & tableaux de bord ───────────────────────────────

@router.get("/comparatif/tableau")
def comparatif_agences(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_perm("agences.pilotage.read")),
):
    """Dashboard comparatif entre agences/ extensions : chaque ligne est une
    agence avec ses KPI reels — pour arbitrer les affectations de ressources
    entre sites (Douala/Limbe, Kribi, Yaounde, extensions, hors CEMAC)."""
    agences = db.query(Agency).filter(Agency.is_active.is_(True)).all()
    agences = [a for a in agences if _agence_visible(a, current_user)]

    rows = []
    for a in agences:
        k = _kpis_agence(db, a.id)
        rows.append({
            "id": a.id,
            "code": a.code,
            "name": a.name,
            "type_agence": a.type_agence,
            "ville": a.city,
            "pays": a.country,
            "is_headquarters": a.is_headquarters,
            **k,
        })

    # Agregat 'non rattache' : donnees sans agency_id (partagees / heritees)
    with bypass_agency_filter():
        from app.models.tiers import Tiers
        from app.models.transport import Mission
        from app.models.finance import Facture
        non_rattache = {
            "tiers": db.query(func.count(Tiers.id)).filter(Tiers.agency_id.is_(None)).scalar() or 0,
            "missions": db.query(func.count(Mission.id)).filter(Mission.agency_id.is_(None)).scalar() or 0,
            "factures": db.query(func.count(Facture.id)).filter(Facture.agency_id.is_(None)).scalar() or 0,
        }

    return {"agences": rows, "donnees_non_rattachees": non_rattache}


@router.get("/{agency_id}/tableau-de-bord")
def tableau_de_bord_agence(
    agency_id: int,
    jours: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_perm("agences.pilotage.read")),
):
    """Dashboard d'une agence : KPI complets + activite recente reelle."""
    agency = _get_agence_or_404(db, agency_id, current_user)
    kpis = _kpis_agence(db, agency_id)

    with bypass_agency_filter():
        from app.models.transport import Mission, MissionStatus
        from app.models.finance import Facture, FactureStatus

        debut = date.today() - timedelta(days=jours)
        missions_periode = db.query(func.count(Mission.id)).filter(
            Mission.agency_id == agency_id,
            Mission.date_debut_prevue >= datetime.combine(debut, datetime.min.time()),
        ).scalar() or 0
        missions_en_cours = db.query(func.count(Mission.id)).filter(
            Mission.agency_id == agency_id,
            Mission.statut == MissionStatus.EN_COURS,
        ).scalar() or 0
        factures_impayees = db.query(func.count(Facture.id)).filter(
            Facture.agency_id == agency_id,
            Facture.statut.in_([FactureStatus.EMISE, FactureStatus.RETARD]),
        ).scalar() or 0

    return {
        "agence": _serialize(agency),
        "periode_jours": jours,
        "kpis": kpis,
        "activite": {
            "missions_periode": missions_periode,
            "missions_en_cours": missions_en_cours,
            "factures_impayees": factures_impayees,
        },
    }


# ─── Effectifs ──────────────────────────────────────────────────────────────

@router.get("/{agency_id}/utilisateurs")
def utilisateurs_agence(
    agency_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_perm("agences.comptes.read")),
):
    """Collaborateurs rattaches a l'agence (affectation = agency_id)."""
    agency = _get_agence_or_404(db, agency_id, current_user)
    with bypass_agency_filter():
        users = db.query(User).filter(User.agency_id == agency_id).order_by(User.full_name).all()
    return {
        "agence": _serialize(agency),
        "total": len(users),
        "items": [
            {
                "id": u.id,
                "email": u.email,
                "full_name": u.full_name,
                "role_level": u.role_level,
                "is_active": u.is_active,
                "current_agency_id": u.current_agency_id,
            }
            for u in users
        ],
    }


@router.put("/{agency_id}/utilisateurs/{user_id}")
def affecter_utilisateur(
    agency_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_perm("agences.comptes.modify")),
):
    """Affecte un utilisateur a l'agence (son agence d'appartenance)."""
    agency = _get_agence_or_404(db, agency_id, current_user)
    with bypass_agency_filter():
        user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"Utilisateur #{user_id} introuvable")

    user.agency_id = agency.id
    db.commit()
    return {"message": f"{user.email} affecte a {agency.name}", "user_id": user_id, "agency_id": agency.id}


@router.delete("/{agency_id}/utilisateurs/{user_id}")
def desaffecter_utilisateur(
    agency_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_perm("agences.comptes.modify")),
):
    """Retire l'affectation agence d'un utilisateur."""
    agency = _get_agence_or_404(db, agency_id, current_user)
    with bypass_agency_filter():
        user = db.query(User).filter(User.id == user_id, User.agency_id == agency_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Affectation introuvable")

    user.agency_id = None
    if user.current_agency_id == agency.id:
        user.current_agency_id = None
    db.commit()
    return {"message": f"{user.email} desaffecte de {agency.name}"}
