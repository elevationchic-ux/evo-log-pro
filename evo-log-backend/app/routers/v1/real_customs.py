"""
Real Customs router - CAMCIS, Sydonia World & Guichet Unique GUCE Cameroun

HONNÊTETÉ PRODUITE (2026-09 correction) :
Ce routeur exposait des « faux succès » : circuits CAMCIS déterminés par un
hash du numéro de DUM, accusés de réception et quittances DGD générés au
`random`, formalités GUCE (DI/AVP/phyto) inventées, caution Trésor codée en
dur. Ces données sont des actes à valeur légale : un client de bonne foi
aurait pu imprimer une fausse référence SYDONIA ou croire une DUM déposée.

Tous ces endpoints renvoient désormais un 501 explicite (voir
app/core/not_implemented.py) jusqu'à ce que les connecteurs réels soient
déployés :
- API CAMCIS / SYDONIA World (certificat DGD, schéma XML officiel)
- API GUCE e-GUCE (messages normés, accusés signés)
- Registre local des cautions (modèle CautionDouaniere + workflow apurement)
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Body, Response
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.not_implemented import not_implemented

router = APIRouter()


# ─── 1. INTERFAÇAGE CAMCIS / SYDONIA WORLD ──────────────────────────────────────

@router.get("/camcis/circuits/{numero_dum}", summary="Obtenir le circuit de contrôle douanier CAMCIS")
def get_camcis_circuit(numero_dum: str):
    """
    Circuit de contrôle attribué par le moteur d'analyse de risque CAMCIS
    (VERT / BLEU / JAUNE / ROUGE).

    501 : seul la DGD (via CAMCIS/SYDONIA World) attribue le circuit.
    Toute attribution locale serait une simulation trompeuse.
    """
    not_implemented(
        "Attribution du circuit de contrôle CAMCIS",
        "connecteur API CAMCIS/SYDONIA World (identifiants DGD, certificat, "
        "schéma de message officiel) ou saisie manuelle du résultat notifié par le déclarant",
    )


@router.post("/camcis/teletransmettre", summary="Télé-transmettre la DUM au serveur central CAMCIS")
def teletransmettre_dum_camcis(payload: Dict[str, Any] = Body(...)):
    """Soumission électronique d'une DUM à la DGD Cameroun."""
    not_implemented(
        "Télé-transmission CAMCIS de la DUM",
        "connecteur EDI CAMCIS/SYDONIA World (format officiel, signatures, "
        "accusés de réception authentiques). En attendant, la liquidation "
        "prévisionnelle est disponible via /api/v1/transit-douane-avance/simulation",
    )


@router.get("/camcis/export-edi/{numero_dum}", summary="Générer le flux EDI XML officiel CAMCIS / Sydonia")
def export_edi_camcis_xml(numero_dum: str):
    """Export du fichier XML normé ASYCUDA / CAMCIS pour le déclarant."""
    not_implemented(
        "Export EDI XML normé CAMCIS/ASYCUDA",
        "schéma XML officiel ASYCUDA World (CCNET) et agrément déclarant "
        "vérifiables ; le gabarit précédent contenait un numéro d'agrément inventé",
    )


# ─── 2. GUICHET UNIQUE GUCE CAMEROUN ────────────────────────────────────────────

@router.get("/guce/formalites/{dossier_id}", summary="Suivi des formalités pré-dédouanement e-GUCE")
def get_guce_formalites(dossier_id: str):
    """État des formalités préalables GUCE (DI, AVP, certificats)."""
    not_implemented(
        "Suivi des formalités e-GUCE",
        "API GUCE (numéros DI/AVP/phyto réellement émis par MINCOMMERCE, "
        "SGS et MINADER). Les numéros précédents étaient générés au hasard",
    )


# ─── 3. CAUTIONS EN DOUANE & CRÉDITS D'ENLÈVEMENT ──────────────────────────────

@router.get("/cautions/statut", summary="Supervision du plafond de caution et crédit d'enlèvement")
def get_cautions_status(db: Session = Depends(get_db)):
    """
    Supervision du cautionnement global souscrit auprès du Trésor Public.

    501 : les montants previously renvoyés (plafond 500 M, dossiers
    DOS-2026-xxxx) étaient codés en dur. Un modèle de suivi des cautions
    par tenant est requis avant tout affichage chiffré.
    """
    not_implemented(
        "Supervision des cautions douanières",
        "modèle CautionDouaniere (plafond, engagements, apurements) renseigné "
        "par le transitaire  aucun chiffre n'est connu tant qu'il n'est pas saisi",
    )


@router.post("/cautions/apurer", summary="Apurer une caution douanière après constatation de sortie")
def apurer_caution(payload: Dict[str, Any] = Body(...)):
    """Libération d'une ligne de crédit d'enlèvement après décharge frontière."""
    not_implemented(
        "Apurement de caution douanière",
        "registre persistant des cautions et workflow de décharge (certificat "
        "de sortie réel, pas un numéro généré aléatoirement)",
    )
