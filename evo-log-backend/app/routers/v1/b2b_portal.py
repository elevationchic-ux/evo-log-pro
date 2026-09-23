"""Router FastAPI  Portail B2B Client EVO-LOG"""
from fastapi import APIRouter, Depends, Query, Body, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
from app.core.database import get_db
from app.services.b2b_portal_service import B2BPortalService
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter()


@router.get("/dossiers", summary="Lister les dossiers du client B2B connecté")
def get_dossiers(client_id: int | None = Query(None), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Retourne tous les dossiers en cours et historiques du client B2B."""
    raise HTTPException(status_code=501, detail="Le portail B2B historique doit être migré vers les données métier persistées.")


@router.get("/factures", summary="Lister les factures du client B2B")
def get_factures(client_id: int | None = Query(None), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Retourne toutes les factures avec TVA 19.25% Cameroun et statut règlement."""
    raise HTTPException(status_code=501, detail="Le portail B2B historique doit être migré vers les données métier persistées.")


@router.post("/quotes", summary="Calculer une cotation instantanée fret & transit")
def calculate_quote(payload: Dict[str, Any] = Body(...)):
    """Calcule le tarif instantané fret, manutention, passage portuaire et assurance."""
    raise HTTPException(status_code=501, detail="Le calcul tarifaire doit utiliser les grilles persistées de la société.")


@router.post("/booking", summary="Créer une réservation e-Booking d'enlèvement conteneur")
def create_booking(payload: Dict[str, Any] = Body(...)):
    """Génère un bon de réservation e-Booking horodaté avec créneau terminal."""
    raise HTTPException(status_code=501, detail="La réservation doit être créée depuis une mission persistée.")


@router.get("/tracking/{query}", summary="Tracking conteneur ISO 6346 ou numéro de B/L")
def track_cargo(query: str):
    """Suivi multi-jalons du conteneur avec alerte franchise surestaries et géolocalisation."""
    raise HTTPException(status_code=501, detail="Le suivi public nécessite une référence de fret persistée.")


@router.post("/payments/checkout", summary="Paiement en ligne sécurisé (MoMo / Carte Bancaire)")
def process_checkout(payload: Dict[str, Any] = Body(...)):
    """Règlement direct de facture débloquant automatiquement le Bon de Sortie."""
    raise HTTPException(status_code=501, detail="Le paiement doit être relié à un fournisseur Mobile Money configuré.")


@router.get("/notifications/preferences", summary="Consulter les préférences de notifications")
def get_notification_preferences(client_id: int | None = Query(None), current_user: User = Depends(get_current_user)):
    """Retourne les canaux SMS, WhatsApp et Email activés pour les alertes statut."""
    raise HTTPException(status_code=501, detail="Les préférences B2B ne sont pas encore persistées.")


@router.put("/notifications/preferences", summary="Mettre à jour les préférences de notifications")
def update_notification_preferences(client_id: int | None = Query(None), payload: Dict[str, Any] = Body(...), current_user: User = Depends(get_current_user)):
    """Met à jour les seuils d'alerte et canaux de notification du chargeur."""
    raise HTTPException(status_code=501, detail="Les préférences B2B ne sont pas encore persistées.")
