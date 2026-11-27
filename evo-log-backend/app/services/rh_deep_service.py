"""Service metier RH deep : performance moyenne et objectifs
atteints par periode, cas disciplinaires par sanction, soldes
tout compte des departs. Aucune donnee inventee."""
from decimal import Decimal
from typing import Dict, Any

from sqlalchemy.orm import Session

from app.models.rh_deep import PerformanceReview, DisciplinaryCase, EmployeeExit


class RhDeepService:
    """KPIs RH avances."""

    @staticmethod
    def performance(db: Session, periode: str = None) -> Dict[str, Any]:
        q = db.query(PerformanceReview).filter(
            PerformanceReview.is_active.is_(True))
        if periode:
            q = q.filter(PerformanceReview.periode == periode)
        reviews = q.all()
        if not reviews:
            return {"periode": periode, "evaluations": 0,
                    "note": "Aucune evaluation."}

        notes = [float(r.note_global) for r in reviews if r.note_global is not None]
        objectifs = [float(r.objectifs_atteints_pct) for r in reviews
                     if r.objectifs_atteints_pct is not None]
        return {
            "periode": periode,
            "evaluations_total": len(reviews),
            "note_moyenne": round(sum(notes) / len(notes), 2) if notes else None,
            "objectifs_moyen_pct": round(sum(objectifs) / len(objectifs), 1) if objectifs else None,
            "nb_avec_notes": len(notes),
        }

    @staticmethod
    def discipline(db: Session) -> Dict[str, Any]:
        cas = db.query(DisciplinaryCase).filter(
            DisciplinaryCase.is_active.is_(True)).all()
        if not cas:
            return {"cas": 0, "note": "Aucun cas disciplinaire."}
        par_sanction: Dict[str, int] = {}
        ouvertes = 0
        for c in cas:
            s = str(c.type_sanction or "inconnu")
            par_sanction[s] = par_sanction.get(s, 0) + 1
            if "ouvert" in str(c.statut or "").lower():
                ouvertes += 1
        return {
            "cas_total": len(cas),
            "ouvertes": ouvertes,
            "par_sanction": par_sanction,
        }

    @staticmethod
    def departs(db: Session) -> Dict[str, Any]:
        departs = db.query(EmployeeExit).filter(
            EmployeeExit.is_active.is_(True)).all()
        if not departs:
            return {"departs": 0, "note": "Aucun depart."}
        par_type: Dict[str, int] = {}
        total_ttc = Decimal(0)
        for d in departs:
            t = str(d.type_depart or "inconnu")
            par_type[t] = par_type.get(t, 0) + 1
            if d.solde_tout_compte_xaf:
                total_ttc += Decimal(str(d.solde_tout_compte_xaf))
        return {
            "departs_total": len(departs),
            "par_type": par_type,
            "soldes_ttc_total_xaf": float(total_ttc),
        }
