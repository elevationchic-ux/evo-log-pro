"""Tests transit CEMAC : frais de corridor selon unites reelles."""
from datetime import date
import pytest
from decimal import Decimal
from fastapi import HTTPException

from app.models.transit_cemac import CorridorCEMACTransit, FraisCorridor
from app.services.transit_cemac_service import CorridorFraisService


def _corridor(db, code="COR-DLA-BZV"):
    c = CorridorCEMACTransit(code=code, nom=f"Corridor {code}",
                             origine="Douala", destination="Bangui",
                             distance_km=1500, duree_estimee_heures=48,
                             pays_origine="Cameroun", pays_destination="Centrafrique",
                             est_actif=True)
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


def _frais(db, corridor_id, type_frais, montant, unite, designation):
    f = FraisCorridor(corridor_id=corridor_id,
                      type_frais=type_frais, designation=designation,
                      montant=Decimal(str(montant)), unite=unite,
                      date_application=date.today(), est_actif=True)
    db.add(f)
    db.commit()
    return f


def test_frais_par_vehicule_et_passage(db):
    """Peesage 50 000/vehicule + redevance 30 000/passage, 2 vehicules
    = 100 000 + 60 000 = 160 000."""
    c = _corridor(db)
    _frais(db, c.id, "PEAGE", 50000, "PAR_VEHICULE", "Peage autoroutier")
    _frais(db, c.id, "REDEVANCE", 30000, "PAR_PASSAGE", "Redevance corridor")

    r = CorridorFraisService.calculer_frais(db, c.id, nb_vehicules=2)
    assert r["total_xaf"] == 160_000
    assert len(r["lignes"]) == 2


def test_frais_par_tonne(db):
    c = _corridor(db, code="COR-BZV-PNK")
    _frais(db, c.id, "REDEVANCE", 500, "PAR_TONNE", "Redevance tonne")

    r = CorridorFraisService.calculer_frais(db, c.id, nb_vehicules=1, tonnes=40)
    assert r["total_xaf"] == 20_000


def test_corridor_sans_frais_refuse(db):
    """Corridor sans frais actif -> 422 honnete, jamais de tarif invente."""
    c = _corridor(db, code="COR-VIDE")
    with pytest.raises(HTTPException) as exc:
        CorridorFraisService.calculer_frais(db, c.id)
    assert exc.value.status_code == 422


def test_corridor_inconnu_404(db):
    with pytest.raises(HTTPException):
        CorridorFraisService.calculer_frais(db, 999999)
