"""Service metier transport B : tournees (km parcourus, duree vs
dates) et preuves de livraison (colis, signature, incidents).
Aucune donnee inventee."""
from typing import Dict, Any

from sqlalchemy.orm import Session

from app.models.transport_b_deep import TransportbDispatch, TransportbPod


class TransportBService:
    """Tournees et PODs."""

    @staticmethod
    def tournees(db: Session, chauffeur: str = None) -> Dict[str, Any]:
        q = db.query(TransportbDispatch).filter(
            TransportbDispatch.is_active.is_(True))
        if chauffeur:
            q = q.filter(TransportbDispatch.chauffeur == chauffeur)
        tournees = q.all()
        if not tournees:
            return {"chauffeur": chauffeur, "tournees": 0,
                    "note": "Aucune tournee."}

        par_statut: Dict[str, int] = {}
        km_total = 0
        completees = 0
        for t in tournees:
            s = t.statut or "sans_statut"
            par_statut[s] = par_statut.get(s, 0) + 1
            km_total += t.km_parcourus or 0
            if t.date_depart and t.date_arrivee:
                completees += 1

        return {
            "chauffeur": chauffeur,
            "tournees_total": len(tournees),
            "km_total": km_total,
            "avec_dates_completes": completees,
            "par_statut": par_statut,
        }

    @staticmethod
    def pods(db: Session) -> Dict[str, Any]:
        pods = db.query(TransportbPod).filter(
            TransportbPod.is_active.is_(True)).all()
        if not pods:
            return {"pods": 0, "note": "Aucune preuve de livraison."}
        signes = 0
        avec_incidents = 0
        colis_total = 0
        for p in pods:
            if p.signature_recu:
                signes += 1
            if p.incidents:
                avec_incidents += 1
            colis_total += p.nb_colis_livres or 0
        return {
            "pods_total": len(pods),
            "signes": signes,
            "avec_incidents": avec_incidents,
            "colis_livres_total": colis_total,
        }
