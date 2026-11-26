"""Tests transport international : statistiques reelles et rapport OT."""
import pytest

from app.models.transport_international import OrdreTransport, StatutTransport
from app.services.transport_international_service import TransportInternationalService


def test_statistiques_vide_honnete(db):
    """Base vide : tous les compteurs a zero, aucun chiffre invente."""
    s = TransportInternationalService.statistiques(db)
    assert s["ordres_transport"]["total"] == 0
    assert s["ordres_transport"]["tonnage_net"] == 0.0
    assert s["carnets_tir"] == 0


def test_statistiques_compte_et_pese_reel(db):
    """2 OT dont un livre : total=2, tonnage = somme des poids nets."""
    db.add(OrdreTransport(numero_ot="OT-T1", statut=StatutTransport.EN_TRANSIT,
                          poids_net=12000, lieu_livraison="Bangui"))
    db.add(OrdreTransport(numero_ot="OT-T2", statut=StatutTransport.LIVRE,
                          poids_net=8000, lieu_livraison="Brazzaville"))
    db.commit()

    s = TransportInternationalService.statistiques(db)

    assert s["ordres_transport"]["total"] == 2
    assert s["ordres_transport"]["tonnage_net"] == 20000.0
    assert s["ordres_transport"]["par_statut"].get("en_transit") == 1
    assert s["ordres_transport"]["par_statut"].get("livre") == 1


def test_rapport_transport_inconnu_refuse(db):
    with pytest.raises(ValueError):
        TransportInternationalService.rapport_transport(db, ot_id=999999)


def test_rapport_transport_agrege_le_suivi(db):
    ot = OrdreTransport(numero_ot="OT-T3", statut=StatutTransport.EN_TRANSIT,
                        lieu_livraison="Douala", pays_destination="CM")
    db.add(ot)
    db.commit()
    db.refresh(ot)

    r = TransportInternationalService.rapport_transport(db, ot.id)

    assert r["ordre_transport"]["numero"] == "OT-T3"
    assert r["ordre_transport"]["statut"] == "en_transit"
    assert r["suivi"]["positions"] == 0
