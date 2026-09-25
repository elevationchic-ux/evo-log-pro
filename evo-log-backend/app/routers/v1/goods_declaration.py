"""
Goods Declaration (Déclaration Unique de Marchandises - DUM / CAMCIS) router
Gestion complète des déclarations en douane de marchandises selon le code douanier CEMAC/Cameroun
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, or_
from typing import Optional, List
from datetime import datetime, date
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.douane_cameroun import DUM, BV, TauxReferenceBEAC

router = APIRouter()


class DUMCreate(BaseModel):
    dossier_transit_id: Optional[int] = None
    type_operation: str = "import"  # import, export, transit
    regime_douanier: str = "Mise à la consommation"
    bureau_douane: str = "DLA-PORT VII"
    date_depot: Optional[date] = None
    declarant: str
    numero_agrement: Optional[str] = None
    importateur: str
    numero_contribuable: Optional[str] = None
    marchandise: str
    nomenclature: Optional[str] = None  # Code SH
    poids_brut: Optional[float] = None
    poids_net: Optional[float] = None
    nombre_colis: Optional[int] = None
    valeur_fob: Optional[float] = None
    valeur_caf: Optional[float] = None
    devise: Optional[str] = "USD"
    taux_change: Optional[float] = 615.0
    notes: Optional[str] = None


class DUMUpdate(BaseModel):
    type_operation: Optional[str] = None
    regime_douanier: Optional[str] = None
    bureau_douane: Optional[str] = None
    declarant: Optional[str] = None
    importateur: Optional[str] = None
    marchandise: Optional[str] = None
    nomenclature: Optional[str] = None
    poids_brut: Optional[float] = None
    poids_net: Optional[float] = None
    valeur_caf: Optional[float] = None
    statut: Optional[str] = None
    notes: Optional[str] = None


@router.get("/")
async def get_goods_declarations(
    type_operation: Optional[str] = Query(None),
    regime: Optional[str] = Query(None),
    statut: Optional[str] = Query(None),
    bureau: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Liste les déclarations uniques de marchandises (DUM)"""
    query = db.query(DUM)

    if type_operation:
        query = query.filter(DUM.type_operation == type_operation)
    if regime:
        query = query.filter(DUM.regime_douanier.ilike(f"%{regime}%"))
    if statut:
        query = query.filter(DUM.statut == statut)
    if bureau:
        query = query.filter(DUM.bureau_douane.ilike(f"%{bureau}%"))
    if search:
        query = query.filter(
            or_(
                DUM.numero_dum.ilike(f"%{search}%"),
                DUM.declarant.ilike(f"%{search}%"),
                DUM.importateur.ilike(f"%{search}%"),
                DUM.marchandise.ilike(f"%{search}%"),
                DUM.nomenclature.ilike(f"%{search}%"),
            )
        )

    total = query.count()
    items = query.order_by(desc(DUM.date_depot), desc(DUM.id)).offset(skip).limit(limit).all()

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": [
            {
                "id": d.id,
                "numero_dum": d.numero_dum,
                "dossier_transit_id": d.dossier_transit_id,
                "type_operation": d.type_operation,
                "regime_douanier": d.regime_douanier,
                "bureau_douane": d.bureau_douane,
                "date_depot": d.date_depot.isoformat() if d.date_depot else None,
                "declarant": d.declarant,
                "importateur": d.importateur,
                "marchandise": d.marchandise,
                "nomenclature": d.nomenclature,
                "poids_brut": float(d.poids_brut) if d.poids_brut else None,
                "valeur_caf": float(d.valeur_caf) if d.valeur_caf else None,
                "valeur_douane_xaf": float(d.valeur_douane_xaf) if d.valeur_douane_xaf else None,
                "droits_douane": float(d.droits_douane) if d.droits_douane else None,
                "tva": float(d.tva) if d.tva else None,
                "montant_total": float(d.montant_total) if d.montant_total else None,
                "statut": d.statut,
                "reference_sydonia": d.reference_sydonia,
                "date_validation": d.date_validation.isoformat() if d.date_validation else None
            }
            for d in items
        ]
    }


