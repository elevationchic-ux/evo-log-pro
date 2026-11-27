"""Routeur metier : endpoints de lecture pour les services
metier avances (analytique, alertes, conformite). Donnees reelles
uniquement — chaque service refuse honnetement sans donnees."""
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.permissions import require_perm
from app.models.user import User
from app.services.capteur_carburant_service import CapteurCarburantService
from app.services.paie_service import PaieService
from app.services.rentabilite_service import RentabiliteService
from app.services.economie_service import EconomieService
from app.services.qhse_deep_service import QhseDeepService
from app.services.comptabilite_deep_service import ComptabiliteDeepService

router = APIRouter(tags=["metier-analytique"], prefix="/metier")


@router.get("/cuves-en-alerte", summary="Cuves carburant sous seuil")
def cuves_en_alerte(
    seuil_pct: float = Query(20.0),
    db: Session = Depends(get_db),
    current: User = Depends(require_perm("transport.carburant.read")),
) -> Dict[str, Any]:
    return CapteurCarburantService.cuves_en_alerte(db, seuil_pct=seuil_pct)


@router.get("/paie/cumuls", summary="Cumuls paie annuels")
def paie_cumuls(
    annee: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current: User = Depends(require_perm("paie.bulletin.read")),
) -> Dict[str, Any]:
    return PaieService.cumuls_annuels(db, annee=annee)


@router.get("/rentabilite", summary="CA par client et type")
def rentabilite(
    client_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current: User = Depends(require_perm("comptabilite.balance.read")),
) -> Dict[str, Any]:
    return RentabiliteService.par_client(db, client_id=client_id)


@router.get("/indicateurs-financiers", summary="Indicateurs par categorie")
def indicateurs(
    categorie: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current: User = Depends(require_perm("comptabilite.balance.read")),
) -> Dict[str, Any]:
    return EconomieService.indicateurs(db, categorie=categorie)


@router.get("/qhse/depassements", summary="Depassements normes environnementales")
def qhse_depassements(
    db: Session = Depends(get_db),
    current: User = Depends(require_perm("qhse.rapport.read")),
) -> Dict[str, Any]:
    return QhseDeepService.depassements(db)


@router.get("/compta/controle-budgetaire", summary="Budgets et depassements")
def controle_budgetaire(
    db: Session = Depends(get_db),
    current: User = Depends(require_perm("comptabilite.budget_control.read")),
) -> Dict[str, Any]:
    return ComptabiliteDeepService.controle_budgetaire(db)
