from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timedelta

from app.database import get_db
from app.utils.tenant import get_current_tenant_context, TenantContext, require_module_access
from app.core.not_implemented import not_implemented

router = APIRouter()

@router.get("/forecast-demand", dependencies=[Depends(require_module_access("bi"))])
def forecast_transport_demand(context: TenantContext = Depends(get_current_tenant_context)):
    """Prevision de demande transport : renvoie 501 au lieu de chiffres inventes."""
    not_implemented(
        "Prevision de demande transport/entrepot",
        "un modele previsionnel alimente par l'historique reel des missions "
        "(base de calcul et non donnees dures), non disponible a ce jour",
    )

@router.get("/fuel-anomalies", dependencies=[Depends(require_module_access("fuelguard"))])
def detect_fuel_anomalies(context: TenantContext = Depends(get_current_tenant_context)):
    """Detection d'anomalies carburant : 501 (aucun telematics/capteur branche)."""
    not_implemented(
        "Detection d'anomalies carburant (FuelGuard)",
        "un flux telematique/GPS et de jauge carburant reel par vehicule, "
        "absent a ce jour (les resultats precedents etaient inventes)",
    )

@router.get("/client-risk-score/{client_id}", dependencies=[Depends(require_module_access("finance"))])
def evaluate_client_risk_score(client_id: int, context: TenantContext = Depends(get_current_tenant_context)):
    """Score de risque client : 501 (un scoring reel reste a corder aux factures/reglements)."""
    not_implemented(
        "Score de risque credit client",
        "un calcul reel base sur les retards de paiement des factures/reglements "
        "du client (le score precedent etait une constante fabrique)",
    )
