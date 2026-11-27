"""Service metier courier avance : performance des livreurs (taux de
reussite des tentatives de livraison) et productivite (colis/km par
shift). Aucun chiffre invente : statuts lus tels quels."""
from typing import Dict, Any

from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.courier_e_deep import (
    Cour2DeliveryAttempt, Cour2CourierShiftLog,)

_STATUTS_REUSSITE = ("livre", "reuss", "success", "delivre")


class CourierEService:
    """KPIs livreurs."""

    @staticmethod
    def performance_livreur(db: Session, livreur: str) -> Dict[str, Any]:
        tentatives = db.query(Cour2DeliveryAttempt).filter(
            Cour2DeliveryAttempt.livreur == livreur,
            Cour2DeliveryAttempt.is_active.is_(True),
        ).all()
        if not tentatives:
            return {"livreur": livreur, "tentatives": 0,
                    "note": "Aucune tentative enregistree pour ce livreur."}

        reussies = sum(
            1 for t in tentatives
            if (t.statut or "").lower() in _STATUTS_REUSSITE
            or any(k in (t.statut or "").lower() for k in _STATUTS_REUSSITE)
        )
        return {
            "livreur": livreur,
            "tentatives_total": len(tentatives),
            "reussies": reussies,
            "echecs": len(tentatives) - reussies,
            "taux_reussite_pct": round(reussies / len(tentatives) * 100, 1),
        }

    @staticmethod
    def productivite_livreur(db: Session, livreur: str) -> Dict[str, Any]:
        shifts = db.query(Cour2CourierShiftLog).filter(
            Cour2CourierShiftLog.livreur == livreur,
            Cour2CourierShiftLog.is_active.is_(True),
        ).all()
        if not shifts:
            return {"livreur": livreur, "shifts": 0,
                    "note": "Aucun shift enregistre pour ce livreur."}

        total_colis = sum(s.colis_livres or 0 for s in shifts)
        total_km = sum(s.km or 0 for s in shifts)
        return {
            "livreur": livreur,
            "nb_shifts": len(shifts),
            "colis_livres_total": total_colis,
            "km_total": total_km,
            "colis_par_km": round(total_colis / total_km, 2) if total_km else None,
        }
