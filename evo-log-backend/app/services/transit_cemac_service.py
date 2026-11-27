"""Service metier transit CEMAC : calcul des frais de corridor
(passeport, redevance, securite, peage) depuis les FraisCorridor
actifs. Aucune redevance n'est inventee : corridor sans frais actif
= calcul impossible, signale honnetement."""
from decimal import Decimal
from typing import Dict, Any

from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.transit_cemac import FraisCorridor, CorridorCEMACTransit


class CorridorFraisService:
    """Frais de transit par corridor CEMAC."""

    @staticmethod
    def calculer_frais(
        db: Session,
        corridor_id: int,
        nb_vehicules: int = 1,
        tonnes: float = 0,
        nb_passages: int = 0,
        poste_frontalier_id: int = None,
    ) -> Dict[str, Any]:
        corridor = db.get(CorridorCEMACTransit, corridor_id)
        if not corridor:
            raise HTTPException(status_code=404, detail="Corridor introuvable")

        frais = db.query(FraisCorridor).filter(
            FraisCorridor.corridor_id == corridor_id,
            FraisCorridor.est_actif.is_(True),
        ).all()
        if not frais:
            raise HTTPException(
                status_code=422,
                detail=f"Aucun frais actif configure pour le corridor {corridor.code}",
            )

        lignes = []
        total = Decimal(0)
        for f in frais:
            unite = (f.unite or "PAR_PASSAGE").upper()
            quantite = {
                "PAR_VEHICULE": nb_vehicules,
                "PAR_TONNE": tonnes,
                "PAR_PASSAGE": nb_passages or nb_vehicules,
            }.get(unite, 1)
            montant = Decimal(str(f.montant)) * Decimal(str(quantite))
            total += montant
            lignes.append({
                "type": f.type_frais,
                "designation": f.designation,
                "unite": f.unite,
                "quantite": quantite,
                "montant_unitaire_xaf": float(f.montant),
                "montant_xaf": float(montant),
            })

        return {
            "corridor": corridor.code,
            "nb_vehicules": nb_vehicules,
            "tonnes": tonnes,
            "total_xaf": float(total),
            "lignes": lignes,
        }
