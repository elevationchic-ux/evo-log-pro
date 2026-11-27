"""Tests tracabilite : genealogie des lots."""
import pytest

from app.models.tracabilite_deep import BatchGenealogy
from app.services.tracabilite_service import TraceabilityService


def _lien(db, child, parent, proportion=1.0, operation="assemblage"):
    l = BatchGenealogy(company_id=1, child_lot=child, parent_lot=parent,
                       child_type="produit fini", parent_type="matiere premiere",
                       proportion=proportion, quantite_mise_en_oeuvre=100,
                       operation=operation, is_active=True)
    db.add(l)
    db.commit()
    db.refresh(l)
    return l


def test_genealogie_simple(db):
    """LOT-FINI <- LOT-SEMI <- LOT-RAW : 2 ascendants, racine LOT-RAW."""
    _lien(db, "LOT-FINI", "LOT-SEMI")
    _lien(db, "LOT-SEMI", "LOT-RAW")
    r = TraceabilityService.provenance(db, "LOT-FINI")
    assert r["ascendants_total"] == 2
    assert "LOT-RAW" in r["racines"]


def test_genealogie_multi_parents(db):
    """Un lot peut avoir plusieurs parents (melange)."""
    _lien(db, "MELANGE-1", "MAT-A", proportion=0.6)
    _lien(db, "MELANGE-1", "MAT-B", proportion=0.4)
    r = TraceabilityService.tracer_ascendants(db, "MELANGE-1")
    assert r["nb_ascendants"] == 2


def test_cycle_ignore(db):
    """A -> B -> A : le cycle est coupe, pas de boucle infinie."""
    _lien(db, "A", "B")
    _lien(db, "B", "A")
    r = TraceabilityService.tracer_ascendants(db, "A")
    assert r["nb_ascendants"] <= 2


def test_lot_sans_parent(db):
    r = TraceabilityService.provenance(db, "LOT-ISOLE")
    assert r["ascendants_total"] == 0
    assert r["racines"] == []
