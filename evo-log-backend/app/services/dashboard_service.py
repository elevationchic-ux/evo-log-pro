"""Service metier dashboard : atteinte des objectifs KPI
(valeur vs objectif par indicateur) et KPI en alerte. Aucune
donnee inventee : KPI sans objectif exclus du calcul d'atteinte."""
from decimal import Decimal
from typing import Dict, Any

from sqlalchemy.orm import Session

from app.models.dashboard_b_deep import DashboardbOperationalKpi


class DashboardService:
    """Atteinte objectifs KPI."""

    @staticmethod
    def atteinte_objectifs(db: Session) -> Dict[str, Any]:
        kpis = db.query(DashboardbOperationalKpi).filter(
            DashboardbOperationalKpi.is_active.is_(True)).all()
        if not kpis:
            return {"kpis": 0, "note": "Aucun KPI enregistre."}

        atteints = 0
        en_retard = []
        sans_objectif = 0
        details = []
        for k in kpis:
            if k.objectif is None or k.valeur is None:
                sans_objectif += 1
                continue
            valeur = Decimal(str(k.valeur))
            objectif = Decimal(str(k.objectif))
            if objectif == 0:
                sans_objectif += 1
                continue
            pct = float(valeur / objectif * 100)
            details.append({
                "libelle": k.libelle,
                "valeur": float(valeur),
                "objectif": float(objectif),
                "atteinte_pct": round(pct, 1),
            })
            if valeur >= objectif:
                atteints += 1
            else:
                en_retard.append(k.libelle)

        return {
            "kpis_total": len(kpis),
            "avec_objectif": len(details),
            "sans_objectif": sans_objectif,
            "atteints": atteints,
            "en_retard": en_retard,
            "details": details,
        }
