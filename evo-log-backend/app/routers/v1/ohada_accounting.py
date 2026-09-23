from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.finance import Compte, EcritureComptable
from app.utils.tenant import get_current_tenant_context, TenantContext, require_module_access

router = APIRouter()

# ETAT REEL : les 3 etats financiers etaient des montants codes en dur
# (presentes comme reels alors que rien n'etait lu en base). Ils sont desormais
# agreges a partir des ecritures saisies dans `ecritures_comptables`, filtrees
# par le tenant courant par le filtre ORM global (tenant_enforcement).
# Presentation SYSCOHADA simplifiee : regroupement par classe du plan comptable
# (numero de compte = 1er chiffre), a affiner avec l'expert-comptable avant
# depot legal.


def _soldes_par_compte(db: Session):
    """Solde (debit - credit) de chaque compte du tenant, agrege depuis les ecritures."""
    debit_sq = (
        db.query(
            EcritureComptable.compte_debit.label("compte_id"),
            func.sum(EcritureComptable.montant_debit).label("total_debit"),
        )
        .group_by(EcritureComptable.compte_debit)
        .subquery()
    )
    credit_sq = (
        db.query(
            EcritureComptable.compte_credit.label("compte_id"),
            func.sum(EcritureComptable.montant_credit).label("total_credit"),
        )
        .group_by(EcritureComptable.compte_credit)
        .subquery()
    )
    rows = (
        db.query(
            Compte.numero_compte,
            Compte.nom_compte,
            func.coalesce(debit_sq.c.total_debit, 0).label("debit"),
            func.coalesce(credit_sq.c.total_credit, 0).label("credit"),
        )
        .outerjoin(debit_sq, debit_sq.c.compte_id == Compte.id)
        .outerjoin(credit_sq, credit_sq.c.compte_id == Compte.id)
        .order_by(Compte.numero_compte)
        .all()
    )
    return rows


@router.get("/general-ledger", dependencies=[Depends(require_module_access("finance"))])
def get_ohada_general_ledger(
    context: TenantContext = Depends(get_current_tenant_context),
    db: Session = Depends(get_db),
):
    """Grand livre SYSCOHADA agrege depuis les ecritures comptables reelles du tenant."""
    entries = []
    for numero, label, debit, credit in _soldes_par_compte(db):
        debit_f, credit_f = float(debit or 0), float(credit or 0)
        if debit_f == 0.0 and credit_f == 0.0:
            continue  # comptes sans mouvement : hors grand livre
        entries.append({
            "account_number": numero,
            "account_label": label,
            "debit": debit_f,
            "credit": credit_f,
            "balance": debit_f - credit_f,
        })
    return {
        "status": "success",
        "accounting_standard": "SYSCOHADA Révisé (agrégation simplifiée par compte)",
        "organization_id": context.organization_id,
        "source": "ecritures_comptables",
        "entries": entries,
    }


def _totaux_par_classe(db: Session):
    """Total (debit - credit) par classe de compte (1er chiffre du numero)."""
    totaux: dict[str, float] = {}
    for numero, _label, debit, credit in _soldes_par_compte(db):
        classe = (numero or "0")[0]
        totaux[classe] = totaux.get(classe, 0.0) + float(debit or 0) - float(credit or 0)
    return totaux


@router.get("/balance-sheet", dependencies=[Depends(require_module_access("finance"))])
def get_ohada_balance_sheet(
    context: TenantContext = Depends(get_current_tenant_context),
    db: Session = Depends(get_db),
):
    """Bilan SYSCOHADA simplifie : actif/passif agreges depuis les ecritures du tenant.

    Actif = soldes debiteurs des classes 1-5 ; Passif = soldes crediteurs.
    Les classes 6/7 (gestion) ne figurent qu'au compte de resultat.
    """
    totaux = _totaux_par_classe(db)
    bilan = {c: s for c, s in totaux.items() if c in "12345"}
    actifs = round(sum(s for s in bilan.values() if s > 0), 2)
    passifs = round(-sum(s for s in bilan.values() if s < 0), 2)
    return {
        "status": "success",
        "period": "cumul des ecritures saisies (exercice en cours)",
        "currency": "XAF",
        "source": "ecritures_comptables",
        "organization_id": context.organization_id,
        "assets": {
            "immobilisations_classe2": round(totaux.get("2", 0.0), 2),
            "stocks_classe3": round(totaux.get("3", 0.0), 2),
            "creances_classe4": round(totaux.get("4", 0.0), 2),
            "tresorerie_debiteure_classe5": round(totaux.get("5", 0.0), 2),
            "autres_actifs_classe1": round(max(totaux.get("1", 0.0), 0.0), 2),
            "total_assets": actifs,
        },
        "liabilities": {
            "capitaux_classe1_credit": round(max(-totaux.get("1", 0.0), 0.0), 2),
            "dettes_classe4_credit": round(max(-totaux.get("4", 0.0), 0.0), 2),
            "tresorerie_crediteuse_classe5": round(max(-totaux.get("5", 0.0), 0.0), 2),
            "autres_passifs": round(max(-totaux.get("2", 0.0) - totaux.get("3", 0.0), 0.0), 2),
            "total_liabilities": passifs,
        },
        "equilibre": abs(actifs - passifs) < 0.01,
        "note": "Agréagation SYSCOHADA simplifiée par classe ; à rapprocher du bilan légal signé par l'expert-comptable.",
    }


@router.get("/income-statement", dependencies=[Depends(require_module_access("finance"))])
def get_ohada_income_statement(
    context: TenantContext = Depends(get_current_tenant_context),
    db: Session = Depends(get_db),
):
    """Compte de resultat SYSCOHADA : produits (classe 7) - charges (classe 6)."""
    totaux = _totaux_par_classe(db)
    charges = round(totaux.get("6", 0.0), 2)
    produits = round(-totaux.get("7", 0.0), 2)
    resultat = round(produits - charges, 2)
    return {
        "status": "success",
        "period": "cumul des ecritures saisies (exercice en cours)",
        "currency": "XAF",
        "source": "ecritures_comptables",
        "organization_id": context.organization_id,
        "revenue": produits,
        "operating_expenses": charges,
        "resultats_synthese": resultat,
        "note": "Charges classe 6 / produits classe 7 agrégés depuis les écritures ; présentation détaillée (EBIT, résultat financier, IS) à établir avec le cabinet comptable.",
    }
