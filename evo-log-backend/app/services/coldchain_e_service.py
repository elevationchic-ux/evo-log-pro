"""Service metier coldchain avance : analyse des evenements
d'ouverture de porte (duree vs seuil de reference) et bilan par
chambre. Seuil depasse = alerte HACCP ; aucune donnee inventee."""
from typing import Dict, Any, List

from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.coldchain_e_deep import Cold2DoorOpenEvent


class Cold2DoorService:
    """Surveillance ouvertures de porte chambres froides."""

    SEUIL_OUVERTURE_SEC = 300  # 5 min = seuil d'alerte par defaut

    @staticmethod
    def evaluer_ouverture(
        db: Session, event_id: int, seuil_sec: int = None
    ) -> Dict[str, Any]:
        ev = db.get(Cold2DoorOpenEvent, event_id)
        if not ev:
            raise HTTPException(status_code=404, detail="Evenement introuvable")
        seuil = seuil_sec or Cold2DoorService.SEUIL_OUVERTURE_SEC
        duree = ev.duree_sec or 0
        return {
            "event_id": ev.id,
            "chambre": ev.chambre,
            "duree_sec": duree,
            "seuil_alerte_sec": seuil,
            "alerte": duree > seuil,
            "criticite": "majeure" if duree > seuil * 3 else ("moderee" if duree > seuil else "normale"),
        }

    @staticmethod
    def bilan_chambre(db: Session, chambre: str) -> Dict[str, Any]:
        """Stats reelles d'une chambre : nb ouvertures, duree max,
        nb au-dela du seuil."""
        events = db.query(Cold2DoorOpenEvent).filter(
            Cold2DoorOpenEvent.chambre == chambre,
            Cold2DoorOpenEvent.is_active.is_(True),
        ).all()
        if not events:
            return {"chambre": chambre, "ouvertures": 0,
                    "note": "Aucun evenement enregistre pour cette chambre."}

        seuil = Cold2DoorService.SEUIL_OUVERTURE_SEC
        depassements = [e for e in events if (e.duree_sec or 0) > seuil]
        return {
            "chambre": chambre,
            "ouvertures_total": len(events),
            "duree_max_sec": max(e.duree_sec or 0 for e in events),
            "duree_moyenne_sec": round(sum(e.duree_sec or 0 for e in events) / len(events), 1),
            "depassements_seuil": len(depassements),
            "taux_depassement_pct": round(len(depassements) / len(events) * 100, 1),
        }
