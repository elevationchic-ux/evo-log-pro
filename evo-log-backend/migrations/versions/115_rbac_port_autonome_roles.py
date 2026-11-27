"""115 : materialise les roles transverses de l'organigramme port autonome.

Trois roles metier ajoutes a ROLE_GRANTS (catalogue = source de verite) :
  - JURISTE (niveau 3) : contrats, contentieux et echeances OHADA.
  - SECRETAIRE (niveau 3) : demandes de conges, pointage et echeances.
  - CHAUFFEUR (niveau 3) : lecture de ses missions, saisie des POD et
    suivi GPS (la regle d'atterrissage /chauffeur existait deja cote
    frontend sans role backend correspondant).

Cette migration reproduit le mecanisme 107 : reconcilier le catalogue vers
la base deja migree, de maniere additive et idempotente :
  1. toute ligne permission absente du catalogue est creee ;
  2. tout code de grant (wildcards) absent est cree comme ligne de reference ;
  3. tout role ROLE_GRANTS absent est cree (company_id NULL, systeme) ;
  4. tout lien role->permission declare mais absent est ajoute.

Additif et idempotent : chaque boucle saute l'existant ; jamais de sur-
grantation au-dela de ROLE_GRANTS, jamais de destruction.
"""
from alembic import op
import sqlalchemy as sa

revision = "115_rbac_port_autonome_roles"
down_revision = "114_juridique"
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


def _tables():
    return set(sa.inspect(op.get_bind()).get_table_names())


def upgrade():
    tables = _tables()
    if not {"permissions", "roles", "role_permissions"} <= tables:
        raise RuntimeError(
            "115 : tables RBAC (permissions/roles/role_permissions) absentes ; "
            "la migration 020 doit avoir ete appliquee avant."
        )

    from app.core.permission_catalog import ROLE_GRANTS, iter_permission_rows

    bind = op.get_bind()

    present = {
        r[0]
        for r in bind.execute(
            sa.text("SELECT code FROM permissions WHERE code IS NOT NULL")
        )
    }

    def _insert_perm(code, domaine=None, module=None, sub=None, action=None):
        bind.execute(
            PERMISSIONS_TBL.insert().values(
                code=code, name=code, description=None, domaine=domaine,
                module=module, sub_module=sub, action=action, resource=sub,
            )
        )
        present.add(code)

    # 1. Reflet du catalogue : toute ligne declaree mais absente est creee.
    for code, domaine, module, sub, action in iter_permission_rows():
        if code not in present:
            _insert_perm(code, domaine, module, sub, action)

    # 2. Codes de grant (wildcards) non issus directement du catalogue.
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
        res = bind.execute(
            sa.text("SELECT id FROM roles WHERE name = :n"), {"n": name}
        ).first()
        return res[0] if res else None

    def _perm_id(code):
        res = bind.execute(
            sa.text("SELECT id FROM permissions WHERE code = :c"), {"c": code}
        ).first()
        return res[0] if res else None

    # 3 + 4. Roles metier systeme (cree si absent) + liens manquants.
    import json

    for nom, _niveau, _description, codes in ROLE_GRANTS:
        rid = _role_id(nom)
        if rid is None:
            niveau, description, _codes = grants_by_role[nom]
            mods = sorted({c.split(".")[0] for c in codes})
            bind.execute(
                ROLES_TBL.insert().values(
                    name=nom, description=description, level=niveau, company_id=None,
                    modules_allowed=json.dumps(mods), is_active=True, is_system=True,
                )
            )
            rid = _role_id(nom)
        existing_links = {
            r[0]
            for r in bind.execute(
                sa.text("SELECT permission_id FROM role_permissions WHERE role_id = :r"),
                {"r": rid},
            )
        }
        for code in codes:
            pid = _perm_id(code)
            if pid is not None and pid not in existing_links:
                bind.execute(
                    ROLE_PERM_TBL.insert().values(role_id=rid, permission_id=pid)
                )
                existing_links.add(pid)


def downgrade():
    # Additif par convention : on ne retrace pas l'etat anterieur ;
    # une destruction des droits serait destructive des liens.
    pass
