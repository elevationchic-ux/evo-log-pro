"""Service metier B2B commercial : controle de la limite de credit
des comptes clients (limite - encours). Refus honnete au-dela du
plafond, jamais d'acceptation fabriquee."""
from decimal import Decimal
from typing import Dict, Any

from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.b2b_c_deep import B2bCCreditAccount


class B2bCCreditService:
    """Controle credit comptes B2B."""

    @staticmethod
    def verifier_credit(
        db: Session, compte_id: int, montant_xaf: float
    ) -> Dict[str, Any]:
        compte = db.get(B2bCCreditAccount, compte_id)
        if not compte:
            raise HTTPException(status_code=404, detail="Compte credit introuvable")
        if montant_xaf <= 0:
            raise HTTPException(status_code=422, detail="Montant invalide")

        limite = Decimal(str(compte.limite_credit or 0))
        encours = Decimal(str(compte.encours or 0))
        disponible = limite - encours

        if limite <= 0:
            return {"compte_id": compte.id, "decision": "refuse",
                    "motif": "aucune limite de credit definie"}
        if Decimal(str(montant_xaf)) > disponible:
            return {
                "compte_id": compte.id, "decision": "refuse",
                "motif": "montant superieur au credit disponible",
                "limite_xaf": float(limite), "encours_xaf": float(encours),
                "disponible_xaf": float(disponible),
                "manquant_xaf": float(Decimal(str(montant_xaf)) - disponible),
            }
        return {
            "compte_id": compte.id, "decision": "accepte",
            "limite_xaf": float(limite), "encours_xaf": float(encours),
            "disponible_avant_xaf": float(disponible),
            "reste_apres_xaf": float(disponible - Decimal(str(montant_xaf))),
        }
