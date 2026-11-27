"""Service metier amenagement portuaire avance : avancement des
chantiers de dragage (volume rejete vs a draguer) et echeance des
concessions portuaires. Aucune donnee inventee : volumes manquants
= avancement NULL."""
from datetime import date
from decimal import Decimal
from typing import Dict, Any

from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.amenagement_b_deep import AmgtbDredgingProject, AmgtbConcessionPlot


class AmenagementBService:
    """Suivi dragage et concessions."""

    @staticmethod
    def avancement_dragage(db: Session, projet_id: int) -> Dict[str, Any]:
        p = db.get(AmgtbDredgingProject, projet_id)
        if not p:
            raise HTTPException(status_code=404, detail="Projet de dragage introuvable")
        if not p.volume_a_draguer_m3:
            return {"projet_id": p.id, "avancement_pct": None,
                    "note": "Volume a draguer non renseigne : avancement non calculable."}
        rejete = p.volume_rejete_m3 or 0
        pct = min(round(rejete / p.volume_a_draguer_m3 * 100, 1), 100.0)
        return {
            "projet_id": p.id,
            "reference": p.reference,
            "zone": p.zone,
            "volume_a_draguer_m3": p.volume_a_draguer_m3,
            "volume_rejete_m3": rejete,
            "reste_a_draguer_m3": max(p.volume_a_draguer_m3 - rejete, 0),
            "avancement_pct": pct,
        }

    @staticmethod
    def echeance_concession(db: Session, concession_id: int) -> Dict[str, Any]:
        c = db.get(AmgtbConcessionPlot, concession_id)
        if not c:
            raise HTTPException(status_code=404, detail="Concession introuvable")
        if not c.date_echeance:
            return {"concession_id": c.id, "jours_restants": None,
                    "note": "Date d'echeance non renseignee."}
        jours = (c.date_echeance - date.today()).days
        return {
            "concession_id": c.id,
            "reference": c.reference,
            "designiation": c.designation,
            "concessionnaire": c.concessionnaire,
            "date_echeance": str(c.date_echeance),
            "jours_restants": jours,
            "expiree": jours < 0,
            "alerte_renouvellement": jours <= 90,
        }
