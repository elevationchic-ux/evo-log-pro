"""020 RBAC granulaire : permissions, accréditations, acces partages, seed.

Aports (tous idempotents, gardes par introspection) :
  1. ``roles``      : ajoute level / company_id / is_system si absents (dérive
     des bases de dev creees avant ces colonnes).
  2. ``permissions``: ajoute code / domaine / module / sub_module + index unique
     sur code (representation canonique module.sous_module.action).
  3. ``accreditations`` et ``shared_access`` : tables creees si absentes.
  4. Seed : lignes ``permissions`` (catalogue + codes des grants), roles metier
     (CHEF_COMPTABLE, COMPTABLE, DIRECTEUR_FINANCIER, ...) et liens
     ``role_permissions``. Toujours safe a rejouer (skip si deja presents).

Rejouable sur base vierge (apres 020_add_gap_bridge_tables) et sur kamlog_erp.db dev drift.
"""
from alembic import op
import sqlalchemy as sa

revision = "020_rbac_granulaire_accreditations"
down_revision = "020_add_gap_bridge_tables"
branch_labels = None
depends_on = None


# ── Helpers d'introspection ───────────────────────────────────────────────────
def _tables():
    return set(sa.inspect(op.get_bind()).get_table_names())


def _columns(table):
    insp = sa.inspect(op.get_bind())
    if table not in set(insp.get_table_names()):
        return set()
    return {c["name"] for c in insp.get_columns(table)}


def _has_index(table, name):
    insp = sa.inspect(op.get_bind())
    return any(ix["name"] == name for ix in insp.get_indexes(table))


# Tables/colonnes cibles definies sans ORM (evite les collisions de registry).
PERMISSIONS_TBL = sa.table(
    "permissions",
    sa.column("id", sa.Integer),
    sa.column("code", sa.String),
    sa.column("name", sa.String),
    sa.column("description", sa.String),
    sa.column("domaine", sa.String),
    sa.column("module", sa.String),
    sa.column("sub_module", sa.String),
    sa.column("action", sa.String),
    sa.column("resource", sa.String),
)
ROLES_TBL = sa.table(
    "roles",
    sa.column("id", sa.Integer),
    sa.column("name", sa.String),
    sa.column("description", sa.String),
    sa.column("level", sa.Integer),
    sa.column("company_id", sa.Integer),
    sa.column("modules_allowed", sa.Text),
    sa.column("is_active", sa.Boolean),
    sa.column("is_system", sa.Boolean),
)
ROLE_PERM_TBL = sa.table(
    "role_permissions",
    sa.column("role_id", sa.Integer),
    sa.column("permission_id", sa.Integer),
)


def _ensure_roles_columns():
    cols = _columns("roles")
    add = []
    if "level" not in cols:
        add.append(sa.Column("level", sa.Integer(), nullable=True, server_default="3"))
    if "company_id" not in cols:
        add.append(sa.Column("company_id", sa.Integer(), nullable=True))
    if "is_system" not in cols:
        add.append(sa.Column("is_system", sa.Boolean(), nullable=True, server_default=sa.false()))
    if add:
        with op.batch_alter_table("roles") as batch:
            for c in add:
                batch.add_column(c)


def _ensure_permissions_columns():
    cols = _columns("permissions")
    add = []
    if "code" not in cols:
        add.append(sa.Column("code", sa.String(length=150), nullable=True))
    if "domaine" not in cols:
        add.append(sa.Column("domaine", sa.String(length=50), nullable=True))
    if "module" not in cols:
        add.append(sa.Column("module", sa.String(length=50), nullable=True))
    if "sub_module" not in cols:
        add.append(sa.Column("sub_module", sa.String(length=80), nullable=True))
    if add:
        with op.batch_alter_table("permissions") as batch:
            for c in add:
                batch.add_column(c)
    # name doit devenir nullable large : on ne touche pas a la contrainte
    # existante (SQLite ne permet pas d'alter simple) ; le seed renseigne name.
    if not _has_index("permissions", "ix_permissions_code"):
        try:
            op.create_index("ix_permissions_code", "permissions", ["code"], unique=False)
        except Exception:
            pass


