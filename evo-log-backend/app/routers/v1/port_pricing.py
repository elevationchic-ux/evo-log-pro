"""
Port Pricing router - manages port service pricing using TarifPortuaire model
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, or_
from typing import Optional
from datetime import datetime, date as date_type
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.port_cameroun import TarifPortuaire, TerminalPortuaire, PortCameroun

router = APIRouter()


@router.get("/")
async def get_port_pricing(
    categorie: Optional[str] = Query(None, description="ACconage | Manutention | Stockage | THC"),
    terminal_id: Optional[int] = Query(None),
    actif_seulement: bool = Query(True),
    search: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Récupère les tarifs portuaires (TPC - Tarif Portuaire Cameroun)"""
    query = db.query(TarifPortuaire)

    if actif_seulement:
        query = query.filter(TarifPortuaire.est_actif == True)  # noqa
    if categorie:
        query = query.filter(TarifPortuaire.categorie.ilike(f"%{categorie}%"))
    if terminal_id:
        query = query.filter(TarifPortuaire.terminal_id == terminal_id)
    if search:
        query = query.filter(
            or_(
                TarifPortuaire.designation.ilike(f"%{search}%"),
                TarifPortuaire.code_tarif.ilike(f"%{search}%"),
                TarifPortuaire.categorie.ilike(f"%{search}%"),
            )
        )

    total = query.count()
    tarifs = query.order_by(TarifPortuaire.categorie, TarifPortuaire.designation).offset(skip).limit(limit).all()

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "data": [
            {
                "id": t.id,
                "code_tarif": t.code_tarif,
                "designation": t.designation,
                "categorie": t.categorie,
                "sous_categorie": t.sous_categorie,
                "unite": t.unite,
                "prix_unitaire": float(t.prix_unitaire),
                "devise": t.devise,
                "taux_tva": float(t.taux_tva) if t.taux_tva else 19.25,
                "prix_ttc": round(float(t.prix_unitaire) * (1 + float(t.taux_tva or 19.25) / 100), 2),
                "date_application": t.date_application.isoformat() if t.date_application else None,
                "date_expiration": t.date_expiration.isoformat() if t.date_expiration else None,
                "est_actif": t.est_actif,
                "terminal_id": t.terminal_id,
                "reference_reglementaire": t.reference_reglementaire,
                "notes": t.notes,
            }
            for t in tarifs
        ]
    }


@router.get("/categories")
async def get_pricing_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Récupère les catégories de tarifs disponibles"""
    categories = db.query(
        TarifPortuaire.categorie,
        func.count(TarifPortuaire.id).label("count"),
        func.min(TarifPortuaire.prix_unitaire).label("prix_min"),
        func.max(TarifPortuaire.prix_unitaire).label("prix_max"),
    ).filter(TarifPortuaire.est_actif == True).group_by(TarifPortuaire.categorie).all()  # noqa

    return {
        "categories": [
            {
                "categorie": c.categorie,
                "nb_tarifs": c.count,
                "prix_min": float(c.prix_min) if c.prix_min else 0.0,
                "prix_max": float(c.prix_max) if c.prix_max else 0.0,
            }
            for c in categories
        ]
    }


@router.get("/simuler")
async def simuler_cout(
    categorie: str = Query(...),
    quantite: float = Query(..., gt=0),
    unite: Optional[str] = Query(None),
    terminal_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Simuler le coût d'une prestation portuaire"""
    query = db.query(TarifPortuaire).filter(
        TarifPortuaire.categorie.ilike(f"%{categorie}%"),
        TarifPortuaire.est_actif == True  # noqa
    )
    if unite:
        query = query.filter(TarifPortuaire.unite == unite)
    if terminal_id:
        query = query.filter(TarifPortuaire.terminal_id == terminal_id)

    tarifs = query.all()
    if not tarifs:
        raise HTTPException(status_code=404, detail=f"Aucun tarif trouvé pour la catégorie '{categorie}'")

    simulations = []
    for t in tarifs:
        prix_ht = float(t.prix_unitaire) * quantite
        tva = prix_ht * (float(t.taux_tva or 19.25) / 100)
        simulations.append({
            "code_tarif": t.code_tarif,
            "designation": t.designation,
            "unite": t.unite,
            "quantite": quantite,
            "prix_unitaire_ht": float(t.prix_unitaire),
            "montant_ht": round(prix_ht, 2),
            "taux_tva": float(t.taux_tva or 19.25),
            "montant_tva": round(tva, 2),
            "montant_ttc": round(prix_ht + tva, 2),
            "devise": t.devise,
        })

    return {"categorie": categorie, "quantite": quantite, "simulations": simulations}


@router.get("/{tarif_id}")
async def get_tarif(
    tarif_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Récupère un tarif spécifique"""
    tarif = db.query(TarifPortuaire).filter(TarifPortuaire.id == tarif_id).first()
    if not tarif:
        raise HTTPException(status_code=404, detail="Tarif introuvable")

    return {
        "id": tarif.id,
        "code_tarif": tarif.code_tarif,
        "designation": tarif.designation,
        "categorie": tarif.categorie,
        "sous_categorie": tarif.sous_categorie,
        "unite": tarif.unite,
        "prix_unitaire": float(tarif.prix_unitaire),
        "devise": tarif.devise,
        "taux_tva": float(tarif.taux_tva) if tarif.taux_tva else 19.25,
        "date_application": tarif.date_application.isoformat() if tarif.date_application else None,
        "date_expiration": tarif.date_expiration.isoformat() if tarif.date_expiration else None,
        "est_actif": tarif.est_actif,
        "reference_reglementaire": tarif.reference_reglementaire,
        "notes": tarif.notes,
    }


@router.post("/")
async def create_tarif(
    data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Créer un nouveau tarif portuaire"""
    if not data.get("code_tarif") or not data.get("designation") or not data.get("categorie"):
        raise HTTPException(status_code=400, detail="code_tarif, designation et categorie sont requis")

    existing = db.query(TarifPortuaire).filter(TarifPortuaire.code_tarif == data["code_tarif"]).first()
    if existing:
        raise HTTPException(status_code=400, detail="Ce code tarif existe déjà")

    tarif = TarifPortuaire(
        code_tarif=data["code_tarif"],
        designation=data["designation"],
        categorie=data["categorie"],
        sous_categorie=data.get("sous_categorie"),
        unite=data.get("unite", "TONNE"),
        prix_unitaire=data.get("prix_unitaire", 0),
        devise=data.get("devise", "XAF"),
        date_application=datetime.strptime(data["date_application"], "%Y-%m-%d").date() if data.get("date_application") else datetime.utcnow().date(),
        date_expiration=datetime.strptime(data["date_expiration"], "%Y-%m-%d").date() if data.get("date_expiration") else None,
        taux_tva=data.get("taux_tva", 19.25),
        est_actif=data.get("est_actif", True),
        terminal_id=data.get("terminal_id"),
        notes=data.get("notes"),
        reference_reglementaire=data.get("reference_reglementaire"),
    )
    db.add(tarif)
    db.commit()
    db.refresh(tarif)
    return {"message": "Tarif créé", "id": tarif.id}