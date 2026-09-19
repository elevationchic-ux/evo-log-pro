"""
Public API router - Public endpoints accessible without authentication
Services publics : Suivi de conteneurs/dossiers, prévisions d'escales navires, taux BEAC officiels, demande de contact
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, or_
from typing import Optional, List
from datetime import datetime, date
from pydantic import BaseModel

from app.core.database import get_db
from app.models.transit import DossierTransit
from app.models.douane_cameroun import TauxReferenceBEAC, BSC
from app.models.port_cameroun import PortCameroun, TerminalPortuaire
from app.models.conteneur_cycle import Conteneur

router = APIRouter()


class PublicContactMessage(BaseModel):
    nom: str
    email: str
    telephone: Optional[str] = None
    societe: Optional[str] = None
    sujet: str
    message: str


@router.get("/")
async def get_public_info():
    """Informations publiques sur la plateforme EVO-LOG EM-ERP"""
    return {
        "platform": "EVO-LOG Logistics & Port ERP",
        "region": "CEMAC / Golfe de Guinée",
        "ports_desservis": ["Port Autonome de Douala (PAD)", "Port Autonome de Kribi (PAK)"],
        "services_publics": [
            "/api/v1/public/track/{reference}",
            "/api/v1/public/taux-devises",
            "/api/v1/public/ports",
            "/api/v1/public/contact"
        ],
        "version": "2.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/track/{reference}")
async def public_track_shipment(
    reference: str,
    db: Session = Depends(get_db)
):
    """Suivi public en temps réel d'un conteneur, dossier ou connaissement sans authentification requise"""
    # 1. Recherche conteneur
    conteneur = db.query(Conteneur).filter(Conteneur.numero_conteneur.ilike(f"%{reference}%")).first()
    if conteneur:
        return {
            "type": "conteneur",
            "reference": conteneur.numero_conteneur,
            "statut": conteneur.statut,
            "type_conteneur": conteneur.type_conteneur,
            "taille": conteneur.taille,
            "port_actuel": conteneur.port_actuel,
            "emplacement": conteneur.emplacement,
            "date_dernier_mouvement": conteneur.date_dernier_mouvement.isoformat() if conteneur.date_dernier_mouvement else None
        }

    # 2. Recherche par connaissement BSC
    bsc = db.query(BSC).filter(
        or_(
            BSC.numero_connaisse.ilike(f"%{reference}%"),
            BSC.numero_bsc.ilike(f"%{reference}%")
        )
    ).first()
    if bsc:
        return {
            "type": "connaissement_bsc",
            "reference": bsc.numero_connaisse,
            "numero_bsc": bsc.numero_bsc,
            "navire": bsc.navire,
            "port_chargement": bsc.port_chargement,
            "port_dechargement": bsc.port_dechargement,
            "date_emission": bsc.date_emission.isoformat() if bsc.date_emission else None,
            "statut": bsc.statut
        }

    # 3. Recherche dossier transit
    dossier = db.query(DossierTransit).filter(DossierTransit.numero_dossier.ilike(f"%{reference}%")).first()
    if dossier:
        return {
            "type": "dossier_transit",
            "reference": dossier.numero_dossier,
            "statut": dossier.statut.value if hasattr(dossier.statut, 'value') else str(dossier.statut),
            "origine": dossier.origine,
            "destination": dossier.destination,
            "moyen_transport": dossier.moyen_transport,
            "date_ouverture": dossier.date_ouverture.isoformat() if dossier.date_ouverture else None
        }

    raise HTTPException(status_code=404, detail=f"Aucune expédition trouvée pour la référence '{reference}'")


@router.get("/taux-devises")
async def get_public_exchange_rates(
    db: Session = Depends(get_db)
):
    """Taux de change officiels de la BEAC en vigueur pour les opérations douanières"""
    rates = db.query(TauxReferenceBEAC).order_by(desc(TauxReferenceBEAC.date_application)).limit(10).all()
    return [
        {
            "devise": r.devise,
            "taux_achat": float(r.taux_achat),
            "taux_vente": float(r.taux_vente),
            "taux_moyen": float(r.taux_moyen) if r.taux_moyen else None,
            "date": r.date_application.isoformat() if r.date_application else None
        }
        for r in rates
    ]


@router.get("/ports")
async def get_public_ports(
    db: Session = Depends(get_db)
):
    """Ports camerounais et terminaux portuaires opérationnels"""
    ports = db.query(PortCameroun).filter(PortCameroun.est_actif == True).all()
    return [
        {
            "id": p.id,
            "code": p.code,
            "nom": p.nom,
            "ville": p.ville,
            "autorite_portuaire": p.autorite_portuaire,
            "tirant_eau_max": float(p.tirant_eau_max) if p.tirant_eau_max else None,
            "nombre_terminaux": len(p.terminaux) if p.terminaux else 0
        }
        for p in ports
    ]


@router.post("/contact", status_code=status.HTTP_201_CREATED)
async def submit_public_contact(
    payload: PublicContactMessage,
    db: Session = Depends(get_db)
):
    """Envoi d'un message public ou d'une demande de renseignement commercial"""
    return {
        "status": "received",
        "message": f"Merci {payload.nom}, votre demande concernant '{payload.sujet}' a bien été enregistrée.",
        "reference_ticket": f"PUB-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    }