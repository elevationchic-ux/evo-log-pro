"""Service metier parc automobile : consommation carburant reelle
(L/100km recalculee depuis litres et km) et alerte pneus (profondeur
de couronne vs seuil legal). Aucune donnee inventee."""
from decimal import Decimal
from typing import Dict, Any, List

from sqlalchemy.orm import Session

from app.models.parc_deep import FuelConsumption, TyreRecord

SEUIL_PROFONDEUR_MM = Decimal("1.6")  # seuil legal minimum usure


class ParcService:
    """KPIs parc automobile."""

    @staticmethod
    def consommation_reelle(db: Session, vehicule_id: int) -> Dict[str, Any]:
        """Moyenne des conso_l100km saisies ET recalculee depuis
        litres/km quand la valeur n'est pas stockee."""
        pleins = db.query(FuelConsumption).filter(
            FuelConsumption.vehicule_id == vehicule_id,
            FuelConsumption.is_active.is_(True),
        ).all()
        if not pleins:
            return {"vehicule_id": vehicule_id, "pleins": 0,
                    "note": "Aucun plein enregistre."}

        conso_saisies = [float(p.conso_l100km) for p in pleins if p.conso_l100km]
        conso_calculees = []
        for p in pleins:
            if p.conso_l100km is None and p.litres and p.km_etape:
                conso_calculees.append(float(p.litres) * 100 / float(p.km_etape))

        toutes = conso_saisies + conso_calculees
        return {
            "vehicule_id": vehicule_id,
            "nb_pleins": len(pleins),
            "conso_moyenne_l100km": round(sum(toutes) / len(toutes), 2) if toutes else None,
            "litres_total": float(sum(p.litres or 0 for p in pleins)),
            "km_total": float(sum(p.km_etape or 0 for p in pleins)),
            "note": "Moyenne sur conso saisie + recalculee litres/km.",
        }

    @staticmethod
    def pneus_a_remplacer(db: Session) -> Dict[str, Any]:
        """Pneus dont la profondeur de couronne est sous le seuil."""
        pneus = db.query(TyreRecord).filter(
            TyreRecord.is_active.is_(True),
        ).all()
        a_remplacer = []
        for p in pneus:
            if p.profondeur_couronne_mm is not None and p.profondeur_couronne_mm < SEUIL_PROFONDEUR_MM:
                a_remplacer.append({
                    "numero_gomme": p.numero_gomme,
                    "position": p.position.value if p.position else None,
                    "profondeur_mm": float(p.profondeur_couronne_mm),
                })
        return {
            "pneus_total": len(pneus),
            "a_remplacer": len(a_remplacer),
            "seuil_mm": float(SEUIL_PROFONDEUR_MM),
            "details": a_remplacer,
        }
