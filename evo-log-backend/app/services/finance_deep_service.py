"""Service metier finance deep : previsions de tresorerie (risque de
decouvert par horizon) et alertes de tresorerie ouvertes. Aucune
donnee inventee : previsions sans montant projete ignorees."""
from decimal import Decimal
from typing import Dict, Any

from sqlalchemy.orm import Session

from app.models.finance_deep import CashForecast, TreasuryAlert


class FinanceDeepService:
    """Tresorerie."""

    @staticmethod
    def previsions(db: Session) -> Dict[str, Any]:
        previsions = db.query(CashForecast).filter(
            CashForecast.is_active.is_(True)).all()
        if not previsions:
            return {"previsions": 0, "note": "Aucune prevision."}

        risques = []
        total_entrees = Decimal(0)
        total_sorties = Decimal(0)
        for p in previsions:
            if p.entree_attendue_xaf is not None:
                total_entrees += Decimal(str(p.entree_attendue_xaf))
            if p.sortie_attendue_xaf is not None:
                total_sorties += Decimal(str(p.sortie_attendue_xaf))
            if p.tresorerie_projete_xaf is not None and p.tresorerie_projete_xaf < 0:
                risques.append({
                    "reference": p.reference,
                    "horizon_mois": p.horizon_mois,
                    "tresorerie_projete_xaf": float(p.tresorerie_projete_xaf),
                })

        return {
            "previsions_total": len(previsions),
            "entrees_xaf": float(total_entrees),
            "sorties_xaf": float(total_sorties),
            "solde_net_xaf": float(total_entrees - total_sorties),
            "risques_decouvert": len(risques),
            "details_risques": risques,
        }

    @staticmethod
    def alertes_ouvertes(db: Session) -> Dict[str, Any]:
        alertes = db.query(TreasuryAlert).filter(
            TreasuryAlert.is_active.is_(True)).all()
        ouvertes = [a for a in alertes
                    if (a.statut and a.statut.value == "ouverte")
                    or (a.statut and str(a.statut) == "ouverte")]
        if not alertes:
            return {"alertes": 0, "note": "Aucune alerte."}
        return {
            "alertes_total": len(alertes),
            "ouvertes": len(ouvertes),
            "par_type": {
                str(a.type_alerte): sum(1 for x in alertes if x.type_alerte == a.type_alerte)
                for a in alertes
            } if alertes else {},
        }
