"""062 : materialise les codes RBAC de l'expansion amenagement_portuaire.

Contexte : le routeur « amenagement_extra_deep » (expansion du departement
amenagement portuaire) expose huit registres operationnels reels (suivi
d'avancement des travaux, maintenance d'infrastructures, enregistrements ISPS,
redevances/perceptions portuaires, rapport d'activite annuel, cartographie SIG,
archivage domanial, indicateurs de developpement) plus une nomenclature. Chacune
de ses routes est gardee par ``require_perm("amenagement.<sous_module>.<action>")``.

Ces 25 codes viennent d'etre declares dans le catalogue (DOMAINS.amenagement).
Mais le catalogue n'est pas la source d'execution : la table « permissions »
-reférentiel des codes valides, utilisee par la matrice de roles de l'admin et
les accréditations - n'est alimentee QUE par les migrations. Sur une base deja
migree (cas Railway), les migrations RBAC anterieures (039/042/046) sont
passees et ne se rejouent pas : sans nouvelle migration tete, les codes de
l'expansion resteraient absents de la table « permissions ».

Pas de lien role->permission explicite ici : les porteurs de l'amenagement sont
des roles a wildcard - CHEF_AMENAGEMENT_PORTUAIRE (« amenagement.*.* ») pilote,
INGENIEUR_AMENAGEMENT et AUDITEUR (« amenagement.*.read ») consultent. Le moteur
d'autorisation has_perm() etend ces wildcards aux nouveaux codes a l'execution
(les lignes « amenagement.*.* » / « amenagement.*.read » existent deja depuis
039). Cette migration est donc un STRICT reflet du catalogue : elle insere
toute ligne « permissions » declaree mais absente, sans creer ni sur-granter
aucun role.

Garde explicite : tables RBAC absentes -> RuntimeError nommant la precondition
(020), jamais un no-op silencieux. Additive par convention : downgrade() pass.
"""
from alembic import op
import sqlalchemy as sa

revision = "062_rbac_amenagement_extra_grants"
# Chaîne strictement linéaire (exigence test_migrations_chain : « rollback
# lineaire propre ») : cette branche RBAC est re-rattachee en queue de la
# branche des tables de modes (061 -> 062_ferroviaire -> ... -> 065_log3pl).
# Ordre sans impact : les migrations RBAC (020/033/034/039/042/046/062/066)
# sont des miroirs idempotents du catalogue ; les tables 062..065 ne
# dépendent pas des grants, et les grants ne dépendent pas de ces tables.
down_revision = "065_log3pl_deep"
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


def _tables():
    return set(sa.inspect(op.get_bind()).get_table_names())


def upgrade():
    tables = _tables()
    if not {"permissions", "roles", "role_permissions"} <= tables:
        raise RuntimeError(
            "062 : tables RBAC (permissions/roles/role_permissions) absentes ; "
            "la migration 020 doit avoir ete appliquee avant."
        )

    from app.core.permission_catalog import iter_permission_rows

    bind = op.get_bind()

    existing = {
        r[0]
        for r in bind.execute(
            sa.text("SELECT code FROM permissions WHERE code IS NOT NULL")
        )
    }

    # Reflet du catalogue : toute code declare mais absent est cree. Les lignes
    # deja presentes (dont les wildcards porteurs) ne sont pas dupliquees.
    for code, domaine, module, sub, action in iter_permission_rows():
        if code in existing:
            continue
        bind.execute(
            PERMISSIONS_TBL.insert().values(
                code=code, name=code, description=None, domaine=domaine,
                module=module, sub_module=sub, action=action, resource=sub,
            )
        )
        existing.add(code)


def downgrade():
    # Additive par convention : on ne retrace pas l'etat anterieur, et une
    # suppression approximative de droits serait destructive.
    pass
