"""Tests frais mission : validation et reconciliation."""
import pytest
from fastapi import HTTPException

from app.models.frais_mission import FraisMission, AvanceMission
from app.services.frais_mission_service import FraisMissionService


def _dep(db, user=1, montant=50000, statut="SOUMIS", reference="F-1"):
    d = FraisMission(user_id=user, nom_collaborateur="Jean",
                     type_frais="REPAS", montant=montant, statut=statut,
                     mission_id=10)
    db.add(d)
    db.commit()
    db.refresh(d)
    return d


def _avance(db, user=1, accorde=200000, demande=200000, reference="A-1"):
    a = AvanceMission(user_id=user, titre_mission="Mission Douala",
                      montant_demande=demande, montant_accorde=accorde,
                      statut="ACCORDEE")
    db.add(a)
    db.commit()
    db.refresh(a)
    return a


def test_validation_approuvee(db):
    d = _dep(db)
    r = FraisMissionService.valider_depense(db, d.id, approuve=True)
    assert r["statut"] == "VALIDE"


def test_rejet_sans_motif_refuse(db):
    d = _dep(db, reference="F-2")
    with pytest.raises(HTTPException) as exc:
        FraisMissionService.valider_depense(db, d.id, approuve=False)
    assert exc.value.status_code == 422


def test_rejet_avec_motif(db):
    d = _dep(db, reference="F-3")
    r = FraisMissionService.valider_depense(
        db, d.id, approuve=False, motif_rejet="Recu illisible")
    assert r["statut"] == "REJETE"


def test_reconciliation_avance(db):
    """Avance 200k, depenses validees 120k -> ecart 80k."""
    a = _avance(db)
    _dep(db, montant=70000, statut="VALIDE", reference="F-4")
    _dep(db, montant=50000, statut="VALIDE", reference="F-5")
    r = FraisMissionService.reconciliation_avance(db, a.id)
    assert r["depenses_validees_xaf"] == 120000
    assert r["ecart_xaf"] == 80000


def test_depense_deja_traitee_409(db):
    d = _dep(db, statut="VALIDE", reference="F-6")
    with pytest.raises(HTTPException) as exc:
        FraisMissionService.valider_depense(db, d.id, approuve=True)
    assert exc.value.status_code == 409
