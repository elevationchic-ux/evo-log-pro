"""
Master Data router - Reference data and nomenclatures for CEMAC & Cameroon logistics
Données de référence : Codes SH/Nomenclature CEMAC, Bureaux de Douane, Taux BEAC, Corridors, Incoterms
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
from app.models.transit_avance import NomenclatureCEMAC, BureauDouane
from app.models.douane_cameroun import ArticleCodeDouanes, TauxReferenceBEAC
from app.models.transit_cemac import CorridorCEMACTransit

router = APIRouter()


class NomenclatureCreate(BaseModel):
    code_hs: str
    description: str
    section: Optional[str] = None
    chapitre: Optional[str] = None
    position: Optional[str] = None
    taux_dd: Optional[float] = 20.0
    taux_tva: Optional[float] = 19.25
    unite: Optional[str] = "kg"
    restrictions: Optional[str] = None


@router.get("/")
async def get_master_data_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Résumé des référentiels maîtres (Master Data) enregistrés en base de données"""
    count_sh = db.query(func.count(NomenclatureCEMAC.id)).scalar() or 0
    count_bureaux = db.query(func.count(BureauDouane.id)).scalar() or 0
    count_taux = db.query(func.count(TauxReferenceBEAC.id)).scalar() or 0
    count_articles_cd = db.query(func.count(ArticleCodeDouanes.id)).scalar() or 0
    count_corridors = db.query(func.count(CorridorCEMACTransit.id)).scalar() or 0

    return {
        "status": "ready",
        "catalogs": {
            "nomenclatures_cemac_sh": count_sh,
            "bureaux_douane": count_bureaux,
            "taux_reference_beac": count_taux,
            "articles_code_douanes": count_articles_cd,
            "corridors_transit_cemac": count_corridors,
            "incoterms_standard": 11,
            "iso_container_types": 8
        },
        "last_sync": datetime.utcnow().isoformat()
    }


