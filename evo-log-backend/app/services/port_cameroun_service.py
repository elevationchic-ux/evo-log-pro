"""Service metier port Cameroun : calcul des redevances portuaires
selon la grille TarifPortuaire (unite x prix + TVA) et indicateurs
de productivite des terminaux. Tarifs expires/inactifs refuses."""
from datetime import date
from decimal import Decimal
from typing import Dict, Any

from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.port_cameroun import TarifPortuaire, TerminalPortuaire


class PortCamerounService:
    """Redevances et indicateurs portuaires camerounais."""

    @staticmethod
    def calculer_redevance(
        db: Session, code_tarif: str, quantite: float
    ) -> Dict[str, Any]:
        tarif = db.query(TarifPortuaire).filter(
            TarifPortuaire.code_tarif == code_tarif,
            TarifPortuaire.est_actif.is_(True),
        ).first()
        if not tarif:
            raise HTTPException(status_code=404, detail=f"Tarif {code_tarif} introuvable")
        aujourdhui = date.today()
        if tarif.date_expiration and aujourdhui > tarif.date_expiration:
            raise HTTPException(status_code=422, detail="Tarif expire")
        if tarif.date_application and aujourdhui < tarif.date_application:
            raise HTTPException(status_code=422, detail="Tarif pas encore en vigueur")
        if quantite <= 0:
            raise HTTPException(status_code=422, detail="Quantite doit etre > 0")

        base = Decimal(str(tarif.prix_unitaire)) * Decimal(str(quantite))
        tva = base * Decimal(str(tarif.taux_tva or 0)) / Decimal(100)
        total = base + tva

        return {
            "code_tarif": code_tarif,
            "designation": tarif.designation,
            "categorie": tarif.categorie,
            "unite": tarif.unite,
            "quantite": quantite,
            "prix_unitaire_xaf": float(tarif.prix_unitaire),
            "base_ht_xaf": float(base),
            "tva_xaf": float(tva),
            "total_ttc_xaf": float(total),
        }

    @staticmethod
    def indicateurs_terminal(db: Session, terminal_id: int) -> Dict[str, Any]:
        t = db.get(TerminalPortuaire, terminal_id)
        if not t:
            raise HTTPException(status_code=404, detail="Terminal introuvable")
        # Productivite grue : TEU capacite / nombre de grues (si renseigne)
        productivite = None
        if t.capacite_teus and t.nombre_grues:
            productivite = round(t.capacite_teus / t.nombre_grues, 1)
        return {
            "terminal_id": t.id,
            "code": t.code,
            "nom": t.nom,
            "type": t.type_terminal.value if t.type_terminal else None,
            "capacite_teus": t.capacite_teus,
            "superficie_ha": float(t.superficie_ha) if t.superficie_ha else None,
            "longueur_quai_m": float(t.longueur_quai_m) if t.longueur_quai_m else None,
            "nombre_grues": t.nombre_grues,
            "teu_par_grue": productivite,
        }
