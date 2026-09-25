"""Cameroon/CEMAC Integration Router - BSC, CSC, DUM/SYGED, APE

Endpoints réels persistant dans les modèles SQLAlchemy correspondants
(app.models.douane_cameroun). Aucune donnée factice : chaque ligne créée
provient des champs fournis par l'utilisateur et chaque liste est une
vraie requête en base.
"""
from datetime import datetime, date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.douane_cameroun import BSC, CSC, DUM, APE, TauxReferenceBEAC

router = APIRouter()


def _serialize(obj) -> dict:
    """Sérialise un modèle en dict JSON-compatible (dates incluses)."""
    out = {}
    for col in obj.__table__.columns:
        val = getattr(obj, col.name)
        if isinstance(val, (datetime, date)):
            val = val.isoformat()
        elif val is not None and hasattr(val, "__float__") and not isinstance(val, (int, float, bool, str)):
            # Decimal -> float
            val = float(val)
        out[col.name] = val
    return out


# ============ BSC ============
@router.post("/bsc")
def creer_bsc(
    numero_connaisse: str,
    navire: str,
    port_chargement: str,
    port_dechargement: str,
    agent: str,
    importateur: str,
    poids_total: Optional[float] = None,
    valeur_fob: Optional[float] = None,
    db: Session = Depends(get_db),
):
    """Créer un BSC - Bordereau de Suivi des Cargaisons (CNCC)."""
    bsc = BSC(
        numero_bsc=f"BSC-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        numero_connaisse=numero_connaisse,
        navire=navire,
        port_chargement=port_chargement,
        port_dechargement=port_dechargement,
        date_emission=date.today(),
        date_validite=date.today(),
        agent=agent,
        importateur=importateur,
        poids_brut_tonnes=poids_total,
        valeur_fob=valeur_fob,
        devise="USD" if valeur_fob else None,
        montant_frais_bsc=(valeur_fob * 0.0002) if valeur_fob else None,
        devise_frais="XAF",
        statut="en_attente",
    )
    db.add(bsc)
    db.commit()
    db.refresh(bsc)
    return {"success": True, "data": _serialize(bsc)}


