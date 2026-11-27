"""Service metier prestataires : homologation (agrement valide,
est_homologue), classement par notes, demandes de cotation par
statut et depassement de budget estime. Aucune donnee inventee."""
from decimal import Decimal
from typing import Dict, Any

from sqlalchemy.orm import Session

from app.models.prestataire import Prestataire, DemandeCotation


class PrestataireService:
    """Prestataires et cotations."""

    @staticmethod
    def homologues(db: Session, specialite: str = None) -> Dict[str, Any]:
        q = db.query(Prestataire).filter(Prestataire.est_actif.is_(True))
        if specialite:
            q = q.filter(Prestataire.specialite == specialite)
        prestataires = q.all()
        if not prestataires:
            return {"specialite": specialite, "prestataires": 0,
                    "note": "Aucun prestataire."}

        eligibles = []
        non_homologues = 0
        for p in prestataires:
            if p.est_homologue and (p.statut_agrement or "").upper() == "VALIDE":
                eligibles.append({
                    "code": p.code,
                    "raison_sociale": p.raison_sociale,
                    "note_globale": p.note_globale,
                    "taux_ponctualite": p.taux_ponctualite,
                    "ville": p.ville,
                })
            else:
                non_homologues += 1

        return {
            "specialite": specialite,
            "prestataires_total": len(prestataires),
            "homologues_valides": len(eligibles),
            "non_homologues": non_homologues,
            "par_niveau": sorted(eligibles, key=lambda x: -(x["note_globale"] or 0)),
        }

    @staticmethod
    def cotations(db: Session) -> Dict[str, Any]:
        demandes = db.query(DemandeCotation).all()
        if not demandes:
            return {"demandes": 0, "note": "Aucune demande de cotation."}

        par_statut: Dict[str, int] = {}
        en_attente = 0
        depassements_budget = []
        for d in demandes:
            s = d.statut or "EN_ATTENTE"
            par_statut[s] = par_statut.get(s, 0) + 1
            if s == "EN_ATTENTE":
                en_attente += 1
            if d.budget_max_estime and d.reponse_montant:
                if Decimal(str(d.reponse_montant)) > Decimal(str(d.budget_max_estime)):
                    depassements_budget.append({
                        "numero_dossier": d.numero_dossier,
                        "depassement": float(Decimal(str(d.reponse_montant)) - Decimal(str(d.budget_max_estime))),
                    })
        return {
            "demandes_total": len(demandes),
            "par_statut": par_statut,
            "en_attente": en_attente,
            "depassements_budget": len(depassements_budget),
            "details_depassements": depassements_budget,
        }
