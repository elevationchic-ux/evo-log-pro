"""Service metier transit B : taux de conformite des inspections
douanieres par bureau/agent et par periode. Aucune donnee inventee :
inspections sans verdict conformite sont exclues et comptees."""
from typing import Dict, Any

from sqlalchemy.orm import Session

from app.models.transit_b_deep import TransitbInspectionRecord


class TransitBService:
    """KPIs inspections transit."""

    @staticmethod
    def taux_conformite(
        db: Session, bureau: str = None, agent: str = None
    ) -> Dict[str, Any]:
        q = db.query(TransitbInspectionRecord).filter(
            TransitbInspectionRecord.is_active.is_(True))
        if bureau:
            q = q.filter(TransitbInspectionRecord.bureau == bureau)
        if agent:
            q = q.filter(TransitbInspectionRecord.agent == agent)
        inspections = q.all()

        with_verdict = [i for i in inspections if i.conformite is not None]
        conformes = [i for i in with_verdict if i.conformite]
        sans_verdict = len(inspections) - len(with_verdict)

        return {
            "bureau": bureau,
            "agent": agent,
            "inspections_total": len(inspections),
            "avec_verdict": len(with_verdict),
            "sans_verdict": sans_verdict,
            "conformes": len(conformes),
            "non_conformes": len(with_verdict) - len(conformes),
            "taux_conformite_pct": (
                round(len(conformes) / len(with_verdict) * 100, 1)
                if with_verdict else None
            ),
            "note": "Taux None sans verdict : jamais de conformite inventee.",
        }
