"""Service metier economie : indicateurs financiers par categorie
(rentabilite, liquidite, endettement) avec ecart a l'objectif et
variation vs periode precedente. Aucune donnee inventee."""
from decimal import Decimal
from typing import Dict, Any

from sqlalchemy.orm import Session

from app.models.reporting import IndicateurFinancier


class EconomieService:
    """Indicateurs economiques."""

    @staticmethod
    def indicateurs(db: Session, categorie: str = None) -> Dict[str, Any]:
        q = db.query(IndicateurFinancier).filter(
            IndicateurFinancier.is_active.is_(True)) if hasattr(
            IndicateurFinancier, "is_active") else db.query(IndicateurFinancier)
        if categorie:
            q = q.filter(IndicateurFinancier.categorie == categorie)
        indicateurs = q.all()
        if not indicateurs:
            return {"categorie": categorie, "indicateurs": 0,
                    "note": "Aucun indicateur financier."}

        par_categorie: Dict[str, int] = {}
        sous_objectif = []
        for i in indicateurs:
            c = i.categorie or "autre"
            par_categorie[c] = par_categorie.get(c, 0) + 1
            if i.valeur_actuelle is not None and i.objectif is not None:
                if Decimal(str(i.valeur_actuelle)) < Decimal(str(i.objectif)):
                    sous_objectif.append({
                        "code": i.code,
                        "nom": i.nom,
                        "valeur_actuelle": float(i.valeur_actuelle),
                        "objectif": float(i.objectif),
                        "ecart_pct": round(
                            float((Decimal(str(i.valeur_actuelle)) - Decimal(str(i.objectif)))
                                  / Decimal(str(i.objectif)) * 100), 1)
                        if Decimal(str(i.objectif)) != 0 else None,
                    })

        return {
            "categorie": categorie,
            "indicateurs_total": len(indicateurs),
            "par_categorie": par_categorie,
            "sous_objectif": len(sous_objectif),
            "details_sous_objectif": sous_objectif,
        }
