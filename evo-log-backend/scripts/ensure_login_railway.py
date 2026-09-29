"""Auto-reparation de la base courante + garantie d'identifiants de connexion.

DEUX problems couverts par ce script (les deux font la MEME chose que
/auth/login, sur la MEME base, donc ils la reparent ou la revelent) :

1) SELECT_USERS_CASSE : la table `users` peut manquer une colonne declaree par
   le modele ORM (les colonnes ajoutees apres le schema initial ne viennent que
   des migrations de parite dynamiques 014/027/028 ; si l'une n'a pas ete posee
   proprement sur PostgreSQL, le `SELECT users ...` de login leve une erreur
   pour TOUT le monde, y compris un identifiant inexistant, alors que /health
   (SELECT 1) reste vert). Ce script refait la parite de `users` lui-meme.

2) COMPTES_ABSENTS : le seed CADC de la migration 025 est dans un SAVEPOINT qui
   avale tout echec en silence (choix : ne jamais bloquer un deploy). Le compte
   peut donc manquer en prod. Ce script le cree/repare.

Proprietes :
  - IDEMPOTENT : relance sans effet de bord (CREATE ... IF NOT EXISTS, ADD
    COLUMN seulement si absente, UPDATE des comptes).
  - NON DESTRUCTIF : ne droppe/modifie aucune donnee existante, ne touche pas
    aux autres comptes, n'ajoute que des colonnes NULLABLES.
  - MOTEUR-AGNOSTIQUE : SQLite (dev) et PostgreSQL (prod).
  - HORS ALEMBIC : ne cree AUCUNE tete de migration, donc IMPOSSIBLE de
    declencher un "multiple heads" / crash-loop. C'est le levier sur, meme si
    d'autres migrations sont poussees en parallele.

Usage (Production Railway, depuis le service backend) :
    railway run python scripts/ensure_login_railway.py
  ou dans le shell du conteneur :
    python scripts/ensure_login_railway.py
  simple diagnostic sans ecriture :
    python scripts/ensure_login_railway.py --check
DATABASE_URL doit pointer sur la base cible (deja requis par l'app).
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from sqlalchemy import inspect as sa_inspect, text  # noqa: E402

from app.core.database import Base, SessionLocal, engine  # noqa: E402
from app.core.security import get_password_hash  # noqa: E402
from app.models.user import User, Role  # noqa: E402
from app.models.tenant import Company  # noqa: E402

import app.models  # noqa: E402,F401 - enregistre TOUTES les tables du Base.metadata


# Comptes garanties : (username, email, mot_de_passe, est_superuser, role_level)
# Credentials alignes sur la migration 025 pour rester coherents.
ACCOUNTS = [
    ("CADC TECH", "cadctechnique@evolog.cm", "@C2A0D2C6", True, 0),
    ("supadmin", "supadmin@evo-log.cm", "supadmin123", True, 0),
    ("admin", "admin@evolog.cm", "admin123", False, 1),
]


# --------------------------------------------------------------------------- #
# 1) Parite de la table `users` (colonnes du modele) + tables manquantes
# --------------------------------------------------------------------------- #
def heal_schema(write: bool) -> None:
    insp = sa_inspect(engine)

    # 1a) Tables totalement absentes -> les creer (checkfirst = IF NOT EXISTS).
    #     create_all n'ALTERE pas les tables existantes, donc c'est sur.
    if write:
        Base.metadata.create_all(bind=engine, checkfirst=True)

    # 1b) Colonnes du modele absentes de la table `users` existante.
    if not insp.has_table("users"):
        print("  [!] table `users` absente apres create_all -- verifie le dump")
        return
    existantes = {c["name"] for c in insp.get_columns("users")}
    attendues = {c.name: c for c in User.__table__.columns}
    manquantes = [nom for nom in attendues if nom not in existantes]

    if not manquantes:
        print(f"  [ok] table `users` complete ({len(existantes)} colonnes)")
    else:
        print(f"  [!] {len(manquantes)} colonne(s) `users` manquante(s) : {manquantes}")
        for nom in manquantes:
            col = attendues[nom]
            sqltype = col.type.compile(dialect=engine.dialect)
            ddl = f'ALTER TABLE users ADD COLUMN "{nom}" {sqltype}'
            if write:
                with engine.begin() as conn:
                    conn.execute(text(ddl))
                print(f"      + ajoute (nullable) : {nom} {sqltype}")
            else:
                print(f"      [check] aurait ajoute : {nom} {sqltype}")


# --------------------------------------------------------------------------- #
# 2) Comptes de secours
# --------------------------------------------------------------------------- #
def _ensure_super_role(db):
    role = db.query(Role).filter(Role.name == "superadmin").first()
    if not role:
        role = Role(name="superadmin", description="Super Administrateur SaaS", level=0)
        db.add(role)
        db.flush()
    return role


def _default_company(db):
    return db.query(Company).order_by(Company.id).first()


def ensure_accounts(db) -> None:
    super_role = _ensure_super_role(db)
    company = _default_company(db)
    for username, email, password, is_superuser, level in ACCOUNTS:
        user = (
            db.query(User)
            .filter((User.username == username) | (User.email == email))
            .first()
        )
        if user is None:
            user = User(username=username, email=email)
            db.add(user)
        user.hashed_password = get_password_hash(password)
        user.is_active = True
        user.is_superuser = is_superuser
        user.role_level = level
        user.must_change_password = False
        if company is not None and user.company_id is None:
            user.company_id = company.id
        if is_superuser and super_role not in (user.roles or []):
            user.roles = list(user.roles or []) + [super_role]
        db.flush()
        print(f"  [ok] {username:10s} | {email:28s} | mdp: {password}")
    db.commit()


def verify_login_select(db) -> None:
    """Rejoue EXACTEMENT le SELECT de /auth/login pour le premier compte."""
    username = ACCOUNTS[0][0]
    row = db.query(User).filter(User.username == username).first()
    print(f"  [verify] SELECT users WHERE username={username!r} -> "
          f"{'TROUVE id=' + str(row.id) if row else 'aucun (normal si --check sans ecriture)'}")


def main() -> int:
    write = "--check" not in sys.argv
    db = SessionLocal()
    try:
        print("== 1) Parite schema (tables + colonnes `users`) ==")
        heal_schema(write)
        if not write:
            print("\n(--check : aucune ecriture effectuee)")
            verify_login_select(db)
            return 0
        print("\n== 2) Comptes de connexion garantis / repares ==")
        ensure_accounts(db)
        print("\n== 3) Verification du SELECT de login ==")
        verify_login_select(db)
        print("\nTermine. Reessaie de te connecter (username OU email).")
        return 0
    except Exception as exc:  # noqa: BLE001 - trace operateur volontaire
        # Traceback COMPLET : ce script execute le MEME `SELECT users` que
        # /auth/login. Un echec ici expose l'erreur PostgreSQL reelle sous le
        # 500 de login (message tronque / colonne / contrainte fautive).
        import traceback
        print(f"\nECHEC : {type(exc).__name__}: {exc}")
        traceback.print_exc()
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    raise main()
