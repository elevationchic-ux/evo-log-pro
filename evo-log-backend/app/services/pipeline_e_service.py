"""Service metier pipeline avance : suivi de la corrosion (epaisseur
mesuree par troncon vs seuil minimal) et analyses des releves pompe.
Aucune epaisseur nominale inventee : seuil fourni par l'appelant."""
from decimal import Decimal
from typing import Dict, Any

from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.pipeline_e_deep import Pipe2CorrosionReading, Pipe2PumpStationRead


class PipelineEService:
    """Integrite pipeline."""

    @staticmethod
    def analyse_corrosion(db: Session, troncon: str, seuil_min_mm: float) -> Dict[str, Any]:
        """Releves corrosion d'un troncon : min/moyenne/max et nb sous
        le seuil minimal (parametre obligatoire, jamais suppose)."""
        releves = db.query(Pipe2CorrosionReading).filter(
            Pipe2CorrosionReading.troncon == troncon,
            Pipe2CorrosionReading.is_active.is_(True),
        ).all()
        if not releves:
            return {"troncon": troncon, "releves": 0,
                    "note": "Aucun releve corrosion pour ce troncon."}

        epaisseurs = [float(r.epaisseur_mm) for r in releves if r.epaisseur_mm is not None]
        if not epaisseurs:
            return {"troncon": troncon, "releves": len(releves),
                    "note": "Releves sans epaisseur renseignee."}

        sous_seuil = [e for e in epaisseurs if e < seuil_min_mm]
        return {
            "troncon": troncon,
            "releves": len(releves),
            "epaisseur_min_mm": min(epaisseurs),
            "epaisseur_moyenne_mm": round(sum(epaisseurs) / len(epaisseurs), 2),
            "epaisseur_max_mm": max(epaisseurs),
            "seuil_min_mm": seuil_min_mm,
            "releves_sous_seuil": len(sous_seuil),
            "alerte": len(sous_seuil) > 0,
        }

    @staticmethod
    def analyse_pompe(db: Session, station: str) -> Dict[str, Any]:
        """Releves pompe : debit moyen, vibration max."""
        releves = db.query(Pipe2PumpStationRead).filter(
            Pipe2PumpStationRead.station == station,
            Pipe2PumpStationRead.is_active.is_(True),
        ).all()
        if not releves:
            return {"station": station, "releves": 0,
                    "note": "Aucun releve pompe pour cette station."}

        debits = [float(r.debit) for r in releves if r.debit is not None]
        vibrations = [float(r.vibration) for r in releves if r.vibration is not None]
        return {
            "station": station,
            "releves": len(releves),
            "debit_moyen": round(sum(debits) / len(debits), 2) if debits else None,
            "vibration_max": max(vibrations) if vibrations else None,
        }
