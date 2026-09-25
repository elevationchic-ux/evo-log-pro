"""Moteur d'autorisation granulaire (module.sous_module.action).

Ce module est la brique centrale qui rend enfin exploitable le modele
``Permission`` (resource/action) historiquement defini mais jamais applique.

Regles de non-retour en arriere (principe "additif") :
    1. SuperAdmin (level 0) et Admin Entreprise (level 1) parcourent librement
       TOUT leur perimetre : ils bypassent la granularite.
    2. Un module "commun" (SharedAccess) actif pour l'entreprise est accessible
       a tout utilisateur authentifie, quel que soit son niveau.
    3. Pour les niveaux >= 2 :
         - si le role de l'utilisateur porte au moins une Permission
           granulaire, ces permissions font foi (union des roles + accréditations
           valides) ;
         - sinon on retombe sur l'ancien controle module ``can_access_module``
           (Role/Department.modules_allowed). Un tenant non "seed" garde donc
           EXACTEMENT son comportement actuel.

Les codes de permission suivent le format point ``module.sous_module.action``
avec jokers segmentaires ``*`` :
    "comptabilite.journal.read"
    "comptabilite.*.read"      -> lecture de tous les sous-modules
    "comptabilite.journal.*"   -> toutes actions sur journal
    "*"                        -> tout (reserve)
"""
from __future__ import annotations

import fnmatch
import json
from typing import Iterable, List, Optional, Set

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.tenant_access import can_access_module, ensure_company_scope
from app.models.user import User

# Niveaux disposant d'un bypass total de la granularite.
_BYPASS_LEVELS = {0, 1}

_SEP = "."


def _match(granted: str, wanted: str) -> bool:
    """Le code accorde ``granted`` couvre-t-il le code requis ``wanted`` ?

    Joker segmentaire ``*`` Gere par ``fnmatch`` point par point pour eviter
    qu'un ``*`` global ne chevauche des segments.
    """
    if granted == "*" or wanted == "*":
        return True
    g = granted.split(_SEP)
    w = wanted.split(_SEP)
    # "comptabilite" accorde couvre "comptabilite.*.*" et toute action dessous
    if len(g) < len(w):
        g = g + ["*"] * (len(w) - len(g))
    for gs, ws in zip(g, w):
        if gs == "*":
            continue
        if gs != ws:
            return False
    return True


def _role_permission_codes(user: User) -> Set[str]:
    codes: Set[str] = set()
    for role in (getattr(user, "roles", None) or []):
        for perm in (getattr(role, "permissions", None) or []):
            if perm.code:
                codes.add(perm.code)
    return codes


def _accreditation_codes(user: User) -> Set[str]:
    """Codes accordes par des accréditations encore valides."""
    codes: Set[str] = set()
    for acc in (getattr(user, "accreditations", None) or []):
        try:
            if acc.est_valide() and acc.type == "permission" and acc.permission_code:
                codes.add(acc.permission_code)
        except Exception:  # pragma: no cover - table absente en tout debut
            continue
    return codes


def load_effective_permissions(user: User) -> Set[str]:
    """Union des codes de permission des roles + accréditations valides."""
    return _role_permission_codes(user) | _accreditation_codes(user)


def has_perm(codes: Iterable[str], wanted: str) -> bool:
    return any(_match(g, wanted) for g in codes)


def _shared_module_keys(user: User) -> Set[str]:
    """Modules communautaires actifs pour l'entreprise de l'utilisateur.

    Principe : les modules de la liste ``DEFAULT_SHARED_MODULES`` (portail RH
    self-service, chat, notifications, ...) sont ouverts a TOUT utilisateur
    authentifie par defaut, meme pour un tenant jamais "seed" en SharedAccess.
    Une entreprise peut desactiver l'un d'eux via une ligne ``SharedAccess``
    explicite ``autorise_tous_utilisateurs=False`` ; une ligne ``True`` ajoute
    un module commun specifique a ce tenant.
    """
    from app.models.accreditation import DEFAULT_SHARED_MODULES

    keys: Set[str] = {k.lower() for (k, _lib) in DEFAULT_SHARED_MODULES}
    company = getattr(user, "company", None)
    for sa in (getattr(company, "shared_access", None) or []):
        mk = (sa.module_key or "").lower()
        if not mk:
            continue
        if sa.autorise_tous_utilisateurs:
            keys.add(mk)
        else:
            keys.discard(mk)
    return keys


def is_shared_module(user: User, module: str) -> bool:
    return (module or "").lower() in _shared_module_keys(user)


def can(user: User, code: str) -> bool:
    """Evaluation complete d'un droit granulaire pour ``user``."""
    if user is None:
        return False
    if getattr(user, "is_superuser", False):
        return True
    level = getattr(user, "role_level", 99)
    if level in _BYPASS_LEVELS:
        return True

    module = (code or "").split(_SEP)[0]
    # Module commun : ouvert a tout utilisateur authentifie du tenant.
    if module and is_shared_module(user, module):
        return True

    codes = load_effective_permissions(user)
    if codes:
        return has_perm(codes, code)
    # Retro-compatibilite : aucun seed granulaire -> controle module historique.
    return can_access_module(user, module)


def require_perm(code: str):
    """Dependency factory FastAPI imposant le droit granulaire ``code``."""

    def dependency(current_user: User = Depends(get_current_user)) -> User:
        ensure_company_scope(
            current_user,
            getattr(current_user, "company_id", None),
            allow_none=True,
        )
        if not can(current_user, code):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Droit insuffisant : {code}",
            )
        return current_user

    return dependency


# ── Visibilite hierarchique ────────────────────────────────────────────────
def _scope_from_accreditations(user: User) -> Optional[Set[int]]:
    """Ids de collaborateurs imposes par une accréditation de type scope."""
    ids: Set[int] = set()
    found = False
    for acc in (getattr(user, "accreditations", None) or []):
        try:
            if acc.est_valide() and acc.type == "scope":
                found = True
                raw = acc.perimetre_utilisateurs
                if raw:
                    vals = json.loads(raw) if isinstance(raw, str) else raw
                    ids |= {int(v) for v in vals}
        except Exception:  # pragma: no cover
            continue
    return ids if found else None


def visible_user_ids(db: Session, user: User) -> Optional[Set[int]]:
    """Ensemble d'ids visibles, ou ``None`` = pas de restriction (dans l'entreprise).

    - SuperAdmin / Admin Entreprise : ``None`` (tout le tenant ; la requete est
      deja filtree par company_id par ``scope_query``).
    - Chef de departement (level 2) : les utilisateurs de son departement,
      eventuellement restreints par une accréditation "scope".
    - Utilisateur standard (level >= 3) : lui-meme uniquement.
    """
    if user is None:
        return set()
    if getattr(user, "is_superuser", False):
        return None
    level = getattr(user, "role_level", 99)
    if level in _BYPASS_LEVELS:
        return None

    if level == 2:
        from app.models.user import User as UserModel
        forced = _scope_from_accreditations(user)
        if forced is not None:
            return forced
        q = db.query(UserModel.id).filter(UserModel.role_level >= 2)
        if user.department_id:
            q = q.filter(UserModel.department_id == user.department_id)
        else:
            q = q.filter(UserModel.id == user.id)
        if user.company_id:
            q = q.filter(UserModel.company_id == user.company_id)
        return {row[0] for row in q.all()} | {user.id}

    return {user.id}


def restrict_to_visible(query, user: User, column, visible: Optional[Set[int]]):
    """Applique un filtre ``column IN (visible)`` si une restriction existe."""
    if visible is None:
        return query
    return query.filter(column.in_(list(visible) or [-1]))
