"""Tests du generateur PDF et du montant en lettres (mention DGI obligatoire).

Cas regression : 71 ("soixante et onze"), 1000 ("mille" sans "un"),
80 ("quatre-vingts"), 91 ("quatre-vingt-onze").
"""
import pytest
from fastapi import HTTPException

from app.utils.pdf_generator import (
    TEMPLATE_DIR,
    generer_pdf,
    montant_en_lettres,
    nombre_en_lettres,
)


@pytest.mark.parametrize(
    "nombre, attendu",
    [
        (0, "zéro"),
        (1, "un"),
        (17, "dix-sept"),
        (21, "vingt-et-un"),
        (70, "soixante-dix"),
        (71, "soixante et onze"),
        (80, "quatre-vingts"),
        (81, "quatre-vingt-un"),
        (90, "quatre-vingt-dix"),
        (91, "quatre-vingt-onze"),
        (100, "cent"),
        (196, "cent quatre-vingt-seize"),
        (480, "quatre cent quatre-vingts"),
        (1000, "mille"),
        (1001, "mille un"),
        (71234, "soixante et onze mille deux cent trente-quatre"),
        (1000000, "un million"),
        (2000000, "deux millions"),
    ],
)
def test_nombre_en_lettres(nombre, attendu):
    assert nombre_en_lettres(nombre) == attendu


def test_montant_en_lettres_xaf():
    texte = montant_en_lettres(894375, "XAF")
    assert texte == (
        "huit cent quatre-vingt-quatorze mille trois cent soixante-quinze francs CFA"
    )


def test_montant_en_lettres_avec_centimes():
    assert montant_en_lettres(119.5, "XAF").endswith("cent dix-neuf francs CFA et cinquante centimes")


def _contexte_facture():
    class Facture:
        numero_facture = "FAC-2026-001"
        type_facture = "vente"
        date_emission = "2026-09-25"
        date_echeance = "2026-10-25"
        date_paiement = None
        montant_ht = 750000
        taux_tva = 19.25
        montant_tva = 144375
        montant_ttc = 894375
        devise = "XAF"
        statut = "emise"
        conditions_paiement = "30 jours net"
        notes = None
        reglement_partiel = 0
        solde_restant = 894375

    class Ligne:
        designation = "Manutention conteneur 40 pieds"
        description = None
        quantite = 12
        unite = "UI"
        prix_unitaire_ht = 62500
        montant_ht = 750000
        taux_tva = 19.25
        montant_ttc = 894375

    return {
        "facture": Facture(),
        "client": None,
        "company": None,
        "lignes": [Ligne()],
        "taux_tva": 19.25,
        "montant_en_lettres": montant_en_lettres(894375, "XAF"),
    }


def test_template_facture_present():
    assert (TEMPLATE_DIR / "facture.html.j2").exists()
    # Le fichier a ete corrompu (octets NUL) : on verifie qu'il est sain.
    contenu = (TEMPLATE_DIR / "facture.html.j2").read_bytes()
    assert b"\x00" not in contenu


def test_generer_pdf_honnete_quand_weasyprint_absent():
    """Sans WeasyPrint (dev Windows), 501 explicite  jamais un faux PDF."""
    weasyprint_present = True
    try:
        import weasyprint  # noqa: F401
    except Exception:
        weasyprint_present = False

    if weasyprint_present:
        pdf = generer_pdf("facture.html.j2", _contexte_facture())
        assert pdf[:5] == b"%PDF-"
    else:
        with pytest.raises(HTTPException) as exc:
            generer_pdf("facture.html.j2", _contexte_facture())
        assert exc.value.status_code == 501


def test_generer_pdf_template_inconnu_501():
    with pytest.raises(HTTPException) as exc:
        generer_pdf("module_inexistant.html.j2", {})
    assert exc.value.status_code == 501


# ─── Endpoint GET /finance/factures/{id}/pdf ────────────────────────────────

from datetime import date  # noqa: E402


def _facture_en_base(db):
    from app.models.finance_ohada import FactureNew, LigneFactureOHADA

    f = FactureNew(
        numero_facture="FAC-TEST-001",
        type_facture="vente",
        date_emission=date(2026, 9, 25),
        montant_ht=750000,
        taux_tva=19.25,
        montant_tva=144375,
        montant_ttc=894375,
        statut="emise",
    )
    db.add(f)
    db.flush()
    db.add(LigneFactureOHADA(
        facture_id=f.id, designation="Manutention conteneur 40 pieds",
        quantite=12, unite="UI", prix_unitaire_ht=62500,
        montant_ht=750000, taux_tva=19.25, montant_ttc=894375,
    ))
    db.commit()
    return f


def _brancher_auth(client):
    """Bypass d'authentification : l'endpoint exige un utilisateur, on lui
    donne un faux sans company_id (le template gere une company absente)."""
    from app.core.security import get_current_user
    from app.main import app

    class FakeUser:
        id = 1
        username = "test"
        company_id = None

    app.dependency_overrides[get_current_user] = lambda: FakeUser()


def test_endpoint_facture_pdf(client, db):
    _brancher_auth(client)
    try:
        assert client.get("/api/v1/finance/factures/999999/pdf").status_code == 404

        f = _facture_en_base(db)
        resp = client.get(f"/api/v1/finance/factures/{f.id}/pdf")
        try:
            import weasyprint  # noqa: F401
            pdf_disponible = True
        except Exception:
            pdf_disponible = False

        if pdf_disponible:
            assert resp.status_code == 200
            assert resp.headers["content-type"] == "application/pdf"
            assert resp.content[:5] == b"%PDF-"
            assert "facture-FAC-TEST-001" in resp.headers.get("content-disposition", "")
        else:
            # Environnement sans Pango/Cairo : 501 explicite, jamais un faux PDF.
            assert resp.status_code == 501
            assert "PDF" in resp.json()["detail"]
    finally:
        from app.main import app
        app.dependency_overrides.clear()


def test_endpoint_facture_pdf_exige_auth(client):
    # Sans utilisateur authentifie, la facture n'est pas telechargeable.
    resp = client.get("/api/v1/finance/factures/1/pdf")
    assert resp.status_code in (401, 403)
