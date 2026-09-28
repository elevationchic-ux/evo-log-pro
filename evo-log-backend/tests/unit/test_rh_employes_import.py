"""Tests RH : annuaire reel des employes (creation, import, fiche).

Couvre ce que l'ecran « Annuaire & Gestion des Employes » appelait sans que le
serveur le fournisse :
  * POST /rh/employes — le bouton « Ajouter un Employe » partait en 404 ;
  * POST /rh/employes/import-excel — il repondait un 202 « pending » sans rien
    importer, ce qui affichait un succes vide ;
  * la fiche d'un employe sans contrat : type_contrat null, pas un CDI par
    defaut (une donnee inventee se diffuse dans l'attestation de travail) ;
  * la validation du contrat AVANT toute ecriture : un CDD sans date de fin ne
    doit pas laisser dans la base un salarie sans contrat, moitie importe.
"""
import io
import zipfile
from contextlib import contextmanager
from datetime import date

import pytest

from app.core.security import get_current_user, get_password_hash
from app.main import app
from app.models.rh import ContratTravail, Organigramme
from app.models.tenant import Company, Department
from app.models.user import User
from app.routers.v1.rh import (
    _champ_depuis_entete, _date_import, _lignes_xlsx, _nombre_import,
)

URL_EMPLOYES = "/api/v1/rh/employes"
URL_IMPORT = "/api/v1/rh/employes/import-excel"


@contextmanager
def _identite(user):
    """Surcharge d'identite qui rend la precedente.

    La fixture `client` pose deja un faux super-utilisateur : un
    `dependency_overrides.pop()` la supprimerait pour les tests suivants. On
    ne remplace que le temps du test.
    """
    saved = app.dependency_overrides.get(get_current_user)
    app.dependency_overrides[get_current_user] = lambda: user
    try:
        yield
    finally:
        if saved is not None:
            app.dependency_overrides[get_current_user] = saved


@pytest.fixture
def company(db):
    c = Company(code="ACME", nom="ACME SA", is_active=True, modules_actives='["rh"]')
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


