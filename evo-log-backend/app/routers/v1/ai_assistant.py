from fastapi import APIRouter
from typing import Optional
from pydantic import BaseModel

from app.core.not_implemented import not_implemented

router = APIRouter(tags=["AI Assistant"])


class ChatMessage(BaseModel):
    message: str
    context: Optional[str] = "GENERAL"  # GENERAL, TRANSPORT, MAGASIN, FINANCE, RH, QHSE
    user_id: Optional[str] = None


class FeedbackMessage(BaseModel):
    message_id: str
    rating: int  # 1-5
    commentaire: Optional[str] = None


@router.post("/chat")
def chat_with_ai(data: ChatMessage):
    """Assistant IA : reponses canonnees simulees. 501 tant qu'aucun LLM/raisonnement
    reel base sur les donnees du tenant n'est branche."""
    not_implemented(
        "Assistant conversationnel IA",
        "un veritable moteur IA (LLM ou analyse sur donnees reelles du tenant) ; "
        "les reponses precedentes etaient des gabarits avec chiffres inventes",
    )


@router.get("/history")
def get_chat_history(user_id: Optional[str] = None, limit: int = 20):
    """Historique de conversation : 501 (aucune persistance reelle des echanges)."""
    not_implemented(
        "Historique des conversations IA",
        "une table persistante des messages (le stock precedent etait en memoire "
        "volatile, perdu au redemarrage)",
    )


@router.post("/feedback")
def submit_feedback(data: FeedbackMessage):
    """Feedback : 501 (ne persistait rien, faux succes)."""
    not_implemented(
        "Enregistrement du feedback utilisateur",
        "une table d'audit/feedback pour tracer les notes (le message de succes "
        "etait retourne sans aucune ecriture)",
    )


@router.get("/suggestions")
def get_ai_suggestions(module: Optional[str] = None):
    """Suggestions contextuelles : 501 (liste codee en dur, non derivees du systeme)."""
    not_implemented(
        "Suggestions contextuelles automatiques",
        "un moteur de regles base sur l'etat reel (maintenance, stock, creance) "
        "au lieu des 4 suggestions codees en dur",
    )


@router.get("/kpis-summary")
def ai_kpis_summary():
    """Resume KPI temps reel : 501 (valeurs inventees, pas agregees depuis la DB)."""
    not_implemented(
        "Resume global des KPI",
        "des aggregations SQL reelles sur missions/stocks/factures/incidents "
        "(les chiffres retournes etaient des constantes)",
    )
