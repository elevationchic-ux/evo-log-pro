"""Router FastAPI pour Transit & Douane Avancé (DUM SYDONIA, Guichet Unique GUCE, Taxation TEC CEMAC)"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.transit_douane_avance_service import DUMService, GuichetUniqueService, TaxationDouaniereService
from app.schemas.transit_douane_avance import (
    DumCreateRequest,
    SimulationTaxationRequest,
    TaxationResultResponse,
    GuceTeletransmissionResponse
)

router = APIRouter()


@router.post("/taxation/simuler", response_model=TaxationResultResponse, summary="Simuler la liquidation des droits et taxes en douane")
def simuler_taxation(payload: SimulationTaxationRequest):
    """Calcule le Droit de Douane (TEC CEMAC), TVA 19.25%, Redevance informatique et précompte IS."""
    return TaxationDouaniereService.calculer_droits_et_taxes(
        valeur_cif_xaf=payload.valeur_cif_xaf,
        code_sh=payload.code_sh,
        regime=payload.regime
    )


@router.post("/dum/creer", summary="Créer une DUM avec liquidation automatique")
def creer_dum(payload: DumCreateRequest, db: Session = Depends(get_db)):
    """Génère une DUM SYDONIA World avec calcul complet des taxes."""
    return DUMService.creer_dum(
        db=db,
        regime=payload.regime,
        importateur_id=payload.importateur_id,
        valeur_cif_xaf=payload.valeur_cif_xaf,
        code_sh=payload.code_sh,
        pays_origine=payload.pays_origine
    )


@router.post("/guce/teletransmettre/{numero_dum}", response_model=GuceTeletransmissionResponse, summary="Télétransmettre au Guichet Unique GUCE Cameroun")
def teletransmettre_guce(numero_dum: str):
    """Télétransmet le dossier électronique au Guichet Unique des Opérations du Commerce Extérieur de Douala."""
    return GuichetUniqueService.teletransmettre_guce(
        numero_dum=numero_dum,
        donnees_declaration={"validated": True}
    )
