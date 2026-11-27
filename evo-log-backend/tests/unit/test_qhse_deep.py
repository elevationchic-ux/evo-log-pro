"""Tests QHSE deep : depassements normes et actions en retard."""
from datetime import date, timedelta
import pytest
from decimal import Decimal

from app.models.qhse_deep import EnvironmentalMeasurement, CorrectiveAction, CorrectiveAction_statut
from app.services.qhse_deep_service import QhseDeepService


def _mesure(db, reference, polluant, valeur, norme, conformite=None):
    m = EnvironmentalMeasurement(company_id=1, reference=reference,
                                 polluant=polluant, valeur=Decimal(str(valeur)),
                                 norme_max=Decimal(str(norme)),
                                 is_active=True)
    db.add(m)
    db.commit()
    db.refresh(m)
    return m


def _action(db, reference, statut, echeance, responsable="Resp"):
    a = CorrectiveAction(company_id=1, reference=reference,
                         source_ecart="audit", responsable=responsable,
                         date_prevue_cloture=echeance, statut=statut,
                         is_active=True)
    db.add(a)
    db.commit()
    db.refresh(a)
    return a


def test_depassements_normes(db):
    """1 depassement (80 > 50), 1 conforme (30 < 50)."""
    _mesure(db, "MES-1", "PM10", 80, 50)
    _mesure(db, "MES-2", "PM10", 30, 50)
    r = QhseDeepService.depassements(db)
    assert r["releves_total"] == 2
    assert r["depassements"] == 1
    assert r["conformes"] == 1
    assert r["details_depassements"][0]["reference"] == "MES-1"


def test_actions_en_retard(db):
    """1 ouverte en retard (echeance passee), 1 ouverte a jour, 1 closee."""
    _action(db, "AC-1", CorrectiveAction_statut.OUVERT, date.today() - timedelta(days=5))
    _action(db, "AC-2", CorrectiveAction_statut.OUVERT, date.today() + timedelta(days=10), "Resp2")
    _action(db, "AC-3", CorrectiveAction_statut.CLOTURE, date.today() - timedelta(days=1), "Resp3")
    r = QhseDeepService.actions_en_retard(db)
    assert r["actions_total"] == 3
    assert r["ouvertes"] == 2
    assert r["en_retard_echeance"] == 1


def test_vide_honnete(db):
    r = QhseDeepService.depassements(db)
    assert r["releves"] == 0
