"""Service metier superadmin deep : incidents plateforme ouverts
par priorite et licences logicielles expirees. Aucune donnee
invente."""
from datetime import date
from decimal import Decimal
from typing import Dict, Any

from sqlalchemy.orm import Session

from app.models.superadmin_deep import PlatformIncident, SoftwareLicense


class SuperadminDeepService:
    """Incidents et licences."""

    @staticmethod
    def incidents(db: Session) -> Dict[str, Any]:
        incidents = db.query(PlatformIncident).filter(
            PlatformIncident.is_active.is_(True)).all()
        if not incidents:
            return {"incidents": 0, "note": "Aucun incident."}
        ouverts = []
        par_priorite: Dict[str, int] = {}
        for i in incidents:
            statut = getattr(i.statut, "value", i.statut) or ""
            if "clos" in str(statut).lower() or "resolu" in str(statut).lower():
                continue
            p = getattr(i.priorite, "value", i.priorite) or "P?"
            par_priorite[p] = par_priorite.get(p, 0) + 1
            ouverts.append({
                "reference": i.reference,
                "titre": i.titre,
                "priorite": p,
                "date_debut": str(i.date_debut) if i.date_debut else None,
            })
        return {
            "incidents_total": len(incidents),
            "ouverts": len(ouverts),
            "par_priorite": par_priorite,
            "details_ouverts": ouverts,
        }

    @staticmethod
    def licences(db: Session) -> Dict[str, Any]:
        licences = db.query(SoftwareLicense).filter(
            SoftwareLicense.is_active.is_(True)).all()
        if not licences:
            return {"licences": 0, "note": "Aucune licence."}
        aujourdhui = date.today()
        actives = []
        expirees = []
        cotisation_totale = Decimal(0)
        for l in licences:
            statut = getattr(l.statut, "value", l.statut) or ""
            if l.cotisation_xaf:
                cotisation_totale += Decimal(str(l.cotisation_xaf))
            if l.date_fin and l.date_fin < aujourdhui and "expir" not in str(statut).lower() and "inact" not in str(statut).lower():
                expirees.append({
                    "reference": l.reference,
                    "module": l.module,
                    "date_fin": str(l.date_fin),
                    "statut": statut,
                })
            elif "actif" in str(statut).lower():
                actives.append(l.reference)
        return {
            "licences_total": len(licences),
            "actives": len(actives),
            "expirees": len(expirees),
            "cotisation_totale_xaf": float(cotisation_totale),
            "details_expirees": expirees,
        }
