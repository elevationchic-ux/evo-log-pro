"""Tests des rapports avances : vides honnetes et compteurs reels."""
from datetime import date
from decimal import Decimal

from app.models.user import User
from app.models.magasin import Stock
from app.services.reporting_avance_service import (
    RHReportingService, MagasinReportingService, TransportReportingService,)


def _user(db, username="u1"):
    u = User(username=username, email=f"{username}@t.cm", hashed_password="x",
             is_active=True)
    db.add(u)
    db.commit()
    return u


def test_rapport_effectif_compte_les_actifs(db):
    _user(db, "actif1")
    s = RHReportingService.rapport_effectif(db, date.today())
    assert s["effectif_total"] >= 1
    assert s["date_rapport"] == date.today()


def test_rapport_ruptures_vide_honnete(db):
    r = MagasinReportingService.rapport_ruptures(db, seuil=10.0)
    assert r["articles_en_rupture"] == 0
    assert r["articles"] == []


def test_rapport_ruptures_detecte_le_seuil(db):
    db.add(Stock(company_id=None, code_article="RUP-1", designation="Piece",
                 quantite_disponible=5, quantite_reservee=0,
                 prix_unitaire=Decimal("1000"), is_active=True))
    db.commit()
    r = MagasinReportingService.rapport_ruptures(db, seuil=10.0)
    assert r["articles_en_rupture"] == 1
    assert r["articles"][0]["quantite"] == 5
    assert r["articles"][0]["code_article"] == "RUP-1"


def test_rapport_accidents_vide_honnete(db):
    r = TransportReportingService.rapport_accidents(db, date(2026, 1, 1), date(2026, 12, 31))
    assert r["total_accidents"] == 0
    assert r["taux_blessures"] == 0
