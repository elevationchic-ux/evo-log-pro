"""Service metier fluvial avance : navigabilite des biefs (cote d'eau
vs seuil de restriction) et verification de convoi (masse/longueur
vs limites section, parametres fournis — jamais supposes)."""
from typing import Dict, Any

from sqlalchemy.orm import Session

from app.models.fluvial_b_deep import FluvialWaterGauge, FluvialConvoy


class FluvialBService:
    """Navigabilite fluviale."""

    @staticmethod
    def navigabilite(db: Session, bief: str = None) -> Dict[str, Any]:
        q = db.query(FluvialWaterGauge).filter(
            FluvialWaterGauge.is_active.is_(True))
        if bief:
            q = q.filter(FluvialWaterGauge.bief == bief)
        jauges = q.all()
        if not jauges:
            return {"bief": bief, "jauges": 0,
                    "note": "Aucune jauge enregistree."}

        restreints = []
        libres = 0
        sans_seuil = 0
        for j in jauges:
            if j.cote_cm is None:
                sans_seuil += 1
                continue
            if j.cote_seuil_restr_cm is not None and j.cote_cm <= j.cote_seuil_restr_cm:
                restreints.append({
                    "poste": j.nom_poste or j.code_poste,
                    "cote_cm": j.cote_cm,
                    "seuil_cm": j.cote_seuil_restr_cm,
                })
            else:
                libres += 1

        return {
            "bief": bief,
            "jauges_total": len(jauges),
            "postes_libres": libres,
            "postes_restreints": len(restreints),
            "sans_mesure": sans_seuil,
            "details_restrictions": restreints,
        }

    @staticmethod
    def verifier_convoi(
        db: Session, numero_convoi: str,
        masse_max_t: int = None, longueur_max_m: int = None
    ) -> Dict[str, Any]:
        """Convoi vs limites de section (parametres obligatoires pour
        le verdict ; sans limite = mesures rapportees sans jugement)."""
        convoi = db.query(FluvialConvoy).filter(
            FluvialConvoy.numero_convoi == numero_convoi,
            FluvialConvoy.is_active.is_(True),
        ).first()
        if not convoi:
            return {"convoi": numero_convoi, "trouve": False,
                    "note": "Convoi inconnu."}

        result = {
            "convoi": numero_convoi,
            "pousseur": convoi.pousseur,
            "nb_peniches": convoi.nb_peniches,
            "masse_total_t": convoi.masse_total_t,
            "longueur_total_m": convoi.longueur_total_m,
        }
        if masse_max_t is not None and convoi.masse_total_t is not None:
            result["masse_conforme"] = convoi.masse_total_t <= masse_max_t
            result["marge_masse_t"] = masse_max_t - convoi.masse_total_t
        if longueur_max_m is not None and convoi.longueur_total_m is not None:
            result["longueur_conforme"] = convoi.longueur_total_m <= longueur_max_m
            result["marge_longueur_m"] = longueur_max_m - convoi.longueur_total_m
        if masse_max_t is None and longueur_max_m is None:
            result["note"] = "Limites non fournies : mesures rapportees sans verdict."
        return result
