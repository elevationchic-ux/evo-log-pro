"""Service metier ferroviaire : calcul du fret lettre de voiture
(LCV) = tonnes x km x prix_par_tonne_km x (1 - remise_volume/100).
Refuse honnetement si aucun tarif valide ne correspond."""
from datetime import date
from decimal import Decimal
from typing import Dict, Any

from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.ferroviaire_deep import RailTariff


class RailFreightService:
    """Fret ferroviaire selon la grille tarifaire en vigueur."""

    @staticmethod
    def _trouver_tarif(
        db: Session, code_tarif: str, type_marchandise: str = None
    ) -> RailTariff:
        tarif = db.query(RailTariff).filter(
            RailTariff.code_tarif == code_tarif,
            RailTariff.is_active.is_(True),
        ).first()
        if not tarif:
            raise HTTPException(status_code=404, detail=f"Tarif {code_tarif} introuvable")
        aujourdhui = date.today()
        if tarif.date_debut_validite and aujourdhui < tarif.date_debut_validite:
            raise HTTPException(status_code=422, detail="Tarif pas encore en vigueur")
        if tarif.date_fin_validite and aujourdhui > tarif.date_fin_validite:
            raise HTTPException(status_code=422, detail="Tarif expire")
        if tarif.prix_par_tonne_km_xaf is None:
            raise HTTPException(status_code=422, detail="Prix par tonne-km non renseigne")
        return tarif

    @staticmethod
    def calculer_fret(
        db: Session,
        code_tarif: str,
        tonnes: float,
        distance_km: float,
        type_marchandise: str = None,
    ) -> Dict[str, Any]:
        """Fret = T x km x P avec remise volume du tarif si definie."""
        if tonnes <= 0 or distance_km <= 0:
            raise HTTPException(status_code=422, detail="Tonnage et distance doivent etre > 0")

        tarif = RailFreightService._trouver_tarif(db, code_tarif, type_marchandise)
        prix = Decimal(str(tarif.prix_par_tonne_km_xaf))
        base = Decimal(str(tonnes)) * Decimal(str(distance_km)) * prix
        remise = Decimal(str(tarif.remise_volume_pct or 0))
        montant = base * (Decimal(1) - remise / Decimal(100))

        return {
            "code_tarif": code_tarif,
            "tonnes": tonnes,
            "distance_km": distance_km,
            "prix_par_tonne_km_xaf": float(prix),
            "base_xaf": float(base),
            "remise_volume_pct": float(remise),
            "fret_xaf": float(montant),
        }
