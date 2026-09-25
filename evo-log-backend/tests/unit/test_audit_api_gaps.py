# -*- coding: utf-8 -*-
"""Tests du script d'audit des ecarts API (scripts/audit_api_gaps.py).

L'audit est un outil de decision : un faux positif fait chercher une route qui
existe, un faux negatif laisse un ecran vide passer inapercu. Les regressions
ci-dessous ont chacune reellement deplace le chiffre (28, puis 10, puis 33 ecarts
selon les regles) ; elles sont figees ici pour qu'aucun futur ajustement du
joker ne redonne une fausse confiance.

Le script n'est pas un paquet importable : il est charge par chemin.
"""
import importlib.util
import os

import pytest

BACKEND = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCRIPT = os.path.join(BACKEND, "scripts", "audit_api_gaps.py")


@pytest.fixture(scope="module")
def audit():
    spec = importlib.util.spec_from_file_location("audit_api_gaps", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# ─── normalisation ─────────────────────────────────────────────────────────
def test_normalise_le_prefixe_versionne(audit):
    # Le middleware de main.py reecrit /api/<x> en /api/v1/<x> : meme route.
    assert audit.normaliser("/api/transport/fuel") == "/api/v1/transport/fuel"
    assert audit.normaliser("/api/v1/transport/fuel") == "/api/v1/transport/fuel"


def test_normalise_ignore_query_et_interpolations(audit):
    assert audit.normaliser("/api/transport/fuel?depuis=2026-01-01") == "/api/v1/transport/fuel"
    assert audit.normaliser("/api/v1/transport/${id}/pannes") == "/api/v1/transport/{p}/pannes"


# ─── comparaison aux templates ─────────────────────────────────────────────
def test_segment_interpole_accepte_le_literal_du_template(audit):
    """/rh/conges/${id}/approuver est servi par /rh/conges/{conge_id}/approuver.

    Traiter le jeton d'interpolation comme un literal produisait un ecart
    fantome sur une route pourtant existante.
    """
    assert audit.compat("/api/v1/rh/conges/{p}/approuver",
                        "/api/v1/rh/conges/{conge_id}/approuver") == "strict"
    # La, le jeton tombe sur un literal du template : possible mais non prouve.
    assert audit.compat("/api/v1/purchase/requisitions/{p}/{p}",
                        "/api/v1/purchase/requisitions/{req_id}/approve") == "lax"


def test_jeton_front_ne_remonte_pas_un_literal_different(audit):
    # Un segment inconnu cote backend reste un trou : le joker ne justifie pas tout.
    assert audit.compat("/api/v1/incidents/client/{p}",
                        "/api/v1/incidents/{incident_id}") is None


def test_joker_ambigu_n_est_pas_compte_comme_couvert(audit):
    """`acconage/${id}` ne doit pas etre absorbe par la route `acconage/yard`.

    Sans cette distinction, rendre le jeton permissif faisait disparaitre de
    vrais ecarts du rapport (10 calls devenus « couverts » sans preuve).
    """
    routes = ["/api/v1/acconage", "/api/v1/acconage/yard", "/api/v1/acconage/baplie"]
    genre, route = audit.classifier("/api/v1/acconage/{p}", routes, set(), frozenset())
    assert genre == "joker_ambigu" and route == "/api/v1/acconage/yard"


def test_domaine_exigeant_interdit_la_couverture_par_ressemblance(audit):
    """En transport/magasin, un joker non prouve est un trou, pas une zone grise.

    Le degre « lax » reste commode ailleurs, mais dans ces domaines la
    ressemblance de chemin ne doit jamais pouvoir se lire comme « couvert » :
    l'appel doit tomber en `pending_sans_donnee`, c'est-a-dire repondre 200
    avec une enveloppe vide.
    """
    routes = ["/api/v1/transport/missions/actives", "/api/v1/transport/missions"]
    genre, route = audit.classifier(
        "/api/v1/transport/missions/{p}", routes, set(), frozenset(), exige_prouve=True
    )
    assert genre == "pending_sans_donnee" and route is None


def test_domaine_exigeant_garde_la_correspondance_prouvee(audit):
    """Durcir ne doit pas inventer des trous : {parametre} reste une preuve."""
    routes = ["/api/v1/transport/missions/{mission_id}/positions"]
    genre, route = audit.classifier(
        "/api/v1/transport/missions/{p}/positions", routes, set(), frozenset(),
        exige_prouve=True,
    )
    assert genre == "couvert" and route == routes[0]


def test_seuls_transport_et_magasin_sont_exigeants(audit):
    assert audit.domaine("/api/v1/magasin/inventaire/{p}") == "magasin"
    assert set(audit.DOMAINES_EXIGEANTS) == {"transport", "magasin"}
    assert audit.domaine("/api/v1/acconage/{p}") not in audit.DOMAINES_EXIGEANTS


def test_nom_de_segment_n_est_pas_un_fallback(audit):
    """/api/v1/prestataires et /api/v1/k-modules sont des routes nominales.

    L'ancienne detection cherchait `rest`/`module` dans toute l'URL et classait
    ces routes comme catch-all, ce qui masquait leurs vrais ecarts.
    """
    routes = ["/api/v1/prestataires", "/api/v1/k-modules/cotations"]
    genre, route = audit.classifier("/api/v1/prestataires", routes, set(), frozenset())
    assert genre == "couvert" and route == "/api/v1/prestataires"


def test_parametre_path_avale_plusieurs_troncons(audit):
    assert audit.compat("/api/v1/ged/notes/a/b/c", "/api/v1/ged/{chemin:path}") == "strict"


# ─── classification ────────────────────────────────────────────────────────
def test_route_stub_501_compte_comme_ecart(audit):
    routes = ["/api/v1/k-modules/cotations"]
    genre, _ = audit.classifier("/api/v1/k-modules/cotations",
                                routes, {"/api/v1/k-modules/cotations"}, frozenset())
    assert genre == "repond_501"


def test_stub_et_reel_sur_meme_chemin_gagne_le_reel(audit):
    """Un joker 501 ne doit pas faire passer une route litterale reelle pour un trou."""
    routes = ["/api/v1/ged/{chemin:path}", "/api/v1/ged/documents"]
    genre, route = audit.classifier("/api/v1/ged/documents", routes,
                                   {"/api/v1/ged/{chemin:path}"}, frozenset())
    assert genre == "couvert" and route == "/api/v1/ged/documents"


def test_appel_inconnu_tombe_sur_le_fallback_pending(audit):
    genre, route = audit.classifier("/api/v1/transport/lieux-magiques", ["/api/v1/transport"],
                                    set(), frozenset(["auth"]))
    assert genre == "pending_sans_donnee" and route is None


def test_surface_auth_garde_un_vrai_404(audit):
    genre, _ = audit.classifier("/api/v1/auth/magique", [], set(), frozenset(["auth"]))
    assert genre == "404_reel"


# ─── filtrage des faux appels ──────────────────────────────────────────────
def test_ignore_les_commentaires(audit):
    ligne = " * Construit une URL : apiUrl('/magasin/articles') -> '/api/v1/magasin/articles'"
    assert not audit.est_un_appel(ligne, ligne.index("/api/v1/"))


def test_ignore_la_normalisation_du_client(audit):
    ligne = "  if (p.startsWith('/api/v1/')) return p;"
    assert not audit.est_un_appel(ligne, ligne.index("/api/v1/"))
    ligne2 = "export const API_PREFIX = '/api/v1';"
    assert not audit.est_un_appel(ligne2, ligne2.index("/api/v1"))


def test_accepte_un_veritable_appel(audit):
    ligne = "    apiClient.get(`/api/v1/transport/fuel`, { params }),"
    assert audit.est_un_appel(ligne, ligne.index("/api/v1/"))


def test_ternaire_entre_deux_routes_reste_signale(audit):
    """Le second membre d'un ternaire est un vrai appel : ne pas le filtrer."""
    ligne = "  const u = b ? '/api/v1/transport/a' : '/api/v1/transport/b'"
    assert audit.est_un_appel(ligne, ligne.index("/api/v1/transport/b"))


def test_interpolation_a_ternaire_ne_casse_pas_le_chemin(audit):
    """`${statut === 'APPROUVE' ? 'approuver' : 'rejeter'}` ne doit pas tronquer.

    Sans pre-nettoyage, le quote du ternaire fermait le literal et l'audit
    publiait un chemin tronque (`/api/v1/rh/conges/{p}/${statut.toUpperCase() ===`).
    """
    ligne = ("apiClient.post(`/api/rh/conges/${id}/"
             "${statut.toUpperCase() === 'APPROUVE' ? 'approuver' : 'rejeter'}`)")
    clean = audit.INTERPOLATION.sub(audit.JETON, ligne)
    bruts = audit.APPEL.findall(clean)
    assert bruts == ["/api/rh/conges/{p}/{p}"]
    assert audit.segments(audit.normaliser(bruts[0])) == [
        "api", "v1", "rh", "conges", "{p}", "{p}"]
