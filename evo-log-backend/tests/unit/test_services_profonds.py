"""Tests des services profonds : surestarie (demurrage) et redevances
portuaires CEMAC (honnetete : jamais de facture fabriquee)."""
from datetime import date

import pytest
from fastapi import HTTPException

from app.services.acconage_service import (
    SurestarieService, PortAdvancedTOSService,)


def test_surestarie_calcule_jours_et_montant_reels(db):
    """5 jours x 5 000 XAF = 25 000 XAF, statut encours."""
    s = SurestarieService.calculer_surestarie(
        db, conteneur_id=999,
        date_debut=date(2026, 6, 1), date_fin=date(2026, 6, 5),
        taux_journalier=5000.0)

    assert s.nombre_jours == 5
    assert float(s.montant_total) == 25_000
    assert s.statut == "encours"
    assert s.devise == "XAF"


def test_surestarie_meme_jour_un_seul_jour(db):
    s = SurestarieService.calculer_surestarie(
        db, conteneur_id=999,
        date_debut=date(2026, 6, 10), date_fin=date(2026, 6, 10))
    assert s.nombre_jours == 1


def test_redevances_portuaires_refusent_escole_inconnue(db):
    """Une escale inexistante ne doit JAMAIS produire de facture
    fabriquee : HTTP 404 explicite."""
    with pytest.raises(HTTPException) as exc:
        PortAdvancedTOSService.calculate_port_dues_cemac(db, escale_id=999999)
    assert exc.value.status_code == 404