@router.get("/stats")
async def get_goods_declarations_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Statistiques consolidées des déclarations en douane"""
    total_dum = db.query(func.count(DUM.id)).scalar() or 0
    en_attente = db.query(func.count(DUM.id)).filter(DUM.statut == "en_attente").scalar() or 0
    validees = db.query(func.count(DUM.id)).filter(DUM.statut == "valide").scalar() or 0
    liquidees = db.query(func.count(DUM.id)).filter(DUM.statut == "liquidé").scalar() or 0

    total_valeur_douane = db.query(func.sum(DUM.valeur_douane_xaf)).scalar() or 0
    total_droits = db.query(func.sum(DUM.droits_douane)).scalar() or 0
    total_tva = db.query(func.sum(DUM.tva)).scalar() or 0
    total_recettes = db.query(func.sum(DUM.montant_total)).scalar() or 0

    return {
        "total_declarations": total_dum,
        "en_attente": en_attente,
        "validees": validees,
        "liquidees": liquidees,
        "valeur_douane_totale_xaf": float(total_valeur_douane),
        "droits_douane_total_xaf": float(total_droits),
        "tva_douaniere_total_xaf": float(total_tva),
        "recettes_fiscales_totales_xaf": float(total_recettes)
    }


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_goods_declaration(
    payload: DUMCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Enregistre une nouvelle déclaration de marchandises DUM avec liquidation fiscale prédictive.

    La liquidation est calculée LOCALEMENT (estimation) : le document n'est ni
    déposé ni acquitté auprès de la DGD/SYDONIA  aucune référence SYDONIA
    n'est générée ici (la référence réelle vient du retour ASYCUDA du déclarant).
    """
    today_str = datetime.now().strftime("%Y%m%d")
    count_today = db.query(func.count(DUM.id)).scalar() or 0
    numero_dum = f"DUM-{today_str}-{count_today + 1:04d}"

    # Taux de change : celui saisi par le déclarant, sinon la référence BEAC
    # enregistrée en base. Jamais de taux inventé (l'ancien fallback 615.0
    # différait de ~6 % de la parité officielle 655,957 et faussait la liquidation).
    taux_change = payload.taux_change
    if not taux_change:
        derniere_ref = (
            db.query(TauxReferenceBEAC)
            .filter(TauxReferenceBEAC.devise == (payload.devise or "USD"))
            .order_by(desc(TauxReferenceBEAC.date_application))
            .first()
        )
        if derniere_ref and derniere_ref.taux_moyen:
            taux_change = float(derniere_ref.taux_moyen)
        else:
            raise HTTPException(
                status_code=400,
                detail=(
                    "taux_change obligatoire : aucun taux BEAC de référence enregistré "
                    "pour cette devise. Renseignez le taux officiel du jour (table "
                    "taux_reference_beac) ou passez taux_change dans la requête."
                ),
            )

    # Calcul de la valeur en douane et des taxes
    val_caf = payload.valeur_caf or (payload.valeur_fob or 0) * 1.15
    valeur_douane_xaf = val_caf * taux_change

    # Taux standard Cameroun: TEC 20% + TVA 19.25% + CAC 10% sur droits
    # NB : estimation  la catégorie TEC réelle dépend de la position tarifaire du code SH.
    droits_douane = valeur_douane_xaf * 0.20
    cac = droits_douane * 0.10
    assiette_tva = valeur_douane_xaf + droits_douane
    tva = assiette_tva * 0.1925
    timbre = 5000.0
    montant_total = droits_douane + cac + tva + timbre

    dum = DUM(
        numero_dum=numero_dum,
        dossier_transit_id=payload.dossier_transit_id,
        type_operation=payload.type_operation,
        regime_douanier=payload.regime_douanier,
        bureau_douane=payload.bureau_douane,
        date_depot=payload.date_depot or date.today(),
        declarant=payload.declarant,
        numero_agrement=payload.numero_agrement,
        importateur=payload.importateur,
        numero_contribuable=payload.numero_contribuable,
        marchandise=payload.marchandise,
        nomenclature=payload.nomenclature,
        poids_brut=payload.poids_brut,
        poids_net=payload.poids_net,
        nombre_colis=payload.nombre_colis,
        valeur_fob=payload.valeur_fob,
        valeur_caf=val_caf,
        devise=payload.devise or "USD",
        taux_change=taux_change,
        valeur_douane_xaf=valeur_douane_xaf,
        droits_douane=droits_douane,
        centimes_additionnels=cac,
        tva=tva,
        timbre_usage=timbre,
        montant_total=montant_total,
        statut="en_attente",
        reference_sydonia=None,  # remplie au retour réel ASYCUDA/SYDONIA par le déclarant
        notes=payload.notes
    )

    db.add(dum)
    db.commit()
    db.refresh(dum)

    return {
        "message": "DUM enregistrée localement avec une liquidation ESTIMATIVE (non télétransmise à SYDONIA)",
        "id": dum.id,
        "numero_dum": dum.numero_dum,
        "estimation": True,
        "valeur_douane_xaf": float(dum.valeur_douane_xaf),
        "montant_total_taxes": float(dum.montant_total)
    }


