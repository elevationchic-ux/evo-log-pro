"""Service metier finance C : positions de tresorerie previsionnelles
(position finale vs solde debut) et avances d'affacturage vs montant
facture. Aucune donnee inventee."""
from datetime import date
from decimal import Decimal
from typing import Dict, Any

from sqlalchemy.orm import Session

from app.models.finance_c_deep import FincCashFlowForecast, FincInvoiceFinancing


class FinanceCService:
    """Tresorerie previsionnelle et affacturage."""

    @staticmethod
    def previsions(db: Session) -> Dict[str, Any]:
        previsions = db.query(FincCashFlowForecast).filter(
            FincCashFlowForecast.is_active.is_(True)).all()
        if not previsions:
            return {"previsions": 0, "note": "Aucune prevision."}
        risques = []
        solde_net = Decimal(0)
        for p in previsions:
            if p.entrees_prevues is not None:
                solde_net += Decimal(str(p.entrees_prevues))
            if p.sorties_prevues is not None:
                solde_net -= Decimal(str(p.sorties_prevues))
            if p.position_finale is not None and p.position_finale < 0:
                risques.append({
                    "reference": p.reference,
                    "periode": p.periode,
                    "position_finale": float(p.position_finale),
                })
        return {
            "previsions_total": len(previsions),
            "solde_net_previsionnel_xaf": float(solde_net),
            "risques_decouvert": len(risques),
            "details_risques": risques,
        }

    @staticmethod
    def affacturage(db: Session) -> Dict[str, Any]:
        financements = db.query(FincInvoiceFinancing).filter(
            FincInvoiceFinancing.is_active.is_(True)).all()
        if not financements:
            return {"financements": 0, "note": "Aucun financement."}
        aujourdhui = date.today()
        en_cours = []
        echus = []
        total_avances = Decimal(0)
        for f in financements:
            avance = Decimal(str(f.montant_facture or 0)) * Decimal(str(f.avance_pct or 0)) / 100
            if (f.statut or "").lower() not in ("solde", "clos", "rembourse"):
                en_cours.append({
                    "reference": f.reference,
                    "facture": f.facture,
                    "avance_calculee_xaf": float(avance),
                })
                total_avances += avance
            if f.date_echeance and f.date_echeance < aujourdhui and \
               (f.statut or "").lower() not in ("solde", "clos", "rembourse"):
                echus.append(f.reference)
        return {
            "financements_total": len(financements),
            "en_cours": len(en_cours),
            "echus_non_rembourses": len(echus),
            "avances_en_cours_xaf": float(total_avances),
            "details_echus": echus,
        }
