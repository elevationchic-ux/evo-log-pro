"""Service metier transport deep : conformite des chargements de
marchandises dangereuses (ADR) — formation chauffeur requise,
etiquettes declarees, regroupement par classe. Aucune donnee
invente : champs absents signales."""
from typing import Dict, Any

from sqlalchemy.orm import Session

from app.models.transport_deep import DangerousGoodsLoad


class TransportDeepService:
    """Conformite ADR."""

    @staticmethod
    def conformite_dg(db: Session) -> Dict[str, Any]:
        chargements = db.query(DangerousGoodsLoad).filter(
            DangerousGoodsLoad.is_active.is_(True)).all()
        if not chargements:
            return {"chargements": 0, "note": "Aucun chargement DG."}

        conformes = 0
        non_conformes = []
        par_classe: Dict[str, int] = {}
        for c in chargements:
            classe = c.classe_adr or "sans_classe"
            par_classe[classe] = par_classe.get(classe, 0) + 1
            problemes = []
            if not c.formation_chauffeur:
                problemes.append("formation_chauffeur_absente")
            if not c.etiquettes:
                problemes.append("etiquettes_non_declarees")
            if c.quantite_kg is None:
                problemes.append("quantite_non_renseignee")
            if problemes:
                non_conformes.append({
                    "reference": c.reference,
                    "classe_adr": c.classe_adr,
                    "onu": c.onu_number,
                    "problemes": problemes,
                })
            else:
                conformes += 1

        return {
            "chargements_total": len(chargements),
            "conformes": conformes,
            "non_conformes": len(non_conformes),
            "par_classe_adr": par_classe,
            "details_non_conformites": non_conformes,
        }
