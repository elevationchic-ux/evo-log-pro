"""Service metier commercial : pipeline des opportunites par statut
et detection des devis expires (validite passee, statut ouvert).
Aucune donnee inventee."""
from datetime import date
from typing import Dict, Any

from sqlalchemy.orm import Session

from app.models.commercial_d_deep import CommOpportunity, CommQuote


class CommercialService:
    """Pipeline commercial."""

    @staticmethod
    def pipeline(db: Session) -> Dict[str, Any]:
        opps = db.query(CommOpportunity).filter(
            CommOpportunity.is_active.is_(True)).all()
        if not opps:
            return {"opportunites": 0, "note": "Aucune opportunite."}
        par_statut: Dict[str, Dict[str, Any]] = {}
        for o in opps:
            s = o.statut or "sans_statut"
            par_statut.setdefault(s, {"count": 0, "montant_total": 0.0})
            par_statut[s]["count"] += 1
            if o.montant_estime is not None:
                par_statut[s]["montant_total"] += float(o.montant_estime)
        return {
            "opportunites_total": len(opps),
            "par_statut": par_statut,
            "montant_pipeline": round(
                sum(v["montant_total"] for v in par_statut.values()), 2),
        }

    @staticmethod
    def devis_expires(db: Session) -> Dict[str, Any]:
        """Devis dont la validite est passee et statut non final."""
        devis = db.query(CommQuote).filter(
            CommQuote.is_active.is_(True)).all()
        aujourdhui = date.today()
        expires = []
        for q in devis:
            if (q.validite and q.validite < aujourdhui
                    and (q.statut or "").lower() not in ("accepte", "perdu", "annule")):
                expires.append({
                    "reference": q.reference,
                    "client": q.client,
                    "validite": str(q.validite),
                    "montant": float(q.montant) if q.montant else None,
                })
        return {
            "devis_total": len(devis),
            "expires": len(expires),
            "details": expires,
        }
