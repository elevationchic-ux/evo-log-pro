"""Tests 3PL : KPI SLA calcules sur operations reelles."""
from datetime import datetime, timezone

from app.models.log3pl_deep import TplPickingLine, TplCrossDock
from app.services.log3pl_service import Log3plSlaService


def _pick(db, client, statut, ref):
    p = TplPickingLine(company_id=1, reference=ref, client=client,
                       statut=statut, is_active=True)
    db.add(p)
    db.commit()
    return p


def test_kpi_vide_honnete(db):
    r = Log3plSlaService.calculer_kpi_client(db, "CLIENT-X", "2026-01")
    assert r["preparation"]["taux_pct"] is None
    assert r["cross_dock"]["taux_equilibre_pct"] is None


def test_taux_preparation_reel(db):
    """2 terminees / 3 operations = 66,7 %."""
    _pick(db, "CLI-A", "termine", "P1")
    _pick(db, "CLI-A", "termine", "P2")
    _pick(db, "CLI-A", "en_cours", "P3")
    _pick(db, "CLI-B", "termine", "P4")  # autre client ignore

    r = Log3plSlaService.calculer_kpi_client(db, "CLI-A", "")
    assert r["preparation"]["operations"] == 3
    assert r["preparation"]["taux_pct"] == 66.7


def test_cross_dock_equilibre(db):
    db.add(TplCrossDock(company_id=1, reference="CD-1", site="SITE-A",
                        date_operation=datetime.now(timezone.utc),
                        nb_entrees=10, nb_sorties=10, is_active=True))
    db.add(TplCrossDock(company_id=1, reference="CD-2", site="SITE-A",
                        date_operation=datetime.now(timezone.utc),
                        nb_entrees=10, nb_sorties=7, is_active=True))
    db.commit()

    r = Log3plSlaService.calculer_kpi_client(db, "CLI-A", "")
    assert r["cross_dock"]["operations"] == 2
    assert r["cross_dock"]["taux_equilibre_pct"] == 50.0


def test_enregistrer_kpi_sans_penalite_inventee(db):
    k = Log3plSlaService.enregistrer_kpi(
        db, client="CLI-A", kpi="taux_preparation", valeur_reelle="95.0",
        valeur_cible="98.0", periode="2026-01")
    assert k.valeur_reelle == "95.0"
    assert k.penalite_appliquee_xaf is None
    assert k.statut == "mesure"
