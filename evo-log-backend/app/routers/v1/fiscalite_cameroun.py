"""Cameroon Taxation Router - IRPP, IS, TCF, TDR, OHADA"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date

from app.core.database import get_db
from app.services.fiscalite_cameroun_service import (
    FiscaliteCamerounService,
    OHADAService
)

router = APIRouter()


@router.post("/declarations")
def creer_declaration_fiscale(
    company_id: int,
    type_impot: str,
    periode_debut: date,
    periode_fin: date,
    chiffre_affaires: float,
    benefice: float,
    db: Session = Depends(get_db)
):
    """Créer déclaration fiscale"""
    try:
        declaration = FiscaliteCamerounService.creer_declaration_fiscale(
            db=db,
            company_id=company_id,
            type_impot=type_impot,
            periode_debut=periode_debut,
            periode_fin=periode_fin,
            chiffre_affaires=chiffre_affaires,
            benefice=benefice
        )
        return {"success": True, "data": declaration}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/declarations/{declaration_id}/soumettre")
def soumettre_declaration(declaration_id: int, db: Session = Depends(get_db)):
    """Soumettre déclaration à l'administration fiscale"""
    try:
        declaration = FiscaliteCamerounService.soumettre_declaration(db, declaration_id)
        return {"success": True, "data": declaration}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/declarations/{declaration_id}/valider")
def valider_declaration(
    declaration_id: int,
    agent_fiscal: str,
    db: Session = Depends(get_db)
):
    """Valider déclaration par l'administration fiscale"""
    try:
        declaration = FiscaliteCamerounService.valider_declaration(
            db,
            declaration_id,
            agent_fiscal
        )
        return {"success": True, "data": declaration}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/declarations/{declaration_id}/payer")
def payer_declaration(
    declaration_id: int,
    montant: float,
    db: Session = Depends(get_db)
):
    """Payer déclaration fiscale"""
    try:
        declaration = FiscaliteCamerounService.payer_declaration(
            db,
            declaration_id,
            montant
        )
        return {"success": True, "data": declaration}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/retenues-source")
def creer_retenue_source(
    company_id: int,
    type_retenue: str,
    montant_brut: float,
    beneficiaire: str,
    numero_contribuable: str,
    db: Session = Depends(get_db)
):
    """Créer retenue à la source"""
    try:
        retenue = FiscaliteCamerounService.creer_retenue_source(
            db=db,
            company_id=company_id,
            type_retenue=type_retenue,
            montant_brut=montant_brut,
            beneficiaire=beneficiaire,
            numero_contribuable=numero_contribuable
        )
        return {"success": True, "data": retenue}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/retenues-source/{retenue_id}/verser")
def verser_retenue(retenue_id: int, db: Session = Depends(get_db)):
    """Verser retenue à l'administration fiscale"""
    try:
        retenue = FiscaliteCamerounService.verser_retenue(db, retenue_id)
        return {"success": True, "data": retenue}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/ohada/tva")
def calculer_tva_ohada(montant_ht: float, taux_tva: float = 19.25):
    """Calculer TVA OHADA (19.25% standard)"""
    try:
        tva = OHADAService.calculer_tva_ohada(montant_ht, taux_tva)
        return {"success": True, "data": tva}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/ohada/centimes")
def calculer_centimes_additionnels(montant: float, taux: float = 10):
    """Calculer centimes additionnels (10% standard)"""
    try:
        centimes = OHADAService.calculer_centimes_additionnels(montant, taux)
        return {"success": True, "data": centimes}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/ohada/is-minimum")
def calculer_is_minimum(chiffre_affaires: float, db: Session = Depends(get_db)):
    """Calculer IS minimum (Cameroon)"""
    try:
        is_min = OHADAService.calculer_is_minimum(db, chiffre_affaires)
        return {"success": True, "data": is_min}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/ohada/bilan/{company_id}/{exercice}")
def generer_bilan(company_id: int, exercice: int, db: Session = Depends(get_db)):
    """Générer bilan OHADA"""
    try:
        bilan = OHADAService.generer_bilan(db, company_id, exercice)
        return {"success": True, "data": bilan}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/ohada/compte-resultat/{company_id}/{exercice}")
def generer_compte_resultat(company_id: int, exercice: int, db: Session = Depends(get_db)):
    """Générer compte de résultat OHADA"""
    try:
        compte_resultat = OHADAService.generer_compte_resultat(db, company_id, exercice)
        return {"success": True, "data": compte_resultat}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
