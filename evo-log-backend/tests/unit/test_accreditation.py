"""Tests accreditation : habilitations expirees et par type."""
from datetime import date, timedelta
import pytest

from app.models.accreditation import Accreditation
from app.services.accreditation_service import AccreditationService


def _acc(db, code, type_acc, statut="actif", debut=None, fin=None, libelle="Acc"):
    a = Accreditation(company_id=1, user_id=1, code=code, libelle=libelle,
                      type=type_acc, date_debut=debut or date.today(),
                      date_fin=fin, statut=statut)
    db.add(a)
    db.commit()
    db.refresh(a)
    return a


def test_accreditations_expirees(db):
    """1 expiree (fin -5j), 1 valide (fin +90j), 1 revoquee."""
    _acc(db, "ACC-1", "permission", fin=date.today() - timedelta(days=5))
    _acc(db, "ACC-2", "permission", fin=date.today() + timedelta(days=90))
    _acc(db, "ACC-3", "deblocage", statut="revoque", fin=date.today() - timedelta(days=1))
    r = AccreditationService.accreditations(db)
    assert r["accreditations_total"] == 3
    assert r["expirees_a_renouveler"] == 1
    assert r["details_expirees"][0]["code"] == "ACC-1"
    assert r["par_type"]["permission"] == 2


def test_vide_honnete(db):
    r = AccreditationService.accreditations(db)
    assert r["accreditations"] == 0
