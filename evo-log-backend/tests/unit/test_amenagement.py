"""Tests amenagement portuaire : releves d'avancement et budget."""
import pytest
from fastapi import HTTPException
from decimal import Decimal

from app.models.amenagement_portuaire import ProjetAmenagement, TypeProjet, StatutProjet
from app.services.amenagement_portuaire_service import AmenagementAvancementService


def _projet(db, code, cout_prev=100_000_000, cout_reel=None):
    p = ProjetAmenagement(
        code_projet=code, libelle=f"Projet {code}",
        type_ouvrage=TypeProjet.QUAI, statut=StatutProjet.EN_CONSTRUCTION,
        cout_previsionnel_xaf=Decimal(str(cout_prev)),
        cout_reel_xaf=Decimal(str(cout_reel)) if cout_reel is not None else None)
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


def test_releve_met_a_jour_avancement_physique(db):
    p = _projet(db, "PRJ-1")
    r = AmenagementAvancementService.enregistrer_releve(
        db, projet_id=p.id, avancement_pct=45.5, lot="Gros oeuvre",
        observateur="Conducteur travaux")

    assert r["avancement_physique_pct"] == 45.5
    assert p.avancement_physique_pct == Decimal("45.50")
    # cout_reel non renseigne -> avancement financier reste None
    assert r["avancement_financier_pct"] is None
    assert r["depassement_budget"] is False


def test_avancement_financier_depuis_couts_reels(db):
    """cout_reel 60M / previsionnel 100M = 60 % financier."""
    p = _projet(db, "PRJ-2", cout_reel=60_000_000)
    r = AmenagementAvancementService.enregistrer_releve(
        db, projet_id=p.id, avancement_pct=55)
    assert r["avancement_financier_pct"] == 60.0


def test_depassement_budget_detecte(db):
    """cout_reel > previsionnel : alerte honnete."""
    p = _projet(db, "PRJ-3", cout_reel=120_000_000)
    r = AmenagementAvancementService.enregistrer_releve(
        db, projet_id=p.id, avancement_pct=90)
    assert r["depassement_budget"] is True
    assert r["ecart_budget_xaf"] == 20_000_000


def test_avancement_hors_bornes_refuse(db):
    p = _projet(db, "PRJ-4")
    with pytest.raises(HTTPException):
        AmenagementAvancementService.enregistrer_releve(
            db, projet_id=p.id, avancement_pct=150)


def test_projet_inconnu_404(db):
    with pytest.raises(HTTPException):
        AmenagementAvancementService.enregistrer_releve(
            db, projet_id=999999, avancement_pct=10)
