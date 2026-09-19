"""Cameroon/CEMAC Integration Router - BSC, CSC, SYGED, APE"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date

from app.core.database import get_db
from app.services.integration_cameroun import (
    IntegrationCamerounService,
    BSCService,
    CSCService,
    SYGEDService,
    APEService
)

router = APIRouter()


@router.post("/bsc")
def creer_bsc(
    navire: str,
    numero_connaisse: str,
    nombre_conteneurs: int,
    poids_total: float,
    db: Session = Depends(get_db)
):
    """Créer BSC - Bordereau de Suivi des Cargaisons"""
    try:
        bsc = BSCService.creer_bsc(
            db=db,
            navire=navire,
            numero_connaisse=numero_connaisse,
            nombre_conteneurs=nombre_conteneurs,
            poids_total=poids_total
        )
        return {"success": True, "data": bsc}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/bsc/{bsc_id}")
def get_bsc(bsc_id: int, db: Session = Depends(get_db)):
    """Récupérer BSC par ID"""
    bsc = BSCService.get_bsc(db, bsc_id)
    if not bsc:
        raise HTTPException(status_code=404, detail="BSC non trouvé")
    return {"success": True, "data": bsc}


@router.post("/csc")
def demander_csc(
    bsc_id: int,
    date_inspection: date,
    type_marchandise: str,
    db: Session = Depends(get_db)
):
    """Demander CSC - Certificat de Sécurité Cargaison"""
    try:
        csc = CSCService.demander_csc(
            db=db,
            bsc_id=bsc_id,
            date_inspection=date_inspection,
            type_marchandise=type_marchandise
        )
        return {"success": True, "data": csc}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/dum")
def creer_dum(
    navire: str,
    numero_connaisse: str,
    regime: str,
    valeur_cif: float,
    db: Session = Depends(get_db)
):
    """Créer DUM - Déclaration Unique de Marchandises"""
    try:
        dum = SYGEDService.creer_dum(
            db=db,
            navire=navire,
            numero_connaisse=numero_connaisse,
            regime=regime,
            valeur_cif=valeur_cif
        )
        return {"success": True, "data": dum}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/ape")
def creer_ape(
    navire: str,
    date_arrivee: date,
    nombre_conteneurs: int,
    db: Session = Depends(get_db)
):
    """Créer APE - Avis d'Expédition"""
    try:
        ape = APEService.creer_ape(
            db=db,
            navire=navire,
            date_arrivee=date_arrivee,
            nombre_conteneurs=nombre_conteneurs
        )
        return {"success": True, "data": ape}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/tarifs-douane")
def get_tarifs_douane(db: Session = Depends(get_db)):
    """Récupérer tarifs de douane BEAC"""
    try:
        tarifs = IntegrationCamerounService.get_tarifs_douane(db)
        return {"success": True, "data": tarifs}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/calculer-droits")
def calculer_droits(
    valeur_cif: float,
    poids: float,
    type_marchandise: str,
    db: Session = Depends(get_db)
):
    """Calculer droits de douane"""
    try:
        droits = IntegrationCamerounService.calculer_droits(
            db=db,
            valeur_cif=valeur_cif,
            poids=poids,
            type_marchandise=type_marchandise
        )
        return {"success": True, "data": droits}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
