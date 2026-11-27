"""Service metier coursier/express : controle des engagements SLA de
livraison (delai contractuel vs livraison reelle) et mesure du taux
d'engagement. Les penalites ne sont appliquees que si le SLA les
definit explicitement — jamais inventees."""
from datetime import datetime
from decimal import Decimal
from typing import Dict, Any

from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.courier_deep import CourierWaybill, CourierSla


class CourierSlaService:
    """Controle SLA des livraisons."""

    @staticmethod
    def controler_livraison(
        db: Session, waybill_id: int, sla_id: int
    ) -> Dict[str, Any]:
        """Compare la livraison reelle a l'engagement SLA.

        SLA en heures (delai_h) ; mesure_pct = part des livraisons dans
        les temps sur la periode du SLA. Penalite appliquee uniquement
        si sla.penalite_xaf est renseigne ET engagement < cible."""
        wb = db.get(CourierWaybill, waybill_id)
        if not wb:
            raise HTTPException(status_code=404, detail="Lettre de voiture introuvable")
        sla = db.get(CourierSla, sla_id)
        if not sla:
            raise HTTPException(status_code=404, detail="SLA introuvable")

        # Livraisons du client dans la periode du SLA
        wbs = db.query(CourierWaybill).filter(
            CourierWaybill.client == sla.client,
            CourierWaybill.is_active.is_(True),
        ).all()
        if sla.date_debut:
            wbs = [w for w in wbs if w.date_emission and w.date_emission >= sla.date_debut]
        if sla.date_fin:
            wbs = [w for w in wbs if w.date_emission and w.date_emission <= sla.date_fin]

        total = len(wbs)
        livrees = [w for w in wbs if w.date_livraison_reelle]
        dans_les_temps = 0
        hors_delai = 0
        if sla.delai_h and sla.date_debut:
            for w in livrees:
                if w.date_livraison_prevue and w.date_livraison_reelle:
                    delta_h = (w.date_livraison_reelle - w.date_livraison_prevue).total_seconds() / 3600
                    if delta_h <= sla.delai_h:
                        dans_les_temps += 1
                    else:
                        hors_delai += 1
        mesure = round(dans_les_temps / len(livrees) * 100, 1) if livrees else None

        engagement_cible = sla.engagement_pct or 0
        penalite = None
        if sla.penalite_xaf and mesure is not None and mesure < engagement_cible:
            penalite = sla.penalite_xaf

        return {
            "sla": sla.code_sla,
            "client": sla.client,
            "periode": {"debut": str(sla.date_debut), "fin": str(sla.date_fin)},
            "livraisons_total": total,
            "livraisons_reelles": len(livrees),
            "dans_les_temps": dans_les_temps,
            "hors_delai": hors_delai,
            "mesure_pct": mesure,
            "engagement_cible_pct": engagement_cible,
            "penalite_appliquee_xaf": penalite,
            "note": "Mesure None sans livraison reelle ; penalite seulement si definie au SLA.",
        }
