"""Tests magasin deep : ruptures et peremptibles."""
from datetime import date, timedelta
import pytest
from decimal import Decimal

from app.models.magasin_deep import StockAlert, ExpiryRecord
from app.services.magasin_deep_service import MagasinDeepService


def _alerte(db, code, quantite, seuil_min, point_commande=None):
    a = StockAlert(company_id=1, code_alerte=code, article_id=1,
                   seuil_min=Decimal(str(seuil_min)) if seuil_min else None,
                   point_commande=Decimal(str(point_commande)) if point_commande else None,
                   quantite_actuelle=Decimal(str(quantite)), is_active=True)
    db.add(a)
    db.commit()
    db.refresh(a)
    return a


def _lot(db, numero, peremption, quantite=10):
    l = ExpiryRecord(company_id=1, numero_lot=numero, article_id=1,
                     quantite=Decimal(str(quantite)),
                     date_peremption=peremption, is_active=True)
    db.add(l)
    db.commit()
    db.refresh(l)
    return l


def test_ruptures(db):
    """1 en rupture (5 < seuil 10), 1 sous point commande."""
    _alerte(db, "AL-1", 5, seuil_min=10, point_commande=20)
    _alerte(db, "AL-2", 15, seuil_min=10, point_commande=20)
    r = MagasinDeepService.ruptures(db)
    assert r["alertes_total"] == 2
    assert r["en_rupture"] == 1
    assert r["sous_point_commande"] == 1


def test_peremptibles(db):
    """1 expire, 1 a risque 10j, 1 lointain 90j."""
    _lot(db, "LOT-EXP", date.today() - timedelta(days=5))
    _lot(db, "LOT-RISK", date.today() + timedelta(days=10))
    _lot(db, "LOT-OK", date.today() + timedelta(days=90))
    r = MagasinDeepService.peremptibles(db)
    assert r["lots_total"] == 3
    assert r["deja_expires"] == 1
    assert r["a_risque_30j"] == 1


def test_vide_honnete(db):
    r = MagasinDeepService.ruptures(db)
    assert r["alertes"] == 0
