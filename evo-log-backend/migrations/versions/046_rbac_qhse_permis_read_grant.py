"""046 : droit RBAC « qhse.permis.read » pour le chef d'exploitation.

Contexte : le Batch 4 a transforme les permis de travail de QHSE en acte reel
(POST /permis-travail persiste, GET /permis-travail liste, signature par
utilisateurs authentifies). Le router exige desormais
``require_perm("qhse.permis.read")`` pour la consultation du registre.

Le catalogue (ROLE_GRANTS) declare ce code pour CHEF_EXPLOITATION, mais le
catalogue n'est pas la source d'execution : les liens role->permission sont
materialises UNIQUEMENT par les migrations. Sur une base deja migree (cas
Railway), CHEF_EXPLOITATION est un role a liste explicite (qhse.accident.*,
qhse.permis.create, qhse.imdg.read, ...) SANS wildcard ; sans lien explicite
vers « qhse.permis.read », le chef qui cree un permis ne pourrait pas le
relire (403). Les roles QHSE (« qhse.*.* ») et AUDITEUR (« qhse.*.read ») sont
couverts par leur wildcard a l'execution : aucun lien nouveau ne leur faut.

Cette migration est strictement additive et reprend le corps pilote-par-catalogue
de 042 (identique a 033/034/035/036/039) :

  * elle insere toute ligne « permissions » du catalogue absente (ici
    qhse.permis.read) ;
  * elle cree les liens role->permission manquants UNIQUEMENT pour les roles
    cibles, a partir de leur propre liste ROLE_GRANTS (donc rien n'est durci
    ici, et aucun role n'est cree : le perimetre CHEF_EXPLOITATION existe deja
    depuis les migrations prece dentes).

Garde explicite : tables RBAC absentes -> RuntimeError nommant la precondition
(020), jamais un no-op silencieux.
"""
from alembic import op
import sqlalchemy as sa
import json

revision = "046_rbac_qhse_permis_read_grant"
down_revision = "045_add_batch4_tables"
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

# Seul role a liste explicite portant « qhse.permis.read » dans le catalogue.
# QHSE et AUDITEUR sont couverts par leurs wildcards a l'execution : pas besoin
# de lien explicite, on ne les inclut donc pas pour eviter toute sur-grantation.
ROLES_CIBLES = ("CHEF_EXPLOITATION",)


def _tables():
    return set(sa.inspect(op.get_bind()).get_table_names())


def upgrade():
    tables = _tables()
    if not {"permissions", "roles", "role_permissions"} <= tables:
        raise RuntimeError(
            "046 : tables RBAC (permissions/roles/role_permissions) absentes ; "
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

    # 1. Toute ligne du catalogue absente est creee (dont qhse.permis.read).
    for code, domaine, module, sub, action in iter_permission_rows():
        if code not in present:
            _insert_perm(code, domaine, module, sub, action)

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

    # 2. Liens role->permission manquants pour les roles cibles seulement.
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
    # Additive par convention : on ne retrace pas l'etat anterieur, et une
    # suppression approximative de droits serait destructive.
    pass
