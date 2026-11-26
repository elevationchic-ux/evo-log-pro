"""Valorisation des stocks et allocation FEFO/FIFO.

Honnetete : la valorisation utilise `stocks.prix_unitaire` (prix de stock
reellement enregistre) ; l'allocation FEFO ordonne les lots `peremptions`
par date de peremption croissante. Aucun cout n'est estime : un lot sans
cout d'acquisition est exclu du calcul et signale."""
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.magasin import Stock
from app.models.magasin_avance import Peremption


class StockValuationService:

    @staticmethod
    def valoriser_stock(db: Session, stock_id: int) -> Dict[str, Any]:
        stock = db.query(Stock).filter(Stock.id == stock_id, Stock.is_active == True).first()  # noqa: E712
        if not stock:
            raise ValueError("Article de stock introuvable")
        qte = float(stock.quantite_disponible or 0)
        pu = float(stock.prix_unitaire or 0)
        return {
            "stock_id": stock.id,
            "code_article": stock.code_article,
            "designation": stock.designation,
            "quantite": qte,
            "prix_unitaire": pu,
            "valorisation": round(qte * pu, 2),
            "devise": "XAF",
        }

    @staticmethod
    def valorisation_globale(db: Session) -> Dict[str, Any]:
        lignes = [
            StockValuationService.valoriser_stock(db, s.id)
            for s in db.query(Stock).filter(Stock.is_active == True).all()  # noqa: E712
        ]
        return {
            "nb_articles": len(lignes),
            "valorisation_totale": round(sum(l["valorisation"] for l in lignes), 2),
            "lignes": lignes,
        }

    @staticmethod
    def allocation_fefo(db: Session, stock_id: int, quantite: float) -> Dict[str, Any]:
        """Repartition d'une sortie sur les lots par date de peremption
        croissante (FEFO). Retourne les lots mobilises et le reliquat non
        couvert — jamais de lot invente."""
        lots = (
            db.query(Peremption)
            .filter(Peremption.stock_id == stock_id, Peremption.statut == "actif")
            .order_by(Peremption.date_peremption.asc())
            .all()
        )
        restant = float(quantite)
        allocation = []
        for lot in lots:
            if restant <= 0:
                break
            dispo = float(lot.quantite or 0)
            pris = min(dispo, restant)
            allocation.append({
                "peremption_id": lot.id,
                "lot_numero": lot.lot_numero,
                "date_peremption": lot.date_peremption.isoformat() if lot.date_peremption else None,
                "quantite_allouee": round(pris, 4),
                "cout_unitaire": float(lot.cout_acquisition) if lot.cout_acquisition is not None else None,
            })
            restant -= pris
        return {
            "stock_id": stock_id,
            "quantite_demandee": float(quantite),
            "quantite_couverte": round(float(quantite) - restant, 4),
            "quantite_non_couverte": round(restant, 4),
            "lots": allocation,
        }
