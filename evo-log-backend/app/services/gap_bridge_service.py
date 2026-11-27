"""Service metier gap bridge : calcul de prix depuis la grille Tarif
(prix x quantite + TVA). Tarif absent/inactif = refus honnete."""
from decimal import Decimal
from typing import Dict, Any

from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.gap_bridge import Tarif


class TarifService:
    """Tarification gap bridge."""

    @staticmethod
    def calculer_prix(db: Session, code: str, quantite: float) -> Dict[str, Any]:
        if quantite <= 0:
            raise HTTPException(status_code=422, detail="Quantite doit etre > 0")
        tarif = db.query(Tarif).filter(
            Tarif.code == code, Tarif.is_active.is_(True)).first()
        if not tarif:
            raise HTTPException(status_code=404, detail=f"Tarif {code} introuvable")

        prix = Decimal(str(tarif.prix)) * Decimal(str(quantite))
        tva = prix * Decimal(str(tarif.tva or 0)) / Decimal(100)
        return {
            "code": code,
            "designation": tarif.designation,
            "quantite": quantite,
            "prix_unitaire": float(tarif.prix),
            "base_ht": float(prix),
            "tva": float(tva),
            "total_ttc": float(prix + tva),
        }
