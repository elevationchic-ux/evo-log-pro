# Fichier conftest.py pour pytest  configuration globale tests EVO-LOG
import pytest

# Fixtures communes disponibles dans tous les tests
@pytest.fixture
def taux_cameroun():
    return {
        "tva": 0.1925,
        "cnps_salarial": 0.028,
        "cnps_patronal": 0.172,
        "cnps_plafond": 750_000,
        "tec_cat0": 0.00,
        "tec_cat1": 0.05,
        "tec_cat2": 0.10,
        "tec_cat3": 0.20,
        "redevance_informatique": 0.0035,
        "taxe_communautaire": 0.01,
    }
