"""API metier chaine du froid : detection d'excursions thermiques."""
from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.permissions import require_perm
from app.models.user import User
from app.services.coldchain_service import ColdChainExcursionService

router = APIRouter()


class ReleveRequest(BaseModel):
    produit_id: int
    temperature_c: float
    duree_h: float
    actif_associe: Optional[str] = None
    valeur_marchandise_xaf: Optional[float] = None


@router.post("/excursions/releve")
def enregistrer_releve(
    payload: ReleveRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("coldchain.excursions.create")),
):
    return ColdChainExcursionService.enregistrer_releve(
        db, produit_id=payload.produit_id, temperature_c=payload.temperature_c,
        duree_h=payload.duree_h, actif_associe=payload.actif_associe,
        valeur_marchandise_xaf=payload.valeur_marchandise_xaf)


@router.post("/excursions/{excursion_id}/cloturer")
def cloturer_excursion(
    excursion_id: int,
    valeur_perdue_xaf: Optional[float] = None,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("coldchain.excursions.modify")),
):
    return ColdChainExcursionService.cloturer_excursion(
        db, excursion_id, valeur_perdue_xaf)
