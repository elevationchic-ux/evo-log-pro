"""Tests numerotation : allocation atomique des numeros."""
import pytest
from fastapi import HTTPException

from app.services.numerotation_service import NumerotationService


def test_allocation_sequentielle(db):
    """3 allocations -> 1, 2, 3 avec format PREFIXE-EXERCICE-NNNNN."""
    r1 = NumerotationService.prochain_numero(db, "FACTURE", 2026, "FAC")
    r2 = NumerotationService.prochain_numero(db, "FACTURE", 2026, "FAC")
    r3 = NumerotationService.prochain_numero(db, "FACTURE", 2026, "FAC")
    assert r1["numero"] == "FAC-2026-00001"
    assert r2["numero"] == "FAC-2026-00002"
    assert r3["numero"] == "FAC-2026-00003"


def test_sequences_independantes(db):
    """FACTURE et AVOIR n'ont pas la meme sequence."""
    f = NumerotationService.prochain_numero(db, "FACTURE", 2026, "FAC")
    a = NumerotationService.prochain_numero(db, "AVOIR", 2026, "AVO")
    assert f["numero"] == "FAC-2026-00001"
    assert a["numero"] == "AVO-2026-00001"


def test_exercice_invalide_refuse(db):
    with pytest.raises(HTTPException):
        NumerotationService.prochain_numero(db, "FACTURE", 0, "FAC")


def test_audit_vide_honnete(db):
    r = NumerotationService.audit_sequence(db, "X", 2026, "X")
    assert r["dernier_numero"] == 0
