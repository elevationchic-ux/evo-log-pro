"""Service metier QHSE deep : depassements de normes environnementales
(valeur vs norme_max) et actions correctives en retard d'echeance.
Aucune donnee inventee : mesures sans norme exclues du verdict."""
from datetime import date
from decimal import Decimal
from typing import Dict, Any

from sqlalchemy.orm import Session

from app.models.qhse_deep import EnvironmentalMeasurement, CorrectiveAction


class QhseDeepService:
    """Environnement et actions correctives."""

    @staticmethod
    def depassements(db: Session) -> Dict[str, Any]:
        releves = db.query(EnvironmentalMeasurement).filter(
            EnvironmentalMeasurement.is_active.is_(True)).all()
        if not releves:
            return {"releves": 0, "note": "Aucun releve environnemental."}

        depassements = []
        sans_norme = 0
        conformes = 0
        for r in releves:
            if r.valeur is None or r.norme_max is None:
                sans_norme += 1
                continue
            if Decimal(str(r.valeur)) > Decimal(str(r.norme_max)):
                depassements.append({
                    "reference": r.reference,
                    "polluant": r.polluant,
                    "valeur": float(r.valeur),
                    "norme_max": float(r.norme_max),
                    "station": r.station,
                })
            else:
                conformes += 1

        return {
            "releves_total": len(releves),
            "conformes": conformes,
            "depassements": len(depassements),
            "sans_norme_comparable": sans_norme,
            "details_depassements": depassements,
        }

    @staticmethod
    def actions_en_retard(db: Session) -> Dict[str, Any]:
        actions = db.query(CorrectiveAction).filter(
            CorrectiveAction.is_active.is_(True)).all()
        if not actions:
            return {"actions": 0, "note": "Aucune action corrective."}
        aujourdhui = date.today()
        en_retard = []
        ouvertes = 0
        for a in actions:
            statut = str(a.statut or "").lower()
            if any(k in statut for k in ("clos", "cloture", "termin", "verifie")):
                continue
            ouvertes += 1
            if a.date_prevue_cloture and a.date_prevue_cloture < aujourdhui:
                en_retard.append({
                    "reference": a.reference,
                    "responsable": a.responsable,
                    "date_prevue": str(a.date_prevue_cloture),
                })
        return {
            "actions_total": len(actions),
            "ouvertes": ouvertes,
            "en_retard_echeance": len(en_retard),
            "details_retard": en_retard,
        }
