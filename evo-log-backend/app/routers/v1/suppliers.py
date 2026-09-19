"""
Suppliers router - manages supplier/prestataire operations
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, or_
from typing import Optional
from datetime import datetime
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.prestataire import Prestataire, DemandeCotation

router = APIRouter()


@router.get("/")
async def get_suppliers(
    specialite: Optional[str] = Query(None),
    ville: Optional[str] = Query(None),
    est_actif: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Récupère la liste des fournisseurs/prestataires"""
    query = db.query(Prestataire)

    if specialite:
        query = query.filter(Prestataire.specialite == specialite)
    if ville:
        query = query.filter(Prestataire.ville == ville)
    if est_actif is not None:
        query = query.filter(Prestataire.est_actif == est_actif)
    if search:
        query = query.filter(
            or_(
                Prestataire.raison_sociale.ilike(f"%{search}%"),
                Prestataire.code.ilike(f"%{search}%"),
                Prestataire.specialite.ilike(f"%{search}%"),
            )
        )

    total = query.count()
    suppliers = query.order_by(desc(Prestataire.note_globale)).offset(skip).limit(limit).all()

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "data": [
            {
                "id": s.id,
                "code": s.code,
                "raison_sociale": s.raison_sociale,
                "sigle": s.sigle,
                "specialite": s.specialite,
                "tax_id": s.tax_id,
                "rccm": s.rccm,
                "agrement_portuaire": s.agrement_portuaire,
                "est_homologue": s.est_homologue,
                "statut_agrement": s.statut_agrement,
                "ville": s.ville,
                "zone_portuaire": s.zone_portuaire,
                "adresse": s.adresse,
                "contact_nom": s.contact_nom,
                "contact_telephone": s.contact_telephone,
                "contact_email": s.contact_email,
                "telephone_astreinte_24h": s.telephone_astreinte_24h,
                "note_globale": s.note_globale,
                "nb_missions_realisees": s.nb_missions_realisees,
                "taux_ponctualite": s.taux_ponctualite,
                "taux_conformite_qhse": s.taux_conformite_qhse,
                "devise": s.devise,
                "taux_journalier_indicatif": float(s.taux_journalier_indicatif) if s.taux_journalier_indicatif else None,
                "conditions_reglement": s.conditions_reglement,
                "est_actif": s.est_actif,
                "created_at": s.created_at.isoformat() if s.created_at else None,
            }
            for s in suppliers
        ]
    }


