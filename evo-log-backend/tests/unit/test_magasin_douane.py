"""Tests magasin douane : rapport entrepot (refus honnete)."""
import pytest

from app.services.magasin_douane_service import MagasinDouaneReportingService


def test_rapport_entrepot_inconnu_refuse(db):
    with pytest.raises(ValueError):
        MagasinDouaneReportingService.rapport_entrepot(db, entrepot_id=999999)
