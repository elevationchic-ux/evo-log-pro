"""Service metier frais D : rapports de notes de frais par statut,
avances en attente de regularisation et TVA recuperable. Aucune
donnee inventee."""
from decimal import Decimal
from typing import Dict, Any

from sqlalchemy.orm import Session

from app.models.frais_d_deep import (
    FraExpenseReport, FraExpenseAdvance, FraVatRecovery)


class FraisDService:
    """Notes de frais et TVA."""

    @staticmethod
    def rapports(db: Session, collaborateur: str = None) -> Dict[str, Any]:
        q = db.query(FraExpenseReport).filter(
            FraExpenseReport.is_active.is_(True))
        if collaborateur:
            q = q.filter(FraExpenseReport.collaborateur == collaborateur)
        rapports = q.all()
        if not rapports:
            return {"collaborateur": collaborateur, "rapports": 0,
                    "note": "Aucun rapport de frais."}
        par_statut: Dict[str, int] = {}
        total = Decimal(0)
        en_attente = 0
        for r in rapports:
            s = r.statut or "sans_statut"
            par_statut[s] = par_statut.get(s, 0) + 1
            total += Decimal(str(r.total or 0))
            if s.lower() in ("soumis", "en_attente", "en_cours", "soumise"):
                en_attente += 1
        return {
            "collaborateur": collaborateur,
            "rapports_total": len(rapports),
            "par_statut": par_statut,
            "en_attente": en_attente,
            "total_frais_xaf": float(total),
        }

    @staticmethod
    def avances(db: Session) -> Dict[str, Any]:
        avances = db.query(FraExpenseAdvance).filter(
            FraExpenseAdvance.is_active.is_(True)).all()
        if not avances:
            return {"avances": 0, "note": "Aucune avance."}
        en_attente = []
        par_statut: Dict[str, int] = {}
        for a in avances:
            s = a.statut or "sans_statut"
            par_statut[s] = par_statut.get(s, 0) + 1
            if s.lower() not in ("solde", "regularise", "clos", "rembourse"):
                en_attente.append({
                    "reference": a.reference,
                    "collaborateur": a.collaborateur,
                    "montant": float(a.montant) if a.montant else None,
                })
        return {
            "avances_total": len(avances),
            "par_statut": par_statut,
            "a_regulariser": len(en_attente),
            "details": en_attente,
        }

    @staticmethod
    def tva_recuperable(db: Session) -> Dict[str, Any]:
        recoveries = db.query(FraVatRecovery).filter(
            FraVatRecovery.is_active.is_(True)).all()
        if not recoveries:
            return {"recoveries": 0, "note": "Aucune TVA a recuperer."}
        en_attente = []
        total_ht = Decimal(0)
        total_tva = Decimal(0)
        for r in recoveries:
            if (r.statut or "").lower() not in ("recuperee", "validee", "clos"):
                en_attente.append({
                    "reference": r.reference,
                    "frais": r.frais,
                    "montant_ht": float(r.montant_ht) if r.montant_ht else None,
                    "tva": float(r.tva) if r.tva else None,
                })
                total_ht += Decimal(str(r.montant_ht or 0))
                total_tva += Decimal(str(r.tva or 0))
        return {
            "recoveries_total": len(recoveries),
            "en_attente": len(en_attente),
            "montant_ht_attente_xaf": float(total_ht),
            "tva_attente_xaf": float(total_tva),
            "details": en_attente,
        }
