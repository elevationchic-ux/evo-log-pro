"""Service metier parc B : affectations de chauffeurs actives
(date_fin passee = terminee) et inspections avec anomalies.
Aucune donnee inventee."""
from datetime import date
from typing import Dict, Any

from sqlalchemy.orm import Session

from app.models.parc_b_deep import ParcDriverAssignment, ParcInspectionChecklist


class ParcBService:
    """Affectations et inspections parc."""

    @staticmethod
    def affectations_actives(db: Session, chauffeur: str = None) -> Dict[str, Any]:
        q = db.query(ParcDriverAssignment).filter(
            ParcDriverAssignment.is_active.is_(True))
        if chauffeur:
            q = q.filter(ParcDriverAssignment.chauffeur == chauffeur)
        affectations = q.all()
        if not affectations:
            return {"chauffeur": chauffeur, "affectations": 0,
                    "note": "Aucune affectation."}
        aujourdhui = date.today()
        actives = []
        terminees = 0
        for a in affectations:
            if a.date_fin and a.date_fin < aujourdhui:
                terminees += 1
            else:
                actives.append({
                    "reference": a.reference,
                    "immatriculation": a.immatriculation,
                    "date_debut": str(a.date_debut) if a.date_debut else None,
                    "date_fin": str(a.date_fin) if a.date_fin else None,
                })
        return {
            "chauffeur": chauffeur,
            "affectations_total": len(affectations),
            "actives": len(actives),
            "terminees": terminees,
            "details_actives": actives,
        }

    @staticmethod
    def inspections(db: Session) -> Dict[str, Any]:
        inspections = db.query(ParcInspectionChecklist).filter(
            ParcInspectionChecklist.is_active.is_(True)).all()
        if not inspections:
            return {"inspections": 0, "note": "Aucune inspection."}
        avec_anomalies = [i for i in inspections if (i.anomalies_nb or 0) > 0]
        return {
            "inspections_total": len(inspections),
            "avec_anomalies": len(avec_anomalies),
            "taux_anomalies_pct": round(len(avec_anomalies) / len(inspections) * 100, 1),
            "details": [
                {"reference": i.reference, "immatriculation": i.immatriculation,
                 "anomalies_nb": i.anomalies_nb, "chauffeur": i.chauffeur}
                for i in avec_anomalies
            ],
        }
