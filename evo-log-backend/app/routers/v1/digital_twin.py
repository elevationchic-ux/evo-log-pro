from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.utils.tenant import get_current_tenant_context, TenantContext, require_module_access
from app.models.parc import ZoneParc, EmplacementParc, MouvementParc

router = APIRouter()


def _company_scope(context: TenantContext, query, model):
    company_id = getattr(context.user, "company_id", None)
    if company_id is not None:
        return query.filter(model.company_id == company_id)
    return query


@router.get("/yard-state", dependencies=[Depends(require_module_access("parc"))])
def get_digital_twin_yard_state(
    context: TenantContext = Depends(get_current_tenant_context),
    db: Session = Depends(get_db),
):
    """Jumeau numerique du parc AGGE depuis les tables reelles : zones,
    emplacements (statut libre/occupe/reserve/bloque) et mouvements gate in/out.
    Aucune capacite n'est inventee : tout provient de la base."""
    zones_q = _company_scope(context, db.query(ZoneParc), ZoneParc).filter(ZoneParc.is_active == True)
    zones = zones_q.all()

    emp_statuts = dict(
        _company_scope(
            context,
            db.query(EmplacementParc.statut, func.count(EmplacementParc.id)),
            EmplacementParc,
        ).filter(EmplacementParc.is_active == True).group_by(EmplacementParc.statut).all()
    )
    total_emp = sum(emp_statuts.values())
    occupation_pct = round((emp_statuts.get("occupe", 0) / total_emp) * 100, 1) if total_emp else 0.0

    mvts = dict(
        _company_scope(
            context,
            db.query(MouvementParc.sens, func.count(MouvementParc.id)),
            MouvementParc,
        ).group_by(MouvementParc.sens).all()
    )

    zones_out = [
        {
            "id": z.id,
            "code": z.code,
            "nom": z.nom,
            "type_zone": z.type_zone,
            "capacite": z.capacite or 0,
            "statut": z.statut,
        }
        for z in zones
    ]

    return {
        "zones": zones_out,
        "total_zones": len(zones_out),
        "emplacements": {
            "total": total_emp,
            "par_statut": emp_statuts,
            "taux_occupation_pct": occupation_pct,
        },
        "mouvements": {"entree": mvts.get("entree", 0), "sortie": mvts.get("sortie", 0)},
        "agrege_depuis_la_base": True,
    }
