"""Cameroon Local Payment Router - Orange Money, MTN, Local Banks

SÉCURITÉ (2026-09 correction) : ces endpoints étaient publics (aucun
get_current_user)  quiconque pouvait tenter d'initier des paiements au nom
d'un tenant. Ils sont désormais authentifiés, et les 501 du service (statuts
non vérifiables, annulations, relevés) ne sont plus transformés en 400 par un
catch-all.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Préparer un brouillon de paiement local (Orange Money, MTN, Virement)."""
    try:
        paiement = PaiementLocalService.choisir_methode_paiement(methode, donnees)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"success": True, "data": paiement}


@router.post("/orange-money")
def initier_orange_money(
    numero: str,
    montant: float,
    reference: str,
    description: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Préparer un brouillon de paiement Orange Money (aucun appel fournisseur)."""
    try:
        paiement = OrangeMoneyService.initier_paiement(
            db=db,
            numero_orange=numero,
            montant=montant,
            reference=reference,
            description=description
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"success": True, "data": paiement}


@router.get("/orange-money/{reference}/verifier")
def verifier_orange_money(
    reference: str,
    current_user: User = Depends(get_current_user)
):
    """Vérifier statut paiement Orange Money (501 tant que le connecteur n'existe pas)."""
    statut = OrangeMoneyService.verifier_paiement(reference)
    return {"success": True, "data": statut}


@router.post("/mtn")
def initier_mtn(
    numero: str,
    montant: float,
    reference: str,
    description: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Préparer un brouillon de paiement MTN Mobile Money (aucun appel fournisseur)."""
    try:
        paiement = MTNMobileMoneyService.initier_paiement(
            db=db,
            numero_mtn=numero,
            montant=montant,
            reference=reference,
            description=description
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"success": True, "data": paiement}


@router.get("/mtn/{reference}/verifier")
def verifier_mtn(
    reference: str,
    current_user: User = Depends(get_current_user)
):
    """Vérifier statut paiement MTN Mobile Money (501 tant que le connecteur n'existe pas)."""
    statut = MTNMobileMoneyService.verifier_paiement(reference)
    return {"success": True, "data": statut}


@router.post("/virement")
def initier_virement(
    banque: str,
    compte: str,
    montant: float,
    beneficiaire: str,
    reference: str,
    motif: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Préparer un brouillon d'ordre de virement (aucune banque contactée)."""
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
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"success": True, "data": virement}


@router.get("/methodes")
def get_methodes_disponibles():
    """Récupérer méthodes de paiement disponibles (liste indicative)."""
    methodes = PaiementLocalService.get_methodes_disponibles()
    return {"success": True, "data": methodes}
