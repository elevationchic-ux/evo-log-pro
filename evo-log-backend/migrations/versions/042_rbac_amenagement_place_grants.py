"""042 : droits RBAC du sous-module « place » du departement Amenagement portuaire.

Contexte : le module promet (docstring de son routeur, lignes 14-16) que les
referentiels nationaux sont « alimentes par les agents ». Or ``ports_cameroun``
n'etait ecrit par AUCUNE route de l'application — public_api ne fait que la
lire. Resultat : les neuf registres du departement ne pouvaient rattacher
aucune ligne a une place portuaire, et le menu « Place » restait vide.

Cette migration est strictement additive et reprend le corps de 039 (identique
a 033/034/035/036) : elle est pilotee par le catalogue, donc ne durcit ici
aucun code. Ce qu'elle ajoute reellement :

  * 3 codes nouveaux : amenagement.place.read / .create / .modify ;
  * liens nouveaux  INGENIEUR_AMENAGEMENT (create + modify : l'ingenieur releve
    code, denomination, autorite concessionnaire et tirant d'eau sur les
    documents officiels), CHEF_EXPLOITATION et DIRECTEUR_FINANCIER (read seul,
    pour que la synthese et les formulaires ne leur soient pas presentees vides) ;
  * AUCUN lien nouveau pour CHEF_AMENAGEMENT_PORTUAIRE (son wildcard
    amenagement.*.* couvre deja le sous-module) ni pour AUDITEUR
    (amenagement.*.read).

Pas de code « place.delete » et donc pas de lien : ports_cameroun est une table
partagee (terminaux, tarification, perimetres). Une place qui sort du perimetre
est desactivee (est_actif = false) par amenagement.place.modify, jamais detruite.

Aucune donnee metier n'est inseree : Douala, Kribi et Limbe seront saisies par
les agents depuis leurs arretes, le logiciel ne peuple rien.

Garde explicite : tables RBAC absentes -> RuntimeError nommant la precondition
(020), jamais un no-op silencieux.
"""
from alembic import op
import sqlalchemy as sa
import json

revision = "042_rbac_amenagement_place_grants"
down_revision = "041_seed_syscohada_referentiels"
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

# Les cinq roles deja lies au departement en 039. Aucun role n'est cree ici :
# le sous-module « place » s'ajoute a un perimetre qui existe deja.
ROLES_CIBLES = (
    "CHEF_AMENAGEMENT_PORTUAIRE",
    "INGENIEUR_AMENAGEMENT",
    "AUDITEUR",
    "CHEF_EXPLOITATION",
    "DIRECTEUR_FINANCIER",
)


def _tables():
    return set(sa.inspect(op.get_bind()).get_table_names())


def upgrade():
    tables = _tables()
    if not {"permissions", "roles", "role_permissions"} <= tables:
        raise RuntimeError(
            "042 : tables RBAC (permissions/roles/role_permissions) absentes ; "
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
