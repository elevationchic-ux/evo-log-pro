"""Garantit un jeu d'identifiants de connexion FONCTIONNELS sur la base courante.

Pourquoi ce script existe : le seed CADC de la migration 025 est enveloppe dans
un SAVEPOINT qui AVALE silencieusement tout echec (choix deliberate : ne jamais
bloquer un deploiement pour un compte). Resultat, sur une base PostgreSQL de
production, le compte CADC peut manquer sans que rien ne le crie, et l'equipe
reste sans acces. Ce script est la reponse operationnelle : il cree (ou
repare) les comptes de secours, met leurs mots de passe a des valeurs connues,
les active, et affiche exactement ce qu'il faut taper dans le formulaire.

Proprietes :
  - IDEMPOTENT : relance sans effet de bord (update, pas de duplicate).
  - NON DESTRUCTIF : ne droppe rien, ne touche pas aux autres comptes.
  - MOTEUR-AGNOSTIQUE : passe sur SQLite (dev) comme PostgreSQL (prod), il ne
    fait que de l'ORM.

Usage (Production Railway, depuis le service backend) :
    railway run python scripts/ensure_login_railway.py
  ou dans le shell du conteneur :
    python scripts/ensure_login_railway.py
DATABASE_URL doit pointer sur la base cible (il est deja requis par l'app).
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from app.core.database import SessionLocal  # noqa: E402
from app.core.security import get_password_hash  # noqa: E402
from app.models.user import User, Role  # noqa: E402
from app.models.tenant import Company  # noqa: E402


# Comptes garanties : (username, email, mot_de_passe, est_superuser, role_level)
# Les credentials CADC sont alignes sur la migration 025 pour rester coherents.
ACCOUNTS = [
    ("CADC TECH", "cadctechnique@evolog.cm", "@C2A0D2C6", True, 0),
    ("supadmin", "supadmin@evo-log.cm", "supadmin123", True, 0),
    ("admin", "admin@evolog.cm", "admin123", False, 1),
]


def _ensure_super_role(db):
    """Le role 'superadmin' doit exister pour que la casquette soit lisible."""
    role = db.query(Role).filter(Role.name == "superadmin").first()
    if not role:
        role = Role(name="superadmin", description="Super Administrateur SaaS", level=0)
        db.add(role)
        db.flush()
    return role


def _default_company(db):
    return db.query(Company).order_by(Company.id).first()


def ensure(db) -> None:
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
        # Ne jamais forcer le gate de changement de mot de passe sur ces comptes
        # de secours : l'objectif est de se connecter immediatement.
        user.must_change_password = False
        if company is not None and user.company_id is None:
            user.company_id = company.id
        # Casquette superadmin pour les comptes superusers (sinon modules vides).
        if is_superuser and super_role not in (user.roles or []):
            user.roles = list(user.roles or []) + [super_role]
        db.flush()
        print(f"  [ok] {username:10s} | {email:28s} | mdp: {password}")

    db.commit()


def main() -> int:
    db = SessionLocal()
    try:
        print("Comptes de connexion garantis / repare :")
        ensure(db)
        print("\nOuvrir le frontend et se connecter avec l'un de ces comptes.")
        print("(Le login accepte le username OU l'email.)")
        return 0
    except Exception as exc:  # noqa: BLE001 - script operateur, trace utile
        print(f"ECHEC : {type(exc).__name__}: {exc}")
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
