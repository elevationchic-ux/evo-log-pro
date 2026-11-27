"""Service metier 3PL avance : calcul du fret transporteur =
prix_base + poids_kg x prix_par_kg selon la grille TplCarrierRate
en vigueur. Tarif absent/expire = refus honnete."""
from datetime import date
from decimal import Decimal
from typing import Dict, Any

from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.log3pl_b_deep import TplCarrierRate


class TplCarrierService:
    """Fret transporteur 3PL."""

    @staticmethod
    def calculer_fret(
        db: Session, code_tarif: str, poids_kg: int
    ) -> Dict[str, Any]:
        if poids_kg <= 0:
            raise HTTPException(status_code=422, detail="Poids doit etre > 0 kg")

        tarif = db.query(TplCarrierRate).filter(
            TplCarrierRate.code_tarif == code_tarif,
            TplCarrierRate.is_active.is_(True),
        ).first()
        if not tarif:
            raise HTTPException(status_code=404, detail=f"Tarif {code_tarif} introuvable")

        aujourdhui = date.today()
        if tarif.validite_debut and aujourdhui < tarif.validite_debut:
            raise HTTPException(status_code=422, detail="Tarif pas encore en vigueur")
        if tarif.validite_fin and aujourdhui > tarif.validite_fin:
            raise HTTPException(status_code=422, detail="Tarif expire")
        if tarif.prix_base_xaf is None and tarif.prix_par_kg_xaf is None:
            raise HTTPException(status_code=422, detail="Aucun prix renseigne sur le tarif")

        base = Decimal(str(tarif.prix_base_xaf or 0))
        au_kilo = Decimal(str(tarif.prix_par_kg_xaf or 0))
        total = base + au_kilo * Decimal(str(poids_kg))

        return {
            "code_tarif": code_tarif,
            "transporteur": tarif.transporteur,
            "zone": tarif.zone,
            "poids_kg": poids_kg,
            "prix_base_xaf": float(base),
            "prix_par_kg_xaf": float(au_kilo),
            "fret_total_xaf": float(total),
        }
