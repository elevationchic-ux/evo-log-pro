"""Service metier organisation : abonnements (statut, plan,
expiration proche, utilisateurs vs max_users). Aucune donnee
invente : modules autorises listes tels qu'enregistres."""
from datetime import datetime, timedelta
from typing import Dict, Any

from sqlalchemy.orm import Session

from app.models.organization import Organization


class OrganizationService:
    """Abonnements organisations."""

    @staticmethod
    def abonnements(db: Session) -> Dict[str, Any]:
        orgs = db.query(Organization).filter(
            Organization.is_active.is_(True)).all()
        if not orgs:
            return {"organisations": 0, "note": "Aucune organisation."}

        par_plan: Dict[str, int] = {}
        par_statut: Dict[str, int] = {}
        expirant_bientot = []
        now = datetime.utcnow()
        for o in orgs:
            par_plan[o.plan or "inconnu"] = par_plan.get(o.plan or "inconnu", 0) + 1
            par_statut[o.status or "inconnu"] = par_statut.get(o.status or "inconnu", 0) + 1
            if o.subscription_expires_at and o.subscription_expires_at < now + timedelta(days=30):
                expirant_bientot.append({
                    "code": o.code,
                    "plan": o.plan,
                    "expire_at": str(o.subscription_expires_at),
                })
        return {
            "organisations_total": len(orgs),
            "par_plan": par_plan,
            "par_statut": par_statut,
            "expirant_30j": len(expirant_bientot),
            "details_expiration": expirant_bientot,
        }

    @staticmethod
    def usage(db: Session) -> Dict[str, Any]:
        """Utilisateurs actifs vs max_users par organisation.
        Le comptage exact necessite une requete sur users ; ici on
        rapporte le plafond et les modules autorises."""
        orgs = db.query(Organization).filter(
            Organization.is_active.is_(True)).all()
        if not orgs:
            return {"organisations": 0}
        return {
            "plafonds": [
                {"code": o.code, "plan": o.plan, "max_users": o.max_users,
                 "modules": o.allowed_modules}
                for o in orgs
            ],
        }
