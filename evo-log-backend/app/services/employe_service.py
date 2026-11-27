"""Service metier employe : suivi des conges (jours consommes par
collaborateur/type, solde vs droit fourni par parametre — jamais
invente) et temps par projet depuis les pointages. Aucune donnee
inventee."""
from datetime import date
from typing import Dict, Any

from sqlalchemy.orm import Session

from app.models.employe_d_deep import EmpLeaveRequest, EmpTimesheetEntry


class EmployeService:
    """RH employe."""

    @staticmethod
    def solde_conges(db: Session, collaborateur: str, droit_annuel: int = 30) -> Dict[str, Any]:
        demandes = db.query(EmpLeaveRequest).filter(
            EmpLeaveRequest.collaborateur == collaborateur,
            EmpLeaveRequest.is_active.is_(True),
        ).all()
        consommes = sum(d.jours or 0 for d in demandes
                        if (d.statut or "").lower() in ("approuve", "valide"))
        en_attente = sum(d.jours or 0 for d in demandes
                         if (d.statut or "").lower() in ("soumis", "en_attente", "demande"))
        return {
            "collaborateur": collaborateur,
            "droit_annuel_jours": droit_annuel,
            "jours_consommes": consommes,
            "jours_en_attente": en_attente,
            "solde_jours": droit_annuel - consommes,
            "note": "Droit annuel fourni par parametre : non deduit du referentiel RH.",
        }

    @staticmethod
    def temps_par_projet(db: Session, collaborateur: str) -> Dict[str, Any]:
        pointages = db.query(EmpTimesheetEntry).filter(
            EmpTimesheetEntry.collaborateur == collaborateur,
            EmpTimesheetEntry.is_active.is_(True),
        ).all()
        if not pointages:
            return {"collaborateur": collaborateur, "pointages": 0,
                    "note": "Aucun pointage enregistre."}
        par_projet: Dict[str, float] = {}
        for p in pointages:
            proj = p.projet or "sans_projet"
            par_projet[proj] = par_projet.get(proj, 0.0) + float(p.heures or 0)
        return {
            "collaborateur": collaborateur,
            "pointages": len(pointages),
            "heures_par_projet": par_projet,
            "heures_total": round(sum(par_projet.values()), 2),
        }
