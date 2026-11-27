"""Service metier magasinier C : ecarts et precision des comptages
cycliques par emplacement. Aucune donnee inventee : lignes sans
comptage physique sont exclues et comptees."""
from typing import Dict, Any

from sqlalchemy.orm import Session

from app.models.magasinier_c_deep import MagcCycleCount


class MagasinierCService:
    """KPIs comptages cycliques."""

    @staticmethod
    def precision_emplacement(db: Session, emplacement: str) -> Dict[str, Any]:
        lignes = db.query(MagcCycleCount).filter(
            MagcCycleCount.emplacement == emplacement,
            MagcCycleCount.is_active.is_(True),
        ).all()
        if not lignes:
            return {"emplacement": emplacement, "lignes": 0,
                    "note": "Aucun comptage enregistre sur cet emplacement."}

        comptees = [l for l in lignes if l.physique is not None and l.theorique is not None]
        sans_comptage = len(lignes) - len(comptees)
        ecarts = [
            {"reference": l.reference, "ecart": l.physique - l.theorique}
            for l in comptees if l.physique != l.theorique
        ]
        exactes = len(comptees) - len(ecarts)

        return {
            "emplacement": emplacement,
            "lignes_total": len(lignes),
            "lignes_comptees": len(comptees),
            "sans_comptage": sans_comptage,
            "lignes_exactes": exactes,
            "ecarts": len(ecarts),
            "taux_precision_pct": round(exactes / len(comptees) * 100, 1) if comptees else None,
            "details_ecarts": ecarts,
        }
