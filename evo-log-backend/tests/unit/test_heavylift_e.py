"""Tests heavy-lift avance : validation du moment de charge."""
import pytest
from decimal import Decimal
from fastapi import HTTPException

from app.models.heavylift_e_deep import Heavy2LoadMomentCalc
from app.services.heavylift_e_service import Heavy2MomentService


def _calc(db, moment, capacite, reference="MOM-1"):
    c = Heavy2LoadMomentCalc(company_id=1, reference=reference,
                             configuration="grue_250t",
                             moment_applique=Decimal(str(moment)),
                             capacite=Decimal(str(capacite)), is_active=True)
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


def test_moment_ok(db):
    """200 / 400 = 50 % -> ok."""
    c = _calc(db, 200, 400)
    r = Heavy2MomentService.valider_moment(db, c.id)
    assert r["verdict"] == "ok"
    assert r["taux_utilisation_pct"] == 50.0


def test_moment_tendu(db):
    """340 / 400 = 85 % > 80 -> tendu."""
    c = _calc(db, 340, 400, reference="MOM-2")
    r = Heavy2MomentService.valider_moment(db, c.id)
    assert r["verdict"] == "tendu"


def test_moment_depasse(db):
    """450 / 400 = 112 % -> depasse."""
    c = _calc(db, 450, 400, reference="MOM-3")
    r = Heavy2MomentService.valider_moment(db, c.id)
    assert r["verdict"] == "depasse"


def test_capacite_absente_honnete(db):
    c = Heavy2LoadMomentCalc(company_id=1, reference="MOM-4",
                             moment_applique=Decimal("200"), is_active=True)
    db.add(c)
    db.commit()
    db.refresh(c)
    r = Heavy2MomentService.valider_moment(db, c.id)
    assert r["verdict"] == "non_evaluable"


def test_calc_inconnu_404(db):
    with pytest.raises(HTTPException):
        Heavy2MomentService.valider_moment(db, 999999)