@pytest.fixture
def rh(db, company):
    """Salarie casquette RH : requireRH accepte role_level 1 (admin entreprise)."""
    u = User(
        username="rh-acme", email="rh@acme.example",
        hashed_password=get_password_hash("Rh12345678"),
        is_active=True, is_superuser=False, role_level=1, company_id=company.id,
        must_change_password=False,
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


FICHE_VALIDE = {
    "email": "mvondo@acme.example",
    "prenom": "Jean-Marc",
    "nom": "MVONDO",
    "phone": "+237 677 00 11 22",
    "poste": "Responsable operations portuaires",
    "departement": "LOGISTIQUE",
    "date_embauche": "2026-01-05",
    "type_contrat": "CDI",
    "salaire_base": 450000,
}


# ---------------------------------------------------------------------------
# Lecture des fichiers : entetes, dates, nombres
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("entete,attendu", [
    ("Nom", "nom"),
    ("Prénom", "prenom"),
    ("Nom complet", "full_name"),
    ("Email professionnel", "email"),
    ("Téléphone", "phone"),
    ("Matricule", "matricule"),
    ("Poste occupé", "poste"),
    ("Département", "departement"),
    ("Date d'embauche", "date_embauche"),
    ("Type de contrat", "type_contrat"),
    ("Date de fin du contrat", "date_fin_contrat"),
    ("Salaire de base (XAF)", "salaire_base"),
    ("Horaire de travail", "horaire_travail"),
    ("Lieu d'affectation", "lieu_travail"),
    # Export anglais : les memes colonnes, trois vocabulaires.
    ("First Name", "prenom"),
    ("Last Name", "nom"),
    ("Full Name", "full_name"),
    ("Hire Date", "date_embauche"),
    ("Salary", "salaire_base"),
    ("Department", "departement"),
])
def test_entetes_import_mappees(entete, attendu):
    assert _champ_depuis_entete(entete) == attendu


def test_prenom_ne_tombe_pas_dans_la_colonne_nom():
    """« Prénom » contient « nom » : le decoupage en mots l'interdit."""
    assert _champ_depuis_entete("Prénom") == "prenom"
    assert _champ_depuis_entete("Nom") == "nom"


def test_entete_inconnu_est_ignore():
    assert _champ_depuis_entete("Signe particulier") is None
    assert _champ_depuis_entete("") is None


def test_date_import_accepte_le_format_francais_et_la_serie_excel():
    assert _date_import("champ", "05/01/2026") == date(2026, 1, 5)
    assert _date_import("champ", "2026-01-05") == date(2026, 1, 5)
    # Serie Excel : 46022 = 05/01/2026 (jours depuis 1899-12-30).
    assert _date_import("champ", "46022") == date(2026, 1, 5)
    assert _date_import("champ", "") is None
    with pytest.raises(ValueError, match="date non reconnue"):
        _date_import("champ", "5 janvier 26")


def test_nombre_import_accepte_les_deux_separateurs():
    assert _nombre_import("champ", "1.234,56") == pytest.approx(1234.56)
    assert _nombre_import("champ", "1,234.56") == pytest.approx(1234.56)
    assert _nombre_import("champ", "450 000") == pytest.approx(450000)
    with pytest.raises(ValueError, match="numerique invalide"):
        _nombre_import("champ", "quarante-cinq mille")


def _xlsx(lignes):
    """Classeur .xlsx minimal, ecrit a la main dans l'archive ZIP de XML.

    Les cases sont ecrites en chaines partagees (t="s") : c'est ce que produit
    Excel pour du texte, et le lecteur du serveur doit le resoudre.
    """
    chaines, index = [], {}
    for ligne in lignes:
        for valeur in ligne:
            cle = str(valeur)
            if valeur not in (None, "") and cle not in index:
                index[cle] = len(chaines)
                chaines.append(cle)

    lignes_xml = []
    for numero, ligne in enumerate(lignes, start=1):
        cases = "".join(
            '<c r="%s%d" t="s"><v>%d</v></c>' % (chr(65 + col), numero, index[str(valeur)])
            for col, valeur in enumerate(ligne)
            if valeur not in (None, "")
        )
        lignes_xml.append('<row r="%d">%s</row>' % (numero, cases))
    sheet = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        "<sheetData>%s</sheetData></worksheet>" % "".join(lignes_xml)
    )
    shared = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'count="%d" uniqueCount="%d">%s</sst>' % (
            len(chaines), len(chaines),
            "".join("<si><t>%s</t></si>" % c for c in chaines),
        )
    )
    tampon = io.BytesIO()
    with zipfile.ZipFile(tampon, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("xl/worksheets/sheet1.xml", sheet)
        archive.writestr("xl/sharedStrings.xml", shared)
    return tampon.getvalue()


def test_lignes_xlsx_lit_un_classeur_reel():
    lignes = _xlsx([["Nom", "Email"], ["MVONDO", "mvondo@acme.example"], [], ["", ""]])
    lu = _lignes_xlsx(lignes)
    assert lu == [["Nom", "Email"], ["MVONDO", "mvondo@acme.example"]]


def test_lignes_xlsx_refuse_une_archive_valide_sans_feuille():
    tampon = io.BytesIO()
    with zipfile.ZipFile(tampon, "w") as archive:
        archive.writestr("hello.txt", "rien")
    with pytest.raises(ValueError, match="Aucune feuille"):
        _lignes_xlsx(tampon.getvalue())


# ---------------------------------------------------------------------------
# POST /rh/employes
# ---------------------------------------------------------------------------
def test_ajouter_employe_ecrit_compte_contrat_et_organigramme(client, db, company, rh):
    with _identite(rh):
        reponse = client.post(URL_EMPLOYES, json=FICHE_VALIDE)
    assert reponse.status_code == 201, reponse.text
    fiche = reponse.json()

    assert fiche["full_name"] == "Jean-Marc MVONDO"
    assert fiche["type_contrat"] == "CDI"
    assert fiche["date_embauche"] == "2026-01-05"
    assert fiche["salaire_base"] == 450000
    assert fiche["departement"] == "LOGISTIQUE"
    assert fiche["statut"] == "actif"
    assert fiche["en_conge"] is False
    # Mot de passe temporaire : genere, communique une fois, force au login.
    mot_de_passe = fiche["temporary_password"]
    assert mot_de_passe and len(mot_de_passe) >= 8

    membre = db.query(User).filter(User.email == "mvondo@acme.example").one()
    assert membre.company_id == company.id
    assert membre.must_change_password is True
    assert membre.hashed_password != mot_de_passe
    assert membre.matricule  # attribue par le serveur, pas invente a l'ecran

    contrat = db.query(ContratTravail).filter(
        ContratTravail.employe_id == membre.id
    ).one()
    assert contrat.type_contrat == "CDI"
    assert contrat.date_fin is None
    assert contrat.departement == "LOGISTIQUE"

    position = db.query(Organigramme).filter(Organigramme.employe_id == membre.id).one()
    assert position.departement == "LOGISTIQUE"

    # Le departement saisi a ete enregistre dans le registre de l'entreprise.
    assert db.query(Department).filter(
        Department.company_id == company.id, Department.nom == "LOGISTIQUE"
    ).one().id == membre.department_id


def test_employe_sans_contrat_n_invente_pas_de_cdi(client, db, company, rh):
    """Un compte sans contrat : les colonnes contrat restent vides a l'ecran."""
    sans_contrat = dict(FICHE_VALIDE)
    sans_contrat.pop("poste")
    sans_contrat.pop("salaire_base")
    with _identite(rh):
        reponse = client.post(URL_EMPLOYES, json=sans_contrat)
    assert reponse.status_code == 201, reponse.text
    fiche = reponse.json()
    assert fiche["type_contrat"] is None
    assert fiche["date_embauche"] is None
    assert fiche["salaire_base"] is None
    assert fiche["statut"] is None
    assert fiche["avertissements"] and "contrat" in fiche["avertissements"][0]
    assert db.query(ContratTravail).count() == 0


def test_cdd_sans_date_de_fin_ne_laisse_aucun_salarie_orphelin(client, db, company, rh):
    """La regle s'applique avant d'ecrire : rien ne doit rester en base."""
    cdd = dict(FICHE_VALIDE, email="cdd@acme.example", type_contrat="CDD")
    with _identite(rh):
        reponse = client.post(URL_EMPLOYES, json=cdd)
    assert reponse.status_code == 400
    assert "date de fin" in reponse.json()["detail"]
    assert db.query(User).filter(User.email == "cdd@acme.example").count() == 0


def test_type_de_contrat_inconnu_est_refuse(client, db, company, rh):
    with _identite(rh):
        reponse = client.post(URL_EMPLOYES, json=dict(FICHE_VALIDE, type_contrat="Freelance"))
    assert reponse.status_code == 400
    assert "Type de contrat inconnu" in reponse.json()["detail"]
    assert db.query(User).count() == 1  # seul le compte RH de la fixture


def test_cdi_ne_porte_pas_de_date_de_fin(client, company, rh):
    with _identite(rh):
        reponse = client.post(
            URL_EMPLOYES,
            json=dict(FICHE_VALIDE, date_fin_contrat="2027-01-05"),
        )
    assert reponse.status_code == 400
    assert "CDI" in reponse.json()["detail"]


def test_email_en_double_est_refuse(client, db, company, rh):
    with _identite(rh):
        assert client.post(URL_EMPLOYES, json=FICHE_VALIDE).status_code == 201
        reponse = client.post(URL_EMPLOYES, json=FICHE_VALIDE)
    assert reponse.status_code == 409
    assert db.query(User).filter(User.email == FICHE_VALIDE["email"]).count() == 1


def test_un_salarie_ordinaire_ne_peut_pas_creer_un_collaborateur(client, db, company, rh):
    pair = User(
        username="chauffeur", email="chauffeur@acme.example",
        hashed_password=get_password_hash("Ch12345678"),
        is_active=True, is_superuser=False, role_level=3, company_id=company.id,
    )
    db.add(pair)
    db.commit()
    with _identite(pair):
        reponse = client.post(URL_EMPLOYES, json=FICHE_VALIDE)
    assert reponse.status_code == 403


# ---------------------------------------------------------------------------
# Import CSV / XLSX
# ---------------------------------------------------------------------------
CSV_TROIS_LIGNES = (
    "Nom,Prénom,Email,Téléphone,Poste,Département,Date d'embauche,Type contrat,"
    "Salaire de base,Matricule\n"
    "MVONDO,Jean-Marc,mvondo@acme.example,+237 677 00 11 22,Declarant,TRANSIT,"
    "05/01/2026,CDI,450000,\n"
    "NGUEMA,Aline,aline.nguema@acme.example,,Magasinier,MAGASIN,12/02/2026,CDD,"
    "1.234.560,\n"
    "SANS EMAIL,,,-,Chauffeur,TRANSPORT,01/03/2026,CDI,300000,\n"
).encode("utf-8")


def test_import_csv_ecrit_les_lignes_valides_et_rejette_les_autres(client, db, company, rh):
    """Un fichier partiellement valide s'importe : la raison est par ligne."""
    with _identite(rh):
        reponse = client.post(
            URL_IMPORT,
            files={"file": ("employes.csv", CSV_TROIS_LIGNES, "text/csv")},
        )
    assert reponse.status_code == 200, reponse.text
    corps = reponse.json()
    assert corps["total_lignes"] == 3
    assert len(corps["importes"]) == 1, corps
    assert len(corps["rejets"]) == 2

    # La ligne 2 (CDD) est rejetee pour sa date de fin absente ; la ligne 4
    # (l'identifiee par son contenu) pour son email manquant.
    raisons = " | ".join(r["raison"] for r in corps["rejets"])
    assert "date de fin" in raisons
    assert "email" in raisons.lower()

    assert db.query(User).filter(User.email == "mvondo@acme.example").count() == 1
    contrat = db.query(ContratTravail).one()
    assert contrat.date_debut == date(2026, 1, 5)
    # L'import a communique les mots de passe temporaires, une fois.
    assert corps["importes"][0]["temporary_password"]


def test_import_xlsx_entetes_anglais(client, db, company, rh):
    lignes = _xlsx([
        ["Full Name", "Email", "Job Title", "Department", "Hire Date", "Contract Type", "Salary"],
        ["Aline NGUEMA", "aline@acme.example", "Magasinier", "MAGASIN",
         "2026-03-01", "CDI", "300000"],
    ])
    with _identite(rh):
        reponse = client.post(
            URL_IMPORT,
            files={"file": ("staff.xlsx", lignes,
                            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        )
    assert reponse.status_code == 200, reponse.text
    corps = reponse.json()
    assert len(corps["importes"]) == 1, corps
    membre = db.query(User).filter(User.email == "aline@acme.example").one()
    assert membre.full_name == "Aline NGUEMA"
    assert db.query(ContratTravail).filter(
        ContratTravail.employe_id == membre.id, ContratTravail.salaire_base == 300000
    ).count() == 1


def test_import_xls_ancien_format_refuse_honnetement(client, company, rh):
    """Pas de faux succes : le binaire 97-2003 n'est pas lisible, c'est dit."""
    with _identite(rh):
        reponse = client.post(
            URL_IMPORT,
            files={"file": ("vieux.xls", b"\xd0\xcf\x11\xe0\x00", "application/vnd.ms-excel")},
        )
    assert reponse.status_code == 400
    assert ".xls" in reponse.json()["detail"]


def test_import_sans_colonne_email_est_refuse(client, company, rh):
    blob = "Nom;Poste\nMVONDO;Declarant\n".encode("utf-8")
    with _identite(rh):
        reponse = client.post(
            URL_IMPORT, files={"file": ("employes.csv", blob, "text/csv")}
        )
    assert reponse.status_code == 400
    assert "Email" in reponse.json()["detail"]


# ---------------------------------------------------------------------------
# Annuaire : enrichi, sans N+1 ni valeur inventee
# ---------------------------------------------------------------------------
def test_annuaire_expose_le_contrat_et_le_conge(client, db, company, rh):
    with _identite(rh):
        assert client.post(URL_EMPLOYES, json=FICHE_VALIDE).status_code == 201
        reponse = client.get(URL_EMPLOYES)
    assert reponse.status_code == 200
    corps = reponse.json()
    noms = [i["full_name"] for i in corps["items"]]
    assert "Jean-Marc MVONDO" in noms
    fiche = next(i for i in corps["items"] if i["full_name"] == "Jean-Marc MVONDO")
    assert fiche["matricule"]
    assert fiche["type_contrat"] == "CDI"
    assert fiche["phone"] == "+237 677 00 11 22"
    assert fiche["en_conge"] is False
    # Le compte RH, sans contrat saisi, remonte des colonnes vide.
    fiche_rh = next(i for i in corps["items"] if i["full_name"] == "rh-acme")
    assert fiche_rh["type_contrat"] is None
    assert fiche_rh["salaire_base"] is None


def test_recherche_par_matricule(client, db, company, rh):
    with _identite(rh):
        fiche = client.post(URL_EMPLOYES, json=FICHE_VALIDE).json()
        resultat = client.get(URL_EMPLOYES, params={"search": fiche["matricule"]})
    items = resultat.json()["items"]
    assert [i["matricule"] for i in items] == [fiche["matricule"]]
