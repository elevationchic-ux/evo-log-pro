"""Service metier technicien : temps de main-d'oeuvre par technicien
(minutes cumulees par OT) et repartition des tickets de panne par
severite. Aucune donnee inventee."""
from typing import Dict, Any

from sqlalchemy.orm import Session

from app.models.technicien_d_deep import TechLaborTimesheet, TechBreakdownTicket


class TechnicienService:
    """KPIs techniciens."""

    @staticmethod
    def temps_mo_technicien(db: Session, technicien: str) -> Dict[str, Any]:
        feuilles = db.query(TechLaborTimesheet).filter(
            TechLaborTimesheet.technicien == technicien,
            TechLaborTimesheet.is_active.is_(True),
        ).all()
        if not feuilles:
            return {"technicien": technicien, "feuilles": 0,
                    "note": "Aucun temps enregistre pour ce technicien."}
        total_min = sum(f.minutes or 0 for f in feuilles)
        par_ot: Dict[str, int] = {}
        for f in feuilles:
            ot = f.ordre_travail or "sans_ot"
            par_ot[ot] = par_ot.get(ot, 0) + (f.minutes or 0)
        return {
            "technicien": technicien,
            "nb_feuilles": len(feuilles),
            "minutes_total": total_min,
            "heures_total": round(total_min / 60, 2),
            "par_ordre_travail": par_ot,
        }

    @staticmethod
    def tickets_par_severite(db: Session) -> Dict[str, Any]:
        tickets = db.query(TechBreakdownTicket).filter(
            TechBreakdownTicket.is_active.is_(True)).all()
        if not tickets:
            return {"tickets": 0, "note": "Aucun ticket de panne."}
        par_sev: Dict[str, int] = {}
        for t in tickets:
            s = t.severite or "non_evaluee"
            par_sev[s] = par_sev.get(s, 0) + 1
        return {
            "tickets_total": len(tickets),
            "par_severite": par_sev,
            "ouverts": sum(1 for t in tickets
                          if (t.statut or "").lower() in ("ouvert", "en_cours", "ouvert")),
        }
