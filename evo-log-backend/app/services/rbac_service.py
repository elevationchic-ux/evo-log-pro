"""
Service RBAC EVO-LOG SaaS (donnees REELLES, basees sur l'ORM).

Remplace l'ancienne implementation qui renvoyait des donnees factices
(tenants/utilisateurs/verification de permission simules en dur). Toutes les
methodes interrogent desormais la base via les modeles reels :

- "tenant"      -> :class:`app.models.tenant.Company`
- "roles"       -> :class:`app.models.user.Role` (+ permissions granulaires)
- "permission"  -> moteur :mod:`app.core.permissions`
"""
import json
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.tenant import Company
from app.models.user import Role, User
from app.core.permissions import can, load_effective_permissions


def _iso(value) -> Optional[str]:
    return value.isoformat() if value else None


class RBACService:
    """Service de gestion des roles, permissions et tenants (multi-entreprise)."""

    @staticmethod
    def get_all_tenants(db: Session) -> List[Dict[str, Any]]:
        """Liste des entreprises (tenants) reellement en base."""
        out: List[Dict[str, Any]] = []
        for c in db.query(Company).order_by(Company.id).all():
            out.append({
                "id": c.id,
                "code": c.code,
                "nom_entreprise": c.nom,
                "pays": c.pays,
                "ville": c.ville,
                "plan": getattr(getattr(c, "subscription_plan", None), "type_plan", None) and c.subscription_plan.type_plan.value,
                "modules_actives": c.modules_actives,
                "nb_utilisateurs_max": c.max_users,
                "actif": bool(c.is_active),
                "created_at": _iso(c.created_at),
            })
        return out

    @staticmethod
    def get_all_roles(db: Session, company_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Roles systemes + roles de l'entreprise, avec leurs permissions."""
        q = db.query(Role)
        if company_id is not None:
            q = q.filter((Role.company_id.is_(None)) | (Role.company_id == company_id))
        out: List[Dict[str, Any]] = []
        for role in q.order_by(Role.level, Role.name).all():
            perms = sorted({p.code for p in (role.permissions or []) if p.code})
            out.append({
                "id": role.id,
                "nom": role.name,
                "niveau": f"L{role.level}",
                "level": role.level,
                "company_id": role.company_id,
                "description": role.description,
                "permissions_json": json.dumps(perms),
                "nb_permissions": len(perms),
                "modules_allowed": _safe_modules(role.modules_allowed),
                "is_system": bool(role.is_system),
                "actif": bool(role.is_active),
            })
        return out

    @staticmethod
    def check_permission(db: Session, user_id: int, tenant_id: Optional[int], permission_code: str) -> Dict[str, Any]:
        """Evalue reellement un droit a partir du profil utilisateur en base."""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {
                "user_id": user_id,
                "permission_code": permission_code,
                "autorise": False,
                "niveau_role": None,
                "raison": "Utilisateur introuvable",
            }
        if tenant_id and user.company_id and user.company_id != tenant_id:
            return {
                "user_id": user_id,
                "permission_code": permission_code,
                "autorise": False,
                "niveau_role": f"L{user.role_level}",
                "raison": "Utilisateur hors du perimetre de l'entreprise",
            }
        autorise = can(user, permission_code)
        return {
            "user_id": user_id,
            "permission_code": permission_code,
            "autorise": autorise,
            "niveau_role": f"L{user.role_level}",
            "raison": (
                "Autorise (permissions : %s)" % ", ".join(sorted(load_effective_permissions(user))[:5])
                if autorise else "Non autorise pour ce role"
            ),
        }

    @staticmethod
    def get_users_by_tenant(db: Session, tenant_id: int) -> List[Dict[str, Any]]:
        """Utilisateurs reels rattachés à l'entreprise."""
        out: List[Dict[str, Any]] = []
        users = db.query(User).filter(User.company_id == tenant_id).order_by(User.id).all()
        for u in users:
            roles = [r.name for r in (u.roles or [])]
            out.append({
                "id": u.id,
                "nom": u.full_name or u.username,
                "email": u.email,
                "role": roles[0] if roles else f"L{u.role_level}",
                "roles": roles,
                "tenant_id": u.company_id,
                "actif": bool(u.is_active),
                "derniere_connexion": _iso(u.last_login),
            })
        return out


def _safe_modules(raw) -> List[str]:
    if not raw:
        return []
    try:
        vals = json.loads(raw)
        return list(vals) if isinstance(vals, list) else [str(vals)]
    except (json.JSONDecodeError, TypeError):
        return [m.strip() for m in str(raw).split(",") if m.strip()]
