"""Tests technicien : temps MO et tickets par severite."""
from datetime import date
import pytest

from app.models.technicien_d_deep import TechLaborTimesheet, TechBreakdownTicket
from app.services.technicien_service import TechnicienService


def _feuille(db, tech, minutes, ot="OT-1", reference="T1"):
    f = TechLaborTimesheet(company_id=1, reference=reference, technicien=tech,
                           ordre_travail=ot, minutes=minutes, date=date.today(),
                           is_active=True)
    db.add(f)
    db.commit()
    db.refresh(f)
    return f


def _ticket(db, severite, statut="ouvert", reference="TK1"):
    t = TechBreakdownTicket(company_id=1, reference=reference, severite=severite,
                            statut=statut, is_active=True)
    db.add(t)
    db.commit()
    db.refresh(t)
    return t


def test_temps_mo_par_technicien(db):
    """2 feuilles : 90 + 30 min sur OT-1, 60 sur OT-2 = 180 min."""
    _feuille(db, "TECH-1", 90, "OT-1", "F1")
    _feuille(db, "TECH-1", 30, "OT-1", "F2")
    _feuille(db, "TECH-1", 60, "OT-2", "F3")
    r = TechnicienService.temps_mo_technicien(db, "TECH-1")
    assert r["minutes_total"] == 180
    assert r["heures_total"] == 3.0
    assert r["par_ordre_travail"]["OT-1"] == 120


def test_tickets_par_severite(db):
    _ticket(db, "critique", "ouvert", "TK-A")
    _ticket(db, "mineure", "resolu", "TK-B")
    _ticket(db, "critique", "ouvert", "TK-C")
    r = TechnicienService.tickets_par_severite(db)
    assert r["tickets_total"] == 3
    assert r["par_severite"]["critique"] == 2
    assert r["ouverts"] == 2


def test_vide_honnete(db):
    r = TechnicienService.temps_mo_technicien(db, "TECH-INCONNU")
    assert r["feuilles"] == 0
