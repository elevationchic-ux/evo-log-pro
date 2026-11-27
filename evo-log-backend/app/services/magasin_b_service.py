"""Service metier magasin B : ecarts d'inventaire (quantite
theorique vs physique, ecart recalcule si absent) et receptions
sans controle qualite. Aucune donnee inventee."""
from decimal import Decimal
from typing import Dict, Any

from sqlalchemy.orm import Session

from app.models.magasin_b_deep import MagasinbStockCount, MagasinbGoodsReceipt


class MagasinBService:
    """Inventaires et receptions."""

    @staticmethod
    def ecarts_inventaire(db: Session, article: str = None) -> Dict[str, Any]:
        q = db.query(MagasinbStockCount).filter(
            MagasinbStockCount.is_active.is_(True))
        if article:
            q = q.filter(MagasinbStockCount.article == article)
        counts = q.all()
        if not counts:
            return {"article": article, "lignes": 0,
                    "note": "Aucune ligne d'inventaire."}

        ecarts = []
        conformes = 0
        non_compares = 0
        for c in counts:
            if c.quantite_theorique is None or c.quantite_physique is None:
                non_compares += 1
                continue
            ecart = c.ecart if c.ecart is not None else c.quantite_physique - c.quantite_theorique
            if ecart != 0:
                ecarts.append({
                    "article": c.article,
                    "emplacement": c.emplacement,
                    "theorique": c.quantite_theorique,
                    "physique": c.quantite_physique,
                    "ecart": ecart,
                    "agent": c.agent,
                })
            else:
                conformes += 1

        return {
            "article": article,
            "lignes_total": len(counts),
            "conformes": conformes,
            "ecarts": len(ecarts),
            "non_compares": non_compares,
            "details_ecarts": ecarts,
        }

    @staticmethod
    def receptions(db: Session) -> Dict[str, Any]:
        receptions = db.query(MagasinbGoodsReceipt).filter(
            MagasinbGoodsReceipt.is_active.is_(True)).all()
        if not receptions:
            return {"receptions": 0, "note": "Aucune reception."}
        sans_controle = [r for r in receptions if not r.controles_fait]
        par_statut: Dict[str, int] = {}
        for r in receptions:
            s = r.statut or "sans_statut"
            par_statut[s] = par_statut.get(s, 0) + 1
        return {
            "receptions_total": len(receptions),
            "sans_controle": len(sans_controle),
            "par_statut": par_statut,
            "details_sans_controle": [
                {"reference": r.reference, "fournisseur": r.fournisseur,
                 "bon_commande": r.bon_commande}
                for r in sans_controle
            ],
        }
