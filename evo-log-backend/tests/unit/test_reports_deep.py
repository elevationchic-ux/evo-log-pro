"""Tests reports deep : scorecards et benchmarks."""
import pytest
from decimal import Decimal

from app.models.reports_deep import Scorecard, IndustryBenchmark
from app.services.reports_deep_service import ReportsDeepService


def _score(db, pole, rouges, oranges, verts, score, periode="2026-T1", reference="SC-1"):
    s = Scorecard(company_id=1, reference=reference, pole=pole, periode=periode,
                  nb_kpis=rouges + oranges + verts,
                  score_global_pct=Decimal(str(score)),
                  kpis_rouges=rouges, kpis_oranges=oranges, kpis_verts=verts,
                  is_active=True)
    db.add(s)
    db.commit()
    db.refresh(s)
    return s


def _bench(db, indicateur, interne, ref, reference="B-1"):
    b = IndustryBenchmark(company_id=1, reference=reference, indicateur=indicateur,
                          valeur_interne=Decimal(str(interne)),
                          valeur_benchmark=Decimal(str(ref)),
                          is_active=True)
    db.add(b)
    db.commit()
    db.refresh(b)
    return b


def test_scorecards(db):
    """2 poles : 1 avec 2 rouges, 1 avec 0 ; scores 70 + 90 = 80."""
    _score(db, "Transport", 2, 1, 3, 70, "2026-T1", "SC1")
    _score(db, "Magasin", 0, 0, 5, 90, "2026-T1", "SC2")
    r = ReportsDeepService.scorecards(db, periode="2026-T1")
    assert r["scorecards_total"] == 2
    assert r["kpis_rouges"] == 2
    assert r["score_moyen_pct"] == 80.0
    assert len(r["par_pole"]) == 2


def test_benchmarks(db):
    """1 au-dessus (+10 %), 1 en retard (-10 %)."""
    _bench(db, "Delai livraison", 110, 100, "B1")
    _bench(db, "Taux casse", 90, 100, "B2")
    r = ReportsDeepService.benchmarks(db)
    assert r["comparables"] == 2
    assert r["au_dessus"] == 1
    assert r["en_retard"] == 1
    assert r["details_retard"][0]["indicateur"] == "Taux casse"


def test_vide_honnete(db):
    r = ReportsDeepService.scorecards(db)
    assert r["scorecards"] == 0
