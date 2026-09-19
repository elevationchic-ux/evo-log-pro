"""Cameroon Local Payment Router - Orange Money, MTN, Local Banks"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date

from app.core.database import get_db
from app.services.paiement_local import (
    PaiementLocalService,
    OrangeMoneyService,
    MTNMobileMoneyService,
    BanqueLocaleService
)

router = APIRouter()


@router.post("/initier")
def initier_paiement(
    methode: str,
    donnees: dict,
    db: Session = Depends(get_db)
):
    """Initier paiement local (Orange Money, MTN, Virement)"""
    try:
        paiement = PaiementLocalService.choisir_methode_paiement(methode, donnees)
        return {"success": True, "data": paiement}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/orange-money")
def initier_orange_money(
    numero: str,
    montant: float,
    reference: str,
    description: str,
    db: Session = Depends(get_db)
):
    """Initier paiement Orange Money"""
    try:
        paiement = OrangeMoneyService.initier_paiement(
            db=db,
            numero_orange=numero,
            montant=montant,
            reference=reference,
            description=description
        )
        return {"success": True, "data": paiement}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/orange-money/{reference}/verifier")
def verifier_orange_money(reference: str):
    """Vérifier statut paiement Orange Money"""
    try:
        statut = OrangeMoneyService.verifier_paiement(reference)
        return {"success": True, "data": statut}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/mtn")
def initier_mtn(
    numero: str,
    montant: float,
    reference: str,
    description: str,
    db: Session = Depends(get_db)
):
    """Initier paiement MTN Mobile Money"""
    try:
        paiement = MTNMobileMoneyService.initier_paiement(
            db=db,
            numero_mtn=numero,
            montant=montant,
            reference=reference,
            description=description
        )
        return {"success": True, "data": paiement}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/mtn/{reference}/verifier")
def verifier_mtn(reference: str):
    """Vérifier statut paiement MTN Mobile Money"""
    try:
        statut = MTNMobileMoneyService.verifier_paiement(reference)
        return {"success": True, "data": statut}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/virement")
def initier_virement(
    banque: str,
    compte: str,
    montant: float,
    beneficiaire: str,
    reference: str,
    motif: str,
    db: Session = Depends(get_db)
):
    """Initier virement bancaire"""
    try:
        virement = BanqueLocaleService.initier_virement(
            db=db,
            code_banque=banque,
            compte_bancaire=compte,
            montant=montant,
            beneficiaire=beneficiaire,
            reference=reference,
            motif=motif
        )
        return {"success": True, "data": virement}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/methodes")
def get_methodes_disponibles():
    """Récupérer méthodes de paiement disponibles"""
    methodes = PaiementLocalService.get_methodes_disponibles()
    return {"success": True, "data": methodes}
