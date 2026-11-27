"""Tests commercial : pipeline et devis expires."""
from datetime import date, timedelta
import pytest
from decimal import Decimal

from app.models.commercial_d_deep import CommOpportunity, CommQuote
from app.services.commercial_service import CommercialService


def _opp(db, statut, montant, reference):
    o = CommOpportunity(company_id=1, reference=reference, client="CLI-1",
                        libelle="Opp", montant_estime=Decimal(str(montant)),
                        statut=statut, is_active=True)
    db.add(o)
    db.commit()
    db.refresh(o)
    return o


def _devis(db, validite, statut="envoye", montant=100000, reference="Q-1"):
    q = CommQuote(company_id=1, reference=reference, client="CLI-1",
                  montant=Decimal(str(montant)), validite=validite,
                  statut=statut, is_active=True)
    db.add(q)
    db.commit()
    db.refresh(q)
    return q


def test_pipeline_par_statut(db):
    """2 en cours (10M+5M), 1 gagne (3M) -> pipeline 18M."""
    _opp(db, "en_cours", 10_000_000, "O1")
    _opp(db, "en_cours", 5_000_000, "O2")
    _opp(db, "gagne", 3_000_000, "O3")
    r = CommercialService.pipeline(db)
    assert r["opportunites_total"] == 3
    assert r["par_statut"]["en_cours"]["montant_total"] == 15_000_000
    assert r["montant_pipeline"] == 18_000_000


def test_devis_expires(db):
    """1 expire ouvert, 1 expire accepte (exclu), 1 valide."""
    _devis(db, date.today() - timedelta(days=10), "envoye", 100000, "Q-EXP")
    _devis(db, date.today() - timedelta(days=10), "accepte", 50000, "Q-ACC")
    _devis(db, date.today() + timedelta(days=10), "envoye", 80000, "Q-OK")
    r = CommercialService.devis_expires(db)
    assert r["expires"] == 1
    assert r["details"][0]["reference"] == "Q-EXP"


def test_vide_honnete(db):
    r = CommercialService.pipeline(db)
    assert r["opportunites"] == 0
