from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(tags=["AI Assistant"])

class ChatMessage(BaseModel):
    message: str
    context: Optional[str] = "GENERAL"  # GENERAL, TRANSPORT, MAGASIN, FINANCE, RH, QHSE
    user_id: Optional[str] = None

class FeedbackMessage(BaseModel):
    message_id: str
    rating: int  # 1-5
    commentaire: Optional[str] = None

_conversation_history = []
_next_msg_id = 1

# Base de connaissances logistique EVO-LOG
_knowledge_base = {
    "TRANSPORT": {
        "missions_actives": 12,
        "chauffeurs_disponibles": 8,
        "flotte_totale": 25,
        "taux_ponctualite": "94.5%"
    },
    "MAGASIN": {
        "references_articles": 6,
        "taux_remplissage": "72%",
        "articles_critiques": 2,
        "mouvements_jour": 15
    },
    "FINANCE": {
        "factures_en_attente": 3,
        "montant_encaisse_mois_xaf": "45.000.000",
        "taux_recouvrement": "87%"
    }
}

def _generate_ai_response(message: str, context: str) -> str:
    """Génère une réponse contextuelle simulée pour l'assistant IA EVO-LOG"""
    msg_lower = message.lower()
    
    # Réponses contextuelles Transport
    if any(w in msg_lower for w in ["mission", "chauffeur", "camion", "transport", "livraison"]):
        return f"""**Assistant IA EVO-LOG – Module Transport**

Voici ce que je vois dans le système en temps réel :

📊 **Situation actuelle :**
- **12 missions actives** en cours de traitement
- **8 chauffeurs disponibles** sur 15 en service
- Flotte : **25 véhicules** (18 tracteurs, 7 remorques)
- Taux de ponctualité : **94.5%** ce mois

🚨 **Alertes en attente :**
- DLA-TRK-007 en maintenance (vidange moteur)
- Pneus usés sur DLA-TRK-001 (urgence)

💡 **Recommandations IA :**
- Affecter DLA-TRK-002 pour la prochaine mission vers N'Djamena
- Planifier le remplacement des pneus DLA-TRK-001 avant le 30/08/2026

*Voulez-vous créer une nouvelle mission ou consulter le dispatch ?*"""

    # Réponses contextuelles Magasin
    elif any(w in msg_lower for w in ["stock", "magasin", "inventaire", "conteneur", "palette"]):
        return f"""**Assistant IA EVO-LOG – Module WMS**

📦 **État des stocks en temps réel :**
- **6 références** articles cataloguées
- Taux de remplissage moyen : **72%**
- **2 articles en rupture critique** (pneus, pièces soudure)

🏭 **Zones actives :**
- YARD-A01 : 12/20 conteneurs 40ft occupés
- MAG3-C01 : 1240/2000 colis stockés
- CUVE-F01 : 8500L gasoil restants (42% capacité)

⚠️ **Alertes stock critique :**
- MAT-SOUDURE-006 : 4 kits restants (seuil: 5)

💡 **Action recommandée :** Déclencher un bon de commande pour le réapprovisionnement des consommables d'atelier.

*Souhaitez-vous créer un bon de mouvement ou une demande de réapprovisionnement ?*"""

    # Réponses Finance
    elif any(w in msg_lower for w in ["facture", "finance", "paiement", "trésorerie", "cotation", "devis"]):
        return f"""**Assistant IA EVO-LOG – Module Finance**

💰 **Situation financière du mois :**
- Encaissements : **45.000.000 XAF** réalisés
- Factures en attente : **3 dossiers** (total 6.850.000 XAF)
- Taux de recouvrement : **87%**

📋 **Actions requises :**
- Relance BOLLORE AFRICA LOGISTICS (FAC-2026-0187 – 30 jours)
- 2 cotations en attente de validation

💡 **Recommandation :** Déclencher une relance automatique par email pour les factures >30 jours.

*Voulez-vous générer un état de trésorerie ou une cotation fret ?*"""

    # Réponse générale
    else:
        return f"""**Assistant IA EVO-LOG** 🤖

Bonjour ! Je suis l'assistant intelligent de EVO-LOG ERP Port de Douala.

Je peux vous aider avec :
- 🚛 **Transport** : Missions, dispatch, flotte, chauffeurs
- 📦 **Magasin WMS** : Stocks, inventaires, mouvements
- 💰 **Finance** : Factures, cotations, trésorerie
- 🛂 **Transit** : Dossiers douaniers CEMAC
- 🔧 **Maintenance** : Ordres réparation, pièces
- 👥 **RH** : Employés, congés, paie
- 📊 **Analytics** : KPIs et tableaux de bord

**Message reçu :** *"{message}"*

Pouvez-vous préciser votre demande ? Je peux rechercher dans tous les modules actifs du système."""

@router.post("/chat")
def chat_with_ai(data: ChatMessage):
    global _next_msg_id
    msg_id = f"MSG-{datetime.now().strftime('%Y%m%d')}-{_next_msg_id:04d}"
    
    response = _generate_ai_response(data.message, data.context or "GENERAL")
    
    entry = {
        "id": msg_id,
        "user_message": data.message,
        "ai_response": response,
        "context": data.context,
        "timestamp": datetime.utcnow().isoformat(),
        "tokens_used": len(data.message.split()) * 2,  # Estimation
    }
    _conversation_history.insert(0, entry)
    _next_msg_id += 1
    
    return {
        "id": msg_id,
        "response": response,
        "context": data.context,
        "timestamp": entry["timestamp"],
    }

@router.get("/history")
def get_chat_history(user_id: Optional[str] = None, limit: int = 20):
    results = _conversation_history[:limit]
    return {"total": len(_conversation_history), "messages": results}

@router.post("/feedback")
def submit_feedback(data: FeedbackMessage):
    return {
        "message": "Feedback enregistré. Merci pour votre retour !",
        "message_id": data.message_id,
        "rating": data.rating
    }

@router.get("/suggestions")
def get_ai_suggestions(module: Optional[str] = None):
    """Suggestions contextuelles basées sur l'état du système"""
    suggestions = [
        {"titre": "Planifier maintenance DLA-TRK-007", "priorite": "URGENTE", "module": "MAINTENANCE", "action": "Créer ordre réparation"},
        {"titre": "Réapprovisionner pneus poids lourds", "priorite": "HAUTE", "module": "PROCUREMENT", "action": "Créer bon commande"},
        {"titre": "Relancer facture BOLLORE 30j", "priorite": "HAUTE", "module": "FINANCE", "action": "Envoyer relance"},
        {"titre": "Dossier CEMAC-2026-087 en attente paiement", "priorite": "NORMALE", "module": "TRANSIT", "action": "Suivre dossier"},
    ]
    if module:
        suggestions = [s for s in suggestions if s["module"].upper() == module.upper()]
    return {"suggestions": suggestions}

@router.get("/kpis-summary")
def ai_kpis_summary():
    """Résumé KPIs global pour l'assistant IA"""
    return {
        "score_sante_global": 87,
        "alertes_critiques": 2,
        "missions_en_cours": 12,
        "stocks_critiques": 2,
        "factures_impayees": 3,
        "incidents_ouverts": 2,
        "last_updated": datetime.utcnow().isoformat(),
    }
