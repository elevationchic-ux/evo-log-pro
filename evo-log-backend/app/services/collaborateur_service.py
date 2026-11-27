"""Service metier collaborateur : taux de conformite des controles
qualite (points testes vs anomalies) par collaborateur et global.
Aucune donnee inventee : controles sans mesures exclus."""
from typing import Dict, Any

from sqlalchemy.orm import Session

from app.models.collaborateur_d_deep import CollQualityCheck


class CollaborateurService:
    """KPIs qualite collaborateur."""

    @staticmethod
    def conformite(db: Session, collaborateur: str = None) -> Dict[str, Any]:
        q = db.query(CollQualityCheck).filter(
            CollQualityCheck.is_active.is_(True))
        if collaborateur:
            q = q.filter(CollQualityCheck.collaborateur == collaborateur)
        controles = q.all()
        if not controles:
            return {"collaborateur": collaborateur, "controles": 0,
                    "note": "Aucun controle qualite."}

        points = sum(c.point_testes or 0 for c in controles)
        anomalies = sum(c.anomalies or 0 for c in controles)
        conformes = sum(1 for c in controles
                        if (c.anomalies or 0) == 0 and (c.point_testes or 0) > 0)
        avec_mesures = [c for c in controles
                        if c.point_testes is not None or c.anomalies is not None]

        return {
            "collaborateur": collaborateur,
            "controles_total": len(controles),
            "avec_mesures": len(avec_mesures),
            "points_testes": points,
            "anomalies": anomalies,
            "controles_sans_anomalie": conformes,
            "taux_conformite_pct": (
                round(conformes / len(controles) * 100, 1) if controles else None
            ),
        }
