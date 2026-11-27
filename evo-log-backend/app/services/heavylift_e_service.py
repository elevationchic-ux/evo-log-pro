"""Service metier heavy-lift avance : validation du moment de charge
(moment_applique vs capacite de la configuration grue). Taux
d'utilisation calcule, verdict OK / tendu / depasse ; aucune capacite
inventee."""
from decimal import Decimal
from typing import Dict, Any

from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.heavylift_e_deep import Heavy2LoadMomentCalc


class Heavy2MomentService:
    """Validation moment de charge."""

    SEUIL_TENDU_PCT = 80

    @staticmethod
    def valider_moment(db: Session, calc_id: int) -> Dict[str, Any]:
        calc = db.get(Heavy2LoadMomentCalc, calc_id)
        if not calc:
            raise HTTPException(status_code=404, detail="Calcul de moment introuvable")
        if calc.moment_applique is None:
            raise HTTPException(status_code=422, detail="Moment applique non renseigne")
        if not calc.capacite:
            return {
                "calc_id": calc.id,
                "verdict": "non_evaluable",
                "note": "Capacite de la configuration non renseignee : jamais estimee.",
            }

        moment = Decimal(str(calc.moment_applique))
        capacite = Decimal(str(calc.capacite))
        if capacite <= 0:
            raise HTTPException(status_code=422, detail="Capacite doit etre > 0")
        if moment <= 0:
            raise HTTPException(status_code=422, detail="Moment doit etre > 0")

        taux = moment / capacite * 100
        if taux > 100:
            verdict = "depasse"
        elif taux > Heavy2MomentService.SEUIL_TENDU_PCT:
            verdict = "tendu"
        else:
            verdict = "ok"

        return {
            "calc_id": calc.id,
            "reference": calc.reference,
            "configuration": calc.configuration,
            "moment_applique": float(moment),
            "capacite": float(capacite),
            "taux_utilisation_pct": round(float(taux), 1),
            "verdict": verdict,
        }
