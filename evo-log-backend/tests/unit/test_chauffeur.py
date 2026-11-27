"""Tests chauffeur : temps de conduite et repos."""
from datetime import datetime, date, timezone
import pytest

from app.models.chauffeur_c_deep import ChfDrivingTimeRecord, ChfRestBreak
from app.services.chauffeur_service import ChauffeurService

JOUR = date(2026, 3, 10)


def _cond(db, chauffeur, minutes, jour=JOUR, reference="D1"):
    d = ChfDrivingTimeRecord(company_id=1, reference=reference, chauffeur=chauffeur,
                             debut=datetime(jour.year, jour.month, jour.day, 6, tzinfo=timezone.utc),
                             minutes_conduite=minutes, is_active=True)
    db.add(d)
    db.commit()
    db.refresh(d)
    return d


def _pause(db, chauffeur, minutes, jour=JOUR, reference="R1"):
    p = ChfRestBreak(company_id=1, reference=reference, chauffeur=chauffeur,
                     debut=datetime(jour.year, jour.month, jour.day, 12, tzinfo=timezone.utc),
                     duree_min=minutes, is_active=True)
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


def test_conduite_dans_limite(db):
    """300 + 200 = 500 min < 540 -> conforme."""
    _cond(db, "CHF-1", 300, reference="D1")
    _cond(db, "CHF-1", 200, reference="D2")
    r = ChauffeurService.conduite_jour(db, "CHF-1", JOUR)
    assert r["minutes_conduite"] == 500
    assert r["conforme"] is True


def test_conduite_depasse_limite(db):
    """600 min > 540 -> depassement 60."""
    _cond(db, "CHF-2", 600, reference="D3")
    r = ChauffeurService.conduite_jour(db, "CHF-2", JOUR)
    assert r["conforme"] is False
    assert r["depassement_minutes"] == 60


def test_repos_insuffisant(db):
    """Pause 30 min < seuil 45 -> alerte."""
    _pause(db, "CHF-3", 30, reference="R1")
    r = ChauffeurService.repos_insuffisants(db, "CHF-3", JOUR)
    assert r["alerte"] is True


def test_sans_pause_alerte(db):
    r = ChauffeurService.repos_insuffisants(db, "CHF-4", JOUR)
    assert r["alerte"] is True
    assert "Aucune pause" in r["note"]
