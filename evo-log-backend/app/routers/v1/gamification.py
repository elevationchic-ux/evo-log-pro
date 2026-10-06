from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.utils.tenant import get_current_tenant_context, TenantContext
from app.models.transport import Conducteur, Mission, MissionStatus

router = APIRouter()


@router.get("/driver-scores")
def get_driver_gamification_scores(
    context: TenantContext = Depends(get_current_tenant_context),
    db: Session = Depends(get_db),
):
    """Classement conducteurs CALCULE depuis les missions reelles (achevement +
    ponctualite + distance). Aucun score ni badge invente.

    Limite honnete : l'eco-conduite (freinages/accelerations) exigerait un flux
    telematique par vehicule, non disponible ; le score porte donc uniquement sur
    des criteres observables en base (achevement et ponctualite)."""
    query = db.query(Mission)
    company_id = getattr(context.user, "company_id", None)
    if company_id is not None:
        query = query.filter(Mission.company_id == company_id)
    missions = query.filter(Mission.conducteur_id.isnot(None)).all()

    per_driver: dict[int, dict] = {}
    for m in missions:
        d = per_driver.setdefault(m.conducteur_id, {
            "missions": 0, "terminees": 0, "ponctuelles": 0, "distance_km": 0.0,
        })
        d["missions"] += 1
        if m.statut == MissionStatus.TERMINEE:
            d["terminees"] += 1
        if m.date_fin_reelle and m.date_fin_prevue and m.date_fin_reelle <= m.date_fin_prevue:
            d["ponctuelles"] += 1
        d["distance_km"] += float(m.distance_km or 0)

    drivers = {c.id: c for c in db.query(Conducteur).all()}
    ranking = []
    for cid, agg in per_driver.items():
        completion = agg["terminees"] / agg["missions"] if agg["missions"] else 0.0
        punctuality = agg["ponctuelles"] / agg["missions"] if agg["missions"] else 0.0
        # score 0-100 : 60 % ponctualite + 40 % achevement (criteres observes)
        score = round((0.6 * punctuality + 0.4 * completion) * 100, 1)
        drv = drivers.get(cid)
        ranking.append({
            "conducteur_id": cid,
            "nom": f"{drv.prenom} {drv.nom}".strip() if drv else None,
            "missions": agg["missions"],
            "terminees": agg["terminees"],
            "ponctuelles": agg["ponctuelles"],
            "taux_ponctualite": round(punctuality * 100, 1),
            "distance_km": round(agg["distance_km"], 1),
            "score": score,
        })

    ranking.sort(key=lambda r: r["score"], reverse=True)
    return {
        "classement": ranking,
        "methodes": {"part_ponctualite": 0.6, "part_achevement": 0.4},
        "eco_conduite": "indisponible (aucune ingestion telematique configuree)",
        "calcule_depuis_missions_reelles": True,
    }
