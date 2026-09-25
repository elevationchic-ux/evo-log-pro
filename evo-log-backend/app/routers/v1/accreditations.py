"""Routers Accréditations & Acces partages (modules communs par entreprise).

- ``/api/v1/accreditations``  : gestion par l'admin entreprise ; l'utilisateur
  voit ses propres accréditations via ``/accreditations/mes-accreditations``.
- ``/api/v1/shared-access``   : bascule des modules accessibles a tous les
  utilisateurs authentifiés du tenant (portail RH self, chat, notifications...).

Le champ JSON ``perimetre_utilisateurs`` est (dés)érialisé ici pour rester
transparent au moteur d'autorisation.
"""
import json
import secrets
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.accreditation import (
    Accreditation, SharedAccess, DEFAULT_SHARED_MODULES,
    ACC_TYPE_PERMISSION, ACC_TYPE_SCOPE,
)
from app.models.user import User
from app.schemas.accreditation import (
    AccreditationCreate, AccreditationUpdate, SharedAccessCreate,
)
from app.utils.rbac import require_company_admin

router = APIRouter()
shared_router = APIRouter()


# ── Sérialisation ─────────────────────────────────────────────────────────────
def _accred_dict(a: Accreditation) -> dict:
    try:
        perim = json.loads(a.perimetre_utilisateurs) if a.perimetre_utilisateurs else []
    except (json.JSONDecodeError, TypeError):
        perim = []
    return {
        "id": a.id,
        "user_id": a.user_id,
        "company_id": a.company_id,
        "code": a.code,
        "libelle": a.libelle,
        "type": a.type,
        "permission_code": a.permission_code,
        "perimetre_utilisateurs": perim,
        "module": a.module,
        "date_debut": a.date_debut,
        "date_fin": a.date_fin,
        "statut": a.statut,
        "motif": a.motif,
        "octroye_par": a.octroye_par,
        "created_at": a.created_at,
    }


def _resolve_target_company(current: User, requested: Optional[int]) -> int:
    if current.is_superuser:
        if not requested:
            raise HTTPException(status_code=400, detail="company_id requis pour un SuperAdmin")
        return requested
    if not current.company_id:
        raise HTTPException(status_code=403, detail="Aucune entreprise associee a ce compte")
    if requested and requested != current.company_id:
        raise HTTPException(status_code=403, detail="Accreditation hors du perimetre de l'entreprise")
    return current.company_id


def _assert_user_in_company(db: Session, user_id: int, company_id: int) -> User:
    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    if target.company_id != company_id:
        raise HTTPException(status_code=403, detail="Utilisateur hors du perimetre de l'entreprise")
    return target


