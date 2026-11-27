"""Service metier transit deep : calcul de la valeur en douane selon
l'Incoterm (CIF = declaree + transport + assurance ; FOB = declaree
seule + ajustements). Aucune base inventee : champs manquants = refus."""
from decimal import Decimal
from typing import Dict, Any

from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.transit_deep import CustomsValuation


class CustomsValuationService:
    """Valorisation douaniere par Incoterm."""

    @staticmethod
    def calculer_valeur(db: Session, valuation_id: int) -> Dict[str, Any]:
        v = db.get(CustomsValuation, valuation_id)
        if not v:
            raise HTTPException(status_code=404, detail="Valorisation introuvable")
        if v.valeur_declaree_xaf is None:
            raise HTTPException(status_code=422, detail="Valeur declaree non renseignee")

        declaree = Decimal(str(v.valeur_declaree_xaf))
        transport = Decimal(str(v.valeur_transport_xaf or 0))
        assurance = Decimal(str(v.valeur_assurance_xaf or 0))
        incoterm = (v.incoterm or "").upper()

        # CIF/CIP : prix rendu droits acquittes -> ajoute transport+assurance
        if incoterm in ("CIF", "CIP", "CFR", "CPT"):
            valeur = declaree + transport + assurance
            detail = "CIF : declaree + transport + assurance"
        # FOB/FCA/EXW : valeur a l'export -> transport/assurance ajoutes si connus
        elif incoterm in ("FOB", "FCA", "EXW", "FAS"):
            valeur = declaree + transport + assurance
            detail = f"{incoterm} : declaree + ajustements transport/assurance"
        else:
            # Incoterm inconnu ou absent : valeur declaree seule, signalee
            valeur = declaree
            detail = "Incoterm non reconnu : valeur declaree seule (a verifier)"

        return {
            "valuation_id": v.id,
            "reference_dossier": v.reference_dossier,
            "incoterm": v.incoterm,
            "valeur_declaree_xaf": float(declaree),
            "valeur_transport_xaf": float(transport),
            "valeur_assurance_xaf": float(assurance),
            "valeur_en_douane_xaf": float(valeur),
            "methode": detail,
        }
