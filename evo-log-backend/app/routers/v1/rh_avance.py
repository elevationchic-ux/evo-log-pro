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
    """Enregistre reellement l'offre en base (table offres_emploi)."""
    try:
        offre = RecrutementService.creer_offre_emploi(
            db=db,
            titre=payload.titre,
            departement=payload.departement,
            description=payload.description,
            type_contrat=payload.type_contrat,
            competences_requises=payload.competences_requises,
            salaire_min=payload.salaire_min,
            salaire_max=payload.salaire_max,
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Erreur enregistrement offre: {str(e)}")
    return {
        "id": offre.id,
        "titre": offre.titre,
        "departement": offre.departement,
        "type_contrat": offre.type_contrat,
        "statut": offre.statut,
        "message": "Offre d'emploi creee et enregistree"
    }


@router.post("/recrutement/candidatures", summary="Enregistrer une candidature")
def enregistrer_candidature(payload: CandidatureCreate, db: Session = Depends(get_db)):
    """Enregistre reellement la candidature (table candidatures). L'offre ciblee
    doit exister, sinon 404 honnete."""
    try:
        cand = RecrutementService.enregistrer_candidature(
            db=db,
            offre_id=payload.offre_id,
            candidat_nom=payload.candidat_nom,
            email=payload.email,
            telephone=payload.telephone,
            cv_url=payload.cv_url,
            experience_annees=payload.experience_annees,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return {
        "id": cand.id,
        "offre_id": cand.offre_id,
        "candidat_nom": cand.candidat_nom,
        "statut": cand.statut,
        "message": "Candidature enregistree"
    }


@router.patch("/recrutement/candidatures/{candidature_id}", summary="Traiter une candidature")
def traiter_candidature(
    candidature_id: int,
    decision: str = Query(..., description="PRESELECTIONNE | ENTREVUE | REFUSEE | EMBAUCHE"),
    notes: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Met a jour reellement le statut de la candidature en base."""
    try:
        cand = RecrutementService.traiter_candidature(db, candidature_id, decision, notes)
    except ValueError as e:
        code = status.HTTP_404_NOT_FOUND if "introuvable" in str(e) else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=code, detail=str(e))
    return {
        "id": cand.id,
        "statut": cand.statut,
        "date_decision": cand.date_decision.isoformat() if cand.date_decision else None,
        "message": f"Candidature {cand.id} traitee : {cand.statut}"
    }


# --- ENDPOINTS FORMATION ---
@router.post("/formations/plans", summary="Créer une session de formation")
def creer_plan_formation(payload: FormationPlanCreate, db: Session = Depends(get_db)):
    """Enregistre reellement la session (table formations). La categorie est
    integree a la description, faute de colonne dedicatee en schema."""
    from app.models.rh import Formation

    if payload.date_fin < payload.date_debut:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="date_fin anterieure a date_debut")
    description = f"[{payload.categorie}] {payload.description}" if getattr(
        payload, "description", None) else f"Categorie : {payload.categorie}"
    f = Formation(
        titre=payload.titre,
        description=description,
        date_debut=payload.date_debut,
        date_fin=payload.date_fin,
        duree_heures=payload.duree_heures,
        cout=payload.cout_par_personne,
        formateur=payload.formateur_ou_organisme,
        statut="planifiee",
    )
    db.add(f)
    db.commit()
    db.refresh(f)
    return {
        "id": f.id,
        "titre": f.titre,
        "categorie": payload.categorie,
        "duree_heures": f.duree_heures,
        "statut": "PROGRAMMEE",
        "statut_base": f.statut,
        "message": "Session de formation creee et enregistree"
    }


@router.get("/formations/plan-annuel", summary="Bilan réel du plan de formation annuel")
def plan_formation_annuel(exercice_id: int = Query(...), db: Session = Depends(get_db)):
    """Agregation reelle depuis la table formations (0 honnete sans donnees)."""
    return FormationService.plan_formation_annuel(db=db, exercice_id=exercice_id)


@router.post("/formations/inscrire", summary="Inscrire des collaborateurs à une formation")
def inscrire_collaborateurs(payload: InscriptionFormationRequest, db: Session = Depends(get_db)):
    """Inscriptions REELLES en table participations_formation. La formation et
    chaque employe doivent exister ; doublons et identifiants invalides sont
    signales honnetement, sans compteurs gonfles."""
    from app.models.rh import Formation, ParticipationFormation

    formation = db.query(Formation).filter(Formation.id == payload.formation_id).first()
    if not formation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Formation {payload.formation_id} introuvable")

    inscrits, deja_inscrits, invalides = 0, [], []
    for employe_id in payload.employe_ids:
        try:
            FormationService.inscrire_formation(db, employe_id, formation.id)
            inscrits += 1
        except RuntimeError:
            deja_inscrits.append(employe_id)
        except ValueError:
            existant = (
                db.query(ParticipationFormation.id)
                .filter(
                    ParticipationFormation.formation_id == formation.id,
                    ParticipationFormation.employe_id == employe_id,
                )
                .first()
            )
            (deja_inscrits if existant else invalides).append(employe_id)

    return {
        "formation_id": formation.id,
        "inscrits_count": inscrits,
        "deja_inscrits": deja_inscrits,
        "employes_invalides": invalides,
        "statut": "CONFIRME" if inscrits else "AUCUNE_INSCRIPTION",
        "message": f"{inscrits} inscription(s) reelle(s) en base"
    }
