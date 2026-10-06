"""
Real Customs router - suivi LOCAL des DUM (circuit CAMCIS notifie) & cautions.

HONNETETE PRODUITE (2026-09, revue 037) :
Le controle douanier est un acte a valeur legale. L'ERP ne peut PAS simuler une
reponse du serveur central CAMCIS/SYDONIA ni emettre une quittance du Tresor :
les anciens « faux succes » (circuit choisi par un hash, quittance au random,
plafond de caution code en dur) ont ete supprimes, puis les endpoints sont
tombes en 501... ce qui laissait l'ecran « real-customs » mort.

Solution honnete : l'ERP devient le REGISTRE ou le declarant enregistre ce que
le guichet lui a reellement notifie, et le suivi de son cautionnement
(modeles CautionDouaniere / DumCustomsRecord, tables scopees par tenant).
Aucune donnee inventee : un champ non saisi reste NULL et s'affique comme
« non enregistre », jamais comme une valeur par defaut.

Ce qui RESTE volontairement en 501 : la generateur du flux EDI XML norme et le
suivi des formalites e-GUCE, qui exigent respectivement le schema ASYCUDA
officiel et les numeros emis par MINCOMMERCE/SGS/MINADER. Ces endpoints ne sont
appeles par aucun bouton de l'interface.
"""
from fastapi import APIRouter, Depends, Body, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
from datetime import datetime, date

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.not_implemented import not_implemented  # noqa: F401 (tenu pour audit)
from app.models.user import User
from app.models.transit import CautionDouaniere, DumCustomsRecord

router = APIRouter()

# Resultats de circuit que la DGD peut notifier (aucune valeur inventee : seul
# le declarant saisit celui qui lui a ete attribue).
CIRCUITS_VALIDES = {"VERT", "BLEU", "JAUNE", "ROUGE"}


def _cid(user: User) -> Optional[int]:
    return getattr(user, "company_id", None)


def _num(v) -> float:
    try:
        return float(v) if v is not None else 0.0
    except (TypeError, ValueError):
        return 0.0


def _iso(dt) -> Optional[str]:
    return dt.isoformat() if isinstance(dt, (datetime, date)) else None


def _dum_dict(r: DumCustomsRecord) -> Dict[str, Any]:
    return {
        "id": r.id,
        "numero_dum": r.numero_dum,
        "systeme": r.systeme,
        "bureau_douane": r.bureau_douane,
        "valeur_cif_xaf": _num(r.valeur_cif_xaf),
        "circuit": r.circuit,
        "statut_recevabilite": r.statut_recevabilite,
        "inspecteur_assigne": r.inspecteur_assigne,
        "delai_traitement_estime": r.delai_traitement_estime,
        "description": r.description,
        "date_attribution": _iso(r.date_attribution_circuit),
        "teletransmis_le": _iso(r.teletransmis_le),
        "numero_accuse_camcis": r.numero_accuse_camcis,
        "caution_id": r.caution_id,
        "montant_garanti_xaf": _num(r.montant_garanti_xaf),
        "quittance_tresor_emise": bool(r.quittance_tresor_emise),
        "numero_quittance": r.numero_quittance,
        "apure": bool(r.apure),
        "date_apurement": _iso(r.date_apurement),
    }


def _caution_dict(c: CautionDouaniere) -> Dict[str, Any]:
    return {
        "id": c.id,
        "reference": c.reference,
        "banque_cautionnaire": c.banque_cautionnaire,
        "formule": c.formule,
        "plafond_autorise_xaf": _num(c.plafond_autorise_xaf),
        "devise": c.devise,
        "statut": c.statut,
        "date_debut": _iso(c.date_debut),
        "date_fin": _iso(c.date_fin),
        "notes": c.notes,
    }


# ─── 1. SUIVI LOCAL DES DUM (circuit notifie + teletransmission attestee) ───────

