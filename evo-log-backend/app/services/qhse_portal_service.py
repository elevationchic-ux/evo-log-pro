"""Service metier portail QHSE : permis de travail par statut,
formations expirees (validite passee) et deversements par statut.
Aucune donnee inventee."""
from datetime import date
from typing import Dict, Any

from sqlalchemy.orm import Session

from app.models.qhse_portal_d_deep import (
    QspWorkPermitRequest, QspSafetyTrainingLog, QspSpillReport)


class QhsePortalService:
    """Portail QHSE terrain."""

    @staticmethod
    def permis(db: Session) -> Dict[str, Any]:
        permis = db.query(QspWorkPermitRequest).filter(
            QspWorkPermitRequest.is_active.is_(True)).all()
        if not permis:
            return {"permis": 0, "note": "Aucun permis."}
        par_statut: Dict[str, int] = {}
        actifs = 0
        for p in permis:
            s = p.statut or "sans_statut"
            par_statut[s] = par_statut.get(s, 0) + 1
            if s.lower() in ("actif", "approuve", "valide", "en_cours"):
                actifs += 1
        return {
            "permis_total": len(permis),
            "actifs": actifs,
            "par_statut": par_statut,
        }

    @staticmethod
    def formations(db: Session) -> Dict[str, Any]:
        formations = db.query(QspSafetyTrainingLog).filter(
            QspSafetyTrainingLog.is_active.is_(True)).all()
        if not formations:
            return {"formations": 0, "note": "Aucune formation."}
        aujourdhui = date.today()
        expirees = []
        for f in formations:
            if f.validite and f.validite < aujourdhui:
                expirees.append({
                    "reference": f.reference,
                    "operateur": f.operateur,
                    "formation": f.formation,
                    "validite": str(f.validite),
                })
        return {
            "formations_total": len(formations),
            "expirees": len(expirees),
            "details_expirees": expirees,
        }

    @staticmethod
    def deversements(db: Session) -> Dict[str, Any]:
        spills = db.query(QspSpillReport).filter(
            QspSpillReport.is_active.is_(True)).all()
        if not spills:
            return {"deversements": 0, "note": "Aucun deversement."}
        par_statut: Dict[str, int] = {}
        non_resolus = 0
        for s in spills:
            st = s.statut or "sans_statut"
            par_statut[st] = par_statut.get(st, 0) + 1
            if st.lower() not in ("resolu", "clos", "cloture", "traite"):
                non_resolus += 1
        return {
            "deversements_total": len(spills),
            "non_resolus": non_resolus,
            "par_statut": par_statut,
        }