def _create_new_tables():
    tables = _tables()
    if "accreditations" not in tables:
        op.create_table(
            "accreditations",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
            sa.Column("company_id", sa.Integer(), sa.ForeignKey("companies.id"), nullable=True),
            sa.Column("code", sa.String(length=80), nullable=True),
            sa.Column("libelle", sa.String(length=150), nullable=False),
            sa.Column("type", sa.String(length=20), nullable=False, server_default="permission"),
            sa.Column("permission_code", sa.String(length=150), nullable=True),
            sa.Column("perimetre_utilisateurs", sa.Text(), nullable=True),
            sa.Column("module", sa.String(length=50), nullable=True),
            sa.Column("date_debut", sa.Date(), nullable=True),
            sa.Column("date_fin", sa.Date(), nullable=True),
            sa.Column("statut", sa.String(length=20), nullable=False, server_default="actif"),
            sa.Column("motif", sa.Text(), nullable=True),
            sa.Column("octroye_par", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        )
        op.create_index("ix_accreditations_user_id", "accreditations", ["user_id"])
        op.create_index("ix_accreditations_code", "accreditations", ["code"], unique=True)
    if "shared_access" not in tables:
        op.create_table(
            "shared_access",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("company_id", sa.Integer(), sa.ForeignKey("companies.id"), nullable=False),
            sa.Column("module_key", sa.String(length=80), nullable=False),
            sa.Column("libelle", sa.String(length=150), nullable=True),
            sa.Column("autorise_tous_utilisateurs", sa.Boolean(), nullable=False, server_default=sa.true()),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "module_key", name="uq_shared_access_company_module"),
        )
        op.create_index("ix_shared_access_company_id", "shared_access", ["company_id"])


def _seed_permissions_and_roles():
    """Insere le catalogue de permissions + les roles metier (idempotent)."""
    from app.core.permission_catalog import iter_permission_rows, ROLE_GRANTS

    bind = op.get_bind()

    # Codes a creer : catalogue concret + tous les codes references par grants.
    rows = []
    for code, domaine, module, sub, action in iter_permission_rows():
        rows.append((code, domaine, module, sub, action))
    grant_codes = []
    for _nom, _lvl, _desc, codes in ROLE_GRANTS:
        for c in codes:
            grant_codes.append(c)

    def _existing_codes():
        res = bind.execute(sa.text("SELECT code FROM permissions WHERE code IS NOT NULL"))
        return {r[0] for r in res}

    present = _existing_codes()

    def _insert_perm(code, domaine, module, sub, action):
        bind.execute(
            PERMISSIONS_TBL.insert().values(
                code=code, name=code, description=None, domaine=domaine,
                module=module, sub_module=sub, action=action, resource=sub,
            )
        )

    for code, domaine, module, sub, action in rows:
        if code not in present:
            _insert_perm(code, domaine, module, sub, action)
            present.add(code)

    # Codes de grant wildcard (module.*.action / *.*) non issus du catalogue.
    for code in grant_codes:
        if code in present:
            continue
        module, sub, action = code.split(".") if code.count(".") == 2 else (code, "*", "*")
        _insert_perm(code, None, module, sub, action)
        present.add(code)

    def _role_id(name):
        res = bind.execute(sa.text("SELECT id FROM roles WHERE name = :n"), {"n": name}).first()
        return res[0] if res else None

    def _perm_id(code):
        res = bind.execute(sa.text("SELECT id FROM permissions WHERE code = :c"), {"c": code}).first()
        return res[0] if res else None

    import json
    for nom, niveau, description, codes in ROLE_GRANTS:
        rid = _role_id(nom)
        if rid is None:
            # modules_allowed derive des codes de premier niveau du grant.
            mods = sorted({c.split(".")[0] for c in codes})
            bind.execute(
                ROLES_TBL.insert().values(
                    name=nom, description=description, level=niveau, company_id=None,
                    modules_allowed=json.dumps(mods), is_active=True, is_system=True,
                )
            )
            rid = _role_id(nom)
        # liens role -> permissions (skip existants)
        existing_links = {
            r[0] for r in bind.execute(
                sa.text("SELECT permission_id FROM role_permissions WHERE role_id = :r"), {"r": rid}
            )
        }
        for code in codes:
            pid = _perm_id(code)
            if pid is not None and pid not in existing_links:
                bind.execute(ROLE_PERM_TBL.insert().values(role_id=rid, permission_id=pid))
                existing_links.add(pid)


def upgrade():
    _ensure_roles_columns()
    _ensure_permissions_columns()
    _create_new_tables()
    try:
        _seed_permissions_and_roles()
    except Exception as exc:  # noqa: BLE001 - le seed ne doit jamais bloquer un deploiement
        import logging
        logging.getLogger("alembic").warning("Seed RBAC 020 ignore : %s", exc)


def downgrade():
    # On ne supprime PAS les tables/colonnes ajoutees (donnees metier).
    # Un drop complet est volontairement evite pour ne pas detruire de donnees.
    pass
