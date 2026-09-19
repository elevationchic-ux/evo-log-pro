"""Router FastAPI — Portail B2B Client EVO-LOG"""
from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.orm import Session
from typing import Dict, Any
from app.core.database import get_db
from app.services.b2b_portal_service import B2BPortalService

router = APIRouter()


@router.get("/dossiers", summary="Lister les dossiers du client B2B connecté")
def get_dossiers(client_id: int = Query(1), db: Session = Depends(get_db)):
    """Retourne tous les dossiers en cours et historiques du client B2B."""
    return B2BPortalService.get_dossiers_client(db, client_id)


@router.get("/factures", summary="Lister les factures du client B2B")
def get_factures(client_id: int = Query(1), db: Session = Depends(get_db)):
    """Retourne toutes les factures avec TVA 19.25% Cameroun et statut règlement."""
    return B2BPortalService.get_factures_client(db, client_id)


@router.post("/quotes", summary="Calculer une cotation instantanée fret & transit")
def calculate_quote(payload: Dict[str, Any] = Body(...)):
    """Calcule le tarif instantané fret, manutention, passage portuaire et assurance."""
    return B2BPortalService.calculate_instant_quote(payload)


@router.post("/booking", summary="Créer une réservation e-Booking d'enlèvement conteneur")
def create_booking(payload: Dict[str, Any] = Body(...)):
    """Génère un bon de réservation e-Booking horodaté avec créneau terminal."""
    return B2BPortalService.create_ebooking(payload)


@router.get("/tracking/{query}", summary="Tracking conteneur ISO 6346 ou numéro de B/L")
def track_cargo(query: str):
    """Suivi multi-jalons du conteneur avec alerte franchise surestaries et géolocalisation."""
    return B2BPortalService.track_cargo(query)


@router.post("/payments/checkout", summary="Paiement en ligne sécurisé (MoMo / Carte Bancaire)")
def process_checkout(payload: Dict[str, Any] = Body(...)):
    """Règlement direct de facture débloquant automatiquement le Bon de Sortie."""
    return B2BPortalService.process_checkout_payment(payload)


@router.get("/notifications/preferences", summary="Consulter les préférences de notifications")
def get_notification_preferences(client_id: int = Query(1)):
    """Retourne les canaux SMS, WhatsApp et Email activés pour les alertes statut."""
    return B2BPortalService.get_notification_preferences(client_id)


@router.put("/notifications/preferences", summary="Mettre à jour les préférences de notifications")
def update_notification_preferences(client_id: int = Query(1), payload: Dict[str, Any] = Body(...)):
    """Met à jour les seuils d'alerte et canaux de notification du chargeur."""
    return B2BPortalService.update_notification_preferences(client_id, payload)
