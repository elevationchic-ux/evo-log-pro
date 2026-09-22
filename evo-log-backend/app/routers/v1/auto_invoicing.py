"""
Auto Invoicing router - manages automatic OHADA invoicing from FactureNew model
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
from typing import Optional
from datetime import datetime, date as date_type
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.finance_ohada import FactureNew, LigneFactureOHADA, TVADeclarable, Reglement

router = APIRouter()


@router.get("/")
async def get_auto_invoices(
    type_facture: Optional[str] = Query(None, description="vente | achat | avoir | prestation"),
    statut: Optional[str] = Query(None),
    periode: Optional[str] = Query(None, description="Format: YYYY-MM"),
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Récupère les factures OHADA avec facturation automatique"""
    query = db.query(FactureNew)

    if type_facture:
        query = query.filter(FactureNew.type_facture == type_facture)
    if statut:
        query = query.filter(FactureNew.statut == statut)
    if periode:
        try:
            year, month = periode.split("-")
            from sqlalchemy import extract
            query = query.filter(
                extract("year", FactureNew.date_emission) == int(year),
                extract("month", FactureNew.date_emission) == int(month)
            )
        except ValueError:
            pass

    total = query.count()
    factures = query.order_by(desc(FactureNew.date_emission)).offset(skip).limit(limit).all()

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "data": [
            {
                "id": f.id,
                "numero_facture": f.numero_facture,
                "type_facture": f.type_facture,
                "date_emission": f.date_emission.isoformat() if f.date_emission else None,
                "date_echeance": f.date_echeance.isoformat() if f.date_echeance else None,
                "montant_ht": float(f.montant_ht) if f.montant_ht else 0.0,
                "taux_tva": float(f.taux_tva) if f.taux_tva else 19.25,
                "montant_tva": float(f.montant_tva) if f.montant_tva else 0.0,
                "montant_ttc": float(f.montant_ttc) if f.montant_ttc else 0.0,
                "devise": f.devise,
                "statut": f.statut,
                "comptabilise": f.comptabilise,
                "solde_restant": float(f.solde_restant) if f.solde_restant else None,
            }
            for f in factures
        ]
    }


@router.get("/stats")
async def get_invoicing_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Statistiques de facturation OHADA"""
    now = datetime.utcnow()
    from sqlalchemy import extract

    total_factures = db.query(func.count(FactureNew.id)).scalar() or 0
    ca_emis = db.query(func.sum(FactureNew.montant_ttc)).filter(
        FactureNew.type_facture == "vente",
        FactureNew.statut != "annulee",
        extract("year", FactureNew.date_emission) == now.year
    ).scalar() or 0.0

    factures_impayees = db.query(func.count(FactureNew.id)).filter(
        FactureNew.statut.in_(["emise", "brouillon"]),
        FactureNew.date_echeance < now.date()
    ).scalar() or 0

    montant_impaye = db.query(func.sum(FactureNew.solde_restant)).filter(
        FactureNew.statut.in_(["emise", "payee_partiel"])
    ).scalar() or 0.0

    tva_a_payer = db.query(func.sum(TVADeclarable.tva_a_payer)).filter(
        TVADeclarable.statut == "due"
    ).scalar() or 0.0

    return {
        "total_factures": total_factures,
        "ca_annee": float(ca_emis),
        "factures_impayees": factures_impayees,
        "montant_impaye": float(montant_impaye),
        "tva_a_payer": float(tva_a_payer),
    }


@router.get("/{facture_id}")
async def get_invoice(
    facture_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Récupère une facture avec ses lignes"""
    facture = db.query(FactureNew).filter(FactureNew.id == facture_id).first()
    if not facture:
        raise HTTPException(status_code=404, detail="Facture introuvable")

    lignes = db.query(LigneFactureOHADA).filter(LigneFactureOHADA.facture_id == facture_id).all()

    return {
        "id": facture.id,
        "numero_facture": facture.numero_facture,
        "type_facture": facture.type_facture,
        "date_emission": facture.date_emission.isoformat() if facture.date_emission else None,
        "date_echeance": facture.date_echeance.isoformat() if facture.date_echeance else None,
        "montant_ht": float(facture.montant_ht),
        "taux_tva": float(facture.taux_tva) if facture.taux_tva else 19.25,
        "montant_tva": float(facture.montant_tva) if facture.montant_tva else 0.0,
        "montant_ttc": float(facture.montant_ttc),
        "devise": facture.devise,
        "statut": facture.statut,
        "comptabilise": facture.comptabilise,
        "notes": facture.notes,
        "lignes": [
            {
                "id": l.id,
                "designation": l.designation,
                "quantite": float(l.quantite),
                "unite": l.unite,
                "prix_unitaire_ht": float(l.prix_unitaire_ht),
                "montant_ht": float(l.montant_ht),
                "taux_tva": float(l.taux_tva) if l.taux_tva else 19.25,
                "montant_ttc": float(l.montant_ttc),
            }
            for l in lignes
        ]
    }


