from fastapi import APIRouter, Depends
from app.utils.tenant import get_current_tenant_context, TenantContext, require_module_access
from app.core.not_implemented import not_implemented

router = APIRouter()

# Jumeau numerique du parc : l'etat retourne precedemment (150 slots, 112
# occupee, zones A/B/C avec temperatures) etait fabrique en dur. Aucune table
# de slots/emplacement parc ni aucun flux de localisation temps reel n'existe
# en base. La route renvoie donc explicitement 501 au lieu d'un faux succes.


@router.get("/yard-state", dependencies=[Depends(require_module_access("parc"))])
def get_digital_twin_yard_state(context: TenantContext = Depends(get_current_tenant_context)):
    """Etat du parc (jumeau numerique) : 501 (occupation inventee, aucun capteur)."""
    not_implemented(
        "Jumeau numerique 2D/3D de l'etat du parc (slots et zones)",
        "une table d'emplacements/slots de parc alimentee reellement par les "
        "operations d'entree/sortie, plus un flux de localisation temps reel "
        "(les capacites et taux d'occupation retournes etaient codes en dur)",
    )