@router.get("/{id}")
async def get_goods_declaration(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Détail d'une déclaration DUM et validations associées"""
    dum = db.query(DUM).filter(DUM.id == id).first()
    if not dum:
        raise HTTPException(status_code=404, detail=f"Déclaration DUM #{id} non trouvée")

    # Validation éventuelle
    bvs = db.query(BV).filter(BV.dum_id == dum.id).all()

    return {
        "id": dum.id,
        "numero_dum": dum.numero_dum,
        "dossier_transit_id": dum.dossier_transit_id,
        "type_operation": dum.type_operation,
        "regime_douanier": dum.regime_douanier,
        "bureau_douane": dum.bureau_douane,
        "date_depot": dum.date_depot.isoformat() if dum.date_depot else None,
        "declarant": dum.declarant,
        "numero_agrement": dum.numero_agrement,
        "importateur": dum.importateur,
        "numero_contribuable": dum.numero_contribuable,
        "marchandise": dum.marchandise,
        "nomenclature": dum.nomenclature,
        "poids_brut": float(dum.poids_brut) if dum.poids_brut else None,
        "poids_net": float(dum.poids_net) if dum.poids_net else None,
        "nombre_colis": dum.nombre_colis,
        "valeur_fob": float(dum.valeur_fob) if dum.valeur_fob else None,
        "valeur_caf": float(dum.valeur_caf) if dum.valeur_caf else None,
        "devise": dum.devise,
        "taux_change": float(dum.taux_change) if dum.taux_change else None,
        "valeur_douane_xaf": float(dum.valeur_douane_xaf) if dum.valeur_douane_xaf else None,
        "droits_douane": float(dum.droits_douane) if dum.droits_douane else None,
        "centimes_additionnels": float(dum.centimes_additionnels) if dum.centimes_additionnels else None,
        "tva": float(dum.tva) if dum.tva else None,
        "timbre_usage": float(dum.timbre_usage) if dum.timbre_usage else None,
        "montant_total": float(dum.montant_total) if dum.montant_total else None,
        "statut": dum.statut,
        "date_validation": dum.date_validation.isoformat() if dum.date_validation else None,
        "date_liquidation": dum.date_liquidation.isoformat() if dum.date_liquidation else None,
        "agent_douane": dum.agent_douane,
        "reference_sydonia": dum.reference_sydonia,
        "notes": dum.notes,
        "validations": [
            {
                "id": bv.id,
                "numero_bv": bv.numero_bv,
                "validateur": bv.validateur,
                "resultat": bv.resultat,
                "date_validation": bv.date_validation.isoformat() if bv.date_validation else None
            }
            for bv in bvs
        ]
    }


@router.put("/{id}")
async def update_goods_declaration(
    id: int,
    payload: DUMUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Met à jour les données d'une déclaration DUM"""
    dum = db.query(DUM).filter(DUM.id == id).first()
    if not dum:
        raise HTTPException(status_code=404, detail=f"Déclaration DUM #{id} non trouvée")

    data = payload.dict(exclude_unset=True)
    for field, value in data.items():
        setattr(dum, field, value)

    dum.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(dum)

    return {"message": "Déclaration mise à jour avec succès", "id": dum.id}


@router.post("/{id}/liquidate")
async def liquidate_goods_declaration(
    id: int,
    agent_douane: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Liquide la déclaration en douane et passe le statut à 'liquidé'"""
    dum = db.query(DUM).filter(DUM.id == id).first()
    if not dum:
        raise HTTPException(status_code=404, detail=f"Déclaration DUM #{id} non trouvée")

    dum.statut = "liquidé"
    dum.date_liquidation = date.today()
    dum.agent_douane = agent_douane or current_user.full_name or current_user.email
    dum.updated_at = datetime.utcnow()

    db.commit()
    return {
        "message": "Déclaration DUM liquidée avec succès",
        "id": dum.id,
        "numero_dum": dum.numero_dum,
        "statut": dum.statut,
        "montant_total_paye": float(dum.montant_total)
    }


@router.delete("/{id}")
async def delete_goods_declaration(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Supprime une déclaration DUM"""
    dum = db.query(DUM).filter(DUM.id == id).first()
    if not dum:
        raise HTTPException(status_code=404, detail=f"Déclaration DUM #{id} non trouvée")

    db.delete(dum)
    db.commit()
    return {"message": f"Déclaration DUM #{id} supprimée"}