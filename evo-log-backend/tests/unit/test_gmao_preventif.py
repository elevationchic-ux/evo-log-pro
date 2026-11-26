"""Tests GMAO avance : generation d'OT preventifs par seuils reels."""
from datetime import datetime, timezone

from app.models.parc import Vehicule, Maintenance
from app.services.maintenance_gmao_avance_service import MaintenancePreventiveService


def _vehicule(db, immat, km):
    v = Vehicule(immatriculation=immat, kilometrage=km, is_active=True,
                 marque="Test", modele="T1")
    db.add(v)
    db.commit()
    db.refresh(v)
    return v


def test_ot_genere_quand_aucun_preventif(db):
    """Vehicule sans historique preventif -> OT planifie, motif honnete."""
    v = _vehicule(db, "OT-TEST-1", 5000)

    res = MaintenancePreventiveService.generer_ordres_preventifs(db, [v.id])

    assert res["ordres_generes"] == 1
    assert "aucun entretien preventif" in res["ordres"][0]["motif"]
    ordre = db.query(Maintenance).filter(Maintenance.vehicule_id == v.id).one()
    assert ordre.statut == "planifie"


def test_vehicule_sous_seuil_ignore(db):
    """Dernier preventif recent et km sous seuil -> ignore, rien de cree."""
    v = _vehicule(db, "OT-TEST-2", 2000)
    db.add(Maintenance(
        vehicule_id=v.id, type_maintenance="preventive",
        date_debut=datetime.now(timezone.utc), kilometrage=1900,
        description="Vidange", statut="termine"))
    db.commit()

    res = MaintenancePreventiveService.generer_ordres_preventifs(db, [v.id])

    assert res["ordres_generes"] == 0
    assert len(res["vehicules_ignores"]) == 1
    assert "sous les seuils" in res["vehicules_ignores"][0]["motif"]


def test_vehicule_inconnu_ignore(db):
    res = MaintenancePreventiveService.generer_ordres_preventifs(db, [999999])
    assert res["ordres_generes"] == 0
    assert "introuvable" in res["vehicules_ignores"][0]["motif"]
