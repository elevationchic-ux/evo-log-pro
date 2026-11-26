"""Service metier heavylift / convoi exceptionnel : validation de plans
de levage (RAMPS) contre la capacite reelle des grues et les regles de
securite du levage (coefficient, centre de gravite)."""
from typing import Dict, Any

from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.heavylift_deep import HeavyLiftCrane, HeavyLiftLiftPlan


class HeavyLiftPlanService:
    """Valide un plan de levage sans jamais approuver au-dela de la
    capacite reelle de la grue annoncee."""

    SEUIL_VERIFICATION_PCT = 80  # > 80 % de la capacite -> verification renforcee

    @staticmethod
    def valider_plan(db: Session, plan_id: int) -> Dict[str, Any]:
        plan = db.get(HeavyLiftLiftPlan, plan_id)
        if not plan:
            raise HTTPException(status_code=404, detail="Plan de levage introuvable")

        motifs_refus = []
        avertissements = []

        # 1. Charge vs capacite de la grue prevue
        charge = plan.charge_t or 0
        grue = None
        if plan.grue_prevue:
            grue = db.query(HeavyLiftCrane).filter(
                HeavyLiftCrane.numero_grue == plan.grue_prevue,
                HeavyLiftCrane.is_active.is_(True),
            ).first()
        if grue is None:
            avertissements.append(
                "Grue non identifiee dans le parc : validation capacitaire impossible"
            )
        elif grue.capacite_max_t is not None:
            if charge > grue.capacite_max_t:
                motifs_refus.append(
                    f"Charge {charge} t > capacite {grue.capacite_max_t} t de la grue {grue.numero_grue}"
                )
            elif charge > grue.capacite_max_t * (HeavyLiftPlanService.SEUIL_VERIFICATION_PCT / 100):
                avertissements.append(
                    f"Charge a {charge / grue.capacite_max_t * 100:.0f} % de la capacite : verification renforcee requise"
                )

        # 2. Centre de gravite haut -> coefficient de securite obligatoire
        if plan.centre_gravite_haut and not plan.coefficient_securite_pct:
            motifs_refus.append(
                "Centre de gravite haut sans coefficient de securite declare"
            )
        elif plan.coefficient_securite_pct is not None and plan.coefficient_securite_pct < 100:
            motifs_refus.append(
                f"Coefficient de securite {plan.coefficient_securite_pct} % < 100 %"
            )

        # 3. Hauteur vs portee/hauteur grue si connues
        if grue and plan.hauteur_m and grue.hauteur_max_m and plan.hauteur_m > grue.hauteur_max_m:
            motifs_refus.append(
                f"Hauteur {plan.hauteur_m} m > hauteur max {grue.hauteur_max_m} m de la grue"
            )

        statut = "refuse" if motifs_refus else ("a_verifier" if avertissements else "valide")
        plan.statut = statut
        db.commit()
        db.refresh(plan)

        return {
            "plan_id": plan.id,
            "reference": plan.reference,
            "statut": statut,
            "motifs_refus": motifs_refus,
            "avertissements": avertissements,
            "charge_t": charge,
            "capacite_grue_t": grue.capacite_max_t if grue else None,
        }