# ── Accréditations ────────────────────────────────────────────────────────────
@router.get("/mes-accreditations", summary="Mes accréditations (utilisateur courant)")
def mes_accreditations(
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    rows = db.query(Accreditation).filter(Accreditation.user_id == current.id).all()
    return [_accred_dict(a) for a in rows]


@router.get("/", summary="Lister les accréditations de l'entreprise")
def list_accreditations(
    company_id: Optional[int] = None,
    user_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current: User = Depends(require_company_admin),
):
    cid = _resolve_target_company(current, company_id)
    q = db.query(Accreditation).filter(Accreditation.company_id == cid)
    if user_id:
        q = q.filter(Accreditation.user_id == user_id)
    return [_accred_dict(a) for a in q.order_by(Accreditation.id.desc()).all()]


@router.post("/", status_code=status.HTTP_201_CREATED, summary="Octroyer une accréditation")
def creer_accreditation(
    payload: AccreditationCreate,
    company_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current: User = Depends(require_company_admin),
):
    cid = _resolve_target_company(current, company_id)
    _assert_user_in_company(db, payload.user_id, cid)
    if payload.type not in (ACC_TYPE_PERMISSION, ACC_TYPE_SCOPE):
        raise HTTPException(status_code=400, detail="type invalide (permission | scope)")
    if payload.type == ACC_TYPE_PERMISSION and not payload.permission_code:
        raise HTTPException(status_code=400, detail="permission_code requis pour type=permission")

    acc = Accreditation(
        user_id=payload.user_id,
        company_id=cid,
        code=payload.code or f"ACC-{secrets.token_hex(4).upper()}",
        libelle=payload.libelle,
        type=payload.type,
        permission_code=payload.permission_code,
        perimetre_utilisateurs=json.dumps(payload.perimetre_utilisateurs or []),
        module=payload.module,
        date_debut=payload.date_debut,
        date_fin=payload.date_fin,
        statut=payload.statut or "actif",
        motif=payload.motif,
        octroye_par=current.id,
    )
    db.add(acc)
    db.commit()
    db.refresh(acc)
    return _accred_dict(acc)


@router.put("/{accred_id}", summary="Modifier une accréditation")
def modifier_accreditation(
    accred_id: int,
    payload: AccreditationUpdate,
    db: Session = Depends(get_db),
    current: User = Depends(require_company_admin),
):
    acc = db.query(Accreditation).filter(Accreditation.id == accred_id).first()
    if not acc:
        raise HTTPException(status_code=404, detail="Accréditation introuvable")
    if not current.is_superuser and acc.company_id != current.company_id:
        raise HTTPException(status_code=403, detail="Accréditation hors du perimetre de l'entreprise")

    data = payload.dict(exclude_unset=True)
    if "perimetre_utilisateurs" in data:
        acc.perimetre_utilisateurs = json.dumps(data.pop("perimetre_utilisateurs") or [])
    for key, value in data.items():
        setattr(acc, key, value)
    db.commit()
    db.refresh(acc)
    return _accred_dict(acc)


@router.delete("/{accred_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Révoquer une accréditation")
def supprimer_accreditation(
    accred_id: int,
    db: Session = Depends(get_db),
    current: User = Depends(require_company_admin),
):
    acc = db.query(Accreditation).filter(Accreditation.id == accred_id).first()
    if not acc:
        raise HTTPException(status_code=404, detail="Accréditation introuvable")
    if not current.is_superuser and acc.company_id != current.company_id:
        raise HTTPException(status_code=403, detail="Accréditation hors du perimetre de l'entreprise")
    db.delete(acc)
    db.commit()
    return None


# ── Acces partages (modules communs) ──────────────────────────────────────────
@shared_router.get("/", summary="Lister les modules communs de l'entreprise")
def list_shared(
    company_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    cid = current.company_id if not current.is_superuser else company_id
    if not cid:
        raise HTTPException(status_code=400, detail="company_id requis pour un SuperAdmin")
    rows = db.query(SharedAccess).filter(SharedAccess.company_id == cid).all()
    return [{
        "id": s.id, "company_id": s.company_id, "module_key": s.module_key,
        "libelle": s.libelle, "autorise_tous_utilisateurs": s.autorise_tous_utilisateurs,
    } for s in rows]


@shared_router.post("/", status_code=status.HTTP_201_CREATED, summary="Activer un module commun")
def creer_shared(
    payload: SharedAccessCreate,
    company_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current: User = Depends(require_company_admin),
):
    cid = _resolve_target_company(current, company_id)
    existing = db.query(SharedAccess).filter(
        SharedAccess.company_id == cid, SharedAccess.module_key == payload.module_key
    ).first()
    if existing:
        existing.autorise_tous_utilisateurs = payload.autorise_tous_utilisateurs
        if payload.libelle:
            existing.libelle = payload.libelle
        db.commit()
        db.refresh(existing)
        return {"id": existing.id, "company_id": cid, "module_key": existing.module_key,
                "libelle": existing.libelle, "autorise_tous_utilisateurs": existing.autorise_tous_utilisateurs}
    s = SharedAccess(
        company_id=cid, module_key=payload.module_key, libelle=payload.libelle,
        autorise_tous_utilisateurs=payload.autorise_tous_utilisateurs,
    )
    db.add(s)
    db.commit()
    db.refresh(s)
    return {"id": s.id, "company_id": cid, "module_key": s.module_key,
            "libelle": s.libelle, "autorise_tous_utilisateurs": s.autorise_tous_utilisateurs}


@shared_router.delete("/{shared_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Retirer un module commun")
def supprimer_shared(
    shared_id: int,
    db: Session = Depends(get_db),
    current: User = Depends(require_company_admin),
):
    s = db.query(SharedAccess).filter(SharedAccess.id == shared_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Acces partagé introuvable")
    if not current.is_superuser and s.company_id != current.company_id:
        raise HTTPException(status_code=403, detail="Acces partagé hors du perimetre de l'entreprise")
    db.delete(s)
    db.commit()
    return None


@shared_router.post("/initialiser", summary="Semer les modules communs par defaut")
def initialiser_shared(
    company_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current: User = Depends(require_company_admin),
):
    cid = _resolve_target_company(current, company_id)
    created = 0
    for key, libelle in DEFAULT_SHARED_MODULES:
        exists = db.query(SharedAccess).filter(
            SharedAccess.company_id == cid, SharedAccess.module_key == key
        ).first()
        if not exists:
            db.add(SharedAccess(company_id=cid, module_key=key, libelle=libelle, autorise_tous_utilisateurs=True))
            created += 1
    db.commit()
    return {"company_id": cid, "created": created}
