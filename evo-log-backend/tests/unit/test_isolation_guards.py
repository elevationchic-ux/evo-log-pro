"""Tests du harnais d'isolation pytest (batch 14).

Zero-Mock applique aux TESTS : la fixture `client` authentifie tout par defaut
(faux super-utilisateur) et surcharge `get_db` vers une base memoire. Ces tests
verrouillent le contrat pour qu'une future modif de conftest ne puisse plus
casser silencieusement l'isolation :

1. `get_db` doit rester surcharge pendant TOUTE la duree d'un test — meme dans
   la fixture `unauthenticated`. Un `app.dependency_overrides.clear()` en cours
   de test reinjecterait l'engine reel de l'application, donc la base de dev
   `kamlog_erp.db` (vue reelle : le fichier etait mutale par les runs avant le
   garde-fou DATABASE_URL).
2. L'engine applicatif ne doit JAMAIS pointer sur le fichier sqlite de dev.
3. Un test d'auth anonyme doit utiliser `unauthenticated`, pas `clear()`.
"""
import pytest
from sqlalchemy.engine import Engine

from app.core.config import settings
from app.core.database import get_db
from app.core.security import get_current_user
from app.main import app


# --------------------------------------------------------------------------- #
# 1. Contrat des fixtures d'authentification
# --------------------------------------------------------------------------- #

def test_client_fixture_surcharge_db_et_identite(client):
    """`client` = base memoire + faux super-utilisateur : les DEUX overrides."""
    assert get_db in app.dependency_overrides
    assert get_current_user in app.dependency_overrides


def test_unauthenticated_conserve_override_get_db(unauthenticated):
    """Le retire-identite NE DOIT jamais emporter l'override get_db.

    C'est exactement la classe de bug du batch 14 : `dependency_overrides
    .clear()` en milieu de test supprimait get_db en meme temps que
    get_current_user, et les requetes suivantes lisaient/écrivaient la vraie
    base de developpement sans que personne ne le voie (les assertions
    401/403 passaient, donc la suite restait verte).
    """
    assert get_current_user not in app.dependency_overrides, (
        "unauthenticated doit retirer l'identite surchargee"
    )
    assert get_db in app.dependency_overrides, (
        "get_db doit SURVIVRE au retrait de l'identite : sans lui, la route "
        "utilise l'engine reel de l'app (kamlog_erp.db en dev)"
    )
    # Comportement attendu : route protegee -> refus anonyme, pas un 200
    # de super-utilisateur ni un 404 lu dans la base de dev.
    resp = unauthenticated.get("/api/v1/purchase/requisitions")
    assert resp.status_code in (401, 403)
    # get_db est toujours la apres la requete.
    assert get_db in app.dependency_overrides


# --------------------------------------------------------------------------- #
# 2. Garde-fou DATABASE_URL
# --------------------------------------------------------------------------- #

def test_engine_applicatif_ne_pointe_pas_sur_la_base_de_dev():
    """L'engine global de l'app ne doit pas etre le sqlite `kamlog_erp.db`.

    Le defaut de `Settings.DATABASE_URL` est `sqlite:///./kamlog_erp.db`. Le
    conftest force une valeur memoire via `os.environ.setdefault` avant
    l'import de l'app ; si quelqu'un retire ce garde-fou, ce test rouge.
    """
    from app.core.database import engine as app_engine

    assert "kamlog_erp.db" not in settings.DATABASE_URL, (
        "DATABASE_URL pointe sur la VRAIE base de dev : le garde-fou du "
        "conftest a disparu (voir tests/conftest.py, 'Guard Zero-Pollution')"
    )
    assert "kamlog_erp.db" not in str(app_engine.url), (
        "l'engine applicatif a ete construit sur le fichier de dev : toute "
        "requete perdue hors override get_db corromprait cette base"
    )
