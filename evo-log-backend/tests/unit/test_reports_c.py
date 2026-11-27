"""Tests reports C : rapports en retard et stats exports."""
from datetime import datetime, timedelta, timezone
import pytest

from app.models.reports_c_deep import RptcScheduledReport, RptcDataExport
from app.services.reports_c_service import ReportsCService


def _rapport(db, reference, prochaine, frequence="quotidien"):
    m = RptcScheduledReport(company_id=1, reference=reference, nom=f"Rapport {reference}",
                            frequence=frequence, prochaine_execution=prochaine,
                            is_active=True)
    db.add(m)
    db.commit()
    db.refresh(m)
    return m


def test_rapports_en_retard(db):
    """1 en retard, 1 a venir."""
    _rapport(db, "R1", datetime.now(timezone.utc) - timedelta(hours=2))
    _rapport(db, "R2", datetime.now(timezone.utc) + timedelta(hours=2))
    r = ReportsCService.rapports_en_retard(db)
    assert r["en_retard"] == 1
    assert r["a_venir"] == 1
    assert r["details_retard"][0]["reference"] == "R1"


def test_vide_honnete(db):
    r = ReportsCService.rapports_en_retard(db)
    assert r["rapports_total"] == 0
    r2 = ReportsCService.stats_exports(db)
    assert r2["exports"] == 0
