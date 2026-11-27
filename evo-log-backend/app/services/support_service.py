"""Service metier support client : tickets par priorite/statut,
delai moyen de resolution et documents flotte expirants. Aucune
donnee inventee."""
from datetime import datetime, timezone, timedelta
from typing import Dict, Any

from sqlalchemy.orm import Session

from app.models.customer_support import SupportTicket, FleetDocument


class SupportService:
    """KPIs support client."""

    @staticmethod
    def stats_tickets(db: Session) -> Dict[str, Any]:
        tickets = db.query(SupportTicket).filter(
            SupportTicket.is_active.is_(True)).all()
        if not tickets:
            return {"tickets": 0, "note": "Aucun ticket."}
        par_statut: Dict[str, int] = {}
        par_priorite: Dict[str, int] = {}
        for t in tickets:
            par_statut[t.statut or "sans_statut"] = par_statut.get(t.statut or "sans_statut", 0) + 1
            par_priorite[t.priorite or "normale"] = par_priorite.get(t.priorite or "normale", 0) + 1
        # Delai moyen resolution (heures) sur tickets resolus
        delais = []
        for t in tickets:
            if t.resolved_at and t.created_at:
                delais.append((t.resolved_at - t.created_at).total_seconds() / 3600)
        return {
            "tickets_total": len(tickets),
            "par_statut": par_statut,
            "par_priorite": par_priorite,
            "delai_moyen_resolution_h": round(sum(delais) / len(delais), 1) if delais else None,
            "nb_resolus": len(delais),
        }

    @staticmethod
    def documents_expirants(db: Session, jours: int = 30) -> Dict[str, Any]:
        docs = db.query(FleetDocument).filter(
            FleetDocument.statut != "expire",
            FleetDocument.date_expiration.isnot(None),
        ).all()
        seuil = datetime.now(timezone.utc) + timedelta(days=jours)
        expirants = []
        for d in docs:
            exp = d.date_expiration
            if exp.tzinfo is None:
                exp = exp.replace(tzinfo=timezone.utc)
            if exp < seuil:
                expirants.append({
                    "type_document": d.type_document,
                    "date_expiration": str(d.date_expiration),
                })
        return {
            "documents_verifies": len(docs),
            "expirants_30j": len(expirants),
            "details": expirants,
        }