@router.get("/stats")
async def get_suppliers_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Statistiques sur les fournisseurs"""
    total = db.query(func.count(Prestataire.id)).scalar() or 0
    actifs = db.query(func.count(Prestataire.id)).filter(Prestataire.est_actif == True).scalar() or 0  # noqa
    homologues = db.query(func.count(Prestataire.id)).filter(Prestataire.est_homologue == True).scalar() or 0  # noqa
    note_moyenne = db.query(func.avg(Prestataire.note_globale)).scalar() or 0.0

    by_specialite = db.query(
        Prestataire.specialite, func.count(Prestataire.id)
    ).group_by(Prestataire.specialite).all()

    cotations_en_attente = db.query(func.count(DemandeCotation.id)).filter(
        DemandeCotation.statut == "EN_ATTENTE"
    ).scalar() or 0

    return {
        "total": total,
        "actifs": actifs,
        "homologues": homologues,
        "note_moyenne": round(float(note_moyenne), 2),
        "cotations_en_attente": cotations_en_attente,
        "par_specialite": [{"specialite": s, "count": c} for s, c in by_specialite],
    }


@router.get("/{supplier_id}")
async def get_supplier(
    supplier_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Récupère un fournisseur spécifique avec ses cotations"""
    supplier = db.query(Prestataire).filter(Prestataire.id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Fournisseur introuvable")

    cotations = db.query(DemandeCotation).filter(
        DemandeCotation.prestataire_id == supplier_id
    ).order_by(desc(DemandeCotation.created_at)).limit(10).all()

    return {
        "id": supplier.id,
        "code": supplier.code,
        "raison_sociale": supplier.raison_sociale,
        "specialite": supplier.specialite,
        "ville": supplier.ville,
        "contact_telephone": supplier.contact_telephone,
        "contact_email": supplier.contact_email,
        "note_globale": supplier.note_globale,
        "nb_missions_realisees": supplier.nb_missions_realisees,
        "est_actif": supplier.est_actif,
        "cotations_recentes": [
            {
                "id": c.id,
                "numero_dossier": c.numero_dossier,
                "titre_besoin": c.titre_besoin,
                "urgence": c.urgence,
                "statut": c.statut,
                "reponse_montant": float(c.reponse_montant) if c.reponse_montant else None,
                "created_at": c.created_at.isoformat() if c.created_at else None,
            }
            for c in cotations
        ]
    }


@router.post("/")
async def create_supplier(
    data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Créer un nouveau fournisseur"""
    # Vérifier l'unicité du code
    existing = db.query(Prestataire).filter(Prestataire.code == data.get("code")).first()
    if existing:
        raise HTTPException(status_code=400, detail="Un fournisseur avec ce code existe déjà")

    supplier = Prestataire(
        code=data.get("code"),
        raison_sociale=data.get("raison_sociale"),
        sigle=data.get("sigle"),
        specialite=data.get("specialite"),
        tax_id=data.get("tax_id"),
        rccm=data.get("rccm"),
        agrement_portuaire=data.get("agrement_portuaire"),
        ville=data.get("ville", "Douala"),
        zone_portuaire=data.get("zone_portuaire"),
        adresse=data.get("adresse"),
        contact_nom=data.get("contact_nom"),
        contact_telephone=data.get("contact_telephone", ""),
        contact_email=data.get("contact_email"),
        telephone_astreinte_24h=data.get("telephone_astreinte_24h"),
        devise=data.get("devise", "XAF"),
        conditions_reglement=data.get("conditions_reglement", "Virement 30j fin de mois"),
        observations=data.get("observations"),
        est_actif=data.get("est_actif", True),
    )
    db.add(supplier)
    db.commit()
    db.refresh(supplier)
    return {"message": "Fournisseur créé avec succès", "id": supplier.id}


@router.put("/{supplier_id}")
async def update_supplier(
    supplier_id: int,
    data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mettre à jour un fournisseur"""
    supplier = db.query(Prestataire).filter(Prestataire.id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Fournisseur introuvable")

    for field in ["raison_sociale", "specialite", "ville", "contact_nom", "contact_telephone",
                  "contact_email", "adresse", "observations", "est_actif", "statut_agrement"]:
        if field in data:
            setattr(supplier, field, data[field])

    db.commit()
    db.refresh(supplier)
    return {"message": "Fournisseur mis à jour", "id": supplier.id}


@router.get("/{supplier_id}/cotations")
async def get_supplier_cotations(
    supplier_id: int,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Récupère les cotations d'un fournisseur"""
    supplier = db.query(Prestataire).filter(Prestataire.id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Fournisseur introuvable")

    cotations = db.query(DemandeCotation).filter(
        DemandeCotation.prestataire_id == supplier_id
    ).order_by(desc(DemandeCotation.created_at)).offset(skip).limit(limit).all()

    return {
        "fournisseur": supplier.raison_sociale,
        "total": db.query(func.count(DemandeCotation.id)).filter(
            DemandeCotation.prestataire_id == supplier_id
        ).scalar(),
        "data": [
            {
                "id": c.id,
                "numero_dossier": c.numero_dossier,
                "titre_besoin": c.titre_besoin,
                "description_besoin": c.description_besoin,
                "urgence": c.urgence,
                "lieu_intervention": c.lieu_intervention,
                "budget_max_estime": float(c.budget_max_estime) if c.budget_max_estime else None,
                "statut": c.statut,
                "reponse_montant": float(c.reponse_montant) if c.reponse_montant else None,
                "commentaires_prestataire": c.commentaires_prestataire,
                "created_at": c.created_at.isoformat() if c.created_at else None,
            }
            for c in cotations
        ]
    }