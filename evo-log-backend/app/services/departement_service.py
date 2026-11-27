"""Service metier departements : demandes de service internes par
urgence, statut et service destinataire. Aucune donnee inventee."""
from typing import Dict, Any

from sqlalchemy.orm import Session

from app.models.departement_d5_deep import DepServiceRequest


class DepartementService:
    """Tickets service interne."""

    @staticmethod
    def demandes(db: Session, service: str = None) -> Dict[str, Any]:
        q = db.query(DepServiceRequest).filter(
            DepServiceRequest.is_active.is_(True))
        if service:
            q = q.filter(DepServiceRequest.service_destinataire == service)
        demandes = q.all()
        if not demandes:
            return {"service": service, "demandes": 0,
                    "note": "Aucune demande de service."}

        par_urgence: Dict[str, int] = {}
        par_statut: Dict[str, int] = {}
        ouvertes = 0
        for d in demandes:
            u = d.urgence or "normale"
            s = d.statut or "sans_statut"
            par_urgence[u] = par_urgence.get(u, 0) + 1
            par_statut[s] = par_statut.get(s, 0) + 1
            if s.lower() in ("ouvert", "en_cours", "recue", "en_attente"):
                ouvertes += 1

        return {
            "service": service,
            "demandes_total": len(demandes),
            "ouvertes": ouvertes,
            "par_urgence": par_urgence,
            "par_statut": par_statut,
        }
