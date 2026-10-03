"""036 seed RBAC qhse (batch 24) : module qhse complet + role QHSE operant.

Contexte : /api/v1/qhse (38 endpoints auth-seuls + 3 endpoints PUBLICS sans
aucune authentification) n'avait AUCUN code dans le catalogue — le role QHSE
du GRANT_TABLE ne couvrait que gouvernance/transport/parc. Les 41 routes sont
desormais protegees par require_perm sur 34 codes (15 sous-modules : risque,
prevention, epi, accident, investigation, certification, audit, haccp,
controle, formation, indicateur, rapport, enregistrement, permis, imdg).

Role cree : QHSE (level 3, officier porteur du module) ; CHEF_EXPLOITATION et
AUDITEUR existent deja et recoivent leurs nouveaux liens via la boucle
additive. Les codes 501-conservateurs (qhse.permis.create, qhse.rapport.read)
sont inseres quand meme : ce sont des intentions, pas des faux succes.

Comme 033/034/035 : purement ADDITIVE (codes manquants inseres, liens
manquants ajoutes, roles absents crees), rien n'est supprime, downgrade = pass.
Garde explicite : tables RBAC absentes -> RuntimeError nommant la
precondition (020), jamais un no-op silencieux.
"""
from alembic import op
import sqlalchemy as sa
import json

revision = "036_rbac_qhse_grants"
down_revision = "035_rbac_acconage_grants"
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

# Roles dont les liens sont (re)censes apres le batch 24 ; QHSE est cree par
# cette migration, les autres existent deja et recoivent seulement les liens
# manquants. Codes source = catalogue (single source of truth).
ROLES_CIBLES = ("QHSE", "CHEF_EXPLOITATION", "AUDITEUR")


def _tables():
    return set(sa.inspect(op.get_bind()).get_table_names())


def upgrade():
    tables = _tables()
    if not {"permissions", "roles", "role_permissions"} <= tables:
        raise RuntimeError(
            "036 : tables RBAC (permissions/roles/role_permissions) absentes ; "
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
