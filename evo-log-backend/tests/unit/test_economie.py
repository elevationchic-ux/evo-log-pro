"""Tests economie : indicateurs financiers par categorie."""
import pytest
from decimal import Decimal

from app.models.reporting import IndicateurFinancier
from app.services.economie_service import EconomieService


def _ind(db, code, nom, categorie, actuelle, objectif=None, precedente=None):
    i = IndicateurFinancier(code=code, nom=nom, categorie=categorie,
                            periode="mensuel",
                            valeur_actuelle=Decimal(str(actuelle)),
                            valeur_precedente=Decimal(str(precedente)) if precedente else None,
                            objectif=Decimal(str(objectif)) if objectif else None)
    db.add(i)
    db.commit()
    db.refresh(i)
    return i


def test_indicateurs_par_categorie(db):
    """2 rentabilite (1 sous objectif), 1 liquidite."""
    _ind(db, "MARGE", "Marge brute", "rentabilite", 15, objectif=20)
    _ind(db, "ROE", "ROE", "rentabilite", 12, objectif=10)
    _ind(db, "BFR", "Besoin en fonds", "liquidite", 500, objectif=600)
    r = EconomieService.indicateurs(db, categorie="rentabilite")
    assert r["indicateurs_total"] == 2
    assert r["par_categorie"]["rentabilite"] == 2
    assert r["sous_objectif"] == 1
    assert r["details_sous_objectif"][0]["code"] == "MARGE"


def test_indicateurs_global(db):
    _ind(db, "LIQ", "Liquidite", "liquidite", 1.5)
    r = EconomieService.indicateurs(db)
    assert r["indicateurs_total"] >= 1
    assert "liquidite" in r["par_categorie"]


def test_vide_honnete(db):
    r = EconomieService.indicateurs(db, categorie="inconnu")
    assert r["indicateurs"] == 0
