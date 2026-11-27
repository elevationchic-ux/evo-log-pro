"""Tests port Cameroun : redevances tarifaires et indicateurs terminal."""
from datetime import date, timedelta
import pytest
from decimal import Decimal
from fastapi import HTTPException

from app.models.port_cameroun import TarifPortuaire, TerminalPortuaire
from app.services.port_cameroun_service import PortCamerounService


def _tarif(db, code="THC-20", prix=350000, unite="CONTENEUR"):
    t = TarifPortuaire(code_tarif=code, designation="THC 20p",
                       categorie="THC", sous_categorie="import",
                       unite=unite, prix_unitaire=Decimal(str(prix)),
                       date_application=date.today() - timedelta(days=30),
                       taux_tva=Decimal("19.25"), est_actif=True)
    db.add(t)
    db.commit()
    db.refresh(t)
    return t


def test_redevance_avec_tva(db):
    """1 conteneur x 350 000 = 350 000 HT, TVA 19,25 % = 67 375, TTC 417 375."""
    _tarif(db)
    r = PortCamerounService.calculer_redevance(db, "THC-20", quantite=1)
    assert r["base_ht_xaf"] == 350_000
    assert r["tva_xaf"] == 67_375
    assert r["total_ttc_xaf"] == 417_375


def test_tarif_expire_refuse(db):
    t = _tarif(db, code="THC-OLD")
    t.date_expiration = date.today() - timedelta(days=1)
    db.commit()
    with pytest.raises(HTTPException) as exc:
        PortCamerounService.calculer_redevance(db, "THC-OLD", quantite=1)
    assert "expire" in exc.value.detail.lower()


def test_tarif_inconnu_404(db):
    with pytest.raises(HTTPException):
        PortCamerounService.calculer_redevance(db, "INCONNU", quantite=1)


def test_indicateurs_terminal(db):
    """Terminal 100 000 TEU / 5 grues = 20 000 TEU/grue."""
    t = TerminalPortuaire(port_id=1, code="TCO", nom="Terminal",
                          type_terminal="conteneurs",
                          capacite_teus=100000, nombre_grues=5,
                          est_actif=True)
    db.add(t)
    db.commit()
    db.refresh(t)
    r = PortCamerounService.indicateurs_terminal(db, t.id)
    assert r["teu_par_grue"] == 20_000.0
