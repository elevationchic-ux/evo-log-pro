"""Tests RH (solde de conge, absenteisme) et cloture d'exercice."""
from datetime import date, timedelta

from app.models.user import User
from app.models.rh import Conge, Absence, TypeConge, StatutConge
from app.models.finance_ohada import ExerciceComptable
from app.services.rh_service import CongeService, AbsenceService
from app.services.finance_service import ExerciceComptableService


def _employe(db):
    u = User(username="rh1", email="rh1@test.cm", hashed_password="x", is_active=True)
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


def test_solde_conge_droit_acquis_moins_conges_pris(db):
    """Droit annuel (24 j max) moins les conges annuels approuves."""
    emp = _employe(db)
    annee = date.today().year
    db.add(Conge(employe_id=emp.id, type_conge=TypeConge.CONGE_ANNUEL,
                 nombre_jours=5, date_debut=date(annee, 3, 1),
                 date_fin=date(annee, 3, 5), statut=StatutConge.APPROUVE))
    db.commit()

    solde = CongeService.calculer_solde_conge(db, emp.id, annee)

    assert solde["utilise"] == 5.0
    assert solde["reste"] == round(solde["solde"] - 5.0, 1)
    assert solde["annee"] == annee


def test_taux_absenteisme_sur_jours_ouvrables(db):
    """2 jours d'absence / 22 jours ouvres = 9.09 %."""
    emp = _employe(db)
    mois, annee = date.today().month, date.today().year
    db.add(Absence(employe_id=emp.id, type_absence="maladie", nombre_jours=2,
                   date_debut=date(annee, mois, 1),
                   date_fin=date(annee, mois, 2)))
    db.commit()

    taux = AbsenceService.calculer_taux_absenteisme(db, emp.id, mois, annee)
    assert abs(taux - (2 / 22 * 100)) < 0.01


def test_cloturer_exercice_change_statut(db):
    ex = ExerciceComptable(
        numero_exercice="EX-T1", annee=2020,
        date_debut=date(2020, 1, 1), date_fin=date(2020, 12, 31),
        statut="ouvert")
    db.add(ex)
    db.commit()
    db.refresh(ex)

    cloture = ExerciceComptableService.cloturer_exercice(db, ex.id, "DAF")

    assert cloture.statut == "cloture"
    assert cloture.cloture_par == "DAF"
    assert cloture.date_cloture is not None
