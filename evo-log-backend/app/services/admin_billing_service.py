"""Service metier admin C : facturation SaaS (factures en retard
d'echeance, encours par tenant). Aucune donnee inventee."""
from datetime import date
from decimal import Decimal
from typing import Dict, Any

from sqlalchemy.orm import Session

from app.models.admin_c_deep import AdmCBillingInvoice

_STATUTS_PAYE = ("payee", "paye", "payée", "soldée", "soldee", "reglee")


class AdminBillingService:
    """Facturation SaaS."""

    @staticmethod
    def factures(db: Session) -> Dict[str, Any]:
        factures = db.query(AdmCBillingInvoice).filter(
            AdmCBillingInvoice.is_active.is_(True)).all()
        if not factures:
            return {"factures": 0, "note": "Aucune facture."}

        aujourdhui = date.today()
        impayees = []
        payees = 0
        par_tenant: Dict[str, float] = {}
        for f in factures:
            statut = (f.statut or "").lower()
            montant = float(f.montant_ttc or f.montant_ht or 0)
            if statut in _STATUTS_PAYE:
                payees += 1
                continue
            en_retard = f.date_echeance and f.date_echeance < aujourdhui
            impayees.append({
                "reference": f.reference,
                "tenant": f.tenant,
                "montant_ttc": montant,
                "date_echeance": str(f.date_echeance) if f.date_echeance else None,
                "en_retard": bool(en_retard),
            })
            par_tenant[f.tenant or "inconnu"] = par_tenant.get(f.tenant or "inconnu", 0) + montant

        return {
            "factures_total": len(factures),
            "payees": payees,
            "impayees": len(impayees),
            "en_retard_echeance": sum(1 for i in impayees if i["en_retard"]),
            "encours_par_tenant": par_tenant,
            "details_impayees": impayees,
        }