@router.get("/bsc")
def lister_bsc(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Lister les BSC réellement enregistrés (plus récents d'abord)."""
    rows = (
        db.query(BSC)
        .order_by(BSC.created_at.desc(), BSC.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return {"success": True, "data": [_serialize(r) for r in rows]}


@router.get("/bsc/{bsc_id}")
def get_bsc(bsc_id: int, db: Session = Depends(get_db)):
    """Récupérer un BSC par ID."""
    bsc = db.query(BSC).filter(BSC.id == bsc_id).first()
    if not bsc:
        raise HTTPException(status_code=404, detail="BSC non trouvé")
    return {"success": True, "data": _serialize(bsc)}


# ============ CSC ============
@router.post("/csc")
def demander_csc(
    numero_connaisse: str,
    navire: str,
    port_origine: str,
    port_destination: str,
    type_marchandise: Optional[str] = None,
    poids_brut_tonnes: Optional[float] = None,
    nombre_colis: Optional[int] = None,
    valeur_fob: Optional[float] = None,
    db: Session = Depends(get_db),
):
    """Demander un CSC - Certificat de Sécurité Cargaison (INS)."""
    csc = CSC(
        numero_csc=f"CSC-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        numero_connaisse=numero_connaisse,
        navire=navire,
        port_origine=port_origine,
        port_destination=port_destination,
        date_demande=date.today(),
        type_marchandise=type_marchandise,
        poids_brut_tonnes=poids_brut_tonnes,
        nombre_colis=nombre_colis,
        valeur_fob=valeur_fob,
        statut="en_attente",
    )
    db.add(csc)
    db.commit()
    db.refresh(csc)
    return {"success": True, "data": _serialize(csc)}


@router.get("/csc")
def lister_csc(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Lister les CSC réellement enregistrés."""
    rows = db.query(CSC).order_by(CSC.id.desc()).offset(skip).limit(limit).all()
    return {"success": True, "data": [_serialize(r) for r in rows]}


# ============ DUM / SYGED ============
@router.post("/dum")
def creer_dum(
    type_operation: str,
    regime_douanier: str,
    bureau_douane: str,
    declarant: str,
    importateur: str,
    marchandise: str,
    valeur_fob: Optional[float] = None,
    taux_change: Optional[float] = None,
    poids_brut: Optional[float] = None,
    nombre_colis: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """Créer un DUM - Déclaration Unique de Marchandises (SYGED)."""
    valeur_caf = (valeur_fob * taux_change) if (valeur_fob and taux_change) else None
    dum = DUM(
        numero_dum=f"DUM-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        type_operation=type_operation,
        regime_douanier=regime_douanier,
        bureau_douane=bureau_douane,
        date_depot=date.today(),
        declarant=declarant,
        importateur=importateur,
        marchandise=marchandise,
        poids_brut=poids_brut,
        nombre_colis=nombre_colis,
        valeur_fob=valeur_fob,
        valeur_caf=valeur_caf,
        devise="USD",
        taux_change=taux_change,
        statut="en_attente",
    )
    db.add(dum)
    db.commit()
    db.refresh(dum)
    return {"success": True, "data": _serialize(dum)}


@router.get("/dum")
def lister_dum(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Lister les DUM réellement enregistrés."""
    rows = db.query(DUM).order_by(DUM.id.desc()).offset(skip).limit(limit).all()
    return {"success": True, "data": [_serialize(r) for r in rows]}


# ============ APE ============
@router.post("/ape")
def creer_ape(
    importateur: str,
    montant_xaf: float,
    devise: str,
    banque: str,
    beneficiaire_etranger: Optional[str] = None,
    pays_beneficiaire: Optional[str] = None,
    objet_transfert: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Créer un APE - Arrêté de Paiement des Étrangers (BEAC)."""
    taux = (
        db.query(TauxReferenceBEAC)
        .filter(
            TauxReferenceBEAC.devise == devise,
            TauxReferenceBEAC.est_taux_officiel == True,  # noqa: E712
        )
        .order_by(TauxReferenceBEAC.date_application.desc())
        .first()
    )
    taux_change = float(taux.taux_moyen) if taux and taux.taux_moyen else None
    ape = APE(
        numero_ape=f"APE-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        importateur=importateur,
        montant_xaf=montant_xaf,
        montant_devise=(montant_xaf / taux_change) if taux_change else None,
        devise=devise,
        taux_change=taux_change,
        banque=banque,
        beneficiaire_etranger=beneficiaire_etranger,
        pays_beneficiaire=pays_beneficiaire,
        objet_transfert=objet_transfert,
        date_demande=date.today(),
        statut="en_attente",
    )
    db.add(ape)
    db.commit()
    db.refresh(ape)
    return {"success": True, "data": _serialize(ape)}


@router.get("/ape")
def lister_ape(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Lister les APE réellement enregistrés."""
    rows = db.query(APE).order_by(APE.id.desc()).offset(skip).limit(limit).all()
    return {"success": True, "data": [_serialize(r) for r in rows]}


# ============ Tarifs / Taux BEAC ============
@router.get("/tarifs-douane")
def get_tarifs_douane(db: Session = Depends(get_db)):
    """Tarifs de référence BEAC réellement enregistrés (taux de change officiels)."""
    rows = (
        db.query(TauxReferenceBEAC)
        .filter(TauxReferenceBEAC.est_taux_officiel == True)  # noqa: E712
        .order_by(TauxReferenceBEAC.date_application.desc())
        .all()
    )
    return {"success": True, "data": [_serialize(r) for r in rows]}


# ============ Calcul droits de douane ============
@router.post("/calculer-droits")
def calculer_droits(valeur_cif: float, taux_douane: float = 20.0, tva: float = 19.25):
    """Calcul des droits de douane CEMAC à partir d'une valeur CIF renseignée.

    Délégué au moteur UNIQUE ``app.services.taxation_douaniere`` (partagé avec
    transit, transit-avance et le calculateur CEMAC) : un même conteneur donne
    désormais le même montant sur tous les écrans. Taux fournis à titre
    d'hypothèse de simulation, aucun montant n'est inventé.
    """
    from app.services.taxation_douaniere import calculer_liquidation

    liq = calculer_liquidation(
        valeur_en_douane=valeur_cif,
        taux_dd_explicite=taux_douane,
        taux_tva_explicite=tva,
    )
    return {
        "success": True,
        "data": {
            "valeur_cif": liq["valeur_en_douane_xaf"],
            "taux_douane": taux_douane,
            "droits_douane": liq["droit_douane_dd"],
            "redevance_informatique": liq["redevance_informatique"],
            "cci_cemac": liq["cci_cemac"],
            "prelevement_ohada": liq["prelevement_ohada"],
            "base_tva": liq["base_tva"],
            "tva": liq["tva_1925"],
            "precompte_is": liq["precompte_is"],
            "montant_total": liq["total_a_liquider_xaf"],
            "devise": "XAF",
            "source_taux": liq["source_taux"],
            "simulation": liq["simulation"],
            "note": liq["note"],
        },
    }
