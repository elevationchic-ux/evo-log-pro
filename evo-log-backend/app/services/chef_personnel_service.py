"""Service metier chef personnel : pipeline de recrutement (candidats
par poste et phase de selection) et entretiens programmes. Aucune
donnee inventee."""
from typing import Dict, Any

from sqlalchemy.orm import Session

from app.models.chef_personnel_d_deep import ChpCandidateSelection, ChpInterviewSchedule


class ChefPersonnelService:
    """Pipeline recrutement."""

    @staticmethod
    def pipeline(db: Session, poste: str = None) -> Dict[str, Any]:
        q = db.query(ChpCandidateSelection).filter(
            ChpCandidateSelection.is_active.is_(True))
        if poste:
            q = q.filter(ChpCandidateSelection.poste == poste)
        candidats = q.all()
        if not candidats:
            return {"poste": poste, "candidats": 0,
                    "note": "Aucun candidat en selection."}

        par_phase: Dict[str, int] = {}
        par_statut: Dict[str, int] = {}
        for c in candidats:
            ph = c.phase or "sans_phase"
            st = c.statut or "sans_statut"
            par_phase[ph] = par_phase.get(ph, 0) + 1
            par_statut[st] = par_statut.get(st, 0) + 1

        return {
            "poste": poste,
            "candidats_total": len(candidats),
            "par_phase": par_phase,
            "par_statut": par_statut,
        }

    @staticmethod
    def entretiens_a_venir(db: Session) -> Dict[str, Any]:
        entretiens = db.query(ChpInterviewSchedule).filter(
            ChpInterviewSchedule.is_active.is_(True)).all()
        a_venir = [e for e in entretiens
                   if (e.statut or "").lower() not in ("realise", "annule", "reporté", "reporte")]
        return {
            "entretiens_total": len(entretiens),
            "a_venir_ou_en_cours": len(a_venir),
        }
