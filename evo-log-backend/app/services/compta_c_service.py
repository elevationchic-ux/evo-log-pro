"""Service metier compta C : rapprochements bancaires (ecart
comptable vs bancaire) et contre-passations en attente.
Aucune donnee inventee."""
from decimal import Decimal
from typing import Dict, Any

from sqlalchemy.orm import Session

from app.models.compta_c_deep import CmptcJournalReversal, CmptcBankReconciliation


class ComptaCService:
    """Rapprochement et contre-passations."""

    @staticmethod
    def rapprochements(db: Session) -> Dict[str, Any]:
        raps = db.query(CmptcBankReconciliation).filter(
            CmptcBankReconciliation.is_active.is_(True)).all()
        if not raps:
            return {"rapprochements": 0, "note": "Aucun rapprochement."}
        ecarts = []
        en_attente = 0
        for r in raps:
            if r.ecart is not None and Decimal(str(r.ecart)) != 0:
                ecarts.append({
                    "compte_banque": r.compte_banque,
                    "ecart": float(r.ecart),
                    "solde_comptable": float(r.solde_comptable) if r.solde_comptable else None,
                    "solde_bancaire": float(r.solde_bancaire) if r.solde_bancaire else None,
                })
            if (r.statut or "").lower() not in ("rapproche", "valide", "clos"):
                en_attente += 1
        return {
            "rapprochements_total": len(raps),
            "avec_ecart": len(ecarts),
            "non_rapproches": en_attente,
            "details_ecarts": ecarts,
        }

    @staticmethod
    def contre_passations(db: Session) -> Dict[str, Any]:
        rev = db.query(CmptcJournalReversal).filter(
            CmptcJournalReversal.is_active.is_(True)).all()
        if not rev:
            return {"reversals": 0, "note": "Aucune contre-passation."}
        en_attente = [r for r in rev
                      if (r.statut or "").lower() not in ("valide", "poste", "comptabilise")]
        total = sum(Decimal(str(r.montant or 0)) for r in en_attente)
        return {
            "reversals_total": len(rev),
            "en_attente": len(en_attente),
            "montant_total_en_attente_xaf": float(total),
        }
