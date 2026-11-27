"""Tests superadmin : alertes et migrations."""
import pytest

from app.models.superadmin_c_deep import SaCPlatformAlert, SaCMigrationRun
from app.services.superadmin_service import SuperadminService


def _alert(db, severite, statut, acquitte=None, reference="A-1"):
    a = SaCPlatformAlert(company_id=1, reference=reference, titre="Alerte",
                         severite=severite, statut=statut,
                         acquitte_par=acquitte, is_active=True)
    db.add(a)
    db.commit()
    db.refresh(a)
    return a


def _mig(db, statut, reference="M-1"):
    m = SaCMigrationRun(company_id=1, reference=reference, revision="001",
                        statut=statut, is_active=True)
    db.add(m)
    db.commit()
    db.refresh(m)
    return m


def test_alertes_par_severite(db):
    """2 critiques (1 non acquittee), 1 mineure resolue."""
    _alert(db, "critique", "ouverte", reference="A1")
    _alert(db, "critique", "en_cours", acquitte="admin", reference="A2")
    _alert(db, "mineure", "resolue", acquitte="admin", reference="A3")
    r = SuperadminService.alertes(db)
    assert r["alertes_total"] == 3
    assert r["par_severite"]["critique"] == 2
    assert r["non_acquittees"] == 1


def test_migrations(db):
    _mig(db, "succes", "M1")
    _mig(db, "echec", "M2")
    _mig(db, "en_cours", "M3")
    r = SuperadminService.migrations(db)
    assert r["migrations_total"] == 3
    assert r["echouees"] == 1


def test_vide_honnete(db):
    r = SuperadminService.alertes(db)
    assert r["alertes"] == 0
