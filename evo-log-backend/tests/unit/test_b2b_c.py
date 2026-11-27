"""Tests B2B commercial : controle limite credit compte client."""
import pytest
from decimal import Decimal
from fastapi import HTTPException

from app.models.b2b_c_deep import B2bCCreditAccount
from app.services.b2b_c_service import B2bCCreditService


def _compte(db, limite=5_000_000, encours=1_000_000, reference="CCA-1"):
    c = B2bCCreditAccount(company_id=1, reference=reference, client="CLI-9",
                          limite_credit=Decimal(str(limite)),
                          encours=Decimal(str(encours)), is_active=True)
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


def test_dans_la_limite(db):
    """Disponible 4M, commande 3M -> accepte, reste 1M."""
    c = _compte(db)
    r = B2bCCreditService.verifier_credit(db, c.id, 3_000_000)
    assert r["decision"] == "accepte"
    assert r["reste_apres_xaf"] == 1_000_000


def test_superieur_refuse(db):
    c = _compte(db)
    r = B2bCCreditService.verifier_credit(db, c.id, 5_000_000)
    assert r["decision"] == "refuse"
    assert r["manquant_xaf"] == 1_000_000


def test_sans_limite_refuse(db):
    c = _compte(db, limite=0)
    r = B2bCCreditService.verifier_credit(db, c.id, 1000)
    assert r["decision"] == "refuse"


def test_inconnu_404(db):
    with pytest.raises(HTTPException):
        B2bCCreditService.verifier_credit(db, 999999, 100)
