"""Service metier chat : annonces par cible et statut, signalements
de contenu en attente de traitement. Aucune donnee inventee."""
from typing import Dict, Any

from sqlalchemy.orm import Session

from app.models.chat_d5_deep import ChtAnnouncement, ChtContentReport


class ChatService:
    """Annonces et moderation."""

    @staticmethod
    def annonces(db: Session, cible: str = None) -> Dict[str, Any]:
        q = db.query(ChtAnnouncement).filter(
            ChtAnnouncement.is_active.is_(True))
        if cible:
            q = q.filter(ChtAnnouncement.cible == cible)
        annonces = q.all()
        if not annonces:
            return {"cible": cible, "annonces": 0,
                    "note": "Aucune annonce."}
        par_cible: Dict[str, int] = {}
        epinglees = 0
        for a in annonces:
            c = a.cible or "tous"
            par_cible[c] = par_cible.get(c, 0) + 1
            if a.epingle:
                epinglees += 1
        return {
            "cible": cible,
            "annonces_total": len(annonces),
            "par_cible": par_cible,
            "epinglees": epinglees,
        }

    @staticmethod
    def signalements(db: Session) -> Dict[str, Any]:
        signalements = db.query(ChtContentReport).filter(
            ChtContentReport.is_active.is_(True)).all()
        if not signalements:
            return {"signalements": 0, "note": "Aucun signalement."}
        en_attente = [s for s in signalements
                      if "clos" not in str(s.statut or "").lower()
                      and "traite" not in str(s.statut or "").lower()]
        return {
            "signalements_total": len(signalements),
            "en_attente": len(en_attente),
        }
