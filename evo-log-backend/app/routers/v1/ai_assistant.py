from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.config import settings
from app.utils.tenant import get_current_tenant_context, TenantContext
from app.utils.llm import llm_available, ask_llm
from app.models.advanced_crud import AIChatMessage, AIFeedback
from app.models.transport import Mission, Camion, MissionStatus, CamionStatus
from app.models.magasin import Stock
from app.models.finance import Facture, FactureStatus

router = APIRouter(tags=["AI Assistant"])


class ChatMessage(BaseModel):
    message: str
    context: Optional[str] = "GENERAL"  # GENERAL, TRANSPORT, MAGASIN, FINANCE, RH, QHSE
    session_id: Optional[str] = None


class FeedbackMessage(BaseModel):
    message_id: int
    rating: int  # 1-5
    commentaire: Optional[str] = None


@router.post("/chat")
def chat_with_ai(
    data: ChatMessage,
    context: TenantContext = Depends(get_current_tenant_context),
    db: Session = Depends(get_db),
):
    """Assistant conversationnel : appel REEL au fournisseur LLM configure.

    Aucun LLM configure => 503 explicite (aucune reponse inventee). Quand il est
    present, la question et la reponse sont toutes deux persistees dans
    l'historique."""
    if not llm_available():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Aucun fournisseur LLM configure (AI_ENABLED/AI_PROVIDER/AI_API_KEY). "
                "Aucune reponse n'est simulee."
            ),
        )
    try:
        answer = ask_llm(data.message, system=f"Contexte module : {data.context}.")
    except Exception as exc:  # reseau / API : on ne fabrique pas de reponse
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Echec d'appel au fournisseur LLM : {exc}",
        )
    msg = AIChatMessage(
        organization_id=context.organization_id,
        session_id=data.session_id,
        user_id=context.user.id,
        module=data.context,
        question=data.message,
        reponse_generee=answer,
        provider=settings.AI_PROVIDER,
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return {"message_id": msg.id, "reponse": answer, "provider": msg.provider, "reel": True}


@router.get("/history")
def get_chat_history(
    session_id: Optional[str] = None,
    limit: int = 20,
    context: TenantContext = Depends(get_current_tenant_context),
    db: Session = Depends(get_db),
):
    """Historique reel : messages lus en base, filtres par tenant."""
    query = db.query(AIChatMessage)
    if context.organization_id is not None:
        query = query.filter(AIChatMessage.organization_id == context.organization_id)
    if session_id:
        query = query.filter(AIChatMessage.session_id == session_id)
    rows = query.order_by(AIChatMessage.cree_le.desc()).limit(max(1, min(limit, 200))).all()
    return [
        {
            "id": m.id,
            "question": m.question,
            "reponse": m.reponse_generee,
            "module": m.module,
            "provider": m.provider,
            "date": m.cree_le.isoformat() if m.cree_le else None,
        }
        for m in rows
    ]


@router.post("/feedback")
def submit_feedback(
    data: FeedbackMessage,
    context: TenantContext = Depends(get_current_tenant_context),
    db: Session = Depends(get_db),
):
    """Feedback reellement persiste (audit des notes)."""
    if not (1 <= data.rating <= 5):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail="Note comprise entre 1 et 5")
    fb = AIFeedback(
        organization_id=context.organization_id,
        message_id=data.message_id,
        note=data.rating,
        commentaire=data.commentaire,
        utilisateur_id=context.user.id,
    )
    db.add(fb)
    db.commit()
    db.refresh(fb)
    return {"feedback_id": fb.id, "message_id": fb.message_id, "note": fb.note, "persiste": True}


def _company_id(context: TenantContext):
    return getattr(context.user, "company_id", None)


