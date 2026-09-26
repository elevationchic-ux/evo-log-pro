"""025 Console Super-Admin CADC : colonnes + seed compte CADC.

Aports (tous idempotents, gardes par introspection) :
  1. ``users``             : ajoute matricule / job_title (identite employe
     distincte du role/casquette, cf. modele Utilisateur != Role). Index sur
     matricule.
  2. ``subscription_plans``: ajoute max_modules (Integer nullable = illimite)
     qui verrouille le nombre de modules allouables a une entreprise une fois
     le plan cree.
  3. Seed role ``CADC`` (level 0, is_system) + utilisateur ``CADC TECH``
     (super-admin plateforme, company_id NULL, must_change_password FALSE).
     Le mot de passe n'est JAMAIS ecrit en clair : seul le hash bcrypt produit
     par ``app.core.security.get_password_hash`` est persiste. Idempotent :
     skip si le username existe deja.

Rejouable sur base vierge et sur base de dev drift. Downgrade volontairement
neutre (on ne detruit pas le compte ni les donnees metier).
"""
from alembic import op
import sqlalchemy as sa

revision = "025_seed_superadmin_cadc"
down_revision = "024_add_chaine_documentaire_links"
branch_labels = None
depends_on = None


# Mot de passe initial du compte CADC (hash uniquement persiste).
CADC_USERNAME = "CADC TECH"
CADC_EMAIL = "cadctechnique@evolog.cm"
CADC_FULL_NAME = "Super Administrateur CADC"
CADC_PASSWORD = "@C2A0D2C6"


def _tables():
    return set(sa.inspect(op.get_bind()).get_table_names())


def _columns(table):
    insp = sa.inspect(op.get_bind())
    if table not in set(insp.get_table_names()):
        return set()
    return {c["name"] for c in insp.get_columns(table)}


def _has_index(table, name):
    insp = sa.inspect(op.get_bind())
    try:
        return any(ix["name"] == name for ix in insp.get_indexes(table))
    except Exception:  # noqa: BLE001
        return False


def _ensure_columns():
    # users.matricule / users.job_title
    cols = _columns("users")
    add = []
    if "matricule" not in cols:
        add.append(sa.Column("matricule", sa.String(length=50), nullable=True))
    if "job_title" not in cols:
        add.append(sa.Column("job_title", sa.String(length=100), nullable=True))
    if add:
        with op.batch_alter_table("users") as batch:
            for c in add:
                batch.add_column(c)
    if "matricule" in _columns("users") and not _has_index("users", "ix_users_matricule"):
        try:
            op.create_index("ix_users_matricule", "users", ["matricule"], unique=False)
        except Exception:  # noqa: BLE001 - index deja present sur certaines bases
            pass

    # subscription_plans.max_modules
    pcols = _columns("subscription_plans")
    if "max_modules" not in pcols:
        with op.batch_alter_table("subscription_plans") as batch:
            batch.add_column(sa.Column("max_modules", sa.Integer(), nullable=True))


def _seed_cadc():
    """Creer le role CADC + le compte CADC TECH et les lier (idempotent)."""
    from app.core.security import get_password_hash

    bind = op.get_bind()
    tables = _tables()
    if "users" not in tables or "roles" not in tables:
        return

    # 1. Role systeme CADC (level 0).
    role_id = bind.execute(
        sa.text("SELECT id FROM roles WHERE name = :n"), {"n": "CADC"}
    ).scalar()
    if role_id is None:
        bind.execute(
            sa.text(
                "INSERT INTO roles (name, description, level, company_id, "
                "modules_allowed, is_active, is_system) VALUES (:n, :d, 0, NULL, "
                "NULL, 1, 1)"
            ),
            {"n": "CADC", "d": "Super Administrateur plateforme CADC"},
        )
        role_id = bind.execute(
            sa.text("SELECT id FROM roles WHERE name = :n"), {"n": "CADC"}
        ).scalar()

    # 2. Utilisateur CADC TECH (super-admin, hors entreprise).
    existing = bind.execute(
        sa.text("SELECT id FROM users WHERE username = :u"), {"u": CADC_USERNAME}
    ).first()
    if existing is not None:
        user_id = existing[0]
    else:
        # Email de repli si CADC_EMAIL est deja pris par un autre compte.
        email_taken = bind.execute(
            sa.text("SELECT 1 FROM users WHERE email = :e"), {"e": CADC_EMAIL}
        ).first()
        email = None if email_taken else CADC_EMAIL
        bind.execute(
            sa.text(
                "INSERT INTO users (username, email, hashed_password, full_name, "
                "is_active, is_superuser, must_change_password, role_level, "
                "company_id, language, timezone, two_factor_enabled) VALUES "
                "(:u, :e, :h, :f, 1, 1, 0, 0, NULL, 'fr', 'Africa/Douala', 0)"
            ),
            {
                "u": CADC_USERNAME,
                "e": email,
                "h": get_password_hash(CADC_PASSWORD),
                "f": CADC_FULL_NAME,
            },
        )
        user_id = bind.execute(
            sa.text("SELECT id FROM users WHERE username = :u"), {"u": CADC_USERNAME}
        ).scalar()

    # 3. Lien user_roles (ignore si deja present).
    if user_id is not None and role_id is not None and "user_roles" in tables:
        link = bind.execute(
            sa.text(
                "SELECT 1 FROM user_roles WHERE user_id = :u AND role_id = :r"
            ),
            {"u": user_id, "r": role_id},
        ).first()
        if link is None:
            bind.execute(
                sa.text("INSERT INTO user_roles (user_id, role_id) VALUES (:u, :r)"),
                {"u": user_id, "r": role_id},
            )


def upgrade():
    _ensure_columns()
    try:
        _seed_cadc()
    except Exception as exc:  # noqa: BLE001 - le seed ne doit jamais bloquer un deploiement
        import logging
        logging.getLogger("alembic").warning("Seed CADC 025 ignore : %s", exc)


def downgrade():
    # On ne supprime ni le compte CADC ni les colonnes (donnees metier /
    # non-regression). Un drop complet est volontairement evite.
    pass
