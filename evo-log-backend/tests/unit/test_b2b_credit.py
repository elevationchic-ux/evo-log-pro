"""Tests B2B : controle de limite de credit client."""
import pytest
from decimal import Decimal
from fastapi import HTTPException

from app.models.b2b_deep import ClientCreditLimit
from app.services.b2b_credit_service import B2bCreditService


def _credit(db, plafond=10_000_000, encours=3_000_000):
    c = ClientCreditLimit(company_id=1, reference=f"CR-{plafond}-{encours}",
                          client_id=1, plafond_xaf=Decimal(str(plafond)),
                          encours_actuel_xaf=Decimal(str(encours)), is_active=True)
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


def test_commande_dans_la_limite(db):
    """Disponible 7M, commande 5M -> accepte, reste 2M."""
    c = _credit(db)
    r = B2bCreditService.verifier_credit(db, c.id, 5_000_000)
    assert r["decision"] == "accepte"
    assert r["disponible_avant_xaf"] == 7_000_000
    assert r["reste_apres_commande_xaf"] == 2_000_000


def test_commande_superieure_refusee(db):
    """Disponible 7M, commande 8M -> refuse avec montant manquant."""
    c = _credit(db)
    r = B2bCreditService.verifier_credit(db, c.id, 8_000_000)
    assert r["decision"] == "refuse"
    assert r["manquant_xaf"] == 1_000_000


def test_sans_plafond_refuse(db):
    c = _credit(db, plafond=0)
    r = B2bCreditService.verifier_credit(db, c.id, 1000)
    assert r["decision"] == "refuse"


def test_credit_inconnu_404(db):
    with pytest.raises(HTTPException):
        B2bCreditService.verifier_credit(db, 999999, 1000)


def test_montant_invalide_refuse(db):
    c = _credit(db)
    with pytest.raises(HTTPException):
        B2bCreditService.verifier_credit(db, c.id, 0)
