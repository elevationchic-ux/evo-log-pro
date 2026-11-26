"""Service metier chaine du froid : detection d'excursions thermiques
depuis les releves reels et evaluation d'impact produit (HACCP)."""
from datetime import datetime, timezone
from typing import Dict, Any, Optional

from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.coldchain_deep import ColdChainProduct, ColdChainExcursion


def _now() -> datetime:
    return datetime.now(timezone.utc)


class ColdChainExcursionService:
    """Detecte et enregistre les excursions de temperature."""

    @staticmethod
    def enregistrer_releve(
        db: Session,
        produit_id: int,
        temperature_c: float,
        duree_h: float,
        actif_associe: Optional[str] = None,
        valeur_marchandise_xaf: Optional[float] = None,
        company_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Compare un releve de temperature a la plage exigee du produit.

        Si la temperature sort de [temp_min_c, temp_max_c] : une excursion
        est creee avec duree, temperature extreme et impact evalue.
        Aucune valeur perdue n'est inventee : valeur_perdue_xaf reste NULL
        sauf si fournie explicitement (ex. decision qualite documentee).
        """
        produit = db.get(ColdChainProduct, produit_id)
        if not produit:
            raise HTTPException(status_code=404, detail="Produit introuvable")
        if produit.temp_min_c is None or produit.temp_max_c is None:
            return {
                "excursion": False,
                "raison": "plage de temperature non configuree sur le produit",
            }

        hors_plage = temperature_c < produit.temp_min_c or temperature_c > produit.temp_max_c
        if not hors_plage:
            return {"excursion": False, "temperature_c": temperature_c,
                    "plage": [produit.temp_min_c, produit.temp_max_c]}

        # Impact : tolerable si la duree reste sous le seuil produit
        seuil = produit.seuil_excursion_h or 0
        depassement = duree_h > seuil if seuil else True
        impact = "critique" if depassement else "majeur"
        if not depassement and seuil:
            impact = "mineur"

        reference = f"EXC-{_now().strftime('%Y%m%d%H%M%S')}-{produit.id}"
        exc = ColdChainExcursion(
            company_id=company_id or produit.company_id,
            reference=reference,
            type="temperature",
            produit_concerne=produit.code_sku,
            actif_associe=actif_associe,
            date_debut=_now(),
            date_fin=_now() if duree_h == 0 else None,
            temp_extreme_c=int(round(temperature_c)),
            duree_h=int(round(duree_h)),
            impact=impact,
            valeur_perdue_xaf=int(valeur_marchandise_xaf) if valeur_marchandise_xaf else None,
            statut="ouverte",
            is_active=True,
        )
        db.add(exc)
        db.commit()
        db.refresh(exc)

        return {
            "excursion": True,
            "reference": reference,
            "impact": impact,
            "seuil_excursion_h": seuil,
            "duree_h": duree_h,
            "temperature_c": temperature_c,
            "plage_exigee": [produit.temp_min_c, produit.temp_max_c],
            "note": (
                "Excursion enregistree. La valeur perdue n'est pas estimee "
                "automatiquement : saisir valeur_marchandise_xaf apres "
                "decision qualite."
            ),
        }

    @staticmethod
    def cloturer_excursion(
        db: Session, excursion_id: int, valeur_perdue_xaf: Optional[float] = None
    ) -> ColdChainExcursion:
        """Cloture une excursion ; la valeur perdue est saisie explicitement."""
        exc = db.get(ColdChainExcursion, excursion_id)
        if not exc:
            raise HTTPException(status_code=404, detail="Excursion introuvable")
        exc.statut = "cloturee"
        exc.date_fin = _now()
        if valeur_perdue_xaf is not None:
            exc.valeur_perdue_xaf = int(valeur_perdue_xaf)
        db.commit()
        db.refresh(exc)
        return exc
