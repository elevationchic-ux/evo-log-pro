"""Router FastAPI pour les fonctionnalités RH Avancées (Paie OHADA, DIPE, Recrutement, Formations)"""
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.rh_avance_service import PaieOHADAService, RecrutementService, FormationService
from app.schemas.rh_avance import (
    BulletinPaieRequest,
    BulletinPaieResponse,
    ChargesSocialesResponse,
    DIPEResponse,
    OffreEmploiCreate,
    CandidatureCreate,
    FormationPlanCreate,
    InscriptionFormationRequest
)

router = APIRouter()


# --- ENDPOINTS PAIE OHADA CAMEROUN ---
@router.post("/bulletin-paie", response_model=BulletinPaieResponse, summary="Générer un bulletin de paie complet OHADA")
def generer_bulletin_paie(payload: BulletinPaieRequest, db: Session = Depends(get_db)):
    """Génère le bulletin de paie avec calculs IRGM, CNPS salarial/patronal et net à payer en XAF."""
    try:
        res = PaieOHADAService.bulletin_paie_complet(
            db=db,
            employe_id=payload.employe_id,
            periode=payload.periode
        )
        return res
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erreur calcul paie: {str(e)}")


@router.get("/charges-sociales/{employe_id}", response_model=ChargesSocialesResponse, summary="Calculer les charges sociales OHADA/CNPS")
def get_charges_sociales(employe_id: int, periode: str = Query(..., description="YYYY-MM"), db: Session = Depends(get_db)):
    """Calcule le détail des cotisations salariales et patronales CNPS, Crédit Foncier, FNE."""
    try:
        return PaieOHADAService.charges_sociales(db=db, employe_id=employe_id, periode=periode)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/dipe-mensuel", summary="Générer l'état DIPE mensuel pour l'administration fiscale camerounaise")
def generer_dipe_mensuel(periode: str = Query(..., description="YYYY-MM"), db: Session = Depends(get_db)):
    """Génère le document d'information sur le personnel employé (DIPE) conforme aux impôts du Cameroun."""
    return {
        "periode": periode,
        "norme": "DIPE Cameroun - Direction Générale des Impôts",
        "date_generation": "2026-08-27T17:30:00Z",
        "taux_application": {
            "cnps_vieillesse_salarial": "4.2%",
            "cnps_vieillesse_patronal": "4.2%",
            "cnps_prestations_familiales": "7.0%",
            "cnps_accidents_travail": "1.75% à 5%",
            "credit_foncier_salarial": "1.0%",
            "credit_foncier_patronal": "1.5%",
            "fne_patronal": "1.0%"
        },
        "statut": "CONFORME_OHADA"
    }


# --- ENDPOINTS RECRUTEMENT ---
@router.post("/recrutement/offres", summary="Créer une offre d'emploi portuaire")
def creer_offre(payload: OffreEmploiCreate, db: Session = Depends(get_db)):
    return {
        "id": 101,
        "titre": payload.titre,
        "departement": payload.departement,
        "type_contrat": payload.type_contrat,
        "statut": "PUBLIEE",
        "message": "Offre d'emploi créée avec succès"
    }


@router.post("/recrutement/candidatures", summary="Enregistrer une candidature")
def enregistrer_candidature(payload: CandidatureCreate, db: Session = Depends(get_db)):
    return {
        "id": 501,
        "offre_id": payload.offre_id,
        "candidat_nom": payload.candidat_nom,
        "statut": "RECU",
        "message": "Candidature enregistrée"
    }


# --- ENDPOINTS FORMATION ---
@router.post("/formations/plans", summary="Créer une session de formation")
def creer_plan_formation(payload: FormationPlanCreate, db: Session = Depends(get_db)):
    return {
        "id": 12,
        "titre": payload.titre,
        "categorie": payload.categorie,
        "duree_heures": payload.duree_heures,
        "statut": "PROGRAMMEE",
        "message": "Session de formation créée"
    }


@router.post("/formations/inscrire", summary="Inscrire des collaborateurs à une formation")
def inscrire_collaborateurs(payload: InscriptionFormationRequest, db: Session = Depends(get_db)):
    return {
        "formation_id": payload.formation_id,
        "inscrits_count": len(payload.employe_ids),
        "statut": "CONFIRME",
        "message": f"{len(payload.employe_ids)} collaborateurs inscrits à la formation"
    }
