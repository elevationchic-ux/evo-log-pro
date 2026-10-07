"""RBAC des expansions profondes (routeurs *_deep) : parite catalogue + porteurs.

Discipline identique au batch amenagement, generalisee aux 14 routeurs profonds
generes et montes dans main.py. Deux familles, deux invariants opposes :

  1. FAMILLE METIER (transit, rh, qhse, magasin, parc, transport, comptabilite,
     tresorerie, port, b2b) : chaque require_perm() doit etre (a) declare au
     catalogue  aucun code fantome, (b) porte par au moins un role metier
     ROLE_GRANTS  aucune route unreachable/403 permanent pour le departement
     legitime.

  2. FAMILLE PLATEFORME (admin, superadmin, dashboard, reports) : chaque code est
     declare au catalogue (visibilite/matrice/audit), mais AUCUN role metier
     (niveau >= 2) ne le porte  volonte explicite. Seuls SUPER_ADMIN (0) et
     ADMIN_ENTREPRISE (1) y accedent, par bypass du moteur (permissions.can,
     _BYPASS_LEVELS = {0,1}). On verifie ce bypass au VRAI moteur, pas un mock :
     niveau 0/1 = True, role metier granulaire = False.

Les noms inventes par le generateur (compta, finance, port_ops) ont ete reconciles
vers les modules canoniques du catalogue (comptabilite, tresorerie, port) ; les
routeurs employent desormais ces codes canoniques, d'ou la parite attendue ici.
"""
import re
import types
from pathlib import Path

import pytest

from app.core.permission_catalog import ROLE_GRANTS, iter_permission_rows
from app.core.permissions import can, has_perm

BACKEND_ROOT = Path(__file__).resolve().parents[2]
V1 = BACKEND_ROOT / "app" / "routers" / "v1"

CATALOGUE = {row[0] for row in iter_permission_rows()}


def _codes(router_name: str):
    src = (V1 / router_name).read_text(encoding="utf-8")
    codes = set(re.findall(r'require_perm\(\s*"([^"]+)"', src))
    # Ignore les placeholders de docstring type "module.{sous_module}.{action}".
    return sorted(c for c in codes if "{" not in c)


def _porteurs(code: str):
    return [nom for nom, _l, _d, grant in ROLE_GRANTS if has_perm(grant, code)]


# Routeurs metier : {fichier : nombre de codes distincts employes}. Le compteur
# est une decision relisible : une route qui change de code doit faire rougir ce
# test et relancer la discussion, pas passer en silence.
METIERS = {
    "transit_deep.py": None,        # +13 sous-modules transit (Phase 1)
    "rh_deep.py": None,             # +14 sous-modules rh (Phase 1)
    "qhse_deep.py": None,           # +12 sous-modules qhse (Phase 1)
    "magasin_deep.py": None,        # +13 sous-modules magasin (Phase 1)
    "parc_deep.py": None,           # +11 sous-modules parc (Phase 1)
    "transport_deep.py": 37,        # module canonique transport (Phase 2)
    "comptabilite_deep.py": 34,     # compta -> comptabilite (Phase 3)
    "finance_deep.py": 37,          # finance -> tresorerie (Phase 3)
    "port_deep.py": 37,             # port_ops -> port (Phase 3)
    "b2b_deep.py": 34,              # nouveau module b2b (Phase 4)
    "aerien_deep.py": 37,           # fret aerien (ajoute par l'expansion)
    "ferroviaire_deep.py": 37,      # fret ferroviaire
    "fluvial_deep.py": 31,          # fret fluvial
    "log3pl_deep.py": 31,           # logistique 3PL
}

# Routeurs plateforme : bypass niveaux 0/1 uniquement, aucun porteur metier.
PLATEFORME = {
    "admin_deep.py": 34,
    "superadmin_deep.py": 31,
    "dashboard_deep.py": 31,
    "reports_deep.py": 34,
}

# Roles metiers (niveau >= 2) : aucun ne doit porter un code plateforme.
def _est_role_metier(nom: str, niveau: int) -> bool:
    return niveau >= 2


@pytest.mark.parametrize("router", sorted(METIERS))
def test_routeur_metier_aucun_code_fantome(router):
    codes = _codes(router)
    assert codes, f"{router} : aucun code require_perm trouve"
    fantomes = [c for c in codes if c not in CATALOGUE]
    assert not fantomes, f"{router} : codes absents du catalogue : {fantomes}"
    if METIERS[router] is not None:
        assert len(codes) == METIERS[router], (
            f"{router} : attendu {METIERS[router]} codes, trouve {len(codes)}"
        )


@pytest.mark.parametrize("router", sorted(METIERS))
def test_routeur_metier_chaque_code_a_un_porteur(router):
    for code in _codes(router):
        assert _porteurs(code), f"{router} : aucun role metier ne porte {code}"


@pytest.mark.parametrize("router", sorted(PLATEFORME))
def test_routeur_plateforme_aucun_code_fantome(router):
    codes = _codes(router)
    assert codes, f"{router} : aucun code require_perm trouve"
    fantomes = [c for c in codes if c not in CATALOGUE]
    assert not fantomes, f"{router} : codes absents du catalogue : {fantomes}"
    assert len(codes) == PLATEFORME[router], (
        f"{router} : attendu {PLATEFORME[router]} codes, trouve {len(codes)}"
    )


@pytest.mark.parametrize("router", sorted(PLATEFORME))
def test_routeur_plateforme_aucun_porteur_metier(router):
    # Invariant inverse : la console est reservee, aucun departement ne la porte.
    for code in _codes(router):
        porteurs = [
            nom for nom, lvl, _d, grant in ROLE_GRANTS
            if _est_role_metier(nom, lvl) and has_perm(grant, code)
        ]
        assert not porteurs, f"{router} : role metier inattendu sur {code} : {porteurs}"


# ── Bypass plateforme au VRAI moteur (permissions.can) ──────────────────────
def _user(niveau: int, codes=()):
    role = types.SimpleNamespace(permissions=[
        types.SimpleNamespace(code=c) for c in codes
    ])
    return types.SimpleNamespace(
        is_superuser=False, role_level=niveau, roles=[role],
        company=None, accreditations=[], department_id=None, company_id=1,
    )


@pytest.mark.parametrize("code", [
    "admin.api_key.read", "superadmin.system_config.create",
    "dashboard.task_center.read", "reports.kpi_definition.modify",
])
def test_plateforme_ouverte_aux_niveaux_bypass(code):
    assert can(_user(0), code) is True   # SUPER_ADMIN
    assert can(_user(1), code) is True   # ADMIN_ENTREPRISE


@pytest.mark.parametrize("code", [
    "admin.api_key.read", "superadmin.system_config.create",
    "dashboard.task_center.read", "reports.kpi_definition.modify",
])
def test_plateforme_fermee_aux_roles_metiers(code):
    # Un chef de departement granulaire (codes non vides) se heurte au 403 :
    # son wildcard metier ne recouvre pas un module plateforme.
    metier = _user(2, codes=["magasin.*.*", "transport.*.*", "port.*.*"])
    assert can(metier, code) is False


def test_codes_reconcilies_canoniques_plus_de_noms_inventes():
    # Les noms inventes par le generateur ne doivent plus apparaitre nulle part
    # dans les routeurs : ils ont ete reconciles vers les modules canoniques.
    for router in ("comptabilite_deep.py", "finance_deep.py", "port_deep.py"):
        for invente in ("compta.", "finance.", "port_ops."):
            assert not _codes(router) or all(
                not c.startswith(invente) for c in _codes(router)
            ), f"{router} : code non reconcile {invente}"
