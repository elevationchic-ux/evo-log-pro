"""Tests du domaine juridique : contrats, contentieux, echeances/preavis."""
from datetime import date, timedelta

import pytest

from app.models.juridique import ContratJuridique
from app.models.tenant import Company
from app.services.juridique_service import JuridiqueService


@pytest.fixture
def societe(db):
    c = Company(code="JUR-TEST", nom="Juridique Test SA", is_active=True, modules_actives="[]")
    db.add(c)
    db.commit()
    return c


def _contrat(db, societe, **kw):
    data = dict(
        company_id=societe.id, reference="CTR-001", type_contrat="bail",
        objet="Bail local warehouse Douala", partie_adverse="SCI Immo",
        montant=5000000, date_debut=date(2025, 1, 1),
        date_fin=date.today() + timedelta(days=60),
        reconduction="tacite", preavis_jours=30, statut="actif")
    data.update(kw)
    return JuridiqueService.creer_contrat(db, data)


def test_contrat_dates_invalides_refusees(db, societe):
    with pytest.raises(ValueError):
        _contrat(db, societe, date_debut=date(2026, 6, 1), date_fin=date(2026, 1, 1))


def test_echeance_et_preavis_tacite(db, societe):
    _contrat(db, societe)
    echeances = JuridiqueService.echeances_a_surveiller(db, jours=120)
    assert len(echeances) == 1
    e = echeances[0]
    assert e["jours_restants"] <= 60
    assert "tacite" in e["motif"]
    assert e["preavis_a_notifier_avant_le"] == e["date_fin"] - timedelta(days=30)


def test_contrat_sans_fin_n_echeance_pas(db, societe):
    _contrat(db, societe, reference="CTR-002", date_fin=None)
    assert JuridiqueService.echeances_a_surveiller(db, jours=365) == []


def test_contentieux_passe_contrat_en_contentieux(db, societe):
    contrat = _contrat(db, societe)
    c = JuridiqueService.creer_contentieux(db, {
        "company_id": societe.id, "reference": "CTJ-001",
        "contrat_id": contrat.id, "type_contentieux": "litige_fournisseur",
        "description": "Retard de livraison", "date_declaration": date.today(),
        "montant_reclame": 1200000, "statut": "ouvert"})
    db.refresh(contrat)
    assert contrat.statut == "contentieux"

    cloture = JuridiqueService.cloturer_contentieux(db, c.id, "transaction", montant_obtenu=800000)
    assert cloture.statut == "transaction"
    assert cloture.date_cloture == date.today()
    assert float(cloture.montant_obtenu) == 800000


def test_resiliation_contrat(db, societe):
    contrat = _contrat(db, societe)
    r = JuridiqueService.resilier_contrat(db, contrat.id, "fin de bail anticipee")
    assert r.statut == "resilie"
    assert "fin de bail" in (r.notes or "")
    with pytest.raises(ValueError):
        JuridiqueService.resilier_contrat(db, contrat.id, "deuxieme tentative")
