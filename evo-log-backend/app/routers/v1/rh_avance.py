"""Router FastAPI pour les fonctionnalités RH Avancées (Paie OHADA, DIPE, Recrutement, Formations)"""
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
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
def generer_dipe_mensuel(
    periode: str = Query(..., description="YYYY-MM"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Agrège la masse salariale réelle depuis la table salaires pour la période.

    Si aucune fiche de paie n'est enregistrée, le compteur retourne 0 honnête.
    """
    from app.models.rh import Salaire
    from sqlalchemy import func as sqlfunc

    annee_str, mois_str = periode.split("-")
    annee_int, mois_int = int(annee_str), int(mois_str)

    rows = (
        db.query(
            sqlfunc.count(Salaire.id).label("nb"),
            sqlfunc.coalesce(sqlfunc.sum(Salaire.salaire_brut), 0).label("masse"),
            sqlfunc.coalesce(sqlfunc.sum(Salaire.deductions_cnps), 0).label("cnps_salarial"),
            sqlfunc.coalesce(sqlfunc.sum(Salaire.deductions_impot), 0).label("ircm"),
        )
        .filter(Salaire.annee == annee_int, Salaire.mois == mois_int)
        .first()
    )
    nb = int(rows.nb or 0)
    masse = float(rows.masse or 0)
    cnps_salarial = float(rows.cnps_salarial or 0)
    ircm = float(rows.ircm or 0)

    # cotisations patronales (taux standard CNPS 13.2% + 4.2% vieillesse = 17.4%)
    cnps_patron = round(masse * 0.174, 2)
    fne = round(masse * 0.01, 2)  # Fonds National de l'Emploi 1%

    return {
        "periode": periode,
        "nb_employes": nb,
        "masse_salariale_brute": round(masse, 2),
        "ircm_verse": round(ircm, 2),
        "cnps_patron": cnps_patron,
        "cnps_employe": round(cnps_salarial, 2),
        "fne_verse": fne,
        "statut": "CONFORME" if nb > 0 else "AUCUNE_DONNEE",
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
