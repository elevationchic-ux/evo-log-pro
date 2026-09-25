"""Tests des redevances portuaires PAD/PAK - moteur HONNETE piloté par données réelles.

Regression verrouillée : l'ancien calculate_port_dues_cemac ignorait escale_id et
recodait en dur 9 taux "officiels" + des quantites inventees (45 TC20, 62 TC40,
3 jours), delivrant la MEMME facture fantaisiste pour toute escale, puis le
routeur estampillait GENEREE_VALIDEE. Desormais les quantites viennent de
l'escale relle et les prix de TarifPortuaire ; tarif absent -> 501 (jamais d'un
taux invente) ; rien n'est certifie.
"""
from datetime import date, datetime

import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.acconage import Conteneur, Connaissement, Escale
from app.models.port_cameroun import TarifPortuaire
from app.services.acconage_service import PortAdvancedTOSService

# Codes attendus par le moteur et prix de reference (taux_tva=0 pour un total net).
TARIFS = {
    "TPC-CHENAL": 425000,
    "TPC-PILOTAGE": 140000,
    "TPC-REMORQUAGE": 325000,
    "TPC-STATIONNEMENT": 185000,
    "TPC-DROITQUAI20": 28000,
    "TPC-DROITQUAI40": 45000,
    "TPC-THC20": 85000,
    "TPC-THC40": 135000,
    "TPC-ISPS": 125000,
}


def _seed_tarifs(db: Session, codes=None):
    codes = codes if codes is not None else list(TARIFS)
    for code in codes:
        db.add(TarifPortuaire(
            code_tarif=code, designation=code, categorie="Manutention",
            unite="X", prix_unitaire=TARIFS[code], taux_tva=0,
            date_application=date(2026, 1, 1), est_actif=True,
        ))
    db.commit()


def _seed_escale(db: Session, avec_conteneurs=True, avec_depart=True, numero="ESC-T1"):
    escale = Escale(
        numero_escale=numero, statut="arrivee",
        date_arrivee_reelle=datetime(2026, 1, 1),
        date_depart_reelle=datetime(2026, 1, 3) if avec_depart else None,
    )
    db.add(escale)
    db.flush()
    if avec_conteneurs:
        for i, (taille, bl) in enumerate(
            [("20'Dry", "BL-A"), ("20'Dry", "BL-B"), ("40'HC", "BL-C")], start=1
        ):
            cont = Conteneur(numero=f"MSKU{i:07d}", type_conteneur=taille)
            db.add(cont)
            db.flush()
            db.add(Connaissement(numero_bl=bl, conteneur_id=cont.id, escale_id=escale.id))
    db.commit()
    return escale


def _ligne(dossier, code):
    for l in dossier["lignes"]:
        if l["code_tarif"] == code:
            return l
    return None


# --------------------------------------------------------------------------- #
def test_escale_inconnue_404(db: Session):
    with pytest.raises(HTTPException) as exc:
        PortAdvancedTOSService.calculate_port_dues_cemac(db, 9999)
    assert exc.value.status_code == 404


def test_tarifs_non_importes_501_sans_inventer(db: Session):
    _seed_escale(db)
    # Aucun TarifPortuaire en base -> 501 nommant les codes attendus, jamais de taux forge.
    with pytest.raises(HTTPException) as exc:
        PortAdvancedTOSService.calculate_port_dues_cemac(db, 1)
    assert exc.value.status_code == 501
    assert "TPC-CHENAL" in exc.value.detail


def test_total_calcule_depuis_donnees_reelles(db: Session):
    _seed_tarifs(db)
    escale = _seed_escale(db)
    d = PortAdvancedTOSService.calculate_port_dues_cemac(db, escale.id)

    # Quantites REELLES : 2 TC20 + 1 TC40 (et non les 45/62 inventes).
    assert _ligne(d, "TPC-DROITQUAI20")["quantite"] == 2
    assert _ligne(d, "TPC-DROITQUAI40")["quantite"] == 1
    assert _ligne(d, "TPC-THC20")["quantite"] == 2
    # Duree reelle = 1er..3 janv = 3 jours (et non le forfait "3" codé en dur par hasard).
    assert _ligne(d, "TPC-STATIONNEMENT")["quantite"] == 3

    # Total net verifie a la main (taux_tva=0) :
    # 425000 + 2*140000 + 2*325000 + 3*185000 + 2*28000 + 1*45000 + 2*85000 + 1*135000 + 125000
    attendu = (425000 + 280000 + 650000 + 555000 + 56000 + 45000 + 170000 + 135000 + 125000)
    assert d["total_ht_xaf"] == pytest.approx(attendu)
    assert d["total_ttc_xaf"] == pytest.approx(attendu)
    # Rien n'est certifie.
    assert d["statut_facturation"] == "BROUILLON_ESTIMATION_NON_CERTIFIE"
    assert d["statut_facturation"] != "GENEREE_VALIDEE"


def test_aucun_conteneur_quantites_zero_pas_inventees(db: Session):
    _seed_tarifs(db)
    escale = _seed_escale(db, avec_conteneurs=False)
    d = PortAdvancedTOSService.calculate_port_dues_cemac(db, escale.id)
    assert _ligne(d, "TPC-DROITQUAI20")["quantite"] == 0
    assert _ligne(d, "TPC-DROITQUAI40")["quantite"] == 0
    # Avertissement honnete, pas un bourrage a 45/62.
    assert any("connaissement" in a.lower() for a in d["avertissements"])


def test_duree_inconnue_stationnement_exclu_pas_forge(db: Session):
    _seed_tarifs(db)
    escale = _seed_escale(db, avec_depart=False)
    d = PortAdvancedTOSService.calculate_port_dues_cemac(db, escale.id)
    assert _ligne(d, "TPC-STATIONNEMENT") is None  # exclu, quantity unknown
    assert any("stationnement" in a.lower() or "duree" in a.lower() for a in d["avertissements"])


def test_routeur_ne_certifie_plus(db: Session, client):
    _seed_tarifs(db)
    escale = _seed_escale(db)
    r = client.post(f"/api/v1/acconage/facturation-quai/{escale.id}/generer-facture", json={})
    assert r.status_code == 200, r.text
    assert "GENEREE_VALIDEE" not in r.text
    assert r.json()["statut_facturation"] == "BROUILLON_ESTIMATION_NON_CERTIFIE"

    missing = client.get("/api/v1/acconage/facturation-quai/424242")
    assert missing.status_code == 404
