"""Service metier fluvial : calcul du fret lettre de voiture bateliere
= tonnes x prix_par_tonne (remise volume du tarif), tarif valide
obligatoire. Aucun montant invente."""
from datetime import date
from decimal import Decimal
from typing import Dict, Any

from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.fluvial_deep import FluvialTariff, FluvialWaybill


class FluvialFreightService:
    """Fret batelier selon la grille tarifaire en vigueur."""

    @staticmethod
    def calculer_fret(db: Session, waybill_id: int, code_tarif: str) -> Dict[str, Any]:
        lcv = db.get(FluvialWaybill, waybill_id)
        if not lcv:
            raise HTTPException(status_code=404, detail="Lettre de voiture introuvable")
        if not lcv.quantite_tonnes or lcv.quantite_tonnes <= 0:
            raise HTTPException(status_code=422, detail="Quantite en tonnes non renseignee")

        tarif = db.query(FluvialTariff).filter(
            FluvialTariff.code_tarif == code_tarif,
            FluvialTariff.is_active.is_(True),
        ).first()
        if not tarif:
            raise HTTPException(status_code=404, detail=f"Tarif {code_tarif} introuvable")

        aujourdhui = date.today()
        if tarif.validite_debut and aujourdhui < tarif.validite_debut:
            raise HTTPException(status_code=422, detail="Tarif pas encore en vigueur")
        if tarif.validite_fin and aujourdhui > tarif.validite_fin:
            raise HTTPException(status_code=422, detail="Tarif expire")
        if tarif.prix_par_tonne_xaf is None:
            raise HTTPException(status_code=422, detail="Prix par tonne non renseigne")

        # Coherence produit : si le tarif vise un produit, il doit matcher
        if tarif.produit and lcv.produit and tarif.produit != lcv.produit:
            raise HTTPException(
                status_code=422,
                detail=f"Tarif pour produit '{tarif.produit}' incompatible avec '{lcv.produit}'",
            )

        base = Decimal(str(lcv.quantite_tonnes)) * Decimal(str(tarif.prix_par_tonne_xaf))
        remise = Decimal(str(tarif.remise_volume_pct or 0))
        fret = base * (Decimal(1) - remise / Decimal(100))

        return {
            "waybill": lcv.numero,
            "code_tarif": code_tarif,
            "quantite_tonnes": lcv.quantite_tonnes,
            "produit": lcv.produit,
            "prix_par_tonne_xaf": float(tarif.prix_par_tonne_xaf),
            "base_xaf": float(base),
            "remise_volume_pct": float(remise),
            "fret_xaf": float(fret),
        }
