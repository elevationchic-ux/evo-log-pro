"""Service metier reports C : rapports planifies en retard
d'execution (prochaine_execution passee, statut actif) et
statistiques d'exports. Aucune donnee inventee."""
from datetime import datetime, timezone
from typing import Dict, Any

from sqlalchemy.orm import Session

from app.models.reports_c_deep import RptcScheduledReport, RptcDataExport


class ReportsCService:
    """Suivi rapports programmes."""

    @staticmethod
    def rapports_en_retard(db: Session) -> Dict[str, Any]:
        rapports = db.query(RptcScheduledReport).filter(
            RptcScheduledReport.is_active.is_(True),
        ).all()
        maintenant = datetime.now(timezone.utc)
        en_retard = []
        a_venir = 0
        for m in rapports:
            if m.prochaine_execution is None:
                continue
            # Normalise timezone si besoin
            exec_date = m.prochaine_execution
            if exec_date.tzinfo is None:
                exec_date = exec_date.replace(tzinfo=timezone.utc)
            if exec_date < maintenant:
                en_retard.append({
                    "reference": m.reference,
                    "nom": m.nom,
                    "frequence": m.frequence,
                    "prochaine_execution": str(m.prochaine_execution),
                })
            else:
                a_venir += 1
        return {
            "rapports_total": len(rapports),
            "en_retard": len(en_retard),
            "a_venir": a_venir,
            "details_retard": en_retard,
        }

    @staticmethod
    def stats_exports(db: Session) -> Dict[str, Any]:
        exports = db.query(RptcDataExport).filter(
            RptcDataExport.is_active.is_(True)).all()
        if not exports:
            return {"exports": 0, "note": "Aucun export enregistre."}
        return {"exports": len(exports),
                "par_format": {f: sum(1 for e in exports if e.format == f)
                               for f in set(e.format for e in exports)}}
