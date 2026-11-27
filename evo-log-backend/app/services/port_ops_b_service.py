"""Service metier operations portuaires avance : occupation des
postes a quai (heures planifiees par escale) et volume de trafic.
Aucune duree inventee : fenetre incomplete = escale ignoree."""
from datetime import datetime
from typing import Dict, Any, List

from sqlalchemy.orm import Session

from app.models.port_ops_b_deep import PortbBerthSchedule


class PortOpsBService:
    """Occupation des quais."""

    @staticmethod
    def occupation_quai(db: Session, poste: str) -> Dict[str, Any]:
        schedules = db.query(PortbBerthSchedule).filter(
            PortbBerthSchedule.poste_amarrage == poste,
            PortbBerthSchedule.is_active.is_(True),
        ).all()
        if not schedules:
            return {"poste": poste, "escales": 0,
                    "note": "Aucune escale planifiee sur ce poste."}

        total_heures = 0.0
        escales_calculees = 0
        escales_incompletes = 0
        navires = []
        for s in schedules:
            if s.date_arrivee_prevue and s.date_depart_prevu:
                h = (s.date_depart_prevu - s.date_arrivee_prevue).total_seconds() / 3600
                if h > 0:
                    total_heures += h
                    escales_calculees += 1
            else:
                escales_incompletes += 1
            if s.navire:
                navires.append(s.navire)

        return {
            "poste": poste,
            "escales_total": len(schedules),
            "escales_horodatees": escales_calculees,
            "escales_sans_fenetre": escales_incompletes,
            "heures_occupation": round(total_heures, 1),
            "navires": navires,
            "note": "Heures = somme des fenetres arrivee->depart prevues.",
        }
