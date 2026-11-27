"""Tests portail QHSE : permis, formations, deversements."""
from datetime import date, timedelta
import pytest
from decimal import Decimal

from app.models.qhse_portal_d_deep import (
    QspWorkPermitRequest, QspSafetyTrainingLog, QspSpillReport)
from app.services.qhse_portal_service import QhsePortalService


def _permis(db, reference, statut="actif"):
    p = QspWorkPermitRequest(company_id=1, reference=reference, type="travail_en_hauteur",
                             lieu="Site A", demandeur="Req", statut=statut, is_active=True)
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


def _form(db, reference, operateur, validite, statut="valide"):
    f = QspSafetyTrainingLog(company_id=1, reference=reference, operateur=operateur,
                             formation="CACES", validite=validite, statut=statut, is_active=True)
    db.add(f)
    db.commit()
    db.refresh(f)
    return f


def _spill(db, reference, statut="ouvert"):
    s = QspSpillReport(company_id=1, reference=reference, produit="Gasoil",
                       volume=Decimal("50"), lieu="Cuve 3", statut=statut, is_active=True)
    db.add(s)
    db.commit()
    db.refresh(s)
    return s


def test_permis(db):
    _permis(db, "PT-1", "actif")
    _permis(db, "PT-2", "suspendu")
    r = QhsePortalService.permis(db)
    assert r["permis_total"] == 2
    assert r["actifs"] == 1
    assert r["par_statut"]["suspendu"] == 1


def test_formations_expirees(db):
    _form(db, "TR-1", "Op-A", date.today() - timedelta(days=5))
    _form(db, "TR-2", "Op-B", date.today() + timedelta(days=90))
    r = QhsePortalService.formations(db)
    assert r["formations_total"] == 2
    assert r["expirees"] == 1
    assert r["details_expirees"][0]["operateur"] == "Op-A"


def test_deversements(db):
    _spill(db, "SP-1", "ouvert")
    _spill(db, "SP-2", "resolu")
    r = QhsePortalService.deversements(db)
    assert r["deversements_total"] == 2
    assert r["non_resolus"] == 1


def test_vide_honnete(db):
    r = QhsePortalService.permis(db)
    assert r["permis"] == 0
