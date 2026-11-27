"""Service metier paie : cumuls annuels par salarie (brut, retenues
impot, net) et masse salariale mensuelle. Aucune donnee inventee :
seuls les salaires payes comptent."""
from decimal import Decimal
from typing import Dict, Any

from sqlalchemy.orm import Session

from app.models.rh import Salaire


class PaieService:
    """Cumuls paie."""

    @staticmethod
    def cumuls_annuels(db: Session, annee: int = None) -> Dict[str, Any]:
        q = db.query(Salaire).filter(Salaire.statut != "annule")
        if annee:
            q = q.filter(Salaire.annee == annee)
        salaires = q.all()
        if not salaires:
            return {"annee": annee, "salaires": 0,
                    "note": "Aucun bulletin."}

        par_employe: Dict[int, Dict[str, float]] = {}
        masse_brute = Decimal(0)
        masse_impot = Decimal(0)
        masse_net = Decimal(0)
        for s in salaires:
            eid = s.employe_id
            brut = Decimal(str(s.salaire_brut or 0))
            impot = Decimal(str(s.deductions_impot or 0))
            net = Decimal(str(s.salaire_net or 0))
            par_employe.setdefault(eid, {"brut": 0.0, "impot": 0.0, "net": 0.0, "mois": 0})
            par_employe[eid]["brut"] += float(brut)
            par_employe[eid]["impot"] += float(impot)
            par_employe[eid]["net"] += float(net)
            par_employe[eid]["mois"] += 1
            masse_brute += brut
            masse_impot += impot
            masse_net += net

        return {
            "annee": annee,
            "bulletins_total": len(salaires),
            "employes": len(par_employe),
            "masse_brute_xaf": float(masse_brute),
            "masse_impot_xaf": float(masse_impot),
            "masse_nette_xaf": float(masse_net),
            "par_employe": par_employe,
        }
