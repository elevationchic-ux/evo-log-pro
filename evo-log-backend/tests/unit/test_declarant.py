"""Tests declarant : soldes paiements et declarations en attente."""
from datetime import datetime, timezone
import pytest
from decimal import Decimal

from app.models.declarant_d_deep import DeclCustomsDeclaration, DeclCustomsPayment
from app.services.declarant_service import DeclarantService


def _decl(db, reference, regime="IM4", statut="en_cours", valeur=1_000_000):
    d = DeclCustomsDeclaration(company_id=1, reference=reference, regime=regime,
                               statut=statut, valeur_douane=Decimal(str(valeur)),
                               is_active=True)
    db.add(d)
    db.commit()
    db.refresh(d)
    return d


def _pay(db, declaration, montant, type_droit="droits_de_douane", reference="P1"):
    p = DeclCustomsPayment(company_id=1, reference=reference, declaration=declaration,
                           montant=Decimal(str(montant)), type_droit=type_droit,
                           is_active=True)
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


def test_soldes_par_type(db):
    """DD 200k + TVA 100k = 300k total."""
    _decl(db, "DECL-1")
    _pay(db, "DECL-1", 200_000, "droits_de_douane", "P1")
    _pay(db, "DECL-1", 100_000, "tva", "P2")
    r = DeclarantService.soldes_paiements(db, "DECL-1")
    assert r["trouvee"] is True
    assert r["par_type_droit"]["droits_de_douane"] == 200_000
    assert r["total_paye_xaf"] == 300_000


def test_declaration_inconnue_honnete(db):
    r = DeclarantService.soldes_paiements(db, "DECL-INEXISTANT")
    assert r["trouvee"] is False


def test_declarations_en_attente(db):
    """1 en_cours, 1 levee (exclue)."""
    _decl(db, "DECL-A", statut="en_cours")
    _decl(db, "DECL-B", statut="levee")
    r = DeclarantService.declarations_en_attente(db)
    assert r["declarations_total"] == 2
    assert r["en_attente"] == 1
    assert r["details"][0]["reference"] == "DECL-A"
