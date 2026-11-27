"""Service metier aerien avance : verification de la charge utile
d'un vol affrete (somme des poids declares vs capacite) et controle
des marchandises perissables. Aucune charge inventee : MAWB sans
cargo = poids 0, affretement absent = note honnete."""
from decimal import Decimal
from typing import Dict, Any

from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.aerien_b_deep import (
    CharteredFlight, PerishableCargo, LiveAnimalShipment,)


class AirBService:
    """Charge utile et conformite aerienne."""

    @staticmethod
    def charge_vol_affrete(db: Session, numero_mawb: str) -> Dict[str, Any]:
        """Poids total declare sur un MAWB vs capacite affretee.

        Le lien cargo <-> affretement se fait par numero : le charter
        doit avoir numero_affretement == numero_mawb."""
        perissables = db.query(PerishableCargo).filter(
            PerishableCargo.numero_mawb == numero_mawb,
            PerishableCargo.is_active.is_(True),
        ).all()
        animaux = db.query(LiveAnimalShipment).filter(
            LiveAnimalShipment.numero_mawb == numero_mawb,
            LiveAnimalShipment.is_active.is_(True),
        ).all()

        poids_kg = sum(p.poids_kg or 0 for p in perissables)
        charter = db.query(CharteredFlight).filter(
            CharteredFlight.numero_affretement == numero_mawb,
            CharteredFlight.is_active.is_(True),
        ).first()

        result = {
            "numero_mawb": numero_mawb,
            "nb_lignes_perissables": len(perissables),
            "nb_lignes_animaux": len(animaux),
            "poids_charge_kg": poids_kg,
            "note": "Animaux vivants sans poids declare non comptabilises dans la charge.",
        }

        if not charter:
            result["affretement"] = None
            result["note"] += " Aucun affretement associe : capacite non verifiable."
            return result

        result["affretement"] = charter.numero_affretement
        if charter.capacite_tonnes is not None:
            capacite_kg = charter.capacite_tonnes * 1000
            taux = round(poids_kg / capacite_kg * 100, 1) if capacite_kg else None
            result["capacite_kg"] = capacite_kg
            result["taux_charge_pct"] = taux
            result["conforme"] = poids_kg <= capacite_kg
        return result
