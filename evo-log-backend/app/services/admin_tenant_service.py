"""Service metier admin tenant : quotas ressources (consomme vs
autorise), sauvegardes tenant et impersonations admin ouvertes.
Aucune donnee inventee."""
from typing import Dict, Any

from sqlalchemy.orm import Session

from app.models.admin_tenant_c_deep import (
    AdmtUsageQuota, AdmtTenantBackup, AdmtImpersonationLog)


class AdminTenantService:
    """Administration multi-tenant."""

    @staticmethod
    def quotas(db: Session, tenant: str = None) -> Dict[str, Any]:
        q = db.query(AdmtUsageQuota).filter(AdmtUsageQuota.is_active.is_(True))
        quotas = q.all()
        if not quotas:
            return {"quotas": 0, "note": "Aucun quota."}
        depassements = []
        alertes = []
        for u in quotas:
            if u.quota_autorise is None or u.quota_autorise <= 0:
                continue
            pct = (u.consomme or 0) / u.quota_autorise * 100
            item = {"ressource": u.ressource, "periode": u.periode,
                    "consomme": u.consomme, "quota": u.quota_autorise,
                    "taux_pct": round(pct, 1)}
            if pct >= 100:
                depassements.append(item)
            elif pct >= 80:
                alertes.append(item)
        return {
            "quotas_total": len(quotas),
            "depassements": len(depassements),
            "alertes_80pct": len(alertes),
            "details_depassements": depassements,
        }

    @staticmethod
    def sauvegardes(db: Session, tenant: str = None) -> Dict[str, Any]:
        q = db.query(AdmtTenantBackup).filter(AdmtTenantBackup.is_active.is_(True))
        backups = q.all()
        if not backups:
            return {"sauvegardes": 0, "note": "Aucune sauvegarde."}
        par_statut: Dict[str, int] = {}
        for b in backups:
            s = b.statut or "sans_statut"
            par_statut[s] = par_statut.get(s, 0) + 1
        return {
            "sauvegardes_total": len(backups),
            "par_statut": par_statut,
        }

    @staticmethod
    def impersonations(db: Session) -> Dict[str, Any]:
        logs = db.query(AdmtImpersonationLog).filter(
            AdmtImpersonationLog.is_active.is_(True)).all()
        if not logs:
            return {"impersonations": 0, "note": "Aucune impersonation."}
        ouvertes = [l for l in logs
                    if "clos" not in str(l.statut or "").lower()
                    and "termin" not in str(l.statut or "").lower()]
        return {
            "impersonations_total": len(logs),
            "ouvertes": len(ouvertes),
        }
