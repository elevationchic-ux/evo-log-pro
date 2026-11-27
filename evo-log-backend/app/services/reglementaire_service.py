"""Service metier reglementaire : reglementations applicables
(date_application atteinte) et a venir, groupees par categorie.
Aucune donnee inventee."""
from datetime import date
from typing import Dict, Any

from sqlalchemy.orm import Session

from app.models.reglementaire import Reglementation


class ReglementaireService:
    """Reglementations applicables."""

    @staticmethod
    def applicables(db: Session) -> Dict[str, Any]:
        regs = db.query(Reglementation).filter(
            Reglementation.est_actif.is_(True)).all()
        aujourdhui = date.today()

        en_vigueur = []
        a_venir = []
        for r in regs:
            item = {
                "code": r.code,
                "titre": r.titre,
                "categorie": r.categorie,
                "date_application": str(r.date_application),
            }
            if r.date_application <= aujourdhui:
                en_vigueur.append(item)
            else:
                a_venir.append(item)

        par_categorie: Dict[str, int] = {}
        for r in en_vigueur:
            c = r["categorie"] or "autre"
            par_categorie[c] = par_categorie.get(c, 0) + 1

        return {
            "en_vigueur": len(en_vigueur),
            "a_venir": len(a_venir),
            "par_categorie": par_categorie,
            "details_a_venir": a_venir,
        }
