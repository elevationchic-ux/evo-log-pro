"""Service metier B2B : controle de la limite de credit client avant
commande (plafond - encours). Refus honnete si la limite est atteinte,
jamais d'acceptation au-dela du plafond."""
from decimal import Decimal
from typing import Dict, Any

from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.b2b_deep import ClientCreditLimit


class B2bCreditService:
    """Controle credit clients B2B."""

    @staticmethod
    def verifier_credit(
        db: Session, credit_limit_id: int, montant_commande_xaf: float
    ) -> Dict[str, Any]:
        credit = db.get(ClientCreditLimit, credit_limit_id)
        if not credit:
            raise HTTPException(status_code=404, detail="Limite de credit introuvable")
        if montant_commande_xaf <= 0:
            raise HTTPException(status_code=422, detail="Montant de commande invalide")

        plafond = Decimal(str(credit.plafond_xaf or 0))
        encours = Decimal(str(credit.encours_actuel_xaf or 0))
        disponible = plafond - encours
        reste_apres = disponible - Decimal(str(montant_commande_xaf))

        if plafond <= 0:
            return {
                "credit_id": credit.id,
                "decision": "refuse",
                "motif": "aucun plafond de credit defini",
            }
        if montant_commande_xaf > disponible:
            return {
                "credit_id": credit.id,
                "decision": "refuse",
                "motif": "montant superieur au credit disponible",
                "plafond_xaf": float(plafond),
                "encours_xaf": float(encours),
                "disponible_xaf": float(disponible),
                "manquant_xaf": float(Decimal(str(montant_commande_xaf)) - disponible),
            }
        return {
            "credit_id": credit.id,
            "decision": "accepte",
            "plafond_xaf": float(plafond),
            "encours_xaf": float(encours),
            "disponible_avant_xaf": float(disponible),
            "reste_apres_commande_xaf": float(reste_apres),
        }
