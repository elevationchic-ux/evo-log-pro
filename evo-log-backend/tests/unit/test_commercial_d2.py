"""Tests commercial D2 : veille concurrentielle."""
from datetime import date
import pytest

from app.models.commercial_d2_deep import CommCompetitorNote
from app.services.commercial_d2_service import CommercialD2Service


def _note(db, reference, concurrent, fait, marche="Cameroun", d=None):
    n = CommCompetitorNote(company_id=1, reference=reference,
                           concurrent=concurrent, fait_observe=fait,
                           marche=marche, date=d or date.today(), is_active=True)
    db.add(n)
    db.commit()
    db.refresh(n)
    return n


def test_veille_par_concurrent(db):
    """2 notes sur Conc-A (marches Cameroun + CEMAC), 1 sur Conc-B."""
    _note(db, "NC-1", "Conc-A", "Baisse tarif fret", "Cameroun")
    _note(db, "NC-2", "Conc-A", "Nouveau terminal", "CEMAC")
    _note(db, "NC-3", "Conc-B", "Fusion", "Cameroun")
    r = CommercialD2Service.veille(db)
    assert r["notes_total"] == 3
    assert r["par_concurrent"]["Conc-A"] == 2
    assert r["par_marche"]["Cameroun"] == 2


def test_veille_filtre(db):
    _note(db, "NC-4", "Conc-A", "Fait A")
    _note(db, "NC-5", "Conc-B", "Fait B")
    r = CommercialD2Service.veille(db, concurrent="Conc-B")
    assert r["notes_total"] == 1
    assert r["details"][0]["fait"] == "Fait B"


def test_vide_honnete(db):
    r = CommercialD2Service.veille(db)
    assert r["notes"] == 0
