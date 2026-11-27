"""Tests amenagement B : avancement dragage et echeance concession."""
from datetime import date, timedelta
import pytest
from fastapi import HTTPException

from app.models.amenagement_b_deep import AmgtbDredgingProject, AmgtbConcessionPlot
from app.services.amenagement_b_service import AmenagementBService


def test_avancement_dragage(db):
    """30 000 / 100 000 = 30 %."""
    p = AmgtbDredgingProject(company_id=1, reference="DRAG-1", zone="Port",
                             volume_a_draguer_m3=100000, volume_rejete_m3=30000,
                             is_active=True)
    db.add(p)
    db.commit()
    db.refresh(p)
    r = AmenagementBService.avancement_dragage(db, p.id)
    assert r["avancement_pct"] == 30.0
    assert r["reste_a_draguer_m3"] == 70000


def test_avancement_honnete_sans_volume(db):
    p = AmgtbDredgingProject(company_id=1, reference="DRAG-2",
                             is_active=True)
    db.add(p)
    db.commit()
    db.refresh(p)
    r = AmenagementBService.avancement_dragage(db, p.id)
    assert r["avancement_pct"] is None


def test_echeance_concession_proche(db):
    """Echeance dans 60 j -> alerte renouvellement."""
    c = AmgtbConcessionPlot(company_id=1, reference="CONC-1",
                            date_echeance=date.today() + timedelta(days=60),
                            is_active=True)
    db.add(c)
    db.commit()
    db.refresh(c)
    r = AmenagementBService.echeance_concession(db, c.id)
    assert r["jours_restants"] == 60
    assert r["alerte_renouvellement"] is True


def test_concession_inconnue_404(db):
    with pytest.raises(HTTPException):
        AmenagementBService.echeance_concession(db, 999999)
