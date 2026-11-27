"""Service metier superadmin : alertes plateforme par severite et
statut (non acquittees prioritaires) et suivi des migrations.
Aucune donnee inventee."""
from typing import Dict, Any

from sqlalchemy.orm import Session

from app.models.superadmin_c_deep import SaCPlatformAlert, SaCMigrationRun


class SuperadminService:
    """Alertes et migrations plateforme."""

    @staticmethod
    def alertes(db: Session) -> Dict[str, Any]:
        alertes = db.query(SaCPlatformAlert).filter(
            SaCPlatformAlert.is_active.is_(True)).all()
        if not alertes:
            return {"alertes": 0, "note": "Aucune alerte."}

        par_sev: Dict[str, int] = {}
        non_acquittees = 0
        for a in alertes:
            s = a.severite or "inconnue"
            par_sev[s] = par_sev.get(s, 0) + 1
            if not a.acquitte_par and (a.statut or "").lower() not in ("resolue", "cloturee"):
                non_acquittees += 1

        return {
            "alertes_total": len(alertes),
            "par_severite": par_sev,
            "non_acquittees": non_acquittees,
        }

    @staticmethod
    def migrations(db: Session) -> Dict[str, Any]:
        runs = db.query(SaCMigrationRun).filter(
            SaCMigrationRun.is_active.is_(True)).all()
        if not runs:
            return {"migrations": 0, "note": "Aucune migration."}
        par_statut: Dict[str, int] = {}
        for m in runs:
            s = m.statut or "sans_statut"
            par_statut[s] = par_statut.get(s, 0) + 1
        return {
            "migrations_total": len(runs),
            "par_statut": par_statut,
            "echouees": par_statut.get("echec", 0) + par_statut.get("failed", 0),
        }
