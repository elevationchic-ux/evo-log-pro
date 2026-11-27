"""Service metier formation : suivi des certifications (expirees,
a renouveler sous X jours). Aucune donnee inventee : certifications
sans date d'expiration ignorees et comptees."""
from datetime import date, timedelta
from typing import Dict, Any

from sqlalchemy.orm import Session

from app.models.formation import CertificationUtilisateur


class FormationService:
    """KPIs certifications."""

    @staticmethod
    def suivi_certifications(db: Session, jours_alerte: int = 30) -> Dict[str, Any]:
        certs = db.query(CertificationUtilisateur).all()
        seuil = date.today() + timedelta(days=jours_alerte)

        expirees = []
        a_renouveler = []
        valides = []
        sans_expiration = 0

        for c in certs:
            if not c.date_expiration:
                sans_expiration += 1
                continue
            if c.date_expiration < date.today():
                expirees.append({
                    "utilisateur_id": c.utilisateur_id,
                    "module_id": c.module_id,
                    "expiration": str(c.date_expiration),
                })
            elif c.date_expiration <= seuil:
                a_renouveler.append({
                    "utilisateur_id": c.utilisateur_id,
                    "module_id": c.module_id,
                    "expiration": str(c.date_expiration),
                    "jours_restants": (c.date_expiration - date.today()).days,
                })
            else:
                valides.append(c.id)

        return {
            "total_certifications": len(certs),
            "expirees": len(expirees),
            "a_renouveler": len(a_renouveler),
            "valides": len(valides),
            "sans_date_expiration": sans_expiration,
            "details_expirees": expirees,
            "details_a_renouveler": a_renouveler,
        }
