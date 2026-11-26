"""Domaine juridique : contrats a valeur documentaire, contentieux, echeances."""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.permissions import require_perm
from app.models.user import User
from app.schemas.juridique import (
    ContratJuridiqueCreate, ContratJuridiqueResponse, ContentieuxJuridiqueCreate,
    ContentieuxJuridiqueResponse, EcheanceContrat,)
from app.services.juridique_service import JuridiqueService


router = APIRouter(tags=["Juridique"])


# --------------------------------------------------------------------------- #
# Contrats
# --------------------------------------------------------------------------- #
@router.post("/contrats", response_model=ContratJuridiqueResponse, status_code=201)
def creer_contrat(
    payload: ContratJuridiqueCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_perm("juridique.contrats.create")),
):
    try:
        return JuridiqueService.creer_contrat(db, payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/contrats", response_model=List[ContratJuridiqueResponse])
def lister_contrats(
    statut: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_perm("juridique.contrats.read")),
):
    return JuridiqueService.lister_contrats(db, statut)


@router.get("/contrats/{contrat_id}", response_model=ContratJuridiqueResponse)
def obtenir_contrat(
    contrat_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_perm("juridique.contrats.read")),
):
    contrat = JuridiqueService.obtenir_contrat(db, contrat_id)
    if not contrat:
        raise HTTPException(status_code=404, detail="Contrat introuvable")
    return contrat


@router.post("/contrats/{contrat_id}/resilier", response_model=ContratJuridiqueResponse)
def resilier_contrat(
    contrat_id: int,
    motif: str = Query(..., min_length=3),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_perm("juridique.contrats.modify")),
):
    try:
        return JuridiqueService.resilier_contrat(db, contrat_id, motif)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


# --------------------------------------------------------------------------- #
# Echeances
# --------------------------------------------------------------------------- #
@router.get("/echeances", response_model=List[EcheanceContrat])
def echeances_contrats(
    jours: int = Query(90, ge=1, le=730),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_perm("juridique.echeances.read")),
):
    return JuridiqueService.echeances_a_surveiller(db, jours)


# --------------------------------------------------------------------------- #
# Contentieux
# --------------------------------------------------------------------------- #
@router.post("/contentieux", response_model=ContentieuxJuridiqueResponse, status_code=201)
def creer_contentieux(
    payload: ContentieuxJuridiqueCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_perm("juridique.contentieux.create")),
):
    try:
        return JuridiqueService.creer_contentieux(db, payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/contentieux", response_model=List[ContentieuxJuridiqueResponse])
def lister_contentieux(
    statut: Optional[str] = Query(None),
    contrat_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_perm("juridique.contentieux.read")),
):
    return JuridiqueService.lister_contentieux(db, statut, contrat_id)


@router.post("/contentieux/{contentieux_id}/cloturer", response_model=ContentieuxJuridiqueResponse)
def cloturer_contentieux(
    contentieux_id: int,
    statut: str = Query(...),
    montant_obtenu: Optional[float] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_perm("juridique.contentieux.modify")),
):
    try:
        return JuridiqueService.cloturer_contentieux(
            db, contentieux_id, statut, montant_obtenu)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
