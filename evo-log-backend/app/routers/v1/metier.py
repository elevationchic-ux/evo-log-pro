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
from app.services.transport_b_service import TransportBService
from app.services.magasin_b_service import MagasinBService
from app.services.finance_c_service import FinanceCService
from app.services.rh_c_service import RhCService
from app.services.frais_d_service import FraisDService
from app.services.organization_service import OrganizationService
from app.services.dashboard_deep_service import DashboardDeepService
from app.services.transport_deep_service import TransportDeepService
from app.services.fluvial_b_service import FluvialBService

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


@router.get("/transport/tournees", summary="Tournees par chauffeur")
def transport_tournees(
    chauffeur: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current: User = Depends(require_perm("transport.dispatch.read")),
) -> Dict[str, Any]:
    return TransportBService.tournees(db, chauffeur=chauffeur)


@router.get("/transport/dg-conformite", summary="Conformite marchandises dangereuses")
def transport_dg(
    db: Session = Depends(get_db),
    current: User = Depends(require_perm("transport.dispatch.read")),
) -> Dict[str, Any]:
    return TransportDeepService.conformite_dg(db)


@router.get("/fluvial/navigabilite", summary="Navigabilite par bief")
def fluvial_nav(
    bief: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current: User = Depends(require_perm("transport.mission.read")),
) -> Dict[str, Any]:
    return FluvialBService.navigabilite(db, bief=bief)


@router.get("/magasin/ecarts", summary="Ecarts d'inventaire")
def magasin_ecarts(
    article: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current: User = Depends(require_perm("magasin.inventaire.read")),
) -> Dict[str, Any]:
    return MagasinBService.ecarts_inventaire(db, article=article)


@router.get("/finance/previsions", summary="Positions de tresorerie previsionnelles")
def finance_previsions(
    db: Session = Depends(get_db),
    current: User = Depends(require_perm("tresorerie.mouvement.read")),
) -> Dict[str, Any]:
    return FinanceCService.previsions(db)


@router.get("/finance/affacturage", summary="Avances d'affacturage")
def finance_affacturage(
    db: Session = Depends(get_db),
    current: User = Depends(require_perm("tresorerie.mouvement.read")),
) -> Dict[str, Any]:
    return FinanceCService.affacturage(db)


@router.get("/rh/formation", summary="Plans de formation et realisation")
def rh_formation(
    db: Session = Depends(get_db),
    current: User = Depends(require_perm("rh.employes.read")),
) -> Dict[str, Any]:
    return RhCService.formation(db)


@router.get("/rh/discipline", summary="Sanctions disciplinaires actives")
def rh_discipline(
    db: Session = Depends(get_db),
    current: User = Depends(require_perm("rh.employes.read")),
) -> Dict[str, Any]:
    return RhCService.discipline(db)


@router.get("/frais/rapports", summary="Notes de frais par statut")
def frais_rapports(
    collaborateur: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current: User = Depends(require_perm("rh.employes.read")),
) -> Dict[str, Any]:
    return FraisDService.rapports(db, collaborateur=collaborateur)


@router.get("/frais/tva-recuperable", summary="TVA recuperable en attente")
def frais_tva(
    db: Session = Depends(get_db),
    current: User = Depends(require_perm("rh.employes.read")),
) -> Dict[str, Any]:
    return FraisDService.tva_recuperable(db)


@router.get("/organisation/abonnements", summary="Sante des abonnements tenant")
def organisation_abonnements(
    db: Session = Depends(get_db),
    current: User = Depends(require_perm("admin.nomenclature.read")),
) -> Dict[str, Any]:
    return OrganizationService.abonnements(db)


@router.get("/dashboard/sante", summary="Sante des modules et alertes")
def dashboard_sante(
    db: Session = Depends(get_db),
    current: User = Depends(require_perm("dashboard.nomenclature.read")),
) -> Dict[str, Any]:
    return {
        "modules": DashboardDeepService.sante_modules(db),
        "alertes": DashboardDeepService.alertes(db),
    }
