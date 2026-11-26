"""033 seed RBAC magasin (batch 21) : role CHEF_MAGASIN + grants magasinier etendus.

Contexte : le routeur /magasin-avance (43 endpoints) est passe de la simple
authentification au droit granulaire ``require_perm``. Pour que les roles metier
reels restent fonctionnels apres cette conversion, le catalogue a ete complete
(MAGASINIER couvre desormais toute l'execution magasin sans validation ;
CHEF_MAGASIN, nouveau, porte les approvals et l'export).

Cette migration applique ces changements sur les bases DEJA SEEDEES (ou 020 a
tourne avec l'ancien catalogue) :
  - codes ``permissions`` manquants : inseres (catalogue + grants, y compris
    le wildcard ``magasin.*.*``) ;
  - role ``CHEF_MAGASIN`` : cree s'il est absent, avec ses liens ;
  - liens ``role_permissions`` supplementaires pour ``MAGASINIER`` : ajoutes.

Purement ADDITIVE : aucun lien, aucun role, aucune ligne existante n'est
supprime (retirer un droit se fera par decision explicite, pas par effet de
migration). downgrade() = pass, convention 027.
"""
from alembic import op
import sqlalchemy as sa
import json

revision = "033_rbac_magasin_grants"
down_revision = "032_add_maintenance_tenant_scope"
branch_labels = None
depends_on = None


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

# Roles touches par le batch 21 ; les codes source restent le catalogue
# (single source of truth) -- cette liste ne fait que selectionner.
ROLES_CIBLES = ("MAGASINIER", "CHEF_MAGASIN")


def _tables():
    return set(sa.inspect(op.get_bind()).get_table_names())


def upgrade():
    tables = _tables()
    if not {"permissions", "roles", "role_permissions"} <= tables:
        # Base partielle : rien a seeder sans les tables RBAC de 020 ;
        # passer en silence serait une fausse assurance. On leve le doute.
        raise RuntimeError(
            "033 : tables RBAC (permissions/roles/role_permissions) absentes ; "
            "la migration 020 doit avoir ete appliquee avant."
        )

    from app.core.permission_catalog import ROLE_GRANTS, iter_permission_rows

    bind = op.get_bind()

    def _existing_codes():
        res = bind.execute(sa.text("SELECT code FROM permissions WHERE code IS NOT NULL"))
        return {r[0] for r in res}

    present = _existing_codes()

    def _insert_perm(code, domaine=None, module=None, sub=None, action=None):
        bind.execute(
            PERMISSIONS_TBL.insert().values(
                code=code, name=code, description=None, domaine=domaine,
                module=module, sub_module=sub, action=action, resource=sub,
            )
        )
        present.add(code)

    # 1. Tous les codes du catalogue concret.
    for code, domaine, module, sub, action in iter_permission_rows():
        if code not in present:
            _insert_perm(code, domaine, module, sub, action)

    # 2. Codes references par les grants (wildcards "magasin.*.*" etc.).
    grants_by_role = {}
    for nom, niveau, description, codes in ROLE_GRANTS:
        grants_by_role[nom] = (niveau, description, codes)
        for code in codes:
            if code in present:
                continue
            if code.count(".") == 2:
                module, sub, action = code.split(".")
            else:
                module, sub, action = code, "*", "*"
            _insert_perm(code, None, module, sub, action)

    def _role_id(name):
        res = bind.execute(sa.text("SELECT id FROM roles WHERE name = :n"), {"n": name}).first()
        return res[0] if res else None

    def _perm_id(code):
        res = bind.execute(sa.text("SELECT id FROM permissions WHERE code = :c"), {"c": code}).first()
        return res[0] if res else None

    for nom in ROLES_CIBLES:
        niveau, description, codes = grants_by_role[nom]
        rid = _role_id(nom)
        if rid is None:
            mods = sorted({c.split(".")[0] for c in codes})
            bind.execute(
                ROLES_TBL.insert().values(
                    name=nom, description=description, level=niveau, company_id=None,
                    modules_allowed=json.dumps(mods), is_active=True, is_system=True,
                )
            )
            rid = _role_id(nom)
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


def downgrade():
    # Additive par convention : on ne retrace pas quels liens existaient
    # avant 033, et une suppression approximative serait destructive.
    pass
