"""Service metier cycle conteneur : durees par phase du cycle de vie
(navire -> dechargement -> quai -> sortie). Chaque phase non horodatee
est renvoyee a None : jamais de duree inventee."""
from datetime import datetime
from typing import Dict, Any, Optional

from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.conteneur_cycle import CycleConteneur


def _heures(a: Optional[datetime], b: Optional[datetime]) -> Optional[float]:
    if a is None or b is None:
        return None
    delta = (b - a).total_seconds() / 3600
    return round(delta, 2) if delta >= 0 else None


class ConteneurCycleService:
    """Analyse le cycle de vie d'un conteneur sur donnees reelles."""

    @staticmethod
    def analyser_cycle(db: Session, cycle_id: int) -> Dict[str, Any]:
        cycle = db.get(CycleConteneur, cycle_id)
        if not cycle:
            raise HTTPException(status_code=404, detail="Cycle conteneur introuvable")

        phases = {
            "arrivee_navire_a_dechargement_h": _heures(
                cycle.date_arrivee_navire, cycle.date_dechargement),
            "dechargement_a_quai_h": _heures(
                cycle.date_dechargement, cycle.date_mise_quai),
            "quai_a_sortie_h": _heures(
                cycle.date_mise_quai, cycle.date_sortie),
        }
        total = _heures(cycle.date_arrivee_navire, cycle.date_sortie)
        if total is None and cycle.date_dechargement and cycle.date_sortie:
            total = _heures(cycle.date_dechargement, cycle.date_sortie)

        return {
            "cycle_id": cycle.id,
            "conteneur_id": cycle.conteneur_id,
            "voyage": cycle.voyage,
            "statut": cycle.statut.value if cycle.statut else None,
            "phases_h": phases,
            "temps_total_cycle_h": total,
            "temps_cycle_enregistre_h": (
                float(cycle.temps_cycle_heures)
                if cycle.temps_cycle_heures is not None else None
            ),
            "note": "Phases non horodatees = None ; aucune duree estimee.",
        }

    @staticmethod
    def marquer_sortie(
        db: Session, cycle_id: int, date_sortie: datetime
    ) -> Dict[str, Any]:
        """Enregistre la sortie et recalcule le temps de cycle si
        l'arrivee navire est connue."""
        cycle = db.get(CycleConteneur, cycle_id)
        if not cycle:
            raise HTTPException(status_code=404, detail="Cycle conteneur introuvable")
        if cycle.date_sortie is not None:
            raise HTTPException(status_code=409, detail="Sortie deja enregistree")

        cycle.date_sortie = date_sortie
        if cycle.date_arrivee_navire:
            duree = _heures(cycle.date_arrivee_navire, date_sortie)
            if duree is not None:
                from decimal import Decimal
                cycle.temps_cycle_heures = Decimal(str(duree))
        db.commit()
        db.refresh(cycle)
        return {"cycle_id": cycle.id, "date_sortie": cycle.date_sortie,
                "temps_cycle_heures": float(cycle.temps_cycle_heures) if cycle.temps_cycle_heures else None}
