"""066 : materialise l'RBAC complet des expansions profondes (queue de chaine).

Contexte. Deux branches etaient nees au-dessus de 061_amenagement_extra_deep :
  - la notre, 062_rbac_amenagement_extra_grants (reflet du catalogue amenagement) ;
  - celle du plan d'expansion, 062_ferroviaire_deep -> 063_aerien_deep ->
    064_fluvial_deep -> 065_log3pl_deep (tables des modes de transport ajoutes).
Le test de chaine exige une chaine strictement lineaire (downgrade « base »
propre, impossible a traverser un merge point), donc 062_rbac_amenagement_extra_grants
a ete re-rattachee en queue de la branche des tables de modes, et cette migration 066
clot la chaine en tete unique lineaire.

Fonction : reconciler le catalogue vers la base deja migree. Le catalogue
(permission_catalog.DOMAINS) a ete etendu de toutes les expansions profondes
(transit/rh/qhse/magasin/parc, transport fret, comptabilite/tresorerie/port
reconcilies depuis les noms inventes compta/finance/port_ops, portail b2b, modes
aerien/ferroviaire/fluvial/log3pl, consoles plateforme) et ROLE_GRANTS porte un
nouveau role (RESPONSABLE_COMMERCIAL) plus des wildcards etendus (CHEF_PARC :
transport/aerien/ferroviaire/fluvial/log3pl.*.* ; CHEF_EXPLOITATION : port.*.* ;
AUDITEUR : lectures transversales). Or la table « permissions » et les liens
« role_permissions » ne sont alimentes QUE par les migrations : sur une base
Railway deja migree, rien ne se rejoue. Cette migration est donc la resynchronisation
idempotente complete, reproduction du mecanisme 020 :

  1. toute ligne du catalogue absente est creee (codes concrets) ;
  2. tout code de grant (wildcards « module.*.* », « module.*.read ») absent est
     cree comme ligne reference ;
  3. tout role de ROLE_GRANTS absent est cree (company_id NULL, systeme) ;
  4. tout lien role->permission declare mais absent est ajoute.

Additif et idempotent : chaque boucle saute ce qui existe deja, jamais de
sur-grantation au-dela de ROLE_GRANTS (source de verite), jamais de destruction.
Garde explicite : tables RBAC absentes -> RuntimeError nommant la precondition
(020). downgrade() pass (convention additive).
"""
from alembic import op
import sqlalchemy as sa

revision = "066_merge_expansion_rbac"
# Queue de la chaine lineaire : 065_log3pl -> 062_rbac_amenagement_extra_grants -> 066.
# (La branche RBAC a ete re-rattachee apres les tables de modes pour garder une
# chaine strictement lineaire — le downgrade "base" du test de chaine ne sait pas
# traverser un merge point.)
down_revision = "062_rbac_amenagement_extra_grants"
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
            "066 : tables RBAC (permissions/roles/role_permissions) absentes ; "
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

    # 2. Codes de grant (dont wildcards) non issus du catalogue.
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

    # 3 + 4. Roles metier (cree si absent) puis liens role->permission manquants.
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
    # Additif par convention : on ne retrace pas l'etat anterieur, et une
    # suppression approximative de droits serait destructive.
    pass
