from fastapi import APIRouter, Depends
from app.utils.tenant import get_current_tenant_context, TenantContext
from app.core.not_implemented import not_implemented

router = APIRouter()

# Classement "gamification" conducteurs : les scores (Kamga 98/95, Nguema
# 94/91...) et badges etaient inventes en dur. Aucune table de scores eco-conduite
# ni de badges n'existe, et aucun flux telematique n'alimente ces note. La route
# renvoie explicitement 501 au lieu d'un faux succes.


@router.get("/driver-scores")
def get_driver_gamification_scores(context: TenantContext = Depends(get_current_tenant_context)):
    """Scores conducteurs : 501 (classement fabrique, aucune donnee telematique)."""
    not_implemented(
        "Classement gamification des conducteurs (scores et badges)",
        "une ingestion telematique reelle par vehicule (eco-conduite, freinages, "
        "ponctualite) et des agregations persistees par conducteur "
        "(les scores et badges retournes etaient codes en dur)",
    )
