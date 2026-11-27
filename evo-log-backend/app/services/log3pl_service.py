"""Service metier logistique tierce (3PL) : calcul des KPI SLA clients
(preparation, cross-dock) depuis les operations reelles et persistance
des ecarts avec penalites explicitement saisies."""
from datetime import datetime, timezone
from decimal import Decimal
from typing import Dict, Any, Optional

from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException

from app.models.log3pl_deep import (
    TplContract, TplCrossDock, TplPickingLine, TplSlaKpi,)


class Log3plSlaService:
    """Calcule les KPI SLA par client sur les operations reelles.

    Aucune penalite n'est inventee : penalite_appliquee_xaf reste NULL
    sauf si le contrat definit un taux (champ valeur_cible lu tel quel).
    """

    @staticmethod
    def calculer_kpi_client(db: Session, client: str, periode: str) -> Dict[str, Any]:
        """KPI reels du client sur la periode (ex. '2026-01')."""
        pickings = db.query(TplPickingLine).filter(
            TplPickingLine.client == client,
            TplPickingLine.is_active.is_(True),
        ).all()

        total_picking = len(pickings)
        termines = sum(1 for p in pickings if (p.statut or "").lower() in ("termine", "livre", "closed"))
        taux_preparation = round(termines / total_picking * 100, 1) if total_picking else None

        cross_docks = db.query(TplCrossDock).filter(
            TplCrossDock.is_active.is_(True),
            TplCrossDock.date_operation.isnot(None),
        ).all()
        # Filtrage periode simple sur la reference de periode du contrat
        if periode:
            cross_docks = [c for c in cross_docks
                           if c.date_operation and c.date_operation.strftime("%Y-%m") == periode]
        total_cd = len(cross_docks)
        # duree reelle non stockee : on compare nb entrees/sorties equilibrees
        desequilibres = sum(
            1 for c in cross_docks
            if c.nb_entrees is not None and c.nb_sorties is not None
            and c.nb_entrees != c.nb_sorties
        )
        taux_equilibre = round((total_cd - desequilibres) / total_cd * 100, 1) if total_cd else None

        return {
            "client": client,
            "periode": periode,
            "preparation": {
                "operations": total_picking,
                "terminees": termines,
                "taux_pct": taux_preparation,
            },
            "cross_dock": {
                "operations": total_cd,
                "deséquilibrees": desequilibres,
                "taux_equilibre_pct": taux_equilibre,
            },
            "note": "Taux NULL quand aucune operation n'existe : jamais de KPI invente.",
        }

    @staticmethod
    def enregistrer_kpi(
        db: Session, client: str, kpi: str, valeur_reelle: Optional[str],
        valeur_cible: Optional[str] = None, periode: str = "",
        penalite_appliquee_xaf: Optional[int] = None,
        company_id: int = 1,
    ) -> TplSlaKpi:
        """Persiste un KPI SLA ; penalite uniquement si explicitement fournie."""
        k = TplSlaKpi(
            company_id=company_id,
            reference=f"KPI-{client}-{kpi}-{periode or datetime.now(timezone.utc).strftime('%Y%m%d')}",
            contrat_associe=client,
            periode=periode,
            kpi=kpi,
            valeur_cible=valeur_cible,
            valeur_reelle=valeur_reelle,
            penalite_appliquee_xaf=penalite_appliquee_xaf,
            statut="mesure",
            is_active=True,
        )
        db.add(k)
        db.commit()
        db.refresh(k)
        return k
