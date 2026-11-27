"""Service metier chauffeur : temps de conduite par jour vs limite
legale (parametre, jamais suppose) et detection des repos
insuffisants. Tachygraphe : aucune donnee inventee."""
from datetime import date
from typing import Dict, Any

from sqlalchemy.orm import Session

from app.models.chauffeur_c_deep import ChfDrivingTimeRecord, ChfRestBreak


class ChauffeurService:
    """Conformite temps de conduite."""

    @staticmethod
    def conduite_jour(
        db: Session, chauffeur: str, jour: date, limite_minutes: int = 540
    ) -> Dict[str, Any]:
        """Total minutes de conduite d'un chauffeur un jour donne.
        limite_minutes par defaut = 9 h (regle UE), surchargeable."""
        records = db.query(ChfDrivingTimeRecord).filter(
            ChfDrivingTimeRecord.chauffeur == chauffeur,
            ChfDrivingTimeRecord.is_active.is_(True),
        ).all()
        total = sum(
            r.minutes_conduite or 0 for r in records
            if r.debut and r.debut.date() == jour
        )
        return {
            "chauffeur": chauffeur,
            "date": str(jour),
            "minutes_conduite": total,
            "limite_minutes": limite_minutes,
            "depassement_minutes": max(total - limite_minutes, 0),
            "conforme": total <= limite_minutes,
        }

    @staticmethod
    def repos_insuffisants(
        db: Session, chauffeur: str, jour: date, repos_min_minutes: int = 45
    ) -> Dict[str, Any]:
        """Pauses du jour : signale si aucune pause >= seuil."""
        pauses = db.query(ChfRestBreak).filter(
            ChfRestBreak.chauffeur == chauffeur,
            ChfRestBreak.is_active.is_(True),
        ).all()
        pauses_jour = [
            p for p in pauses if p.debut and p.debut.date() == jour
        ]
        if not pauses_jour:
            return {
                "chauffeur": chauffeur, "date": str(jour),
                "pauses": 0, "alerte": True,
                "note": "Aucune pause enregistree ce jour.",
            }
        max_pause = max((p.duree_min or 0) for p in pauses_jour)
        return {
            "chauffeur": chauffeur, "date": str(jour),
            "pauses": len(pauses_jour),
            "pause_max_min": max_pause,
            "seuil_min": repos_min_minutes,
            "alerte": max_pause < repos_min_minutes,
        }
