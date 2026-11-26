"""Tests transit CEMAC : refus honnete sans nomenclature SH et calcul
des droits de port (quantite x taux)."""
from datetime import date

import pytest

from app.services.transit_avance_service import (
    NomenclatureCEMACService, DroitPortService,)


def test_calculer_droits_refuse_sans_nomenclature(db):
    """Position SH absente de la nomenclature CEMAC et aucun taux fourni :
    ValueError explicite — jamais de droit fabrique."""
    with pytest.raises(ValueError):
        NomenclatureCEMACService.calculer_droits(
            db, code_hs="9999999999", valeur_declaree=1_000_000)


def test_calculer_droit_port_montant_reel(db):
    """quantite x taux = montant exact, statut facture."""
    droit = DroitPortService.calculer_droit_port(
        db, dossier_transit_id=999,
        type_droit="stockage", description="Stockage 3 jours",
        base_calcul="jour", quantite=3, taux=25000)

    assert float(droit.montant) == 75_000
    assert droit.devise == "XAF"
    assert droit.statut == "facture"
