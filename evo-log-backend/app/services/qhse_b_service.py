"""Service metier QHSE avance : analyse des quasi-accidents par site
et gravite potentielle, et detection des instruments de mesure en
retard d'etalonage. Aucune donnee inventee."""
from datetime import date
from typing import Dict, Any

from sqlalchemy.orm import Session

from app.models.qhse_b_deep import QhseNearMiss, QhseCalibration


class QhseBService:
    """KPIs QHSE avance."""

    @staticmethod
    def analyse_quasi_accidents(db: Session, site: str = None) -> Dict[str, Any]:
        q = db.query(QhseNearMiss).filter(QhseNearMiss.is_active.is_(True))
        if site:
            q = q.filter(QhseNearMiss.site == site)
        evenements = q.all()
        if not evenements:
            return {"site": site, "evenements": 0,
                    "note": "Aucun quasi-accident enregistre."}

        par_site: Dict[str, int] = {}
        par_gravite: Dict[str, int] = {}
        for e in evenements:
            par_site[e.site or "inconnu"] = par_site.get(e.site or "inconnu", 0) + 1
            g = e.gravite_potentielle or "non_evaluee"
            par_gravite[g] = par_gravite.get(g, 0) + 1

        return {
            "site": site,
            "evenements_total": len(evenements),
            "par_site": par_site,
            "par_gravite_potentielle": par_gravite,
        }

    @staticmethod
    def instruments_en_retard(db: Session) -> Dict[str, Any]:
        """Instruments dont la prochaine etalonnee est depassee."""
        instruments = db.query(QhseCalibration).filter(
            QhseCalibration.is_active.is_(True),
            QhseCalibration.date_prochaine.isnot(None),
        ).all()
        aujourdhui = date.today()
        en_retard = [i for i in instruments if i.date_prochaine < aujourdhui]
        a_venir = [i for i in instruments if i.date_prochaine >= aujourdhui]
        return {
            "instruments_total": len(instruments),
            "en_retard_etalonage": len(en_retard),
            "a_jour_ou_a_venir": len(a_venir),
            "details_retard": [
                {"numero": i.numero_instrument, "prochaine": str(i.date_prochaine)}
                for i in en_retard
            ],
        }
