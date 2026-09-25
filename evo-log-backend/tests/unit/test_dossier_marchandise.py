"""Tests du dossier unique de marchandise (P2 #7, approche honnete / zero-mock).

Ce qui est verrouille ici :
  • les etapes reellement reliees (FK, numero physique, ou lien de la chaine
    documentaire 024 saisi explicitement) sont exposees ;
  • une etape aval sans lien saisi est signalee 'absent' avec un tableau vide :
    rien n'est jamais devine par client, date ou proximite ;
  • une 404 franche quand l'ancre physique n'existe pas (aucun dossier invente) ;
  • une 400 quand aucun identifiant physique n'est fourni.
"""
from sqlalchemy.orm import Session

from app.models.acconage import (
    Conteneur,
    Connaissement,
    Escale,
    Navire,
    OperationAcconage,
    PackingList,
)
from app.services.dossier_marchandise import consigner_dossier_marchandise


def _chaine_complet_db(db: Session):
    """Navire -> Escale -> Conteneur -> B/L -> PackingList -> Operation (liens reels)."""
    navire = Navire(nom="MSC Ayla", imo="9074729", armateur="MSC")
    db.add(navire)
    db.flush()
    escale = Escale(numero_escale="ESC-2026-001", navire_id=navire.id, statut="arrivee")
    db.add(escale)
    db.flush()
    conteneur = Conteneur(numero="MSKU7654321", type_conteneur="40' Dry",
                          statut="full", navire_id=navire.id)
    db.add(conteneur)
    db.flush()
    bl = Connaissement(numero_bl="MEDUPBL12345", conteneur_id=conteneur.id,
                       escale_id=escale.id, chargeur="Export SARL",
                       destinataire="Import Douala", statut="emis")
    db.add(bl)
    pl = PackingList(numero_pl="PL-0001", conteneur_id=conteneur.id,
                     connaissement_id=bl.id, marchandise="Pieces auto",
                     nombre_colis=120)
    db.add(pl)
    op = OperationAcconage(reference="OPA-0001", escale_id=escale.id,
                           type_operation="dechargement", marchandise="Pieces auto")
    db.add(op)
    db.commit()
    return conteneur, bl


def _etat(dossier, cle):
    for e in dossier["etapes"]:
        if e["cle"] == cle:
            return e
    raise AssertionError(f"etape {cle!r} absente du dossier")


# --------------------------------------------------------------------------- #
# 1. Chaine reellement reliee -> etapes 'reel' avec enregistrements
# --------------------------------------------------------------------------- #
def test_chaine_reelle_exposee_par_numero_conteneur(db: Session):
    conteneur, bl = _chaine_complet_db(db)
    d = consigner_dossier_marchandise(db, numero_conteneur="MSKU7654321")

    assert d["ancre"]["conteneur_resolu"] is True
    assert d["ancre"]["numero_bl"] == "MEDUPBL12345"
    assert _etat(d, "conteneur")["etat"] == "reel"
    assert _etat(d, "connaissement")["etat"] == "reel"
    assert _etat(d, "packing_list")["etat"] == "reel"
    assert _etat(d, "acconage")["etat"] == "reel"
    assert _etat(d, "arrivee")["etat"] == "reel"
    # Contenu reellement lu, pas invente.
    assert _etat(d, "connaissement")["enregistrements"][0]["numero_bl"] == "MEDUPBL12345"


def test_ancre_par_numero_bl_resout_le_conteneur(db: Session):
    _chaine_complet_db(db)
    d = consigner_dossier_marchandise(db, numero_bl="MEDUPBL12345")
    assert d["ancre"]["conteneur_resolu"] is True
    assert d["ancre"]["numero_conteneur"] == "MSKU7654321"
    assert _etat(d, "conteneur")["etat"] == "reel"


# --------------------------------------------------------------------------- #
# 2. Etapes aval sans lien saisi -> 'absent' avec enregistrements vides :
#    le lien est possible (colonnes 024) mais JAMAIS devine.
# --------------------------------------------------------------------------- #
def test_etapes_aval_sans_lien_saisi_jamais_inventees(db: Session):
    _chaine_complet_db(db)
    d = consigner_dossier_marchandise(db, numero_conteneur="MSKU7654321")
    for cle in ("declaration", "magasin", "facture"):
        e = _etat(d, cle)
        assert e["etat"] == "absent", cle
        assert e["enregistrements"] == [], f"{cle} ne doit contenir aucune donnee inventee"
    # La mission de livraison ne porte pas d'escale_id : sans conteneur_id ni
    # numero_bl saisi, elle reste 'absent' egalement.
    assert _etat(d, "livraison")["etat"] == "absent"