@router.post("/")
async def create_invoice(
    data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Créer une facture OHADA"""
    import uuid
    numero = f"FAC-{datetime.utcnow().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"

    montant_ht = float(data.get("montant_ht", 0))
    taux_tva = float(data.get("taux_tva", 19.25))
    montant_tva = montant_ht * (taux_tva / 100)
    montant_ttc = montant_ht + montant_tva

    facture = FactureNew(
        numero_facture=numero,
        client_id=data.get("client_id"),
        type_facture=data.get("type_facture", "vente"),
        date_emission=datetime.strptime(data["date_emission"], "%Y-%m-%d").date() if data.get("date_emission") else datetime.utcnow().date(),
        date_echeance=datetime.strptime(data["date_echeance"], "%Y-%m-%d").date() if data.get("date_echeance") else None,
        montant_ht=montant_ht,
        taux_tva=taux_tva,
        montant_tva=montant_tva,
        montant_ttc=montant_ttc,
        devise=data.get("devise", "XAF"),
        statut=data.get("statut", "brouillon"),
        conditions_paiement=data.get("conditions_paiement"),
        notes=data.get("notes"),
        solde_restant=montant_ttc,
    )
    db.add(facture)
    db.commit()
    db.refresh(facture)
    return {"message": "Facture créée", "id": facture.id, "numero_facture": numero}


@router.post("/{facture_id}/emettre")
async def emettre_facture(
    facture_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Émettre une facture (passer de brouillon à émise)"""
    facture = db.query(FactureNew).filter(FactureNew.id == facture_id).first()
    if not facture:
        raise HTTPException(status_code=404, detail="Facture introuvable")
    if facture.statut != "brouillon":
        raise HTTPException(status_code=400, detail=f"Impossible d'émettre une facture au statut '{facture.statut}'")

    facture.statut = "emise"
    db.commit()
    return {"message": "Facture émise avec succès", "id": facture_id}


@router.get("/tva/declarations")
async def get_tva_declarations(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Récupère les déclarations TVA"""
    declarations = db.query(TVADeclarable).order_by(desc(TVADeclarable.periode)).offset(skip).limit(limit).all()
    total = db.query(func.count(TVADeclarable.id)).scalar() or 0

    return {
        "total": total,
        "data": [
            {
                "id": d.id,
                "numero_declaration": d.numero_declaration,
                "periode": d.periode,
                "date_declaration": d.date_declaration.isoformat() if d.date_declaration else None,
                "date_limite": d.date_limite.isoformat() if d.date_limite else None,
                "tva_collectee": float(d.tva_collectee) if d.tva_collectee else 0.0,
                "tva_deductible": float(d.tva_deductible) if d.tva_deductible else 0.0,
                "tva_a_payer": float(d.tva_a_payer) if d.tva_a_payer else 0.0,
                "statut": d.statut.value if hasattr(d.statut, "value") else str(d.statut),
            }
            for d in declarations
        ]
    }