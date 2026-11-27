"""Service metier magasin deep : ruptures de stock (quantite vs seuil
min/point de commande) et lots proches de peremption. Aucune donnee
invente : articles sans quantite actuelle exclus."""
from datetime import date, timedelta
from decimal import Decimal
from typing import Dict, Any

from sqlalchemy.orm import Session

from app.models.magasin_deep import StockAlert, ExpiryRecord


class MagasinDeepService:
    """Alertes stock et peremption."""

    @staticmethod
    def ruptures(db: Session) -> Dict[str, Any]:
        alertes = db.query(StockAlert).filter(
            StockAlert.is_active.is_(True)).all()
        if not alertes:
            return {"alertes": 0, "note": "Aucune alerte stock."}

        en_rupture = []
        sous_seuil = []
        for a in alertes:
            if a.quantite_actuelle is None:
                continue
            q = Decimal(str(a.quantite_actuelle))
            if a.seuil_min is not None and q < Decimal(str(a.seuil_min)):
                en_rupture.append({
                    "code_alerte": a.code_alerte,
                    "article_id": a.article_id,
                    "quantite_actuelle": float(q),
                    "seuil_min": float(a.seuil_min),
                })
            elif a.point_commande is not None and q <= Decimal(str(a.point_commande)):
                sous_seuil.append(a.code_alerte)

        return {
            "alertes_total": len(alertes),
            "en_rupture": len(en_rupture),
            "sous_point_commande": len(sous_seuil),
            "details_ruptures": en_rupture,
        }

    @staticmethod
    def peremptibles(db: Session, jours: int = 30) -> Dict[str, Any]:
        lots = db.query(ExpiryRecord).filter(
            ExpiryRecord.is_active.is_(True),
            ExpiryRecord.date_peremption.isnot(None),
        ).all()
        if not lots:
            return {"lots": 0, "note": "Aucun lot avec peremption."}
        seuil = date.today() + timedelta(days=jours)
        a_risque = []
        expires = []
        for l in lots:
            if l.date_peremption < date.today():
                expires.append({"numero_lot": l.numero_lot,
                                "date_peremption": str(l.date_peremption)})
            elif l.date_peremption <= seuil:
                a_risque.append({"numero_lot": l.numero_lot,
                                 "date_peremption": str(l.date_peremption),
                                 "quantite": float(l.quantite) if l.quantite else None})
        return {
            "lots_total": len(lots),
            "deja_expires": len(expires),
            "a_risque_30j": len(a_risque),
            "details_expires": expires,
            "details_a_risque": a_risque,
        }
