"""Tests magasin B : ecarts inventaire et receptions."""
import pytest

from app.models.magasin_b_deep import MagasinbStockCount, MagasinbGoodsReceipt
from app.services.magasin_b_service import MagasinBService


def _count(db, article, theo, phys, ecart=None, emplacement="A-1"):
    c = MagasinbStockCount(company_id=1, reference=f"SC-{article}-{theo}-{phys}",
                           article=article, emplacement=emplacement,
                           quantite_theorique=theo, quantite_physique=phys,
                           ecart=ecart, agent="Agent-1", is_active=True)
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


def _receipt(db, reference, fournisseur, controles=False, statut="recue"):
    r = MagasinbGoodsReceipt(company_id=1, reference=reference,
                             bon_commande="BC-100", fournisseur=fournisseur,
                             nb_articles=5, quantite_recue=100,
                             controles_fait=controles, statut=statut, is_active=True)
    db.add(r)
    db.commit()
    db.refresh(r)
    return r


def test_ecarts_inventaire(db):
    """1 ecart (-5), 1 conforme, 1 ecart stocke."""
    _count(db, "ART-A", 100, 95)          # ecart calcule -5
    _count(db, "ART-B", 50, 50)           # conforme
    _count(db, "ART-C", 200, 190, ecart=-10)  # ecart stocke
    r = MagasinBService.ecarts_inventaire(db)
    assert r["lignes_total"] == 3
    assert r["ecarts"] == 2
    assert r["conformes"] == 1
    assert r["details_ecarts"][0]["ecart"] == -5


def test_receptions_sans_controle(db):
    _receipt(db, "GR-1", "Fourn-A", controles=False)
    _receipt(db, "GR-2", "Fourn-B", controles=True)
    r = MagasinBService.receptions(db)
    assert r["receptions_total"] == 2
    assert r["sans_controle"] == 1
    assert r["details_sans_controle"][0]["reference"] == "GR-1"


def test_vide_honnete(db):
    r = MagasinBService.ecarts_inventaire(db)
    assert r["lignes"] == 0
