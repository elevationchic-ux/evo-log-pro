"""Service metier fret aerien : calcul du fret lettre de transport
aerien (AWB) = poids_kg x prix_par_kg + surcharges, selon le tarif
valide (origine/destination, tranche de poids, dates de validite).
Aucun montant n'est invente : tarif introuvable = refus."""
from datetime import date
from decimal import Decimal
from typing import Dict, Any

from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.aerien_deep import AirTariff


class AirFreightService:
    """Fret aerien selon la grille tarifaire en vigueur."""

    @staticmethod
    def _trouver_tarif(
        db: Session, code_tarif: str, poids_kg: int
    ) -> AirTariff:
        tarif = db.query(AirTariff).filter(
            AirTariff.code_tarif == code_tarif,
            AirTariff.is_active.is_(True),
        ).first()
        if not tarif:
            raise HTTPException(status_code=404, detail=f"Tarif {code_tarif} introuvable")

        aujourdhui = date.today()
        if tarif.validite_debut and aujourdhui < tarif.validite_debut:
            raise HTTPException(status_code=422, detail="Tarif pas encore en vigueur")
        if tarif.validite_fin and aujourdhui > tarif.validite_fin:
            raise HTTPException(status_code=422, detail="Tarif expire")
        if tarif.prix_par_kg_xaf is None:
            raise HTTPException(status_code=422, detail="Prix par kg non renseigne")
        # Tranche de poids : poids_min_kg = poids minimum de la tranche
        if tarif.poids_min_kg is not None and poids_kg < tarif.poids_min_kg:
            raise HTTPException(
                status_code=422,
                detail=f"Poids {poids_kg} kg < tranche minimum {tarif.poids_min_kg} kg du tarif",
            )
        return tarif

    @staticmethod
    def calculer_fret(
        db: Session, code_tarif: str, poids_kg: int
    ) -> Dict[str, Any]:
        """Fret = poids x prix_kg + surcharges forfaitaires du tarif."""
        if poids_kg <= 0:
            raise HTTPException(status_code=422, detail="Poids doit etre > 0 kg")

        tarif = AirFreightService._trouver_tarif(db, code_tarif, poids_kg)
        base = Decimal(str(poids_kg)) * Decimal(str(tarif.prix_par_kg_xaf))
        surcharges = Decimal(str(tarif.surcharges_xaf or 0))
        total = base + surcharges

        return {
            "code_tarif": code_tarif,
            "poids_kg": poids_kg,
            "prix_par_kg_xaf": float(tarif.prix_par_kg_xaf),
            "base_xaf": float(base),
            "surcharges_xaf": float(surcharges),
            "fret_total_xaf": float(total),
        }
