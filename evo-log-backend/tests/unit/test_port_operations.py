"""Tests operations portuaires : facturation remorquage et cadence."""
import pytest
from decimal import Decimal
from fastapi import HTTPException

from app.models.port_operations_deep import TowageOperation, CargoHandlingPlan
from app.services.port_operations_service import PortOperationsService


def test_facturation_remorquage_complete(db):
    """3 h x 450 000 XAF x 2 remorqueurs = 2 700 000 XAF."""
    op = TowageOperation(company_id=1, reference="REM-1",
                         nombre_remorqueurs=2, duree_heures=Decimal("3"),
                         tarif_xaf=Decimal("450000"))
    db.add(op)
    db.commit()
    db.refresh(op)

    r = PortOperationsService.calculer_facturation_remorquage(db, op.id)
    assert r["montant_xaf"] == 2_700_000
    assert r["nombre_remorqueurs"] == 2


def test_facturation_refusee_sans_tarif(db):
    """Pas de tarif -> 422 honnete, jamais de facture fabriquee."""
    op = TowageOperation(company_id=1, reference="REM-2",
                         duree_heures=Decimal("2"))
    db.add(op)
    db.commit()
    db.refresh(op)

    with pytest.raises(HTTPException) as exc:
        PortOperationsService.calculer_facturation_remorquage(db, op.id)
    assert exc.value.status_code == 422


def test_cadence_reelle_vs_prevue(db):
    plan = CargoHandlingPlan(company_id=1, reference_plan="PLAN-1",
                             cadence_prevue_t_h=Decimal("50"),
                             cadence_reelle_t_h=Decimal("60"))
    db.add(plan)
    db.commit()
    db.refresh(plan)

    r = PortOperationsService.analyse_cadence_manutenance(db, plan.id)
    assert r["ecart_pct"] == 20.0
    assert r["performance"] == "superieure"


def test_cadence_non_mesuree_honnete(db):
    plan = CargoHandlingPlan(company_id=1, reference_plan="PLAN-2",
                             cadence_prevue_t_h=Decimal("50"))
    db.add(plan)
    db.commit()
    db.refresh(plan)

    r = PortOperationsService.analyse_cadence_manutenance(db, plan.id)
    assert r["ecart_pct"] is None
    assert "jamais estime" in r["note"]


def test_operation_inconnue_404(db):
    with pytest.raises(HTTPException):
        PortOperationsService.calculer_facturation_remorquage(db, 999999)
