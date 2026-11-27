"""Service metier dashboard deep : sante des modules (etat, taux
d'erreur, latence) et alertes operationnelles ouvertes. Aucune
donnee inventee."""
from typing import Dict, Any

from sqlalchemy.orm import Session

from app.models.dashboard_deep import ModuleHealth, OperationalAlert


class DashboardDeepService:
    """Sante modules et alertes."""

    @staticmethod
    def sante_modules(db: Session) -> Dict[str, Any]:
        modules = db.query(ModuleHealth).filter(
            ModuleHealth.is_active.is_(True)).all()
        if not modules:
            return {"modules": 0, "note": "Aucun module suivi."}
        par_etat: Dict[str, int] = {}
        degradees = []
        for m in modules:
            etat = getattr(m.etat, "value", m.etat) or "inconnu"
            par_etat[etat] = par_etat.get(etat, 0) + 1
            if etat.lower() not in ("operationnel", "ok", "nominal"):
                degradees.append({
                    "code_module": m.code_module,
                    "etat": etat,
                    "taux_erreur_pct": float(m.taux_erreur_pct) if m.taux_erreur_pct else None,
                    "latence_p95_ms": m.latence_p95_ms,
                })
        return {
            "modules_total": len(modules),
            "par_etat": par_etat,
            "degradees": len(degradees),
            "details_degradees": degradees,
        }

    @staticmethod
    def alertes(db: Session) -> Dict[str, Any]:
        alertes = db.query(OperationalAlert).filter(
            OperationalAlert.is_active.is_(True)).all()
        if not alertes:
            return {"alertes": 0, "note": "Aucune alerte."}
        par_niveau: Dict[str, int] = {}
        ouvertes = 0
        for a in alertes:
            n = getattr(a.niveau, "value", a.niveau) or "warning"
            par_niveau[n] = par_niveau.get(n, 0) + 1
            statut = getattr(a.statut, "value", a.statut) or ""
            if "ouvert" in str(statut).lower() or "charge" in str(statut).lower():
                ouvertes += 1
        return {
            "alertes_total": len(alertes),
            "par_niveau": par_niveau,
            "ouvertes": ouvertes,
        }
