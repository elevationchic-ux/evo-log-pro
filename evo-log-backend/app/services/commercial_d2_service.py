"""Service metier commercial D2 : veille concurrentielle
(faits observes par concurrent et marche). Aucune donnee
invente."""
from typing import Dict, Any

from sqlalchemy.orm import Session

from app.models.commercial_d2_deep import CommCompetitorNote


class CommercialD2Service:
    """Veille concurrentielle."""

    @staticmethod
    def veille(db: Session, concurrent: str = None) -> Dict[str, Any]:
        q = db.query(CommCompetitorNote).filter(
            CommCompetitorNote.is_active.is_(True))
        if concurrent:
            q = q.filter(CommCompetitorNote.concurrent == concurrent)
        notes = q.all()
        if not notes:
            return {"concurrent": concurrent, "notes": 0,
                    "note": "Aucune note concurrentielle."}

        par_concurrent: Dict[str, int] = {}
        par_marche: Dict[str, int] = {}
        for n in notes:
            c = n.concurrent or "inconnu"
            m = n.marche or "inconnu"
            par_concurrent[c] = par_concurrent.get(c, 0) + 1
            par_marche[m] = par_marche.get(m, 0) + 1

        return {
            "concurrent": concurrent,
            "notes_total": len(notes),
            "par_concurrent": par_concurrent,
            "par_marche": par_marche,
            "details": [
                {"reference": n.reference, "concurrent": n.concurrent,
                 "fait": n.fait_observe, "marche": n.marche,
                 "date": str(n.date) if n.date else None}
                for n in notes
            ],
        }
