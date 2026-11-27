"""Tests dashboard : atteinte objectifs KPI."""
import pytest
from decimal import Decimal

from app.models.dashboard_b_deep import DashboardbOperationalKpi
from app.services.dashboard_service import DashboardService


def _kpi(db, libelle, valeur, objectif, reference="KPI-1"):
    k = DashboardbOperationalKpi(company_id=1, reference=reference, libelle=libelle,
                                 module_source="logistique", valeur=Decimal(str(valeur)),
                                 objectif=Decimal(str(objectif)), unite="unit",
                                 is_active=True)
    db.add(k)
    db.commit()
    db.refresh(k)
    return k


def test_atteinte_et_retard(db):
    """1 KPI atteint (110/100), 1 en retard (50/100), 1 sans objectif."""
    _kpi(db, "KPI-A", 110, 100, "K1")
    _kpi(db, "KPI-B", 50, 100, "K2")
    k3 = DashboardbOperationalKpi(company_id=1, reference="K3", libelle="KPI-C",
                                  valeur=Decimal("5"), is_active=True)
    db.add(k3)
    db.commit()
    r = DashboardService.atteinte_objectifs(db)
    assert r["kpis_total"] == 3
    assert r["atteints"] == 1
    assert r["en_retard"] == ["KPI-B"]
    assert r["sans_objectif"] == 1


def test_vide_honnete(db):
    r = DashboardService.atteinte_objectifs(db)
    assert r["kpis"] == 0
