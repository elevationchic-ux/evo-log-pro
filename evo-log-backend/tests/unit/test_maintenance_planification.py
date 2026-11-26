"""Tests du moteur de planification preventive GMAO.

Couvre les trois declencheurs reels : compteur technique (heures moteur),
echeance calendaire, et calendrier de lubrification — plus l'idempotence
quotidienne et la non-generation sans releve exploitable."""
from datetime import date, datetime, timedelta

import pytest

from app.models.maintenance_deep import (
    ConditionReading, LubricationSchedule, MaintenancePlan,
    TechnicalAsset, WorkOrder,)
from app.models.tenant import Company
from app.services.maintenance_planification_service import MaintenancePlanificationService


@pytest.fixture
def gmao(db):
    company = Company(code="GMAO-TEST", nom="GMAO Test SA", is_active=True, modules_actives="[]")
    db.add(company)
    db.flush()
    asset = TechnicalAsset(
        company_id=company.id, tag_actif="MOTEUR-01", nom="Groupe electrogene",
        categorie="groupe", criticite="A", statut="actif", is_active=True)
    db.add(asset)
    db.flush()
    return {"company": company, "asset": asset}


def _plan(db, g, **kw):
    data = dict(
        company_id=g["company"].id, code_plan="PLAN-HUILE", nom="Vidange huile moteur",
        asset_id=g["asset"].id, type_plan="preventif",
        frequence_type="heures", frequence_valeur=500, frequence_unite="heures",
        statut="actif", is_active=True, duree_estimee_h=2.0)
    data.update(kw)
    plan = MaintenancePlan(**data)
    db.add(plan)
    db.commit()
    return plan


def _releve(db, g, valeur, quand=None):
    r = ConditionReading(
        company_id=g["company"].id, reference_lecture=f"REL-{valeur}",
        asset_id=g["asset"].id, type_technique="vibration",
        date_lecture=quand or datetime(2026, 1, 10),
        valeur_principale=valeur, unite="heures", is_active=True)
    db.add(r)
    db.commit()
    return r


def test_compteur_premier_releve_cale_la_baseline_sans_ot(db, gmao):
    plan = _plan(db, gmao)
    _releve(db, gmao, 1000)

    rapport = MaintenancePlanificationService.evaluer(db)

    assert rapport["ots_crees"] == []
    db.refresh(plan)
    assert plan.dernier_releve_compteur == 1000


def test_compteur_seuil_atteint_genere_ot_preventif(db, gmao):
    plan = _plan(db, gmao)
    _releve(db, gmao, 1000)
    MaintenancePlanificationService.evaluer(db)  # baseline = 1000

    _releve(db, gmao, 1600, quand=datetime(2026, 2, 10))
    rapport = MaintenancePlanificationService.evaluer(db)

    assert len(rapport["ots_crees"]) == 1
    ot = rapport["ots_crees"][0]
    assert ot["plan_id"] == plan.id
    assert ot["motif"].find("heures") >= 0
    enregistre = db.query(WorkOrder).filter(WorkOrder.id == ot["ot_id"]).one()
    assert enregistre.type_ot == "preventif"
    assert enregistre.statut == "planifie"
    assert enregistre.priorite == "P1"  # criticite A
    db.refresh(plan)
    assert plan.dernier_releve_compteur == 1600


def test_echeance_calendaire_depassee_genere_ot(db, gmao):
    hier = date.today() - timedelta(days=1)
    plan = _plan(db, gmao, frequence_type="calendaire", frequence_valeur=3,
                 frequence_unite="mois", prochaine_echeance=hier)

    rapport = MaintenancePlanificationService.evaluer(db)

    assert len(rapport["ots_crees"]) == 1
    db.refresh(plan)
    assert plan.prochaine_echeance > date.today()


def test_sans_releve_aucun_ot_compteur(db, gmao):
    _plan(db, gmao)
    rapport = MaintenancePlanificationService.evaluer(db)
    assert rapport["ots_crees"] == []
    assert any("releve" in i["motif"] for i in rapport["plans_ignores"])


def test_idempotence_meme_jour(db, gmao):
    plan = _plan(db, gmao, prochaine_echeance=date.today() - timedelta(days=1),
                 frequence_type="calendaire", frequence_unite="mois")
    r1 = MaintenancePlanificationService.evaluer(db)
    r2 = MaintenancePlanificationService.evaluer(db)
    assert len(r1["ots_crees"]) == 1
    assert len(r2["ots_crees"]) == 0


def test_lubrification_echeance_depassee_genere_ot_graissage(db, gmao):
    lub = LubricationSchedule(
        company_id=gmao["company"].id, asset_id=gmao["asset"].id,
        point_lubrifiant="vidange", type_lubrifiant="huile moteur",
        grade="SAE 15W-40", quantite_litre=15, frequence_jours=180,
        prochaine_date=date.today() - timedelta(days=10), statut="actif", is_active=True)
    db.add(lub)
    db.commit()

    rapport = MaintenancePlanificationService.evaluer(db)

    assert len(rapport["lubrifications_declenchees"]) == 1
    ot = db.query(WorkOrder).filter(WorkOrder.id == rapport["lubrifications_declenchees"][0]["ot_id"]).one()
    assert "Graissage" in ot.titre
    db.refresh(lub)
    assert lub.prochaine_date > date.today()


# --------------------------------------------------------------------------- #
# Pont GMAO -> immobilisations amortissables (comptabilite OHADA) #
# --------------------------------------------------------------------------- #
def test_immobilisation_creee_depuis_actif_gmao(db, gmao):
    from decimal import Decimal
    from app.models.maintenance_deep import TechnicalAsset
    from app.services.comptabilite_avance_service import ImmobilisationService

    actif = TechnicalAsset(
        company_id=gmao["company"].id, tag_actif="CHARIOT-07",
        nom="Chariot elevateur 3T", categorie="manutention",
        cout_acquisition_xaf=Decimal("15000000"), duree_vieutile_ans=8,
        date_mise_service=date(2026, 1, 10), criticite="A",
        statut="actif", is_active=True)
    db.add(actif)
    db.commit()

    imm = ImmobilisationService.creer_depuis_actif_gmao(
        db, actif.id, "215", "2815", "6815")

    assert imm.numero_immobilisation == "CHARIOT-07"
    assert imm.designation.startswith("Chariot elevateur 3T")
    assert float(imm.valeur_acquisition) == 15_000_000
    assert imm.duree_mois == 96          # 8 ans x 12
    assert imm.compte_immobilisation == "215"
    assert imm.company_id == gmao["company"].id


def test_immobilisation_refusee_sans_donnees_comptables(db, gmao):
    from app.models.maintenance_deep import TechnicalAsset
    from app.services.comptabilite_avance_service import ImmobilisationService

    actif = TechnicalAsset(
        company_id=gmao["company"].id, tag_actif="EQUIPE-VIDE",
        nom="Equipement sans valorisation", statut="actif", is_active=True)
    db.add(actif)
    db.commit()

    with pytest.raises(ValueError):
        ImmobilisationService.creer_depuis_actif_gmao(db, actif.id, "215", "2815")
