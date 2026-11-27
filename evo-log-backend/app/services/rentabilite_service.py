"""Service metier rentabilite : chiffre d'affaires par client et
type de facture (vente/prestation), encaisse vs solde restant.
Aucune donnee inventee : factures annulees exclues."""
from decimal import Decimal
from typing import Dict, Any

from sqlalchemy.orm import Session

from app.models.finance_ohada import FactureNew


class RentabiliteService:
    """Rentabilite clients."""

    @staticmethod
    def par_client(db: Session, client_id: int = None) -> Dict[str, Any]:
        q = db.query(FactureNew).filter(
            FactureNew.statut != "annulee")
        if client_id:
            q = q.filter(FactureNew.client_id == client_id)
        factures = q.all()
        if not factures:
            return {"client_id": client_id, "factures": 0,
                    "note": "Aucune facture."}

        par_client: Dict[int, Dict[str, float]] = {}
        par_type: Dict[str, float] = {}
        total_ht = Decimal(0)
        total_ttc = Decimal(0)
        encaisse = Decimal(0)
        restant = Decimal(0)
        for f in factures:
            cid = f.client_id or 0
            t = f.type_facture or "inconnu"
            ht = Decimal(str(f.montant_ht or 0))
            ttc = Decimal(str(f.montant_ttc or 0))
            total_ht += ht
            total_ttc += ttc
            par_client.setdefault(cid, {"ht": 0.0, "ttc": 0.0, "nb": 0})
            par_client[cid]["ht"] += float(ht)
            par_client[cid]["ttc"] += float(ttc)
            par_client[cid]["nb"] += 1
            par_type[t] = par_type.get(t, 0.0) + float(ttc)
            if f.statut == "payee":
                encaisse += ttc
            elif f.solde_restant:
                restant += Decimal(str(f.solde_restant))

        return {
            "client_id": client_id,
            "factures_total": len(factures),
            "ca_ht_xaf": float(total_ht),
            "ca_ttc_xaf": float(total_ttc),
            "encaisse_xaf": float(encaisse),
            "solde_restant_xaf": float(restant) if restant else None,
            "par_type": par_type,
            "par_client": par_client,
        }
