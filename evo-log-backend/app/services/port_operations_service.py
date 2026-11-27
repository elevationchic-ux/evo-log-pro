"""Service metier operations portuaires : facturation remorquage et
analyse de performance de manutention (cadence prevue vs reelle).
Aucun montant n'est invente : tarif et duree viennent des donnees."""
from decimal import Decimal
from typing import Dict, Any

from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.port_operations_deep import (
    TowageOperation, CargoHandlingPlan,)


class PortOperationsService:
    """Calculs portuaires sur donnees reelles."""

    @staticmethod
    def calculer_facturation_remorquage(
        db: Session, operation_id: int
    ) -> Dict[str, Any]:
        """Montant = duree_heures x tarif_xaf x nombre_remorqueurs.

        Refuse si une donnee tarifaire manque : jamais de facture
        fabriquee."""
        op = db.get(TowageOperation, operation_id)
        if not op:
            raise HTTPException(status_code=404, detail="Operation de remorquage introuvable")

        manquants = []
        if op.duree_heures is None:
            manquants.append("duree_heures")
        if op.tarif_xaf is None:
            manquants.append("tarif_xaf")
        nb_rem = op.nombre_remorqueurs or 1

        if manquants:
            raise HTTPException(
                status_code=422,
                detail=f"Donnees tarifaires manquantes : {', '.join(manquants)}",
            )

        montant = Decimal(str(op.duree_heures)) * Decimal(str(op.tarif_xaf)) * nb_rem
        return {
            "operation_id": op.id,
            "reference": op.reference,
            "duree_heures": float(op.duree_heures),
            "tarif_xaf": float(op.tarif_xaf),
            "nombre_remorqueurs": nb_rem,
            "montant_xaf": float(montant),
        }

    @staticmethod
    def analyse_cadence_manutenance(
        db: Session, plan_id: int
    ) -> Dict[str, Any]:
        """Ecart cadence reelle vs prevue ; NULL si non mesure."""
        plan = db.get(CargoHandlingPlan, plan_id)
        if not plan:
            raise HTTPException(status_code=404, detail="Plan de manutention introuvable")

        prevue = float(plan.cadence_prevue_t_h) if plan.cadence_prevue_t_h else None
        reelle = float(plan.cadence_reelle_t_h) if plan.cadence_reelle_t_h else None

        if reelle is None or prevue in (None, 0):
            return {
                "plan_id": plan.id,
                "cadence_prevue_t_h": prevue,
                "cadence_reelle_t_h": reelle,
                "ecart_pct": None,
                "note": "Cadence reelle non mesuree : ecart non calculable, jamais estime.",
            }

        ecart = (reelle - prevue) / prevue * 100
        return {
            "plan_id": plan.id,
            "reference": plan.reference_plan,
            "cadence_prevue_t_h": prevue,
            "cadence_reelle_t_h": reelle,
            "ecart_pct": round(ecart, 1),
            "performance": "superieure" if ecart > 0 else ("inferieure" if ecart < 0 else "conforme"),
        }
