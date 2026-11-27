"""Service metier reports deep : scorecards par pole (KPI rouges/
oranges/verts, score global) et ecarts vs benchmark sectoriel.
Aucune donnee inventee."""
from decimal import Decimal
from typing import Dict, Any

from sqlalchemy.orm import Session

from app.models.reports_deep import Scorecard, IndustryBenchmark


class ReportsDeepService:
    """Scorecards et benchmarks."""

    @staticmethod
    def scorecards(db: Session, periode: str = None) -> Dict[str, Any]:
        q = db.query(Scorecard).filter(Scorecard.is_active.is_(True))
        if periode:
            q = q.filter(Scorecard.periode == periode)
        scorecards = q.all()
        if not scorecards:
            return {"periode": periode, "scorecards": 0,
                    "note": "Aucun scorecard."}

        total_rouges = sum(s.kpis_rouges or 0 for s in scorecards)
        total_oranges = sum(s.kpis_oranges or 0 for s in scorecards)
        total_verts = sum(s.kpis_verts or 0 for s in scorecards)
        scores = [float(s.score_global_pct) for s in scorecards
                  if s.score_global_pct is not None]

        return {
            "periode": periode,
            "scorecards_total": len(scorecards),
            "kpis_rouges": total_rouges,
            "kpis_oranges": total_oranges,
            "kpis_verts": total_verts,
            "score_moyen_pct": round(sum(scores) / len(scores), 1) if scores else None,
            "par_pole": [
                {"pole": s.pole, "score_pct": float(s.score_global_pct) if s.score_global_pct else None,
                 "rouges": s.kpis_rouges or 0}
                for s in scorecards
            ],
        }

    @staticmethod
    def benchmarks(db: Session) -> Dict[str, Any]:
        bench = db.query(IndustryBenchmark).filter(
            IndustryBenchmark.is_active.is_(True)).all()
        if not bench:
            return {"benchmarks": 0, "note": "Aucun benchmark."}
        au_dessus = []
        en_retard = []
        for b in bench:
            if b.valeur_interne is None or b.valeur_benchmark is None:
                continue
            interne = Decimal(str(b.valeur_interne))
            ref = Decimal(str(b.valeur_benchmark))
            ecart = (interne - ref) / ref * 100 if ref else None
            item = {
                "indicateur": b.indicateur,
                "valeur_interne": float(interne),
                "valeur_benchmark": float(ref),
                "ecart_pct": round(float(ecart), 1) if ecart is not None else None,
            }
            if ecart is not None and ecart >= 0:
                au_dessus.append(item)
            else:
                en_retard.append(item)
        return {
            "benchmarks_total": len(bench),
            "comparables": len(au_dessus) + len(en_retard),
            "au_dessus": len(au_dessus),
            "en_retard": len(en_retard),
            "details_retard": en_retard,
        }
