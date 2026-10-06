from datetime import date, datetime, timedelta
from typing import List, Optional, Dict, Any

from fastapi import APIRouter, Depends, status
from sqlalchemy import func, and_, or_, extract
from sqlalchemy.orm import Session

from app.database import get_db
from app.utils.tenant import get_current_tenant_context, TenantContext, require_module_access
from app.models.transport import Mission, Camion, MissionStatus, CamionStatus
from app.models.magasin import Stock
from app.models.advanced_crud import ScheduledReport

router = APIRouter()


def _company_filter(context: TenantContext, query, model):
    """Scoping metier reel : les modeles transport/magasin sont tenants par
    company_id. Un user rattache a une company ne voit que son perimetre."""
    company_id = getattr(context.user, "company_id", None)
    if company_id is not None:
        return query.filter(model.company_id == company_id)
    return query


def _period_range(period: str) -> tuple[date, date]:
    p = (period or "THIS_MONTH").upper()
    today = date.today()
    if p == "LAST_7_DAYS":
        return today - timedelta(days=7), today
    if p == "THIS_YEAR":
        return date(today.year, 1, 1), date(today.year, 12, 31)
    if p == "LAST_MONTH":
        first = today.replace(day=1)
        last_prev = first - timedelta(days=1)
        return last_prev.replace(day=1), last_prev
    if p == "THIS_QUARTER":
        q_start_month = ((today.month - 1) // 3) * 3 + 1
        start = date(today.year, q_start_month, 1)
        end_month = q_start_month + 2
        end = date(today.year, end_month, 28)
        while (end + timedelta(days=1)).month == end_month:
            end += timedelta(days=1)
        return start, end
    # THIS_MONTH (default)
    first = today.replace(day=1)
    nxt = (first + timedelta(days=32)).replace(day=1)
    return first, nxt - timedelta(days=1)


@router.get("/dashboard-custom", dependencies=[Depends(require_module_access("bi"))])
def get_custom_bi_dashboard(
    period: str = "THIS_MONTH",
    context: TenantContext = Depends(get_current_tenant_context),
    db: Session = Depends(get_db),
):
    """Tableau de bord exec. : aggregations SQL REELLES sur missions/flotte/stock."""
    debut, fin = _period_range(period)
    d0 = datetime.combine(debut, datetime.min.time())
    d1 = datetime.combine(fin, datetime.max.time())

    m_base = _company_filter(context, db.query(Mission), Mission).filter(
        Mission.date_debut_prevue >= d0, Mission.date_debut_prevue <= d1
    )
    missions_total = m_base.count()
    par_statut = dict(
        db.query(Mission.statut, func.count(Mission.id))
        .filter(Mission.date_debut_prevue >= d0, Mission.date_debut_prevue <= d1)
        .group_by(Mission.statut).all()
    )
    par_statut = {
        (s.value if hasattr(s, "value") else str(s)): c for s, c in par_statut.items()
    }
    total_km = float(m_base.with_entities(func.sum(Mission.distance_km)).scalar() or 0)
    cout_reel = float(m_base.with_entities(func.sum(Mission.cout_reel)).scalar() or 0)

    cam_base = _company_filter(context, db.query(Camion.status, func.count(Camion.id)), Camion).group_by(Camion.status)
    dispo = dict(cam_base.all())
    dispo = {(s.value if hasattr(s, "value") else str(s)): c for s, c in dispo.items()}

    stock_q = _company_filter(context, db.query(func.sum(Stock.quantite_disponible)), Stock).scalar() or 0
    ruptures = _company_filter(
        context, db.query(func.count(Stock.id)), Stock
    ).filter(Stock.quantite_disponible <= 0).scalar() or 0

    return {
        "periode": period,
        "bornes": {"debut": debut.isoformat(), "fin": fin.isoformat()},
        "transport": {
            "missions_total": missions_total,
            "par_statut": par_statut,
            "total_distance_km": round(total_km, 2),
            "cout_reel_total": round(cout_reel, 2),
        },
        "flotte": {"par_status": dispo, "total": sum(dispo.values())},
        "magasin": {"quantite_disponible": float(stock_q), "articles_en_rupture": int(ruptures)},
        "agrege_depuis_la_base": True,
    }


class ScheduledExportSchema(_ := object):  # placeholder replaced below
    pass


from pydantic import BaseModel, Field


class ScheduledExportSchema(BaseModel):  # type: ignore[no-redef]
    report_name: str = Field(..., example="Rapport Mensuel d'Exploitation Transport & Magasin")
    format: str = Field("PDF", example="PDF")  # PDF, EXCEL, CSV
    frequency: str = Field("MONTHLY", example="MONTHLY")  # DAILY, WEEKLY, MONTHLY
    recipients: List[str] = Field(..., example=["direction@tce-logistics.cm"])


def _next_run(frequency: str) -> datetime:
    now = datetime.utcnow()
    f = (frequency or "MONTHLY").upper()
    if f == "DAILY":
        return now + timedelta(days=1)
    if f == "WEEKLY":
        return now + timedelta(weeks=1)
    return now + timedelta(days=30)


@router.post("/scheduled-reports", status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_module_access("bi"))])
def schedule_bi_export(
    payload: ScheduledExportSchema,
    context: TenantContext = Depends(get_current_tenant_context),
    db: Session = Depends(get_db),
):
    """Planification reellement persistee en base (table scheduled_reports)."""
    job = ScheduledReport(
        organization_id=context.organization_id,
        cree_par=getattr(context.user, "id", None),
        report_name=payload.report_name,
        format=payload.format,
        frequency=payload.frequency,
        recipients=payload.recipients,
        actif=True,
        prochaine_execution=_next_run(payload.frequency),
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return {
        "id": job.id,
        "report_name": job.report_name,
        "format": job.format,
        "frequency": job.frequency,
        "recipients": job.recipients,
        "prochaine_execution": job.prochaine_execution.isoformat() if job.prochaine_execution else None,
        "persiste": True,
    }


@router.get("/scheduled-reports", dependencies=[Depends(require_module_access("bi"))])
def list_scheduled_reports(
    context: TenantContext = Depends(get_current_tenant_context),
    db: Session = Depends(get_db),
):
    """Liste des taches planifiees lues en base (filtre tenant)."""
    query = db.query(ScheduledReport)
    if context.organization_id is not None:
        query = query.filter(ScheduledReport.organization_id == context.organization_id)
    return [
        {
            "id": j.id,
            "report_name": j.report_name,
            "format": j.format,
            "frequency": j.frequency,
            "recipients": j.recipients,
            "actif": j.actif,
            "prochaine_execution": j.prochaine_execution.isoformat() if j.prochaine_execution else None,
        }
        for j in query.order_by(ScheduledReport.created_at.desc()).all()
    ]


@router.post("/predictive/flux-saisonniers", dependencies=[Depends(require_module_access("bi"))])
def predire_flux_saisonniers(
    payload: dict = None,
    context: TenantContext = Depends(get_current_tenant_context),
    db: Session = Depends(get_db),
):
    """Prevision de flux par INDEX SAISONNIER calcule sur l'historique REEL des
    missions (moyenne mensuelle / moyenne globale). Aucune valeur inventee : si
    l'historique est vide, l'indice vaut 1.0 et la prevision vaut 0."""
    nb_mois = int((payload or {}).get("historique_mois", 24))
    depuis = datetime.utcnow() - timedelta(days=nb_mois * 31)
    base = _company_filter(
        context,
        db.query(
            extract("year", Mission.date_debut_prevue).label("an"),
            extract("month", Mission.date_debut_prevue).label("mois"),
            func.count(Mission.id).label("n"),
        ),
        Mission,
    ).filter(Mission.date_debut_prevue >= depuis).group_by("an", "mois")
    rows = base.all()

    par_mois: Dict[int, List[int]] = {m: [] for m in range(1, 13)}
    valeurs = []
    for an, mois, n in rows:
        if mois is None:
            continue
        par_mois[int(mois)].append(int(n))
        valeurs.append(int(n))

    moyenne_globale = (sum(valeurs) / len(valeurs)) if valeurs else 0.0
    indices = {}
    for mois, lst in par_mois.items():
        moy = (sum(lst) / len(lst)) if lst else moyenne_globale
        indices[mois] = round((moy / moyenne_globale), 3) if moyenne_globale else 1.0

    target = (payload or {}).get("mois_cible")
    prevision = None
    if target and moyenne_globale:
        prevision = round(moyenne_globale * indices.get(int(target), 1.0))

    return {
        "historique_mois": nb_mois,
        "points_historiques": len(valeurs),
        "moyenne_mensuelle_reelle": round(moyenne_globale, 2),
        "indice_saisonnier": indices,
        "mois_cible": target,
        "prevision": prevision,
        "methode": "index saisonnaire sur agregation SQL reelle",
        "base_historique_suffisante": len(valeurs) >= 3,
    }


def _quarter_range(dim: str) -> Optional[tuple[date, date]]:
    try:
        an, q = dim.upper().split("-Q")
        an = int(an)
        q = int(q)
        start_month = (q - 1) * 3 + 1
        debut = date(an, start_month, 1)
        fin = date(an, start_month + 2, 28)
        while (fin + timedelta(days=1)).month == start_month + 2:
            fin += timedelta(days=1)
        return debut, fin
    except (ValueError, AttributeError):
        return None


@router.get("/olap/star-schema-query", dependencies=[Depends(require_module_access("bi"))])
def interroger_cube_olap(
    dimension_temps: str = "2026-Q1",
    dimension_corridor: str = "",
    context: TenantContext = Depends(get_current_tenant_context),
    db: Session = Depends(get_db),
):
    """Cube OLAP reel : mesures agregees SQL sur la table de faits (missions),
    decoupees par dimension temps et corridor (point_depart/point_arrivee)."""
    q = _quarter_range(dimension_temps)
    query = _company_filter(context, db.query(Mission), Mission)
    if q:
        d0 = datetime.combine(q[0], datetime.min.time())
        d1 = datetime.combine(q[1], datetime.max.time())
        query = query.filter(Mission.date_debut_prevue >= d0, Mission.date_debut_prevue <= d1)

    corridor_filtre = False
    if dimension_corridor:
        tokens = [t for t in dimension_corridor.upper().split("_") if t]
        if len(tokens) >= 2:
            dep, arr = tokens[0], tokens[1]
            query = query.filter(
                and_(
                    Mission.point_depart.ilike(f"%{dep}%"),
                    Mission.point_arrivee.ilike(f"%{arr}%"),
                )
            )
            corridor_filtre = True

    rows = query.all()
    measures = {
        "nombre_missions": len(rows),
        "somme_distance_km": round(float(sum(float(m.distance_km or 0) for m in rows)), 2),
        "somme_cout_reel": round(float(sum(float(m.cout_reel or 0) for m in rows)), 2),
        "camions_distincts": len({m.camion_id for m in rows if m.camion_id}),
        "conducteurs_distincts": len({m.conducteur_id for m in rows if m.conducteur_id}),
    }
    return {
        "dimensions": {"temps": dimension_temps, "corridor": dimension_corridor or None},
        "corridor_applique": corridor_filtre,
        "mesures": measures,
        "source": "missions (table de faits)",
    }
