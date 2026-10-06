"""Cameroon Local Payment Router - Orange Money, MTN, Local Banks

SÉCURITÉ (2026-09 correction) : ces endpoints étaient publics (aucun
get_current_user)  quiconque pouvait tenter d'initier des paiements au nom
d'un tenant. Ils sont désormais authentifiés.

Batch 3 : plus aucun 501 nu. Les demandes sont persistees (PaymentTransaction)
et, selon la configuration des gateways PAYMENT_ORANGE / PAYMENT_MTN /
PAYMENT_BANK, reellement remises au fournisseur (503 si non configure,
502 si le fournisseur rejette).
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
    """Preparer un paiement local : brouillon persiste, remise au fournisseur
    si sa gateway est configuree."""
    try:
        paiement = PaiementLocalService.choisir_methode_paiement(
            methode, donnees, db=db, company_id=getattr(current_user, "company_id", None)
        )
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
    """Demande Orange Money : persistee ; envoyee au fournisseur si configure."""
    try:
        paiement = OrangeMoneyService.initier_paiement(
            db=db,
            numero_orange=numero,
            montant=montant,
            reference=reference,
            description=description,
            company_id=getattr(current_user, "company_id", None),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"success": True, "data": paiement}


@router.get("/orange-money/{reference}/verifier")
def verifier_orange_money(
    reference: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Statut : reponse fournisseur si gateway configuree, statut local sinon."""
    statut = OrangeMoneyService.verifier_paiement(db, reference)
    return {"success": True, "data": statut}


@router.post("/orange-money/{reference}/annuler")
def annuler_orange_money(
    reference: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Revers fournisseur si configure ; annulation du brouillon local sinon."""
    resultat = OrangeMoneyService.annuler_paiement(db, reference)
    return {"success": True, "data": resultat}


@router.post("/mtn")
def initier_mtn(
    numero: str,
    montant: float,
    reference: str,
    description: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Demande MTN Mobile Money : persistee ; request-to-pay reel si configure."""
    try:
        paiement = MTNMobileMoneyService.initier_paiement(
            db=db,
            numero_mtn=numero,
            montant=montant,
            reference=reference,
            description=description,
            company_id=getattr(current_user, "company_id", None),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"success": True, "data": paiement}


@router.get("/mtn/{reference}/verifier")
def verifier_mtn(
    reference: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Statut : reponse fournisseur si gateway configuree, statut local sinon."""
    statut = MTNMobileMoneyService.verifier_paiement(db, reference)
    return {"success": True, "data": statut}


@router.post("/mtn/{reference}/annuler")
def annuler_mtn(
    reference: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Revers fournisseur si configure ; annulation du brouillon local sinon."""
    resultat = MTNMobileMoneyService.annuler_paiement(db, reference)
    return {"success": True, "data": resultat}


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
    """Ordre de virement persiste ; remis a la banque si gateway configuree."""
    try:
        virement = BanqueLocaleService.initier_virement(
            db=db,
            code_banque=banque,
            compte_bancaire=compte,
            montant=montant,
            beneficiaire=beneficiaire,
            reference=reference,
            motif=motif,
            company_id=getattr(current_user, "company_id", None),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"success": True, "data": virement}


@router.get("/virement/{reference}/verifier")
def verifier_virement(
    reference: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Statut du virement : connecteur bancaire si configure, sinon statut local."""
    statut = BanqueLocaleService.verifier_virement(db, reference)
    return {"success": True, "data": statut}


@router.get("/releve/{code_banque}/{compte}")
def releve_compte(
    code_banque: str,
    compte: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Releve de compte : 503 tant que le connecteur bancaire n'est pas declare
    (aucun solde invente), releve reel du fournisseur quand il l'est."""
    releve = BanqueLocaleService.get_releve_compte(db, code_banque, compte)
    return {"success": True, "data": releve}


@router.get("/methodes")
def get_methodes_disponibles():
    """Methodes disponibles + etat reel de configuration des gateways."""
    methodes = PaiementLocalService.get_methodes_disponibles()
    return {"success": True, "data": methodes}
