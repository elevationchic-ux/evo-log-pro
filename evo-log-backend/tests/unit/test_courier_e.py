"""Tests courier avance : performance et productivite livreur."""
from datetime import date
import pytest
from fastapi import HTTPException

from app.models.courier_e_deep import (
    Cour2DeliveryAttempt, Cour2CourierShiftLog,)
from app.services.courier_e_service import CourierEService


def _attempt(db, livreur, statut, reference):
    a = Cour2DeliveryAttempt(company_id=1, reference=reference,
                             livreur=livreur, statut=statut, is_active=True)
    db.add(a)
    db.commit()
    db.refresh(a)
    return a


def _shift(db, livreur, colis, km, reference):
    s = Cour2CourierShiftLog(company_id=1, reference=reference, livreur=livreur,
                             date=date.today(), colis_livres=colis, km=km,
                             is_active=True)
    db.add(s)
    db.commit()
    db.refresh(s)
    return s


def test_taux_reussite(db):
    """3 livrees / 4 tentatives = 75 %."""
    _attempt(db, "LIV-1", "livre", "T1")
    _attempt(db, "LIV-1", "livre", "T2")
    _attempt(db, "LIV-1", "livre", "T3")
    _attempt(db, "LIV-1", "echec_absent", "T4")
    r = CourierEService.performance_livreur(db, "LIV-1")
    assert r["tentatives_total"] == 4
    assert r["taux_reussite_pct"] == 75.0


def test_livreur_sans_tentative_honnete(db):
    r = CourierEService.performance_livreur(db, "LIV-INCONNU")
    assert r["tentatives"] == 0


def test_productivite(db):
    """2 shifts : 40 colis / 80 km = 0,5 colis/km."""
    _shift(db, "LIV-2", 20, 40, "S1")
    _shift(db, "LIV-2", 20, 40, "S2")
    r = CourierEService.productivite_livreur(db, "LIV-2")
    assert r["colis_livres_total"] == 40
    assert r["colis_par_km"] == 0.5