# --------------------------------------------------------------------------- #
# 2bis. Chaine fermee (migration 024) : liens saisis explicitement -> 'reel'
# --------------------------------------------------------------------------- #
def test_chaine_aval_reliee_par_liens_saisis(db: Session):
    conteneur, bl = _chaine_complet_db(db)
    escale_id = bl.escale_id
    from app.models.transit_avance import (
        DeclarationDouaniereAvance, RegimeDouanier,
    )
    from app.models.magasin_douane import DeclarationEntrepot, RegimeEntrepot
    from app.models.transport import Mission
    from app.models.finance_ohada import FactureNew
    from datetime import date

    db.add(DeclarationDouaniereAvance(
        numero_declaration="DEC-024-001",
        regime_douanier=RegimeDouanier.MISE_CONSOMMATION,
        conteneur_id=conteneur.id, valeur_declaree=1_500_000,
        code_hs="8708.99.00", statut="valide",
    ))
    db.add(DeclarationEntrepot(
        numero_declaration="ENT-024-001",
        regime=RegimeEntrepot.SUSPENDU,
        numero_bl="MEDUPBL12345",  # rattrape par B/L, pas par FK conteneur
        valeur_marchandise=1_500_000,
    ))
    db.add(Mission(
        reference="MIS-024-001", type_mission="livraison",
        conteneur_id=conteneur.id,
    ))
    db.add(FactureNew(
        numero_facture="FAC-024-001", type_facture="prestation",
        date_emission=date(2026, 1, 5), montant_ht=250_000,
        montant_ttc=298_125, escale_id=escale_id,
    ))
    db.commit()

    d = consigner_dossier_marchandise(db, numero_conteneur="MSKU7654321")
    dec = _etat(d, "declaration")
    assert dec["etat"] == "reel" and dec["enregistrements"][0]["numero_declaration"] == "DEC-024-001"
    mag = _etat(d, "magasin")
    assert mag["etat"] == "reel" and mag["enregistrements"][0]["numero_bl"] == "MEDUPBL12345"
    liv = _etat(d, "livraison")
    assert liv["etat"] == "reel" and liv["enregistrements"][0]["reference"] == "MIS-024-001"
    fac = _etat(d, "facture")
    assert fac["etat"] == "reel" and fac["enregistrements"][0]["numero_facture"] == "FAC-024-001"
    # Le mode de rattachement est affiche, pas implicite.
    assert "conteneur_id" in dec["mode_correspondance"]
    assert "numero_bl" in mag["mode_correspondance"]
    assert "escale_id" in fac["mode_correspondance"]


def test_mission_d_un_autre_conteneur_n_apparait_pas(db: Session):
    """Pas de devinette par client/date : seules les lignes liees sortent."""
    conteneur, bl = _chaine_complet_db(db)
    from app.models.transport import Mission
    other = Conteneur(numero="OTHER0000001", type_conteneur="20'Dry", statut="empty")
    db.add(other)
    db.flush()
    db.add(Mission(reference="MIS-AUTRE-1", type_mission="livraison",
                   conteneur_id=other.id))
    db.add(Mission(reference="MIS-LIEE-1", type_mission="livraison",
                   numero_bl="MEDUPBL12345"))
    db.commit()
    d = consigner_dossier_marchandise(db, numero_conteneur="MSKU7654321")
    refs = {r["reference"] for r in _etat(d, "livraison")["enregistrements"]}
    assert refs == {"MIS-LIEE-1"}


# --------------------------------------------------------------------------- #
# 3. Cycle de vie + parc relies par NUMERO physique (correspondance legitime)
# --------------------------------------------------------------------------- #
def test_cycle_et_parc_relies_par_numero(db: Session):
    _chaine_complet_db(db)
    from app.models.conteneur_cycle import ConteneurCycle, CycleConteneur
    from app.models.parc import MouvementParc

    cc = ConteneurCycle(numero="MSKU7654321", type_conteneur="dry_40", taille_pieds=40)
    db.add(cc)
    db.flush()
    db.add(CycleConteneur(conteneur_id=cc.id, statut="stocke", localisation="Terminal 1"))
    db.add(MouvementParc(sens="entree", numero_conteneur="MSKU7654321", etat="BON_ETAT"))
    db.commit()

    d = consigner_dossier_marchandise(db, numero_conteneur="MSKU7654321")
    assert _etat(d, "cycle_de_vie")["etat"] == "reel"
    assert _etat(d, "parc")["etat"] == "reel"
    assert _etat(d, "parc")["enregistrements"][0]["sens"] == "entree"


def test_absence_de_cycle_signale_absent_pas_invente(db: Session):
    _chaine_complet_db(db)
    d = consigner_dossier_marchandise(db, numero_conteneur="MSKU7654321")
    # Pas de ConteneurCycle/MouvementParc crees -> 'absent' (lien possible mais
    # aucun enregistrement), et surtout pas 'reel' avec des donnees fausses.
    assert _etat(d, "cycle_de_vie")["etat"] == "absent"
    assert _etat(d, "cycle_de_vie")["enregistrements"] == []


# --------------------------------------------------------------------------- #
# 4. Echecs francs : aucune donnee fabriquee
# --------------------------------------------------------------------------- #
def test_ancre_inconnue_404(db: Session):
    from fastapi import HTTPException
    import pytest
    with pytest.raises(HTTPException) as exc:
        consigner_dossier_marchandise(db, numero_conteneur="INCONNU000")
    assert exc.value.status_code == 404


def test_sans_identifiant_400(db: Session):
    from fastapi import HTTPException
    import pytest
    with pytest.raises(HTTPException) as exc:
        consigner_dossier_marchandise(db)
    assert exc.value.status_code == 400


# --------------------------------------------------------------------------- #
# 5. Endpoint (lecture seule, sans authentification sur ce routeur)
# --------------------------------------------------------------------------- #
def test_endpoint_dossier_marchandise(client, db):
    _chaine_complet_db(db)
    r = client.get("/api/v1/acconage/dossier-marchandise",
                   params={"numero_conteneur": "MSKU7654321"})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["ancre"]["conteneur_resolu"] is True
    assert len(body["etapes"]) == 11  # 7 etapes explorees + 4 non liciables

    missing = client.get("/api/v1/acconage/dossier-marchandise",
                         params={"numero_conteneur": "ABSENT123"})
    assert missing.status_code == 404

    nokey = client.get("/api/v1/acconage/dossier-marchandise")
    assert nokey.status_code == 400
