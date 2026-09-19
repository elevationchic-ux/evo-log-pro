"""
Partner API router - B2B integration endpoints for external partners
API dédiée aux chargeurs, transitaires, consignataires et transporteurs partenaires
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, or_
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.integration import WebhookIntegration, Integration
from app.models.transit import DossierTransit
from app.models.transport import Mission
from app.models.prestataire import DemandeCotation

router = APIRouter()


class WebhookCreate(BaseModel):
    integration_id: Optional[int] = None
    nom: str
    url_webhook: str
    evenements: List[str] = ["container.moved", "customs.cleared", "invoice.issued"]
    secret: Optional[str] = None


class PartnerCotationRequest(BaseModel):
    titre: str
    description: str
    origine: str
    destination: str
    type_transport: Optional[str] = "routier"
    poids_kg: Optional[float] = None
    volume_m3: Optional[float] = None
    date_chargement_souhaitee: Optional[date] = None


@router.get("/")
async def get_partner_api_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Vue d'ensemble de l'API Partenaires B2B et webhooks enregistrés"""
    total_webhooks = db.query(func.count(WebhookIntegration.id)).scalar() or 0
    active_webhooks = db.query(func.count(WebhookIntegration.id)).filter(WebhookIntegration.statut == "actif").scalar() or 0

    return {
        "api_name": "EVO-LOG B2B Partner Gateway",
        "version": "v1.2",
        "auth_type": "Bearer JWT / API Key",
        "webhooks_count": total_webhooks,
        "active_webhooks": active_webhooks,
        "supported_events": [
            "container.gate_in",
            "container.gate_out",
            "customs.circuit_assigned",
            "customs.cleared",
            "transport.mission_started",
            "transport.delivered",
            "invoice.created"
        ]
    }


@router.get("/webhooks")
async def get_webhooks(
    statut: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Liste des webhooks configurés par les partenaires"""
    query = db.query(WebhookIntegration)
    if statut:
        query = query.filter(WebhookIntegration.statut == statut)

    items = query.order_by(desc(WebhookIntegration.created_at)).all()
    return [
        {
            "id": w.id,
            "nom": w.nom,
            "url_webhook": w.url_webhook,
            "evenements": w.evenements,
            "statut": w.statut,
            "nombre_reussites": w.nombre_reussites,
            "nombre_echecs": w.nombre_echecs,
            "derniere_utilisation": w.derniere_utilisation.isoformat() if w.derniere_utilisation else None
        }
        for w in items
    ]


@router.post("/webhooks", status_code=status.HTTP_201_CREATED)
async def create_webhook(
    payload: WebhookCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Enregistre un nouveau webhook d'écoute d'événements logistiques"""
    wb = WebhookIntegration(
        integration_id=payload.integration_id,
        nom=payload.nom,
        url_webhook=payload.url_webhook,
        evenements=str(payload.evenements),
        secret=payload.secret or f"sec_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        statut="actif"
    )

    db.add(wb)
    db.commit()
    db.refresh(wb)

    return {
        "message": "Webhook B2B enregistré avec succès",
        "id": wb.id,
        "nom": wb.nom,
        "url_webhook": wb.url_webhook
    }


@router.get("/track/{reference}")
async def partner_tracking(
    reference: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Recherche multi-modale de suivi pour les partenaires par numéro de dossier, mission ou connaissement"""
    # 1. Recherche par dossier de transit
    dossier = db.query(DossierTransit).filter(
        or_(
            DossierTransit.numero_dossier.ilike(f"%{reference}%"),
            DossierTransit.numero_connaisse.ilike(f"%{reference}%")
        )
    ).first()

    if dossier:
        return {
            "type": "dossier_transit",
            "reference": dossier.numero_dossier,
            "numero_connaisse": dossier.numero_connaisse,
            "statut": dossier.statut.value if hasattr(dossier.statut, 'value') else str(dossier.statut),
            "origine": dossier.origine,
            "destination": dossier.destination,
            "moyen_transport": dossier.moyen_transport,
            "marchandise": dossier.marchandise,
            "date_ouverture": dossier.date_ouverture.isoformat() if dossier.date_ouverture else None
        }

    # 2. Recherche par mission de transport
    mission = db.query(Mission).filter(
        or_(
            Mission.code_mission.ilike(f"%{reference}%"),
            Mission.id == int(reference) if reference.isdigit() else False
        )
    ).first()

    if mission:
        return {
            "type": "mission_transport",
            "reference": mission.code_mission,
            "statut": mission.statut.value if hasattr(mission.statut, 'value') else str(mission.statut),
            "origine": mission.lieu_depart,
            "destination": mission.lieu_arrivee,
            "date_depart_prevue": mission.date_depart_prevue.isoformat() if mission.date_depart_prevue else None,
            "vehicule_id": mission.vehicule_id,
            "conducteur_id": mission.conducteur_id
        }

    return {
        "found": False,
        "reference": reference,
        "message": f"Aucun dossier ou mission correspondant à la référence '{reference}'"
    }


@router.post("/cotation-request", status_code=status.HTTP_201_CREATED)
async def submit_partner_cotation(
    payload: PartnerCotationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Soumission d'une demande de cotation fret/transit par un partenaire B2B"""
    today_str = datetime.now().strftime("%Y%m%d")
    count_today = db.query(func.count(DemandeCotation.id)).scalar() or 0
    ref = f"COT-B2B-{today_str}-{count_today + 1:04d}"

    demande = DemandeCotation(
        reference=ref,
        titre=payload.titre,
        description=payload.description,
        type_prestation=payload.type_transport or "transport",
        budget_estime=None,
        date_limite_reponse=payload.date_chargement_souhaitee,
        statut="ouverte"
    )

    db.add(demande)
    db.commit()
    db.refresh(demande)

    return {
        "message": "Demande de cotation transmise avec succès",
        "id": demande.id,
        "reference": demande.reference,
        "statut": demande.statut
    }


@router.delete("/webhooks/{id}")
async def delete_webhook(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Supprime un webhook partenaire"""
    wb = db.query(WebhookIntegration).filter(WebhookIntegration.id == id).first()
    if not wb:
        raise HTTPException(status_code=404, detail=f"Webhook #{id} non trouvé")

    db.delete(wb)
    db.commit()
    return {"message": f"Webhook #{id} supprimé"}