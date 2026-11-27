"""Service metier pipeline : evaluation des releves de pression contre
la pression maximale de la section et detection d'anomalies (chute de
charge, surpression, temperature anormale). Alertes honnetes :
seuil non configure = pas d'alerte fabriquee."""
from typing import Dict, Any

from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.pipeline_deep import (
    PipelineSection, PipelinePressureReading,)


class PipelineSafetyService:
    """Surveillance pression/température des sections."""

    SEUIL_SURPRESSION_PCT = 95   # % de pression max -> alerte
    SEUIL_CHUTE_CHARGE_BAR = 5   # chute entree->sortie suspecte

    @staticmethod
    def evaluer_releve(db: Session, releve_id: int) -> Dict[str, Any]:
        r = db.get(PipelinePressureReading, releve_id)
        if not r:
            raise HTTPException(status_code=404, detail="Releve introuvable")
        if not r.section_associee:
            return {"releve_id": r.id, "alertes": [],
                    "note": "Section non associee : evaluation impossible."}

        section = db.query(PipelineSection).filter(
            PipelineSection.code_section == r.section_associee
        ).first()
        alertes = []
        if section and section.pression_max_bar:
            max_bar = section.pression_max_bar
            for label, val in (("entree", r.pression_entree_bar),
                               ("sortie", r.pression_sortie_bar)):
                if val is not None and val > max_bar * PipelineSafetyService.SEUIL_SURPRESSION_PCT / 100:
                    alertes.append({
                        "type": "surpression",
                        "point": label,
                        "valeur_bar": val,
                        "seuil_alerte_bar": max_bar * PipelineSafetyService.SEUIL_SURPRESSION_PCT / 100,
                        "criticite": "critique" if val > max_bar else "majeure",
                    })
        else:
            alertes.append({"type": "config", "detail": "pression_max_bar non configuree sur la section"})

        # Chute de charge anormale entree -> sortie
        if (r.pression_entree_bar is not None and r.pression_sortie_bar is not None
                and r.pression_entree_bar - r.pression_sortie_bar
                > PipelineSafetyService.SEUIL_CHUTE_CHARGE_BAR):
            alertes.append({
                "type": "chute_charge",
                "delta_bar": r.pression_entree_bar - r.pression_sortie_bar,
                "criticite": "a_investiguer",
            })

        return {
            "releve_id": r.id,
            "section": r.section_associee,
            "pression_entree_bar": r.pression_entree_bar,
            "pression_sortie_bar": r.pression_sortie_bar,
            "debit_m3h": r.debit_m3h,
            "temperature_c": r.temperature_c,
            "alertes": alertes,
            "nb_alertes": len(alertes),
        }
