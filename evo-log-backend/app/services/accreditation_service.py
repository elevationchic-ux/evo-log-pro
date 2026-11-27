"""Service metier accreditation : habilitations expirees (date_fin
passee, statut actif) et repartition par type. Aucune donnee
invente."""
from datetime import date
from typing import Dict, Any

from sqlalchemy.orm import Session

from app.models.accreditation import Accreditation


class AccreditationService:
    """Habilitations et accreditations."""

    @staticmethod
    def accreditations(db: Session) -> Dict[str, Any]:
        accs = db.query(Accreditation).all()
        if not accs:
            return {"accreditations": 0, "note": "Aucune accreditation."}
        aujourdhui = date.today()
        par_type: Dict[str, int] = {}
        expirees = []
        actives = 0
        for a in accs:
            t = a.type or "inconnu"
            par_type[t] = par_type.get(t, 0) + 1
            if (a.statut or "").lower() not in ("actif", "active"):
                continue
            if a.date_fin and a.date_fin < aujourdhui:
                expirees.append({
                    "code": a.code,
                    "libelle": a.libelle,
                    "date_fin": str(a.date_fin),
                })
            else:
                actives += 1
        return {
            "accreditations_total": len(accs),
            "actives": actives,
            "expirees_a_renouveler": len(expirees),
            "par_type": par_type,
            "details_expirees": expirees,
        }
