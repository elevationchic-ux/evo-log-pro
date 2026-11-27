"""Service metier amenagement portuaire : relevés d'avancement des
ouvrages (physique sur chantier, financier depuis les couts reels)
et alerte honnete de depassement budgetaire."""
from datetime import date
from decimal import Decimal
from typing import Dict, Any, Optional

from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.amenagement_portuaire import ProjetAmenagement
from app.models.amenagement_extra_deep import ConstructionProgress


class AmenagementAvancementService:
    """Enregistre un releve d'avancement et recalcule les indicateurs
    du projet. Aucune donnee n'est inventee : l'avancement financier
    derive des couts reels saisis, jamais estime."""

    @staticmethod
    def enregistrer_releve(
        db: Session,
        projet_id: int,
        avancement_pct: float,
        surface_m2: Optional[float] = None,
        lot: Optional[str] = None,
        observateur: Optional[str] = None,
        company_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        projet = db.get(ProjetAmenagement, projet_id)
        if not projet:
            raise HTTPException(status_code=404, detail="Projet introuvable")

        if not (0 <= avancement_pct <= 100):
            raise HTTPException(status_code=422, detail="Avancement hors bornes 0-100 %")

        releve = ConstructionProgress(
            company_id=company_id or 1,
            reference=f"REL-{projet.code_projet}-{date.today().isoformat()}",
            lot=lot,
            avancement_pct=Decimal(str(avancement_pct)),
            date_releve=date.today(),
            surface_m2=Decimal(str(surface_m2)) if surface_m2 is not None else None,
            observateur=observateur,
            is_active=True,
        )
        db.add(releve)

        # Avancement physique = dernier releve (le plus recent fait foi)
        projet.avancement_physique_pct = Decimal(str(avancement_pct))

        # Avancement financier : derive des couts reels / previsonnel
        depassement = False
        ecart_budget = None
        if projet.cout_previsionnel_xaf and projet.cout_reel_xaf is not None:
            projet.avancement_financier_pct = (
                projet.cout_reel_xaf / projet.cout_previsionnel_xaf * 100
            )
            if projet.cout_reel_xaf > projet.cout_previsionnel_xaf:
                depassement = True
                ecart_budget = float(projet.cout_reel_xaf - projet.cout_previsionnel_xaf)

        db.commit()
        db.refresh(projet)
        db.refresh(releve)

        return {
            "releve_id": releve.id,
            "projet": projet.code_projet,
            "avancement_physique_pct": float(projet.avancement_physique_pct or 0),
            "avancement_financier_pct": (
                float(projet.avancement_financier_pct)
                if projet.avancement_financier_pct is not None else None
            ),
            "depassement_budget": depassement,
            "ecart_budget_xaf": ecart_budget,
            "note": (
                "Avancement financier calcule sur les couts reels saisis ; "
                "NULL si cout_reel non renseigne (jamais estime)."
            ),
        }
