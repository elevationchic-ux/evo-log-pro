"""Service metier comptabilite deep : rapprochements bancaires
(ecart banque vs compta) et controle budgetaire (consomme vs prevu).
Aucune donnee inventee : soldes absents signales."""
from decimal import Decimal
from typing import Dict, Any

from sqlalchemy.orm import Session

from app.models.comptabilite_deep import BankReconciliation, BudgetControl


class ComptabiliteDeepService:
    """Rapprochement et budget."""

    @staticmethod
    def rapprochements(db: Session) -> Dict[str, Any]:
        raps = db.query(BankReconciliation).filter(
            BankReconciliation.is_active.is_(True)).all()
        if not raps:
            return {"rapprochements": 0, "note": "Aucun rapprochement."}

        ouverts = 0
        avec_ecart = []
        for r in raps:
            statut = str(r.statut or "").lower()
            if "clot" not in statut and "valid" not in statut:
                ouverts += 1
            if r.ecart_xaf is not None and Decimal(str(r.ecart_xaf)) != 0:
                avec_ecart.append({
                    "reference": r.reference,
                    "compte_banque": r.compte_banque,
                    "ecart_xaf": float(r.ecart_xaf),
                    "solde_banque_xaf": float(r.solde_banque_xaf) if r.solde_banque_xaf else None,
                    "solde_compta_xaf": float(r.solde_compta_xaf) if r.solde_compta_xaf else None,
                })

        return {
            "rapprochements_total": len(raps),
            "ouverts": ouverts,
            "avec_ecart": len(avec_ecart),
            "details_ecarts": avec_ecart,
        }

    @staticmethod
    def controle_budgetaire(db: Session) -> Dict[str, Any]:
        budgets = db.query(BudgetControl).filter(
            BudgetControl.is_active.is_(True)).all()
        if not budgets:
            return {"budgets": 0, "note": "Aucun budget."}

        depassements = []
        total_prevu = Decimal(0)
        total_consomme = Decimal(0)
        for b in budgets:
            if b.budget_prevu_xaf is not None:
                total_prevu += Decimal(str(b.budget_prevu_xaf))
            if b.consomme_xaf is not None:
                total_consomme += Decimal(str(b.consomme_xaf))
            if b.budget_prevu_xaf and b.consomme_xaf:
                if Decimal(str(b.consomme_xaf)) > Decimal(str(b.budget_prevu_xaf)):
                    depassements.append({
                        "reference": b.reference,
                        "centre_cout": b.centre_cout,
                        "depassement_xaf": float(Decimal(str(b.consomme_xaf)) - Decimal(str(b.budget_prevu_xaf))),
                    })

        return {
            "budgets_total": len(budgets),
            "budget_prevu_xaf": float(total_prevu),
            "consomme_xaf": float(total_consomme),
            "taux_consommation_pct": round(float(total_consomme / total_prevu * 100), 1) if total_prevu else None,
            "depassements": len(depassements),
            "details_depassements": depassements,
        }
