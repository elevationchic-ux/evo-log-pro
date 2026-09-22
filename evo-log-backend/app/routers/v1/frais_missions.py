"""
Router FastAPI pour la gestion des Frais de Mission et Avances Collaborateurs
Architecture 100% connectée à la base de données PostgreSQL
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.core.database import get_db
from app.models.frais_mission import FraisMission, AvanceMission

router = APIRouter(prefix="/frais-missions", tags=["Notes de Frais & Avances Missions"])


class FraisCreate(BaseModel):
    user_id: Optional[int] = None
    nom_collaborateur: Optional[str] = "Collaborateur"
    mission_id: Optional[int] = None
    titre_mission: Optional[str] = None
    type_frais: str = "DIVERS"
    montant: float
    devise: str = "XAF"
    fournisseur: Optional[str] = None
    ville_lieu: Optional[str] = None
    justificatif_url: Optional[str] = None
    numero_recu: Optional[str] = None
    commentaire: Optional[str] = None


class AvanceCreate(BaseModel):
    user_id: Optional[int] = None
    nom_collaborateur: Optional[str] = "Collaborateur"
    titre_mission: str
    corridor_destination: Optional[str] = None
    montant_demande: float
    devise: str = "XAF"
    motif: Optional[str] = None


class ValidationRequest(BaseModel):
    action: str  # VALIDER ou REJETER
    valide_par_nom: str = "Manager"
    motif_rejet: Optional[str] = None


@router.get("")
def list_frais(
    statut: Optional[str] = None,
    user_id: Optional[int] = None,
    type_frais: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Récupère la liste des notes de frais avec filtres"""
    query = db.query(FraisMission)
    if statut:
        query = query.filter(FraisMission.statut == statut)
    if user_id:
        query = query.filter(FraisMission.user_id == user_id)
    if type_frais:
        query = query.filter(FraisMission.type_frais == type_frais)
    
    items = query.order_by(FraisMission.created_at.desc()).limit(limit).all()
    return {"total": len(items), "items": items}


@router.post("", status_code=201)
def create_frais(payload: FraisCreate, db: Session = Depends(get_db)):
    """Soumet une nouvelle note de frais"""
    frais = FraisMission(
        user_id=payload.user_id,
        nom_collaborateur=payload.nom_collaborateur,
        mission_id=payload.mission_id,
        titre_mission=payload.titre_mission,
        type_frais=payload.type_frais,
        montant=payload.montant,
        devise=payload.devise,
        fournisseur=payload.fournisseur,
        ville_lieu=payload.ville_lieu,
        justificatif_url=payload.justificatif_url,
        numero_recu=payload.numero_recu,
        commentaire=payload.commentaire,
        statut="SOUMIS",
    )
    db.add(frais)
    db.commit()
    db.refresh(frais)
    return {"message": "Note de frais enregistrée avec succès", "frais": frais}


@router.post("/{frais_id}/validate")
def validate_frais(frais_id: int, payload: ValidationRequest, db: Session = Depends(get_db)):
    """Valide ou rejette une note de frais par le manager ou la comptabilité"""
    frais = db.query(FraisMission).filter(FraisMission.id == frais_id).first()
    if not frais:
        raise HTTPException(status_code=404, detail="Note de frais introuvable")

    if payload.action.upper() == "VALIDER":
        frais.statut = "VALIDE"
        frais.valide_par_nom = payload.valide_par_nom
        frais.date_validation = datetime.utcnow()
    elif payload.action.upper() == "REJETER":
        frais.statut = "REJETE"
        frais.valide_par_nom = payload.valide_par_nom
        frais.motif_rejet = payload.motif_rejet
        frais.date_validation = datetime.utcnow()
    else:
        raise HTTPException(status_code=400, detail="Action non reconnue (utiliser VALIDER ou REJETER)")

    db.commit()
    db.refresh(frais)
    return {"message": f"Note de frais {frais.statut}", "frais": frais}


@router.get("/avances")
def list_avances(
    statut: Optional[str] = None,
    user_id: Optional[int] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Récupère les demandes d'avances de mission"""
    query = db.query(AvanceMission)
    if statut:
        query = query.filter(AvanceMission.statut == statut)
    if user_id:
        query = query.filter(AvanceMission.user_id == user_id)
    items = query.order_by(AvanceMission.created_at.desc()).limit(limit).all()
    return {"total": len(items), "items": items}


@router.post("/avances", status_code=201)
def create_avance(payload: AvanceCreate, db: Session = Depends(get_db)):
    """Crée une demande d'avance sur mission"""
    avance = AvanceMission(
        user_id=payload.user_id,
        nom_collaborateur=payload.nom_collaborateur,
        titre_mission=payload.titre_mission,
        corridor_destination=payload.corridor_destination,
        montant_demande=payload.montant_demande,
        montant_accorde=payload.montant_demande,  # Par défaut montant demandé en attente d'approbation
        devise=payload.devise,
        motif=payload.motif,
        statut="DEMANDEE",
    )
    db.add(avance)
    db.commit()
    db.refresh(avance)
    return {"message": "Demande d'avance enregistrée", "avance": avance}


@router.get("/stats")
def get_stats(user_id: Optional[int] = None, db: Session = Depends(get_db)):
    """Statistiques financières des frais et avances"""
    query_frais = db.query(FraisMission)
    query_avances = db.query(AvanceMission)
    if user_id:
        query_frais = query_frais.filter(FraisMission.user_id == user_id)
        query_avances = query_avances.filter(AvanceMission.user_id == user_id)

    all_frais = query_frais.all()
    all_avances = query_avances.all()

    total_engage = sum(f.montant for f in all_frais)
    total_valide = sum(f.montant for f in all_frais if f.statut == "VALIDE")
    total_en_attente = sum(f.montant for f in all_frais if f.statut == "SOUMIS")
    total_avances_accordees = sum(a.montant_accorde or 0 for a in all_avances if a.statut == "ACCORDEE")

    solde_a_regulariser = total_avances_accordees - total_valide

    return {
        "nb_frais_total": len(all_frais),
        "total_engage_xaf": total_engage,
        "total_valide_xaf": total_valide,
        "total_en_attente_xaf": total_en_attente,
        "total_avances_accordees_xaf": total_avances_accordees,
        "solde_a_regulariser_xaf": solde_a_regulariser,
    }
