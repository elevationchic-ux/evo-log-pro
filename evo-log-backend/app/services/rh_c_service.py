"""Service metier RH C : plans de formation (heures financees vs
realisees) et sanctions disciplinaires actives. Aucune donnee
invente."""
from datetime import date
from typing import Dict, Any

from sqlalchemy.orm import Session

from app.models.rh_c_deep import RhCTrainingPlan, RhCDisciplinaryRecord


class RhCService:
    """Formation et discipline."""

    @staticmethod
    def formation(db: Session) -> Dict[str, Any]:
        plans = db.query(RhCTrainingPlan).filter(
            RhCTrainingPlan.is_active.is_(True)).all()
        if not plans:
            return {"plans": 0, "note": "Aucun plan de formation."}
        par_statut: Dict[str, int] = {}
        heures_fin = 0
        heures_rea = 0
        incomplets = []
        for p in plans:
            s = p.statut or "sans_statut"
            par_statut[s] = par_statut.get(s, 0) + 1
            heures_fin += p.heures_financees or 0
            heures_rea += p.heures_realisees or 0
            if p.heures_financees and (p.heures_realisees or 0) < p.heures_financees:
                incomplets.append({
                    "reference": p.reference,
                    "intitule": p.intitule,
                    "heures_financees": p.heures_financees,
                    "heures_realisees": p.heures_realisees or 0,
                })
        return {
            "plans_total": len(plans),
            "heures_financees": heures_fin,
            "heures_realisees": heures_rea,
            "taux_realisation_pct": round(heures_rea / heures_fin * 100, 1) if heures_fin else None,
            "par_statut": par_statut,
            "incomplets": incomplets,
        }

    @staticmethod
    def discipline(db: Session) -> Dict[str, Any]:
        sanctions = db.query(RhCDisciplinaryRecord).filter(
            RhCDisciplinaryRecord.is_active.is_(True)).all()
        if not sanctions:
            return {"sanctions": 0, "note": "Aucune sanction."}
        aujourdhui = date.today()
        actives = []
        par_type: Dict[str, int] = {}
        for s in sanctions:
            t = s.type_sanction or "inconnu"
            par_type[t] = par_type.get(t, 0) + 1
            if s.date_fin_effet is None or s.date_fin_effet >= aujourdhui:
                if "clos" not in str(s.statut or "").lower() and "annul" not in str(s.statut or "").lower():
                    actives.append({
                        "reference": s.reference,
                        "collaborateur": s.collaborateur,
                        "type_sanction": t,
                        "date_fin_effet": str(s.date_fin_effet) if s.date_fin_effet else None,
                    })
        return {
            "sanctions_total": len(sanctions),
            "actives": len(actives),
            "par_type": par_type,
            "details_actives": actives,
        }
