"""Service metier annuaire prestataires : score moyen d'evaluation,
certifications et assurances expirees, incidents ouverts.
Aucune donnee inventee."""
from datetime import date
from typing import Dict, Any

from sqlalchemy.orm import Session

from app.models.annuaire_d_deep import (
    ProvEvaluation, ProvCertification, ProvInsuranceAttestation, ProvIncident)


class AnnuaireService:
    """Annuaire prestataires."""

    @staticmethod
    def performance(db: Session) -> Dict[str, Any]:
        evals = db.query(ProvEvaluation).filter(
            ProvEvaluation.is_active.is_(True)).all()
        if not evals:
            return {"evaluations": 0, "note": "Aucune evaluation."}
        par_prestataire: Dict[str, list] = {}
        for e in evals:
            if e.score is not None and e.prestataire:
                par_prestataire.setdefault(e.prestataire, []).append(e.score)
        moyennes = {
            p: round(sum(scores) / len(scores), 1)
            for p, scores in par_prestataire.items()
        }
        return {
            "evaluations_total": len(evals),
            "prestataires_evalues": len(moyennes),
            "score_moyen_global": round(
                sum(moyennes.values()) / len(moyennes), 1) if moyennes else None,
            "par_prestataire": moyennes,
        }

    @staticmethod
    def documents_expires(db: Session) -> Dict[str, Any]:
        aujourdhui = date.today()
        certs = db.query(ProvCertification).filter(
            ProvCertification.is_active.is_(True),
            ProvCertification.expire_le.isnot(None)).all()
        assurances = db.query(ProvInsuranceAttestation).filter(
            ProvInsuranceAttestation.is_active.is_(True),
            ProvInsuranceAttestation.expire_le.isnot(None)).all()

        certs_expires = [c for c in certs if c.expire_le < aujourdhui]
        assurances_expires = [a for a in assurances if a.expire_le < aujourdhui]
        return {
            "certifications_total": len(certs),
            "certifications_expirees": len(certs_expires),
            "assurances_total": len(assurances),
            "assurances_expirees": len(assurances_expires),
            "prestataires_a_risque": sorted(
                {c.prestataire for c in certs_expires if c.prestataire} |
                {a.prestataire for a in assurances_expires if a.prestataire}
            ),
        }

    @staticmethod
    def incidents_ouverts(db: Session) -> Dict[str, Any]:
        incidents = db.query(ProvIncident).filter(
            ProvIncident.is_active.is_(True)).all()
        if not incidents:
            return {"incidents": 0, "note": "Aucun incident."}
        ouverts = [i for i in incidents
                   if "clos" not in str(i.statut or "").lower()
                   and "resolu" not in str(i.statut or "").lower()]
        return {
            "incidents_total": len(incidents),
            "ouverts": len(ouverts),
            "par_prestataire": {
                p: sum(1 for i in ouverts if i.prestataire == p)
                for p in {i.prestataire for i in ouverts if i.prestataire}
            },
        }
