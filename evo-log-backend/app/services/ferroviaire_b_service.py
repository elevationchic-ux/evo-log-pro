"""Service metier ferroviaire avance : verification du gabarit de
chargement d'un convoi (masse totale vs masse max de la ligne) et
analyse de composition. Refus honnete si gabarit ou convoi absent."""
from decimal import Decimal
from typing import Dict, Any

from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.ferroviaire_b_deep import RailLoadingGauge, RailTrainConsist


class RailGaugeService:
    """Verification gabarit ferroviaire."""

    @staticmethod
    def verifier_gabarit(
        db: Session, consist_id: int, code_gabarit: str
    ) -> Dict[str, Any]:
        consist = db.get(RailTrainConsist, consist_id)
        if not consist:
            raise HTTPException(status_code=404, detail="Convoi introuvable")
        if consist.masse_total_t is None:
            raise HTTPException(status_code=422, detail="Masse totale du convoi non renseignee")

        gauge = db.query(RailLoadingGauge).filter(
            RailLoadingGauge.code_gabarit == code_gabarit,
            RailLoadingGauge.is_active.is_(True),
        ).first()
        if not gauge:
            raise HTTPException(status_code=404, detail=f"Gabarit {code_gabarit} introuvable")

        masse = Decimal(str(consist.masse_total_t))
        if gauge.masse_max_t is not None:
            limite = Decimal(str(gauge.masse_max_t))
            depasse = masse > limite
            return {
                "consist_id": consist.id,
                "numero_train": consist.numero_train,
                "gabarit": code_gabarit,
                "ligne": gauge.ligne,
                "masse_convoi_t": float(masse),
                "masse_max_gabarit_t": float(limite),
                "marge_t": float(limite - masse),
                "conforme": not depasse,
            }
        # Gabarit sans limite de masse : conforme sur ce critere
        return {
            "consist_id": consist.id,
            "numero_train": consist.numero_train,
            "gabarit": code_gabarit,
            "ligne": gauge.ligne,
            "masse_convoi_t": float(masse),
            "masse_max_gabarit_t": None,
            "conforme": True,
            "note": "Gabarit sans limite de masse renseignee.",
        }

    @staticmethod
    def analyse_convoi(db: Session, consist_id: int) -> Dict[str, Any]:
        consist = db.get(RailTrainConsist, consist_id)
        if not consist:
            raise HTTPException(status_code=404, detail="Convoi introuvable")
        nb = consist.nb_wagons or 0
        masse_par_wagon = (
            round(float(consist.masse_total_t) / nb, 1)
            if consist.masse_total_t is not None and nb > 0 else None
        )
        return {
            "consist_id": consist.id,
            "numero_train": consist.numero_train,
            "nb_wagons": nb or None,
            "masse_total_t": float(consist.masse_total_t) if consist.masse_total_t is not None else None,
            "masse_par_wagon_t": masse_par_wagon,
            "longueur_m": consist.longueur_m,
        }
