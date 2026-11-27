"""Tests transit deep : valorisation douaniere par Incoterm."""
import pytest
from decimal import Decimal
from fastapi import HTTPException

from app.models.transit_deep import CustomsValuation
from app.services.transit_deep_service import CustomsValuationService


def _val(db, declaree, transport=0, assurance=0, incoterm="CIF", reference="VAL-1"):
    v = CustomsValuation(company_id=1, reference_dossier=reference,
                         valeur_declaree_xaf=Decimal(str(declaree)),
                         valeur_transport_xaf=Decimal(str(transport)),
                         valeur_assurance_xaf=Decimal(str(assurance)),
                         incoterm=incoterm, is_active=True)
    db.add(v)
    db.commit()
    db.refresh(v)
    return v


def test_cif_valeur_complete(db):
    """CIF : 1 000 000 + 200 000 + 50 000 = 1 250 000."""
    v = _val(db, 1_000_000, transport=200_000, assurance=50_000, incoterm="CIF")
    r = CustomsValuationService.calculer_valeur(db, v.id)
    assert r["valeur_en_douane_xaf"] == 1_250_000


def test_incoterm_inconnu_honnete(db):
    """Incoterm absent : declaree seule, methode signalee."""
    v = _val(db, 500_000, incoterm=None)
    r = CustomsValuationService.calculer_valeur(db, v.id)
    assert r["valeur_en_douane_xaf"] == 500_000
    assert "a verifier" in r["methode"]


def test_sans_declaree_refuse(db):
    v = CustomsValuation(company_id=1, reference_dossier="VAL-ND",
                         incoterm="CIF", is_active=True)
    db.add(v)
    db.commit()
    db.refresh(v)
    with pytest.raises(HTTPException) as exc:
        CustomsValuationService.calculer_valeur(db, v.id)
    assert exc.value.status_code == 422


def test_inconnu_404(db):
    with pytest.raises(HTTPException):
        CustomsValuationService.calculer_valeur(db, 999999)
