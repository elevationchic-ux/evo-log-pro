"""Router FastAPI pour Magasin & WMS Avancé (Picking FIFO/FEFO, Inventaires Tournants OHADA)"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.magasin_wms_avance_service import PickingAvanceService, InventaireCompletService
from app.schemas.magasin_wms_avance import (
    VaguePickingRequest, VaguePickingResponse,
    CampagneInventaireRequest, InventaireRegularisationResponse
)

router = APIRouter()


@router.post("/picking/vague", response_model=VaguePickingResponse, summary="Générer une vague de picking optimisée FIFO/FEFO")
def generer_vague(payload: VaguePickingRequest, db: Session = Depends(get_db)):
    """Optimise le parcours de préparation de commandes selon la règle FIFO ou FEFO."""
    return PickingAvanceService.generer_vague_picking(
        db=db,
        commandes_ids=payload.commandes_ids,
        regle=payload.regle
    )


@router.post("/inventaire/regulariser", response_model=InventaireRegularisationResponse, summary="Calculer les écarts de stock et générer le PV OHADA")
def regulariser_inventaire(payload: CampagneInventaireRequest, db: Session = Depends(get_db)):
    """Calcule les écarts entre stock théorique et physique et génère le PV de régularisation comptable 603/703."""
    return InventaireCompletService.calculer_ecarts_et_regulariser(
        db=db,
        campagne_id=payload.campagne_id,
        lignes_comptage=[l.dict() for l in payload.lignes_comptage]
    )
