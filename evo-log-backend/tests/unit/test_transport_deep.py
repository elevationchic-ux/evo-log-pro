"""Tests transport deep : conformite marchandises dangereuses."""
import pytest
from decimal import Decimal

from app.models.transport_deep import DangerousGoodsLoad
from app.services.transport_deep_service import TransportDeepService


def _dg(db, reference, classe="3", formation=True, etiquettes="3",
        quantite=1000, onu="1203"):
    c = DangerousGoodsLoad(company_id=1, reference=reference,
                           classe_adr=classe, onu_number=onu,
                           quantite_kg=Decimal(str(quantite)) if quantite is not None else None,
                           etiquettes=etiquettes,
                           formation_chauffeur=formation,
                           is_active=True)
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


def test_dg_conforme(db):
    """Chargement complet -> conforme."""
    _dg(db, "DG-1")
    r = TransportDeepService.conformite_dg(db)
    assert r["conformes"] == 1
    assert r["non_conformes"] == 0


def test_dg_sans_formation(db):
    """Pas de formation chauffeur -> non conforme."""
    _dg(db, "DG-2", formation=False)
    r = TransportDeepService.conformite_dg(db)
    assert r["non_conformes"] == 1
    assert "formation_chauffeur_absente" in r["details_non_conformites"][0]["problemes"]


def test_dg_sans_etiquettes_ni_quantite(db):
    _dg(db, "DG-3", etiquettes=None, quantite=None)
    r = TransportDeepService.conformite_dg(db)
    pbs = r["details_non_conformites"][0]["problemes"]
    assert "etiquettes_non_declarees" in pbs
    assert "quantite_non_renseignee" in pbs


def test_vide_honnete(db):
    r = TransportDeepService.conformite_dg(db)
    assert r["chargements"] == 0
