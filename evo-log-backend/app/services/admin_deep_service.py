"""Service metier admin deep : quotas API (consommation vs limites
minute/jour) et tickets plateforme par priorite/statut. Aucune
donnee inventee : quotas sans limite ignores."""
from decimal import Decimal
from typing import Dict, Any

from sqlalchemy.orm import Session

from app.models.admin_deep import ApiQuota, PlatformTicket


class AdminDeepService:
    """Quotas et tickets admin."""

    @staticmethod
    def quotas(db: Session) -> Dict[str, Any]:
        quotas = db.query(ApiQuota).filter(
            ApiQuota.is_active.is_(True)).all()
        if not quotas:
            return {"quotas": 0, "note": "Aucun quota."}

        depassements = []
        alertes = []
        for q in quotas:
            conso = q.consommation_actuelle or 0
            for periode, limite in (("jour", q.limite_jour), ("minute", q.limite_minute)):
                if limite is None or limite <= 0:
                    continue
                pct = conso / limite * 100
                if pct >= 100:
                    depassements.append({
                        "reference": q.reference,
                        "api_group": q.api_group,
                        "periode": periode,
                        "consommation": conso,
                        "limite": limite,
                    })
                elif pct >= 80:
                    alertes.append({
                        "reference": q.reference,
                        "api_group": q.api_group,
                        "periode": periode,
                        "taux_pct": round(pct, 1),
                    })

        return {
            "quotas_total": len(quotas),
            "depassements": len(depassements),
            "alertes_80pct": len(alertes),
            "details_depassements": depassements,
            "details_alertes": alertes,
        }

    @staticmethod
    def tickets(db: Session) -> Dict[str, Any]:
        tickets = db.query(PlatformTicket).filter(
            PlatformTicket.is_active.is_(True)).all()
        if not tickets:
            return {"tickets": 0, "note": "Aucun ticket."}
        par_priorite: Dict[str, int] = {}
        ouvertes = 0
        for t in tickets:
            p = getattr(t.priorite, "value", t.priorite) or "normale"
            par_priorite[p] = par_priorite.get(p, 0) + 1
            statut_val = getattr(t.statut, "value", t.statut) or ""
            if "ouvert" in str(statut_val).lower():
                ouvertes += 1
        return {
            "tickets_total": len(tickets),
            "ouvertes": ouvertes,
            "par_priorite": par_priorite,
        }
