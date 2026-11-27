"""Service metier declarant douane : reconciliation des paiements
par declaration et type de droit (droits de douane, TVA, redevances).
Aucune redevance inventee : totaux reels uniquement."""
from decimal import Decimal
from typing import Dict, Any

from sqlalchemy.orm import Session

from app.models.declarant_d_deep import DeclCustomsDeclaration, DeclCustomsPayment


class DeclarantService:
    """Paiements douane."""

    @staticmethod
    def soldes_paiements(db: Session, declaration_ref: str) -> Dict[str, Any]:
        decl = db.query(DeclCustomsDeclaration).filter(
            DeclCustomsDeclaration.reference == declaration_ref,
            DeclCustomsDeclaration.is_active.is_(True),
        ).first()
        if not decl:
            return {"declaration": declaration_ref, "trouvee": False,
                    "note": "Declaration inconnue."}

        paiements = db.query(DeclCustomsPayment).filter(
            DeclCustomsPayment.declaration == declaration_ref,
            DeclCustomsPayment.is_active.is_(True),
        ).all()
        par_type: Dict[str, float] = {}
        total = Decimal(0)
        for p in paiements:
            m = Decimal(str(p.montant or 0))
            total += m
            t = p.type_droit or "autre"
            par_type[t] = par_type.get(t, 0.0) + float(m)

        return {
            "declaration": declaration_ref,
            "trouvee": True,
            "regime": decl.regime,
            "valeur_douane_xaf": float(decl.valeur_douane) if decl.valeur_douane else None,
            "nb_paiements": len(paiements),
            "par_type_droit": par_type,
            "total_paye_xaf": float(total),
        }

    @staticmethod
    def declarations_en_attente(db: Session) -> Dict[str, Any]:
        """Declarations dont le statut n'est pas final."""
        decls = db.query(DeclCustomsDeclaration).filter(
            DeclCustomsDeclaration.is_active.is_(True)).all()
        en_attente = [
            {"reference": d.reference, "regime": d.regime,
             "statut": d.statut, "valeur_douane": float(d.valeur_douane) if d.valeur_douane else None}
            for d in decls
            if (d.statut or "").lower() not in ("levee", "cloturee", "validée", "validee")
        ]
        return {"declarations_total": len(decls), "en_attente": len(en_attente),
                "details": en_attente}
