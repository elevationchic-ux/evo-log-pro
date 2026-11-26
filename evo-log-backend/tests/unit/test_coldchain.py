"""Tests chaine du froid : detection d'excursions et impact honnete."""
import pytest
from fastapi import HTTPException

from app.models.coldchain_deep import ColdChainProduct, ColdChainExcursion
from app.services.coldchain_service import ColdChainExcursionService


def _produit(db, temp_min=-25, temp_max=-15, seuil=4):
    p = ColdChainProduct(company_id=1, code_sku=f"SKU-{temp_min}-{temp_max}",
                         nom="Vaccin test", temp_min_c=temp_min,
                         temp_max_c=temp_max, seuil_excursion_h=seuil)
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


def test_releve_dans_plage_pas_d_excursion(db):
    p = _produit(db)
    r = ColdChainExcursionService.enregistrer_releve(
        db, produit_id=p.id, temperature_c=-20, duree_h=1)
    assert r["excursion"] is False
    assert db.query(ColdChainExcursion).count() == 0


def test_excursion_hors_plage_creee(db):
    """-5 C pendant 8 h (> seuil 4 h) : excursion critique creee."""
    p = _produit(db)
    r = ColdChainExcursionService.enregistrer_releve(
        db, produit_id=p.id, temperature_c=-5, duree_h=8,
        actif_associe="REEFER-01")

    assert r["excursion"] is True
    assert r["impact"] == "critique"
    exc = db.query(ColdChainExcursion).one()
    assert exc.temp_extreme_c == -5
    assert exc.statut == "ouverte"
    assert exc.valeur_perdue_xaf is None  # jamais inventee


def test_excursion_courte_impact_mineur(db):
    """-5 C pendant 2 h (< seuil 4 h) : impact mineur."""
    p = _produit(db)
    r = ColdChainExcursionService.enregistrer_releve(
        db, produit_id=p.id, temperature_c=-5, duree_h=2)
    assert r["excursion"] is True
    assert r["impact"] == "mineur"


def test_produit_sans_plage_honnete(db):
    p = ColdChainProduct(company_id=1, code_sku="SKU-NOPLAGE", nom="Sans plage")
    db.add(p)
    db.commit()
    db.refresh(p)
    r = ColdChainExcursionService.enregistrer_releve(
        db, produit_id=p.id, temperature_c=30, duree_h=1)
    assert r["excursion"] is False
    assert "non configuree" in r["raison"]


def test_produit_inconnu_404(db):
    with pytest.raises(HTTPException):
        ColdChainExcursionService.enregistrer_releve(
            db, produit_id=999999, temperature_c=0, duree_h=1)


def test_cloture_sans_valeur_inventee(db):
    p = _produit(db)
    r = ColdChainExcursionService.enregistrer_releve(
        db, produit_id=p.id, temperature_c=-5, duree_h=8)
    exc_id = db.query(ColdChainExcursion).one().id
    exc = ColdChainExcursionService.cloturer_excursion(db, exc_id)
    assert exc.statut == "cloturee"
    assert exc.valeur_perdue_xaf is None
