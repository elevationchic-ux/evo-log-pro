"""Router FastAPI pour Maintenance GMAO Avancée (Préventif, MTBF/MTTR, TCO)"""
from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.maintenance_gmao_avance_service import MaintenancePreventiveService, AnalyticsMaintenanceService

router = APIRouter()


@router.post("/preventif/generer-ordres", summary="Générer automatiquement les ordres de travail préventifs")
def generer_ordres(vehicule_ids: List[int], db: Session = Depends(get_db)):
    """Génère les ordres de travail préventifs selon les seuils kilométriques et intervalles de temps."""
    return MaintenancePreventiveService.generer_ordres_preventifs(db=db, vehicule_ids=vehicule_ids)


@router.get("/analytics/mtbf-mttr/{vehicule_id}", summary="Calculer MTBF, MTTR et disponibilité")
def get_mtbf_mttr(vehicule_id: int, periode_mois: int = Query(12), db: Session = Depends(get_db)):
    """Calcule la fiabilité du véhicule: Temps Moyen Entre Pannes (MTBF) et Temps Moyen de Réparation (MTTR)."""
    return AnalyticsMaintenanceService.calculer_mtbf_mttr(db=db, vehicule_id=vehicule_id, periode_mois=periode_mois)


@router.get("/analytics/tco/{vehicule_id}", summary="Calculer le Coût Total de Détention (TCO)")
def get_tco(vehicule_id: int, db: Session = Depends(get_db)):
    """Calcule le TCO mensuel par véhicule: amortissement, carburant, maintenance, pneumatiques, assurance."""
    return AnalyticsMaintenanceService.calculer_tco_vehicule(db=db, vehicule_id=vehicule_id)
