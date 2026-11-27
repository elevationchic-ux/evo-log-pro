"""Tests rentabilite par mission."""
from datetime import date, datetime, timezone
from decimal import Decimal
import pytest

from app.models.transport import Mission, MissionStatus
from app.models.transport_deep import FreightBill, FreightBill_statut
from app.models.frais_mission import FraisMission
from app.services.rentabilite_mission_service import RentabiliteMissionService


def _mission(db, reference, cout_reel=None, statut=MissionStatus.TERMINEE):
    m = Mission(company_id=1, reference=reference, camion_id=None,
                conducteur_id=None, client_id=1, type_mission="livraison",
                statut=statut, cout_reel=Decimal(str(cout_reel)) if cout_reel else None,
                date_debut_prevue=datetime.now(timezone.utc))
    db.add(m)
    db.commit()
    db.refresh(m)
    return m


def _bill(db, numero, mission_id, ttc, statut=FreightBill_statut.EMISE):
    b = FreightBill(company_id=1, numero_facture=numero, client_id=1,
                    mission_id=mission_id, montant_ht_xaf=Decimal("0"),
                    tva_xaf=Decimal("0"), total_ttc_xaf=Decimal(str(ttc)),
                    statut=statut, is_active=True)
    db.add(b)
    db.commit()
    db.refresh(b)
    return b


def _frais(db, mission_id, montant, statut="VALIDE"):
    f = FraisMission(mission_id=mission_id, type_frais="CARBURANT",
                     montant=montant, statut=statut)
    db.add(f)
    db.commit()
    db.refresh(f)
    return f


def test_rentabilite_par_mission(db):
    """Mission 1 : recette 2 factures 100k+50k, cout_reel 80k, frais 20k."""
    m1 = _mission(db, "M-1", cout_reel=80_000)
    _bill(db, "FB-1", m1.id, 100_000)
    _bill(db, "FB-2", m1.id, 50_000)
    _bill(db, "FB-3", m1.id, 999_999, statut=FreightBill_statut.BROUILLON)  # exclue
    _frais(db, m1.id, 20_000)
    _frais(db, m1.id, 5_000, statut="REJETE")  # exclue

    m2 = _mission(db, "M-2")  # sans donnees -> honnete

    r = RentabiliteMissionService.par_mission(db, mission_id=m1.id)
    assert r["missions_total"] == 1
    d = r["details"][0]
    assert d["recette_xaf"] == 150_000
    assert d["nb_factures"] == 2
    assert d["cout_total_xaf"] == 100_000  # 80k + 20k frais valides
    assert d["marge_xaf"] == 50_000
    assert d["marge_pct"] == 33.3

    r2 = RentabiliteMissionService.par_mission(db, mission_id=m2.id)
    d2 = r2["details"][0]
    assert d2["recette_xaf"] == 0.0
    assert d2["cout_total_xaf"] is None
    assert d2["marge_xaf"] is None


def test_vide_honnete(db):
    r = RentabiliteMissionService.par_mission(db)
    assert r["missions"] == 0
