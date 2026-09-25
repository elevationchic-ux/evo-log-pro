"""Tests de la numerotation legale (exigence DGI : sequence continue sans trou).

Verrouille les comportements suivants :
  • suite continue FAC-ANNEE-0001, 0002... par entreprise / type / annee ;
  • amorçage au max existant (impossible de re-attribuer un numéro posé) ;
  • rollback = numero restitue (aucun trou) ;
  • le routeur POST /finance/factures sans numero delivre un numero legal.
"""
from datetime import date

import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.finance_ohada import FactureNew
from app.utils.numerotation import prochaine_reference


def test_sequence_continue_annee(db: Session):
    refs = [prochaine_reference(db, "FACTURE", date_reference=date(2026, 5, 1)) for _ in range(3)]
    db.commit()
    assert refs == ["FAC-2026-0001", "FAC-2026-0002", "FAC-2026-0003"]


def test_changement_d_annee_repart(db: Session):
    a = prochaine_reference(db, "FACTURE", date_reference=date(2026, 12, 31))
    b = prochaine_reference(db, "FACTURE", date_reference=date(2027, 1, 1))
    db.commit()
    assert a == "FAC-2026-0001"
    assert b == "FAC-2027-0001"


def test_avoir_prefixe_distinct(db: Session):
    fac = prochaine_reference(db, "FACTURE", date_reference=date(2026, 1, 1))
    avoir = prochaine_reference(db, "AVOIR", date_reference=date(2026, 1, 1))
    db.commit()
    assert fac == "FAC-2026-0001"
    assert avoir == "AV-2026-0001"


def test_type_inconnu_refuse_honnetement(db: Session):
    with pytest.raises(HTTPException) as exc:
        prochaine_reference(db, "CONTRAT_MYSTERE")
    assert exc.value.status_code == 400


def test_amorce_sur_numeros_historiques(db: Session):
    """Un numero FAC-2026-0007 deja pose ne doit jamais etre re-attribue."""
    db.add(FactureNew(
        numero_facture="FAC-2026-0007", client_id=None, type_facture="vente",
        date_emission=date(2026, 1, 1), montant_ht=1000, montant_ttc=1192.5,
    ))
    db.commit()
    ref = prochaine_reference(db, "FACTURE", date_reference=date(2026, 6, 1))
    db.commit()
    assert ref == "FAC-2026-0008"


def test_rollback_ne_consomme_pas_de_numero(db: Session):
    ref1 = prochaine_reference(db, "FACTURE", date_reference=date(2026, 3, 1))
    db.rollback()  # la facture qui suivait echoue -> le numero est restitue
    ref2 = prochaine_reference(db, "FACTURE", date_reference=date(2026, 3, 1))
    db.commit()
    assert ref1 == ref2 == "FAC-2026-0001"


def test_separation_par_entreprise(db: Session):
    from app.models.tenant import Company

    c1 = Company(code="PD1", nom="Port Douala SARL", legal_form="SARL")
    c2 = Company(code="TK1", nom="Terminal Kribi SA", legal_form="SA")
    db.add_all([c1, c2])
    db.flush()
    r1 = prochaine_reference(db, "FACTURE", company_id=c1.id, date_reference=date(2026, 1, 1))
    r2 = prochaine_reference(db, "FACTURE", company_id=c2.id, date_reference=date(2026, 1, 1))
    r1b = prochaine_reference(db, "FACTURE", company_id=c1.id, date_reference=date(2026, 1, 1))
    db.commit()
    assert (r1, r2, r1b) == ("FAC-2026-0001", "FAC-2026-0001", "FAC-2026-0002")


class _FakeUser:
    id = 1
    username = "test"
    company_id = None


def test_routeur_factures_sans_numero_delivre_sequence_legale(client, db):
    from app.core.security import get_current_user
    from app.main import app

    app.dependency_overrides[get_current_user] = lambda: _FakeUser()
    try:
        payload = {
            "client_id": 1,
            "type_facture": "vente",
            "date_emission": "2026-09-25",
            "montant_ht": 100000.0,
            "taux_tva": 19.25,
        }
        r1 = client.post("/api/v1/finance/factures", json=payload)
        assert r1.status_code == 201, r1.text
        assert r1.json()["numero_facture"] == "FAC-2026-0001"
        # Totaux reellement calcules cote service, pas inventes.
        assert r1.json()["montant_tva"] == pytest.approx(19250.0)
        assert r1.json()["montant_ttc"] == pytest.approx(119250.0)

        r2 = client.post("/api/v1/finance/factures", json=payload)
        assert r2.status_code == 201, r2.text
        assert r2.json()["numero_facture"] == "FAC-2026-0002"
    finally:
        app.dependency_overrides.clear()