@router.get("/nomenclatures-cemac")
async def get_nomenclatures(
    search: Optional[str] = Query(None, description="Recherche par code SH ou description"),
    chapitre: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Recherche dans le tarif des douanes CEMAC (Nomenclature SH)"""
    query = db.query(NomenclatureCEMAC)

    if chapitre:
        query = query.filter(NomenclatureCEMAC.chapitre == chapitre)
    if search:
        query = query.filter(
            or_(
                NomenclatureCEMAC.code_hs.ilike(f"%{search}%"),
                NomenclatureCEMAC.description.ilike(f"%{search}%")
            )
        )

    total = query.count()
    items = query.order_by(NomenclatureCEMAC.code_hs.asc()).offset(skip).limit(limit).all()

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": [
            {
                "id": n.id,
                "code_hs": n.code_hs,
                "description": n.description,
                "section": n.section,
                "chapitre": n.chapitre,
                "position": n.position,
                "taux_dd": float(n.taux_dd) if n.taux_dd else 20.0,
                "taux_tva": float(n.taux_tva) if n.taux_tva else 19.25,
                "unite": n.unite,
                "restrictions": n.restrictions,
                "statut": n.statut
            }
            for n in items
        ]
    }


@router.post("/nomenclatures-cemac", status_code=status.HTTP_201_CREATED)
async def create_nomenclature(
    payload: NomenclatureCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Ajoute une nouvelle ligne de nomenclature tarifaire SH"""
    existing = db.query(NomenclatureCEMAC).filter(NomenclatureCEMAC.code_hs == payload.code_hs).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Code SH {payload.code_hs} déjà existant")

    nom = NomenclatureCEMAC(
        code_hs=payload.code_hs,
        description=payload.description,
        section=payload.section,
        chapitre=payload.chapitre,
        position=payload.position,
        taux_dd=payload.taux_dd,
        taux_tva=payload.taux_tva,
        unite=payload.unite,
        restrictions=payload.restrictions,
        statut="actif",
        date_effet=date.today()
    )
    db.add(nom)
    db.commit()
    db.refresh(nom)

    return {"message": "Code SH créé avec succès", "id": nom.id, "code_hs": nom.code_hs}


@router.get("/bureaux-douane")
async def get_bureaux_douane(
    type_bureau: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Liste des bureaux de douane camerounais enregistrés"""
    query = db.query(BureauDouane)
    if type_bureau:
        query = query.filter(BureauDouane.type_bureau == type_bureau)

    items = query.order_by(BureauDouane.nom.asc()).all()
    return [
        {
            "id": b.id,
            "code": b.code,
            "nom": b.nom,
            "type_bureau": b.type_bureau,
            "region": b.region,
            "adresse": b.adresse,
            "telephone": b.telephone,
            "statut": b.statut
        }
        for b in items
    ]


@router.get("/taux-beac")
async def get_taux_beac(
    devise: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Taux de change officiels de référence BEAC (Banque des États de l'Afrique Centrale)"""
    query = db.query(TauxReferenceBEAC)
    if devise:
        query = query.filter(TauxReferenceBEAC.devise == devise.upper())

    items = query.order_by(desc(TauxReferenceBEAC.date_application)).limit(30).all()

    return [
        {
            "id": t.id,
            "devise": t.devise,
            "taux_achat": float(t.taux_achat),
            "taux_vente": float(t.taux_vente),
            "taux_moyen": float(t.taux_moyen) if t.taux_moyen else None,
            "date_application": t.date_application.isoformat() if t.date_application else None,
            "source": t.source
        }
        for t in items
    ]


@router.get("/corridors")
async def get_corridors_cemac(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Corridors de transit routier CEMAC (Douala-N'Djamena, Douala-Bangui, etc.)"""
    corridors = db.query(CorridorCEMACTransit).filter(CorridorCEMACTransit.est_actif == True).all()
    return [
        {
            "id": c.id,
            "code": c.code,
            "nom": c.nom,
            "origine": c.origine,
            "destination": c.destination,
            "distance_km": c.distance_km,
            "duree_estimee_heures": c.duree_estimee_heures,
            "pays_origine": c.pays_origine,
            "pays_destination": c.pays_destination,
            "etat_route": c.etat_route.value if hasattr(c.etat_route, 'value') else str(c.etat_route)
        }
        for c in corridors
    ]


@router.get("/incoterms")
async def get_incoterms(
    current_user: User = Depends(get_current_user)
):
    """Référentiel des Incoterms ICC 2020 avec règles d'assurance et de transfert de frais"""
    return [
        {"code": "EXW", "nom": "Ex Works (À l'usine)", "mode": "Tous modes", "transfert_risque": "Locaux du vendeur"},
        {"code": "FCA", "nom": "Free Carrier (Franco transporteur)", "mode": "Tous modes", "transfert_risque": "Remise au transporteur"},
        {"code": "FAS", "nom": "Free Alongside Ship (Franco le long du navire)", "mode": "Maritime", "transfert_risque": "Le long du navire au port de départ"},
        {"code": "FOB", "nom": "Free On Board (Franco à bord)", "mode": "Maritime", "transfert_risque": "À bord du navire au port de départ"},
        {"code": "CFR", "nom": "Cost and Freight (Coût et Fret)", "mode": "Maritime", "transfert_risque": "À bord du navire au départ (fret payé à destination)"},
        {"code": "CIF", "nom": "Cost, Insurance and Freight (Coût, Assurance et Fret)", "mode": "Maritime", "transfert_risque": "À bord au départ (fret et assurance payés)"},
        {"code": "CPT", "nom": "Carriage Paid To (Port payé jusqu'à)", "mode": "Tous modes", "transfert_risque": "Premier transporteur"},
        {"code": "CIP", "nom": "Carriage and Insurance Paid To", "mode": "Tous modes", "transfert_risque": "Premier transporteur (assurance payée)"},
        {"code": "DAP", "nom": "Delivered At Place (Rendu au lieu de destination)", "mode": "Tous modes", "transfert_risque": "Au lieu désigné non déchargé"},
        {"code": "DPU", "nom": "Delivered at Place Unloaded (Rendu au lieu déchargé)", "mode": "Tous modes", "transfert_risque": "Déchargé au lieu convenu"},
        {"code": "DDP", "nom": "Delivered Duty Paid (Rendu droits acquittés)", "mode": "Tous modes", "transfert_risque": "Au lieu désigné, droits payés"}
    ]


@router.get("/container-types")
async def get_container_types(
    current_user: User = Depends(get_current_user)
):
    """Types standards de conteneurs maritimes ISO 668"""
    return [
        {"code": "20GP", "nom": "20' General Purpose", "teu": 1.0, "longueur_m": 6.06, "largeur_m": 2.44, "hauteur_m": 2.59, "charge_max_kg": 28200, "volume_m3": 33.2},
        {"code": "40GP", "nom": "40' General Purpose", "teu": 2.0, "longueur_m": 12.19, "largeur_m": 2.44, "hauteur_m": 2.59, "charge_max_kg": 28800, "volume_m3": 67.7},
        {"code": "40HC", "nom": "40' High Cube", "teu": 2.0, "longueur_m": 12.19, "largeur_m": 2.44, "hauteur_m": 2.90, "charge_max_kg": 28600, "volume_m3": 76.4},
        {"code": "20RF", "nom": "20' Reefer (Frigorifique)", "teu": 1.0, "longueur_m": 6.06, "largeur_m": 2.44, "hauteur_m": 2.59, "charge_max_kg": 27400, "volume_m3": 28.3},
        {"code": "40RF", "nom": "40' Reefer (Frigorifique)", "teu": 2.0, "longueur_m": 12.19, "largeur_m": 2.44, "hauteur_m": 2.59, "charge_max_kg": 29400, "volume_m3": 59.3},
        {"code": "20OT", "nom": "20' Open Top", "teu": 1.0, "longueur_m": 6.06, "largeur_m": 2.44, "hauteur_m": 2.59, "charge_max_kg": 28200, "volume_m3": 32.5},
        {"code": "40OT", "nom": "40' Open Top", "teu": 2.0, "longueur_m": 12.19, "largeur_m": 2.44, "hauteur_m": 2.59, "charge_max_kg": 28600, "volume_m3": 66.5},
        {"code": "20FR", "nom": "20' Flat Rack", "teu": 1.0, "longueur_m": 6.06, "largeur_m": 2.44, "hauteur_m": 2.59, "charge_max_kg": 31000, "volume_m3": 0.0}
    ]