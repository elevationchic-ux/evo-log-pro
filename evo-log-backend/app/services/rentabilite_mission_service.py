"""Service metier rentabilite par mission : recette (factures de
 fret emises/payees) vs couts (cout_reel mission + frais valides).
 Aucune donnee inventee : un cote absent reste None honnete."""
from decimal import Decimal
from typing import Dict, Any, Optional

from sqlalchemy.orm import Session

from app.models.transport import Mission
from app.models.transport_deep import FreightBill, FreightBill_statut
from app.models.frais_mission import FraisMission


class RentabiliteMissionService:
    """Rentabilite mission par mission."""

    @staticmethod
    def par_mission(db: Session, mission_id: Optional[int] = None) -> Dict[str, Any]:
        q = db.query(Mission)
        if mission_id:
            q = q.filter(Mission.id == mission_id)
        missions = q.all()
        if not missions:
            return {"mission_id": mission_id, "missions": 0,
                    "note": "Aucune mission."}

        resultats = []
        for m in missions:
            # Recette : factures de fret emises ou payees liees a la mission
            factures = db.query(FreightBill).filter(
                FreightBill.mission_id == m.id,
                FreightBill.is_active.is_(True),
                FreightBill.statut.in_([FreightBill_statut.EMISE, FreightBill_statut.PAYEE]),
            ).all()
            recette = sum(
                (Decimal(str(f.total_ttc_xaf or 0)) for f in factures),
                Decimal(0))
            nb_factures = len(factures)

            # Couts : cout_reel de la mission + frais valides
            cout_mission = Decimal(str(m.cout_reel)) if m.cout_reel is not None else None
            frais = db.query(FraisMission).filter(
                FraisMission.mission_id == m.id,
                FraisMission.statut == "VALIDE",
            ).all()
            cout_frais = sum(
                (Decimal(str(f.montant or 0)) for f in frais), Decimal(0))

            cout_total = None
            if cout_mission is not None or frais:
                cout_total = (cout_mission or Decimal(0)) + cout_frais

            marge = None
            if recette > 0 and cout_total is not None:
                marge = recette - cout_total

            resultats.append({
                "mission_id": m.id,
                "reference": m.reference,
                "client_id": m.client_id,
                "type_mission": m.type_mission,
                "statut": getattr(m.statut, "value", m.statut),
                "recette_xaf": float(recette) if recette else 0.0,
                "nb_factures": nb_factures,
                "cout_mission_xaf": float(cout_mission) if cout_mission is not None else None,
                "cout_frais_valide_xaf": float(cout_frais) if frais else 0.0,
                "cout_total_xaf": float(cout_total) if cout_total is not None else None,
                "marge_xaf": float(marge) if marge is not None else None,
                "marge_pct": round(float(marge) / float(recette) * 100, 1)
                if marge is not None and recette > 0 else None,
            })

        marges = [r["marge_xaf"] for r in resultats if r["marge_xaf"] is not None]
        return {
            "mission_id": mission_id,
            "missions_total": len(resultats),
            "recette_totale_xaf": sum(r["recette_xaf"] for r in resultats),
            "cout_total_xaf": sum(r["cout_total_xaf"] or 0 for r in resultats),
            "marge_totale_xaf": sum(marges) if marges else None,
            "details": resultats,
        }
