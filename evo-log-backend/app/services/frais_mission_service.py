"""Service metier frais de mission : workflow de validation des
depenses (rejet exige un motif obligatoire) et reconciliation
avance mission vs depenses declarees. Aucune depense fabriquee."""
from decimal import Decimal
from typing import Dict, Any

from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.frais_mission import FraisMission, AvanceMission


class FraisMissionService:
    """Workflow et reconciliation frais mission."""

    @staticmethod
    def valider_depense(
        db: Session, depense_id: int, approuve: bool, motif_rejet: str = None
    ) -> Dict[str, Any]:
        d = db.get(FraisMission, depense_id)
        if not d:
            raise HTTPException(status_code=404, detail="Depense introuvable")
        if (d.statut or "").upper() not in ("SOUMIS", "EN_ATTENTE"):
            raise HTTPException(status_code=409, detail=f"Depense deja {d.statut}")

        if not approuve and not motif_rejet:
            raise HTTPException(status_code=422, detail="Motif de rejet obligatoire")

        d.statut = "VALIDE" if approuve else "REJETE"
        if approuve:
            from datetime import datetime, timezone
            d.date_validation = datetime.now(timezone.utc)
        else:
            d.motif_rejet = motif_rejet
        db.commit()
        db.refresh(d)
        return {"depense_id": d.id, "statut": d.statut,
                "montant": d.montant}

    @staticmethod
    def reconciliation_avance(db: Session, avance_id: int) -> Dict[str, Any]:
        """Avance vs depenses validees du collaborateur sur la mission."""
        avance = db.get(AvanceMission, avance_id)
        if not avance:
            raise HTTPException(status_code=404, detail="Avance introuvable")

        depenses = db.query(FraisMission).filter(
            FraisMission.user_id == avance.user_id,
            FraisMission.statut == "VALIDE",
            FraisMission.is_active.is_(True) if hasattr(FraisMission, "is_active") else True,
        ).all()
        total_valide = sum(Decimal(str(d.montant or 0)) for d in depenses)
        accorde = Decimal(str(avance.montant_accorde or avance.montant_demande or 0))

        return {
            "avance_id": avance.id,
            "titre": avance.titre_mission,
            "avance_accordee_xaf": float(accorde),
            "depenses_validees_xaf": float(total_valide),
            "ecart_xaf": float(accorde - total_valide),
            "a_rembourser_xaf": float(max(total_valide - accorde, 0)),
        }
