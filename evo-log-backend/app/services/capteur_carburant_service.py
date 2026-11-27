"""Service metier capteurs : surveillance des cuves carburant (niveau
vs capacite, alerte vol, jours avant epuisement estime par conso).
Aucune donnee inventee : capteur absent = note honnete."""
from typing import Dict, Any

from sqlalchemy.orm import Session

from app.models.new_k_modules import FuelTankSensor


class CapteurCarburantService:
    """Surveillance cuves carburant."""

    @staticmethod
    def statut_cuve(
        db: Session, immatriculation: str,
        seuil_alerte_pct: float = 20.0, conso_l_jour: float = None
    ) -> Dict[str, Any]:
        capteur = db.query(FuelTankSensor).filter(
            FuelTankSensor.immatriculation_camion == immatriculation).first()
        if not capteur:
            return {"immatriculation": immatriculation, "capteur": False,
                    "note": "Aucun capteur enregistre pour ce vehicule."}

        capacite = capteur.capacite_totale_litres or 400.0
        niveau = capteur.niveau_actuel_litres or 0.0
        pct = round(niveau / capacite * 100, 1) if capacite else None
        en_alerte = pct is not None and pct < seuil_alerte_pct

        result = {
            "immatriculation": immatriculation,
            "niveau_litres": niveau,
            "capacite_litres": capacite,
            "niveau_pct": pct,
            "seuil_alerte_pct": seuil_alerte_pct,
            "en_alerte": en_alerte,
            "alerte_vol_capteur": bool(capteur.alerte_vol_detectee),
            "derniere_station": capteur.derniere_station,
        }
        if conso_l_jour and conso_l_jour > 0 and niveau > 0:
            result["jours_avant_epuisement"] = round(niveau / conso_l_jour, 1)
        return result

    @staticmethod
    def cuves_en_alerte(db: Session, seuil_pct: float = 20.0) -> Dict[str, Any]:
        capteurs = db.query(FuelTankSensor).all()
        en_alerte = []
        vols = []
        for c in capteurs:
            capacite = c.capacite_totale_litres or 400.0
            pct = (c.niveau_actuel_litres or 0) / capacite * 100 if capacite else 0
            if pct < seuil_pct:
                en_alerte.append({"vehicule": c.immatriculation_camion, "niveau_pct": round(pct, 1)})
            if c.alerte_vol_detectee:
                vols.append(c.immatriculation_camion)
        return {
            "capteurs_total": len(capteurs),
            "cuves_en_alerte": len(en_alerte),
            "details_alerte": en_alerte,
            "alertes_vol": vols,
        }
