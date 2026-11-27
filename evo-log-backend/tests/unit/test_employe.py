"""Tests employe : conges et temps par projet."""
from datetime import date
import pytest
from decimal import Decimal

from app.models.employe_d_deep import EmpLeaveRequest, EmpTimesheetEntry
from app.services.employe_service import EmployeService


def _conge(db, collab, jours, statut="approuve", reference="C1"):
    c = EmpLeaveRequest(company_id=1, reference=reference, collaborateur=collab,
                        type_conge="annuel", debut=date.today(),
                        fin=date.today(), jours=jours, statut=statut,
                        is_active=True)
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


def _pointage(db, collab, heures, projet="PROJ-A", reference="P1"):
    p = EmpTimesheetEntry(company_id=1, reference=reference, collaborateur=collab,
                          date=date.today(), heures=Decimal(str(heures)),
                          projet=projet, is_active=True)
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


def test_solde_conges(db):
    """Droit 30j, consommes 15, en attente 5 -> solde 15."""
    _conge(db, "EMP-1", 10, "approuve", "C1")
    _conge(db, "EMP-1", 5, "approuve", "C2")
    _conge(db, "EMP-1", 5, "soumis", "C3")
    r = EmployeService.solde_conges(db, "EMP-1", droit_annuel=30)
    assert r["jours_consommes"] == 15
    assert r["jours_en_attente"] == 5
    assert r["solde_jours"] == 15


def test_temps_par_projet(db):
    _pointage(db, "EMP-2", 8, "PROJ-A", "P1")
    _pointage(db, "EMP-2", 4, "PROJ-B", "P2")
    _pointage(db, "EMP-2", 8, "PROJ-A", "P3")
    r = EmployeService.temps_par_projet(db, "EMP-2")
    assert r["heures_par_projet"]["PROJ-A"] == 16.0
    assert r["heures_total"] == 20.0


def test_vide_honnete(db):
    r = EmployeService.solde_conges(db, "EMP-INCONNU")
    assert r["jours_consommes"] == 0
