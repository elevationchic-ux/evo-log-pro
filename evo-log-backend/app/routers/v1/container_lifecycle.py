"""
Container Lifecycle router - manages container lifecycle management using Conteneur, CycleConteneur models
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, or_
from typing import Optional
from datetime import datetime
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.conteneur_cycle import (
    Conteneur, CycleConteneur, DommageConteneur, EmpotageDepotage,
    InspectionConteneur, StatutConteneur, EtatConteneur
)

router = APIRouter()


@router.get("/")
async def get_containers(
    statut: Optional[str] = Query(None),
    type_conteneur: Optional[str] = Query(None),
    proprietaire: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Récupère la liste des conteneurs avec leur cycle de vie"""
    query = db.query(Conteneur)

    if type_conteneur:
        query = query.filter(Conteneur.type_conteneur == type_conteneur)
    if proprietaire:
        query = query.filter(Conteneur.proprietaire.ilike(f"%{proprietaire}%"))
    if search:
        query = query.filter(
            or_(
                Conteneur.numero.ilike(f"%{search}%"),
                Conteneur.proprietaire.ilike(f"%{search}%"),
                Conteneur.compagnie.ilike(f"%{search}%"),
            )
        )

    total = query.count()
    conteneurs = query.order_by(desc(Conteneur.created_at)).offset(skip).limit(limit).all()

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "data": [
            {
                "id": c.id,
                "numero": c.numero,
                "type_conteneur": c.type_conteneur.value if hasattr(c.type_conteneur, "value") else str(c.type_conteneur),
                "taille_pieds": c.taille_pieds,
                "etat": c.etat.value if hasattr(c.etat, "value") else str(c.etat),
                "proprietaire": c.proprietaire,
                "compagnie": c.compagnie,
                "tare_kg": float(c.tare_kg) if c.tare_kg else None,
                "max_payload_kg": float(c.max_payload_kg) if c.max_payload_kg else None,
                "volume_m3": float(c.volume_m3) if c.volume_m3 else None,
                "est_hazardous": c.est_hazardous,
                "date_derniere_inspection": c.date_derniere_inspection.isoformat() if c.date_derniere_inspection else None,
                "prochaine_inspection": c.prochaine_inspection.isoformat() if c.prochaine_inspection else None,
                "created_at": c.created_at.isoformat() if c.created_at else None,
            }
            for c in conteneurs
        ]
    }


