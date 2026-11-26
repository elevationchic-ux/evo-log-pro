"""Tests integration Cameroun : BSC/CNCC (generation, frais, validation)."""
import pytest

from app.services.integration_cameroun import BSCService


def test_generer_bsc_calcule_frais_sur_fob(db):
    """Frais BSC = 0,02 % de la valeur FOB, statut en_attente."""
    bsc = BSCService.generer_bsc(
        db, numero_connaisse="BL-2026-001", navire="MT Africa Star",
        port_chargement="Shanghai", port_dechargement="Douala",
        agent="AGENT-CMR", importateur="IMPORT-X",
        poids_brut_tonnes=1200.0, valeur_fob=500_000)

    assert bsc.numero_bsc.startswith("BSC-")
    assert float(bsc.montant_frais_bsc) == 100.0      # 500 000 x 0,0002
    assert bsc.statut == "en_attente"
    assert bsc.date_validite > bsc.date_emission


def test_valider_bsc_change_statut(db):
    bsc = BSCService.generer_bsc(
        db, numero_connaisse="BL-1", navire="V", port_chargement="A",
        port_dechargement="B", agent="AG", importateur="IM",
        poids_brut_tonnes=10.0, valeur_fob=50_000)

    valide = BSCService.valider_bsc(db, bsc.numero_bsc)
    assert valide.statut == "valide"
    assert valide.date_validation is not None


def test_valider_bsc_inconnu_refuse(db):
    with pytest.raises(ValueError):
        BSCService.valider_bsc(db, "BSC-INEXISTANT")