@router.get("/dossiers", summary="Liste des DUM enregistrees pour l'entreprise")
def lister_dossiers(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = (
        db.query(DumCustomsRecord)
        .filter(DumCustomsRecord.company_id == _cid(user))
        .order_by(DumCustomsRecord.created_at.desc())
        .all()
    )
    return {"data": [_dum_dict(r) for r in rows], "total": len(rows)}


@router.post("/dossiers", summary="Enregistrer (ou mettre a jour) une DUM suivie")
def enregistrer_dossier(payload: Dict[str, Any] = Body(...),
                        db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    numero = (payload.get("numero_dum") or "").strip()
    if not numero:
        raise HTTPException(status_code=422, detail="Le numero de DUM est obligatoire.")
    cid = _cid(user)
    row = db.query(DumCustomsRecord).filter(
        DumCustomsRecord.company_id == cid,
        DumCustomsRecord.numero_dum == numero,
    ).first()
    if row is None:
        row = DumCustomsRecord(company_id=cid, numero_dum=numero)
        db.add(row)
    for champ in ("systeme", "bureau_douane", "statut_recevabilite",
                  "inspecteur_assigne", "delai_traitement_estime", "description"):
        if payload.get(champ) is not None:
            setattr(row, champ, payload[champ])
    if payload.get("valeur_cif_xaf") is not None:
        row.valeur_cif_xaf = _num(payload["valeur_cif_xaf"])
    circuit = payload.get("circuit")
    if circuit:
        c = str(circuit).upper()
        if c not in CIRCUITS_VALIDES:
            raise HTTPException(status_code=422, detail=f"Circuit inconnu : {circuit}. Attendu VERT/BLEU/JAUNE/ROUGE.")
        row.circuit = c
        row.date_attribution_circuit = datetime.utcnow()
    db.commit()
    db.refresh(row)
    return {"data": _dum_dict(row), "message": "DUM enregistree."}


@router.get("/camcis/circuits/{numero_dum}", summary="Circuit de controle reellement notifie pour une DUM")
def get_camcis_circuit(numero_dum: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """
    Renvoie le circuit OFFICIELLEMENT attribue, tel qu'enregistre par le declarant.
    Aucune simulation : si rien n'a ete enregistre, `enregistre` vaut False et
    l'ecran propose la saisie du resultat recu du guichet.
    """
    row = db.query(DumCustomsRecord).filter(
        DumCustomsRecord.company_id == _cid(user),
        DumCustomsRecord.numero_dum == numero_dum,
    ).first()
    if row is None:
        return {
            "enregistre": False,
            "numero_dum": numero_dum,
            "systeme": "CAMCIS",
            "circuit": None,
            "statut_recevabilite": None,
            "date_attribution": None,
            "description": None,
            "delai_traitement_estime": None,
            "inspecteur_assigne": None,
            "quittance_tresor_emise": False,
            "numero_quittance": None,
        }
    out = _dum_dict(row)
    out["enregistre"] = True
    return out


@router.post("/camcis/circuits", summary="Enregistrer le circuit notifie par la DGD")
def enregistrer_circuit(payload: Dict[str, Any] = Body(...),
                        db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    numero = (payload.get("numero_dum") or "").strip()
    circuit = (payload.get("circuit") or "").upper()
    if not numero or circuit not in CIRCUITS_VALIDES:
        raise HTTPException(status_code=422, detail="numero_dum et circuit (VERT/BLEU/JAUNE/ROUGE) requis.")
    cid = _cid(user)
    row = db.query(DumCustomsRecord).filter(
        DumCustomsRecord.company_id == cid,
        DumCustomsRecord.numero_dum == numero,
    ).first()
    if row is None:
        row = DumCustomsRecord(company_id=cid, numero_dum=numero)
        db.add(row)
    row.circuit = circuit
    row.date_attribution_circuit = datetime.utcnow()
    for champ in ("statut_recevabilite", "inspecteur_assigne", "delai_traitement_estime", "description"):
        if payload.get(champ) is not None:
            setattr(row, champ, payload[champ])
    db.commit()
    db.refresh(row)
    return {"data": _dum_dict(row), "message": f"Circuit {circuit} enregistre pour {numero}."}


@router.post("/camcis/teletransmettre", summary="Attester la teletransmission d'une DUM (accuse reel)")
def teletransmettre_dum_camcis(payload: Dict[str, Any] = Body(...),
                               db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """
    N'emet AUCUN faux succes : enregistre la date de teletransmission et le
    numero d'accuse COLLE par le declarant depuis le portail CAMCIS. L'ERP agit
    comme journal de preuve, pas comme simulateur EDI.
    """
    numero = (payload.get("numero_dum") or "").strip()
    if not numero:
        raise HTTPException(status_code=422, detail="Le numero de DUM est obligatoire.")
    cid = _cid(user)
    row = db.query(DumCustomsRecord).filter(
        DumCustomsRecord.company_id == cid,
        DumCustomsRecord.numero_dum == numero,
    ).first()
    if row is None:
        row = DumCustomsRecord(company_id=cid, numero_dum=numero)
        db.add(row)
    if payload.get("valeur_cif_xaf") is not None:
        row.valeur_cif_xaf = _num(payload["valeur_cif_xaf"])
    if payload.get("bureau_douane"):
        row.bureau_douane = payload["bureau_douane"]
    row.teletransmis_le = datetime.utcnow()
    accuse = payload.get("numero_accuse_camcis")
    row.numero_accuse_camcis = (str(accuse).strip() if accuse else None)
    db.commit()
    db.refresh(row)
    return {
        "data": _dum_dict(row),
        "message": (
            "Teletransmission journalisee."
            if row.numero_accuse_camcis
            else "Teletransmission journalisee SANS numero d'accuse : "
                 "reportez le numero reel delivre par CAMCIS des reception."
        ),
    }


# ─── 2. CAUTIONS DOUANIERES (registre persistant reel) ──────────────────────────

@router.get("/cautions", summary="Liste des cautions souscrites")
def lister_cautions(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = db.query(CautionDouaniere).filter(
        CautionDouaniere.company_id == _cid(user)
    ).order_by(CautionDouaniere.created_at.desc()).all()
    return {"data": [_caution_dict(c) for c in rows], "total": len(rows)}


@router.post("/cautions", summary="Souscrire/enregistrer une caution douaniere")
def creer_caution(payload: Dict[str, Any] = Body(...),
                  db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    plafond = payload.get("plafond_autorise_xaf")
    if plafond is None:
        raise HTTPException(status_code=422, detail="Le plafond autorise est obligatoire.")
    cid = _cid(user)
    reference = (payload.get("reference") or "").strip()
    if not reference:
        n = db.query(CautionDouaniere).filter(CautionDouaniere.company_id == cid).count() + 1
        reference = f"CAU-{datetime.utcnow().year}-{n:04d}"
    if db.query(CautionDouaniere).filter(
        CautionDouaniere.company_id == cid, CautionDouaniere.reference == reference
    ).first():
        raise HTTPException(status_code=409, detail=f"La reference {reference} existe deja.")
    row = CautionDouaniere(
        company_id=cid,
        reference=reference,
        banque_cautionnaire=payload.get("banque_cautionnaire"),
        formule=payload.get("formule"),
        plafond_autorise_xaf=_num(plafond),
        devise=payload.get("devise") or "XAF",
        statut=(payload.get("statut") or "ACTIVE").upper(),
        notes=payload.get("notes"),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return {"data": _caution_dict(row), "message": "Caution enregistree."}


@router.get("/cautions/statut", summary="Supervision du plafond de caution (calculee sur les donnees reelles)")
def get_cautions_status(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """
    Agrége les cautions ACTIVE du tenant et les DUM non apurees qui les
    consomment. Aucun chiffre n'est code en dur : si le transitaire n'a rien
    saisi, tout est a zero et l'ecran l'affiche honnetement.
    """
    cid = _cid(user)
    cautions = db.query(CautionDouaniere).filter(
        CautionDouaniere.company_id == cid,
        CautionDouaniere.statut == "ACTIVE",
    ).all()
    plafond = sum(_num(c.plafond_autorise_xaf) for c in cautions)

    dossiers = (
        db.query(DumCustomsRecord)
        .filter(DumCustomsRecord.company_id == cid, DumCustomsRecord.apure.is_(False))
        .all()
    )
    engage = sum(_num(d.montant_garanti_xaf) for d in dossiers)
    disponible = plafond - engage
    taux = round((engage / plafond) * 100, 1) if plafond > 0 else 0.0
    banques = sorted({c.banque_cautionnaire for c in cautions if c.banque_cautionnaire})

    return {
        "banque_cautionnaire": banques[0] if len(banques) == 1 else (", ".join(banques) if banques else None),
        "nb_cautions_actives": len(cautions),
        "plafond_autorise_xaf": plafond,
        "montant_engage_xaf": engage,
        "disponible_xaf": disponible,
        "taux_utilisation_pourcent": taux,
        "alerte_depassement": engage > plafond,
        "dossiers_en_cours": [_dum_dict(d) for d in dossiers],
    }


@router.post("/cautions/apurer", summary="Apurer la caution consommee par une DUM")
def apurer_caution(payload: Dict[str, Any] = Body(...),
                   db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    numero = (payload.get("numero_dum") or "").strip()
    if not numero:
        raise HTTPException(status_code=422, detail="Le numero de DUM est obligatoire.")
    row = db.query(DumCustomsRecord).filter(
        DumCustomsRecord.company_id == _cid(user),
        DumCustomsRecord.numero_dum == numero,
    ).first()
    if row is None:
        raise HTTPException(status_code=404, detail=f"Aucune DUM {numero} enregistree.")
    row.apure = True
    row.date_apurement = datetime.utcnow()
    quittance = payload.get("numero_quittance")
    if quittance:
        row.numero_quittance = str(quittance).strip()
        row.quittance_tresor_emise = True
    db.commit()
    db.refresh(row)
    return {"data": _dum_dict(row), "message": f"Caution apuree pour {numero}."}


# ─── 3. CE QUI RESTE EXTERNE (connecteur pilote par la configuration) ─────────

@router.get("/camcis/export-edi/{numero_dum}", summary="Générer le flux EDI XML officiel CAMCIS / Sydonia")
def export_edi_camcis_xml(numero_dum: str):
    """Demande reelle au connecteur EDI douanier (CUSTOMS_EDI_*).

    503 si aucune gateway ASYCUDA/CAMCIS n'est declaree : aucun flux XML
    « conforme » n'est invente localement.
    """
    from app.utils.external import call_provider

    return call_provider(
        "CUSTOMS_EDI",
        "Export EDI XML normé CAMCIS/ASYCUDA",
        path=f"/camcis/export-edi/{numero_dum}",
        method="GET",
    )


@router.get("/guce/formalites/{dossier_id}", summary="Suivi des formalités pré-dédouanement e-GUCE")
def get_guce_formalites(dossier_id: str):
    """Interrogation reelle du connecteur e-GUCE (CUSTOMS_EDI_*).

    503 si non configure : les numeros DI/AVP/phyto ne peuvent venir que du
    guichet officiel, jamais d'une simulation locale.
    """
    from app.utils.external import call_provider

    return call_provider(
        "CUSTOMS_EDI",
        "Suivi des formalites e-GUCE",
        path=f"/guce/formalites/{dossier_id}",
        method="GET",
    )