@router.get("/stats")
async def get_container_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Statistiques des conteneurs"""
    total = db.query(func.count(Conteneur.id)).scalar() or 0
    hazardous = db.query(func.count(Conteneur.id)).filter(Conteneur.est_hazardous == True).scalar() or 0  # noqa

    par_type = db.query(
        Conteneur.type_conteneur, func.count(Conteneur.id)
    ).group_by(Conteneur.type_conteneur).all()

    par_etat = db.query(
        Conteneur.etat, func.count(Conteneur.id)
    ).group_by(Conteneur.etat).all()

    cycles_actifs = db.query(func.count(CycleConteneur.id)).filter(
        CycleConteneur.statut.in_([StatutConteneur.ARRIVE, StatutConteneur.STOCKE, StatutConteneur.QUAI])
    ).scalar() or 0

    dommages_en_attente = db.query(func.count(DommageConteneur.id)).filter(
        DommageConteneur.statut_reclamation == "en_attente"
    ).scalar() or 0

    return {
        "total_conteneurs": total,
        "hazardous": hazardous,
        "cycles_actifs": cycles_actifs,
        "dommages_en_attente": dommages_en_attente,
        "par_type": [
            {"type": t.value if hasattr(t, "value") else str(t), "count": c}
            for t, c in par_type
        ],
        "par_etat": [
            {"etat": e.value if hasattr(e, "value") else str(e), "count": c}
            for e, c in par_etat
        ],
    }


@router.get("/{conteneur_id}")
async def get_container(
    conteneur_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Récupère un conteneur avec son historique de cycles"""
    conteneur = db.query(Conteneur).filter(Conteneur.id == conteneur_id).first()
    if not conteneur:
        raise HTTPException(status_code=404, detail="Conteneur introuvable")

    cycles = db.query(CycleConteneur).filter(
        CycleConteneur.conteneur_id == conteneur_id
    ).order_by(desc(CycleConteneur.date_arrivee_navire)).limit(10).all()

    dommages = db.query(DommageConteneur).filter(
        DommageConteneur.conteneur_id == conteneur_id
    ).all()

    return {
        "id": conteneur.id,
        "numero": conteneur.numero,
        "type_conteneur": conteneur.type_conteneur.value if hasattr(conteneur.type_conteneur, "value") else str(conteneur.type_conteneur),
        "taille_pieds": conteneur.taille_pieds,
        "etat": conteneur.etat.value if hasattr(conteneur.etat, "value") else str(conteneur.etat),
        "proprietaire": conteneur.proprietaire,
        "compagnie": conteneur.compagnie,
        "tare_kg": float(conteneur.tare_kg) if conteneur.tare_kg else None,
        "est_hazardous": conteneur.est_hazardous,
        "cycles": [
            {
                "id": cy.id,
                "voyage": cy.voyage,
                "statut": cy.statut.value if hasattr(cy.statut, "value") else str(cy.statut),
                "localisation": cy.localisation,
                "date_arrivee": cy.date_arrivee_navire.isoformat() if cy.date_arrivee_navire else None,
                "date_sortie": cy.date_sortie.isoformat() if cy.date_sortie else None,
                "temps_cycle_heures": float(cy.temps_cycle_heures) if cy.temps_cycle_heures else None,
            }
            for cy in cycles
        ],
        "dommages": [
            {
                "id": d.id,
                "type_dommage": d.type_dommage,
                "gravite": d.gravite,
                "description": d.description,
                "statut_reclamation": d.statut_reclamation,
                "cout_reparation": float(d.cout_reparation) if d.cout_reparation else None,
            }
            for d in dommages
        ],
    }


@router.post("/")
async def create_container(
    data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Enregistrer un nouveau conteneur"""
    if not data.get("numero") or not data.get("type_conteneur"):
        raise HTTPException(status_code=400, detail="numero et type_conteneur sont requis")

    existing = db.query(Conteneur).filter(Conteneur.numero == data["numero"]).first()
    if existing:
        raise HTTPException(status_code=400, detail="Ce numéro de conteneur existe déjà")

    conteneur = Conteneur(
        numero=data["numero"],
        type_conteneur=data["type_conteneur"],
        taille_pieds=data.get("taille_pieds", 20),
        etat=data.get("etat", "clean"),
        proprietaire=data.get("proprietaire"),
        compagnie=data.get("compagnie"),
        tare_kg=data.get("tare_kg"),
        max_payload_kg=data.get("max_payload_kg"),
        volume_m3=data.get("volume_m3"),
        est_hazardous=data.get("est_hazardous", False),
        classe_hazard=data.get("classe_hazard"),
        notes=data.get("notes"),
    )
    db.add(conteneur)
    db.commit()
    db.refresh(conteneur)
    return {"message": "Conteneur créé", "id": conteneur.id, "numero": conteneur.numero}


@router.post("/{conteneur_id}/cycle")
async def create_cycle(
    conteneur_id: int,
    data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Créer un cycle de vie pour un conteneur"""
    conteneur = db.query(Conteneur).filter(Conteneur.id == conteneur_id).first()
    if not conteneur:
        raise HTTPException(status_code=404, detail="Conteneur introuvable")

    cycle = CycleConteneur(
        conteneur_id=conteneur_id,
        voyage=data.get("voyage"),
        statut=data.get("statut", StatutConteneur.ARRIVE),
        localisation=data.get("localisation"),
        operateur_dechargement=data.get("operateur_dechargement"),
        operateur_manutention=data.get("operateur_manutention"),
    )
    db.add(cycle)
    db.commit()
    db.refresh(cycle)
    return {"message": "Cycle créé", "id": cycle.id}