@router.get("/suggestions")
def get_ai_suggestions(
    module: Optional[str] = None,
    context: TenantContext = Depends(get_current_tenant_context),
    db: Session = Depends(get_db),
):
    """Suggestions DERIVEES DE L'ETAT REEL du systeme (maintenance due, ruptures,
    creances en retard). Rien n'est code en dur."""
    cid = _company_id(context)
    now = datetime.utcnow()
    suggestions = []

    if module in (None, "TRANSPORT", "PARC"):
        maint_q = db.query(func.count(Camion.id)).filter(
            Camion.prochaine_maintenance.isnot(None),
            Camion.prochaine_maintenance <= now,
            Camion.status != CamionStatus.IN_MAINTENANCE,
        )
        if cid is not None:
            maint_q = maint_q.filter(Camion.company_id == cid)
        n_maint = maint_q.scalar() or 0
        if n_maint:
            suggestions.append({
                "module": "PARC", "priorite": "haute",
                "signal": f"{n_maint} vehicle(s) ont une maintenance echue",
                "action": "Planifier les maintenances preventives en retard",
            })

    if module in (None, "MAGASIN"):
        rupture_q = db.query(func.count(Stock.id)).filter(Stock.quantite_disponible <= 0)
        if cid is not None:
            rupture_q = rupture_q.filter(Stock.company_id == cid)
        n_rupture = rupture_q.scalar() or 0
        if n_rupture:
            suggestions.append({
                "module": "MAGASIN", "priorite": "haute",
                "signal": f"{n_rupture} reference(s) en rupture de stock",
                "action": "Declencher reapprovisionnement / commandes fournisseurs",
            })

    if module in (None, "FINANCE"):
        creance_q = db.query(
            func.count(Facture.id), func.sum(Facture.montant_ttc)
        ).filter(
            Facture.statut.in_([FactureStatus.EMISE, FactureStatus.RETARD, FactureStatus.PAYEE_PARTIELLEMENT]),
            Facture.date_echeance.isnot(None),
            Facture.date_echeance < now.date(),
        )
        if cid is not None:
            creance_q = creance_q.filter(Facture.company_id == cid)
        n_cre, montant = creance_q.one()
        if n_cre:
            suggestions.append({
                "module": "FINANCE", "priorite": "moyenne",
                "signal": f"{n_cre} facture(s) echues ({float(montant or 0):.0f} XAF)",
                "action": "Lancer la relance client / recouvrement",
            })

    return {"derived_from_live_state": True, "suggestions": suggestions}


@router.get("/kpis-summary")
def ai_kpis_summary(
    context: TenantContext = Depends(get_current_tenant_context),
    db: Session = Depends(get_db),
):
    """Resume global des KPI : aggregations SQL REELLES (missions, flotte, stock,
    creances). Aucune constante inventee."""
    cid = _company_id(context)

    def scoped(q, model):
        return q.filter(model.company_id == cid) if cid is not None else q

    missions_total = scoped(db.query(func.count(Mission.id)), Mission).scalar() or 0
    missions_en_cours = scoped(
        db.query(func.count(Mission.id)), Mission
    ).filter(Mission.statut == MissionStatus.EN_COURS).scalar() or 0

    flotte_total = scoped(db.query(func.count(Camion.id)), Camion).scalar() or 0
    flotte_active = scoped(
        db.query(func.count(Camion.id)), Camion
    ).filter(Camion.status == CamionStatus.ACTIVE).scalar() or 0

    stock_total = scoped(db.query(func.sum(Stock.quantite_disponible)), Stock).scalar() or 0

    now = datetime.utcnow().date()
    creances = scoped(
        db.query(func.sum(Facture.montant_ttc)), Facture
    ).filter(
        Facture.statut.in_([FactureStatus.EMISE, FactureStatus.RETARD, FactureStatus.PAYEE_PARTIELLEMENT]),
        Facture.date_echeance.isnot(None),
        Facture.date_echeance < now,
    ).scalar() or 0

    return {
        "missions": {"total": missions_total, "en_cours": missions_en_cours},
        "flotte": {"total": flotte_total, "active": flotte_active},
        "magasin": {"quantite_disponible": float(stock_total)},
        "finance": {"creances_echues_xaf": float(creances)},
        "agrege_depuis_la_base": True,
    }
