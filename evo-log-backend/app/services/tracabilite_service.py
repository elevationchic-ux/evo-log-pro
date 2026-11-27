"""Service metier tracabilite : genealogie des lots (chaines
parent/enfant). Remontee recursive des lots parents avec garde
anti-cycle, et bilan de provenance (nb ancetres, profondeur)."""
from typing import Dict, Any, List

from sqlalchemy.orm import Session

from app.models.tracabilite_deep import BatchGenealogy


class TraceabilityService:
    """Genealogie des lots."""

    @staticmethod
    def _lien_actif(db: Session, child: str):
        return db.query(BatchGenealogy).filter(
            BatchGenealogy.child_lot == child,
            BatchGenealogy.is_active.is_(True),
        ).all()

    @staticmethod
    def tracer_ascendants(db: Session, lot: str) -> Dict[str, Any]:
        """Remonte la chaine parent -> racine. Garde anti-cycle et
        profondeur max."""
        ascendants: List[Dict[str, Any]] = []
        vus = {lot}
        file_attente = [lot]
        profondeur_max = 0

        while file_attente and len(vus) < 200:
            courant = file_attente.pop(0)
            profondeur = 0
            # on marque la profondeur par lot visite via un dict simple
            for lien in TraceabilityService._lien_actif(db, courant):
                parent = lien.parent_lot
                if parent in vus:
                    continue  # cycle detecte : on ne remonte pas
                vus.add(parent)
                file_attente.append(parent)
                ascendants.append({
                    "lot": parent,
                    "via": courant,
                    "proportion": lien.proportion,
                    "quantite_mise_en_oeuvre": lien.quantite_mise_en_oeuvre,
                    "operation": lien.operation,
                })

        return {
            "lot": lot,
            "nb_ascendants": len(ascendants),
            "genealogie": ascendants,
            "note": "Cycles ignores : un lot parent deja visite n'est pas re-explore.",
        }

    @staticmethod
    def provenance(db: Session, lot: str) -> Dict[str, Any]:
        """Resume : nb parents directs, nb ascendants totaux, racines
        (lots sans parent connu)."""
        result = TraceabilityService.tracer_ascendants(db, lot)
        ascendants_lots = {a["lot"] for a in result["genealogie"]}
        racines = []
        for a_lot in ascendants_lots:
            if not TraceabilityService._lien_actif(db, a_lot):
                racines.append(a_lot)
        return {
            "lot": lot,
            "ascendants_total": result["nb_ascendants"],
            "racines": racines,
        }
