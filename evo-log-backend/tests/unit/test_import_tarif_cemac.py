"""Tests du pipeline d'import du tarif CEMAC officiel (P1 #1, approche honnete).

Le principe verrouille ici : l'import ne INVENTE AUCUN taux. Il ne fait que
charger des donnees officielles, rejette toute ligne douteuse, et trace sa
provenance. Une fois le tarif reel importe, le moteur de liquidation consomme
des taux reels (simulation=False) au lieu du defaut 20%.
"""
import pytest
from sqlalchemy.orm import Session

from scripts.import_tarif_cemac import (
    importer,
    valider_et_normaliser,
)
from app.services.taxation_douaniere import calculer_liquidation


# --------------------------------------------------------------------------- #
# 1. Validation stricte : aucune donnee inventee, aucune completion silenciee
# --------------------------------------------------------------------------- #
def test_rejet_taux_manquant_sans_inventer():
    lignes = [{"code_hs": "85176290", "description": "Tel", "taux_tva": "19.25"}]
    entries, erreurs = valider_et_normaliser(lignes)
    assert entries == []
    assert any("taux_dd" in e for e in erreurs)


def test_rejet_code_sh_invalide():
    lignes = [{"code_hs": "85AB", "description": "X", "taux_dd": "20", "taux_tva": "19.25"}]
    entries, _ = valider_et_normaliser(lignes)
    assert entries == []


def test_rejet_taux_hors_borne():
    lignes = [{"code_hs": "85176290", "description": "X", "taux_dd": "250", "taux_tva": "19.25"}]
    entries, erreurs = valider_et_normaliser(lignes)
    assert entries == []
    assert any("hors [0..100]" in e for e in erreurs)


def test_ligne_valide_derive_chapitre_position():
    lignes = [{"code_hs": "85176290", "description": "Appareils telephoniques",
               "taux_dd": "20", "taux_tva": "19.25"}]
    entries, erreurs = valider_et_normaliser(lignes)
    assert erreurs == []
    assert len(entries) == 1
    e = entries[0]
    assert e["chapitre"] == "85" and e["position"] == "8517"   # derives du SH
    assert e["statut"] == "actif"
    assert e["section"] is None                                 # jamais devinee


# --------------------------------------------------------------------------- #
# 2. Import -> le moteur consomme un taux REEL (fin de la simulation)
# --------------------------------------------------------------------------- #
def test_import_alimente_le_moteur(db: Session):
    lignes = [{"code_hs": "84713000", "description": "Ordinateurs portables",
               "taux_dd": "5", "taux_tva": "19.25"}]
    entries, _ = valider_et_normaliser(lignes)
    ins, up = importer(db, entries, source_globale="Arrete CEMAC test", lot="t", dry_run=False)
    assert (ins, up) == (1, 0)

    r = calculer_liquidation(valeur_en_douane=10_000_000, db=db, code_sh="84713000")
    assert r["source_taux"] == "nomenclature_cemac"
    assert r["simulation"] is False
    assert r["taux_dd"] == pytest.approx(0.05)
    assert r["droit_douane_dd"] == pytest.approx(500_000.0)
    assert r["total_a_liquider_xaf"] == pytest.approx(2_919_162.5)


def test_import_dry_run_necrit_rien(db: Session):
    from app.models.transit_avance import NomenclatureCEMAC

    lignes = [{"code_hs": "84713000", "description": "X", "taux_dd": "5", "taux_tva": "19.25"}]
    entries, _ = valider_et_normaliser(lignes)
    importer(db, entries, source_globale="test", lot="t", dry_run=True)
    db.rollback()
    assert db.query(NomenclatureCEMAC).count() == 0


def test_import_upsert_et_provenance(db: Session):
    from app.models.transit_avance import NomenclatureCEMAC

    lignes1 = [{"code_hs": "84715000", "description": "Serveurs", "taux_dd": "10",
                "taux_tva": "19.25"}]
    e1, _ = valider_et_normaliser(lignes1)
    importer(db, e1, source_globale="Arrete 2025", lot="l1", dry_run=False)

    # Re-import avec taux corrige -> mise a jour, pas de doublon.
    lignes2 = [{"code_hs": "84715000", "description": "Serveurs", "taux_dd": "0",
                "taux_tva": "19.25"}]
    e2, _ = valider_et_normaliser(lignes2)
    ins, up = importer(db, e2, source_globale="Arrete 2026", lot="l2", dry_run=False)
    assert (ins, up) == (0, 1)

    entry = db.query(NomenclatureCEMAC).filter_by(code_hs="84715000").one()
    assert float(entry.taux_dd) == 0.0
    assert entry.source_reference == "Arrete 2026 [l2]"


# --------------------------------------------------------------------------- #
# 3. Surface admin : la correction de taux exige une provenance
# --------------------------------------------------------------------------- #
def _brancher_auth():
    from app.core.security import get_current_user
    from app.main import app

    class _U:
        id = 1
        username = "douanier"
        company_id = None

    app.dependency_overrides[get_current_user] = lambda: _U()
    return app


def test_put_taux_refuse_sans_provenance(client, db):
    from app.models.transit_avance import NomenclatureCEMAC

    db.add(NomenclatureCEMAC(code_hs="85176200", description="Tel", section="XVI",
                             chapitre="85", position="8517", taux_dd=20, taux_tva=19.25,
                             statut="actif"))
    db.commit()
    app = _brancher_auth()
    try:
        r = client.put("/api/v1/transit-avance/nomenclature-cemac/85176200",
                       json={"taux_dd": 5})
        assert r.status_code == 400   # pas de source_reference -> refus
    finally:
        app.dependency_overrides.clear()


def test_put_taux_avec_provenance_et_liste(client, db):
    from app.models.transit_avance import NomenclatureCEMAC

    db.add(NomenclatureCEMAC(code_hs="85176210", description="Tel", section="XVI",
                             chapitre="85", position="8517", taux_dd=20, taux_tva=19.25,
                             statut="actif"))
    db.commit()
    app = _brancher_auth()
    try:
        r = client.put("/api/v1/transit-avance/nomenclature-cemac/85176210",
                       json={"taux_dd": 5, "source_reference": "Arrete CEMAC 2026 (DGD)"})
        assert r.status_code == 200, r.text
        assert float(r.json()["taux_dd"]) == 5.0
        assert "Arrete CEMAC" in r.json()["source_reference"]

        lst = client.get("/api/v1/transit-avance/nomenclature-cemac", params={"search": "8517"})
        assert lst.status_code == 200, lst.text
        assert any(x["code_hs"] == "85176210" for x in lst.json())
    finally:
        app.dependency_overrides.clear()
