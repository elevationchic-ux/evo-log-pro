"""Tests reglementaire : reglementations applicables/a venir."""
from datetime import date, timedelta
import pytest

from app.models.reglementaire import Reglementation, TypeReglementation
from app.services.reglementaire_service import ReglementaireService


def _reg(db, code, application, categorie="DOUANE", est_actif=True):
    r = Reglementation(code=code, titre=f"Reg {code}",
                       description="Texte reglementaire",
                       type_reglement=TypeReglementation.DECRET,
                       date_promulgation=date.today() - timedelta(days=60),
                       date_application=application,
                       categorie=categorie, est_actif=est_actif)
    db.add(r)
    db.commit()
    db.refresh(r)
    return r


def test_en_vigueur_et_a_venir(db):
    """1 en vigueur, 1 a venir (future), 1 inactive ignoree."""
    _reg(db, "REG-1", date.today() - timedelta(days=10), "DOUANE")
    _reg(db, "REG-2", date.today() + timedelta(days=30), "FISCALITE")
    _reg(db, "REG-3", date.today() - timedelta(days=5), "ENVIRONNEMENT", est_actif=False)
    r = ReglementaireService.applicables(db)
    assert r["en_vigueur"] == 1
    assert r["a_venir"] == 1
    assert r["par_categorie"]["DOUANE"] == 1
    assert r["details_a_venir"][0]["code"] == "REG-2"


def test_vide_honnete(db):
    r = ReglementaireService.applicables(db)
    assert r["en_vigueur"] == 0
    assert r["a_venir"] == 0
