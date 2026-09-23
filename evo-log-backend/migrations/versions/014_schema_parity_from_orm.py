"""014 consolidation du schema initial : parite ORM (best-effort)

Revision ID: 014_schema_parity_from_orm
Revises: 013_retenues_source_ohada
Create Date: 2026-09-23

Contexte / pourquoi cette revision :
    La chaine de migrations 001..013 ne couvre PAS la totalite du modele ORM.
    31 tables (dont ``cotations_devis``, ``reglements``, ``clients``,
    ``factures_ohada``...) n'etaient materialisees QUE par
    ``Base.metadata.create_all()`` execute au demarrage de l'app (voir
    app/main.py). Resultat : ``alembic upgrade head`` sur une base TOTALEMENT
    vierge produisait un schema incomplet ; seule une base deja "bootstrapee"
    par create_all etait valide. C'est ce que decriit la note de synthese.

    Cette revision est la tache dediee de "consolidation du schema initial" :
    elle cree, depuis les definitions ORM (source de verite unique), toute
    table declaree par le modele mais absente de la base. Le DDL est emis par
    SQLAlchemy lui-meme (``table.create``), donc strictement identique a
    create_all() -- aucun DDL recrit a la main qui pourrait diverger.

Proprietes :
    - IDEMPOTENT : ne cree que les tables manquantes (garde "table existante"),
      donc no-op total sur une base deja complete (prod, ou base creee par
      create_all). Aucune donnee existante n'est jamais touchee.
    - PARITE (best-effort) : cree toute table ORM manquante dont les cles
      etrangeres sont resolubles dans la metadata. La metadata chargee inclut
      app.models.acconage (navires, escales, conteneurs...) que l'app charge
      deja via ses routeurs mais PAS via app.models.__init__ ; sans lui, des FK
      "orphelines" (ex. cycle_conteneur_cycle.navire_id -> navires) peupleraient
      echouer le tri de create_all. Toute table dont UNE FK resterait
      non resoluble est journalisee et laissee de cote SANS jamais casser la
      chaine (garde de securite pour d'eventuels autres modules orphelins).

Ordre de creation : tri topologique interne par create_all() du sous-ensemble
resoluble ; les cles etrangeres vers des tables deja presentes (001..013) ou
vers d'autres tables du sous-ensemble se resolvent d'elles-memes.
"""
from alembic import op
import logging
import sqlalchemy as sa

_log = logging.getLogger("alembic.env")

revision = "014_schema_parity_from_orm"
down_revision = "013_retenues_source_ohada"
branch_labels = None
depends_on = None


# Tables que la chaine 001..013 ne creait pas (gap ORM-verso-migrations mesure
# sur une base reconstruite de zero). Figees ici UNIQUEMENT pour que downgrade()
# sache quoi retirer sans dependre de l'inspection dynamique ; upgrade() ne
# s'appuie pas sur cette liste mais recalcule le manque depuis l'ORM (aucune
# divergence possible si un modele est ajoute/renomme plus tard).
PARITY_TABLES = [
    "avances_missions",
    "centimes_additionnels",
    "clients",
    "compliance_audits",
    "conteneurs_cycle",
    "cotations_devis",
    "cycle_conteneur_cycle",
    "demandes_cotation_prestataires",
    "dommages_conteneur_cycle",
    "dotations_epi_materiel",
    "ecritures_comptables_ohada",
    "electronic_pods",
    "empotage_depotage_cycle",
    "factures_ohada",
    "fournisseurs",
    "frais_missions",
    "fuel_tank_sensors",
    "inspections_conteneur_cycle",
    "lignes_facture_ohada",
    "lignes_facture_simple",
    "maintenances",
    "organizations",
    "partenaires",
    "patentes",
    "plannings_gardes",
    "pointages_vacations",
    "prestataires",
    "procurement_purchase_orders",
    "reglements",
    "signatures_electroniques",
    "trajets",
]


def _orm_metadata():
    # Parite stricte avec le create_all() de l'app : on reutilise la MEME
    # Base/metadata. Mais app.models.__init__ est une liste VOLONTAIREMENT
    # restreinte (evite des collisions de noms de classes ORM, ex. 'Role'
    # declare dans plusieurs modules -> configure_mappers leverait une erreur).
    # Le hic : conteneur_cycle.py (charge) a une ForeignKey vers 'navires',
    # definie uniquement dans acconage.py, lui NON charge par l'__init__.
    # Resultat : FK "orpheline" => create_all() d'une base vierge ne peut pas
    # trier ces tables. A l'execution reelle, l'app charge acconage via ses
    # routeurs (app/routers/v1/acconage.py), donc sa metadata runtime est
    # complete ; seule la voie alembic-only (env.py -> app.models) etait en
    # retard. On aligne la migration en important ce module precis (et
    # uniquement lui : un scan complet des 42 sous-modules reintroduirait la
    # collision 'Role').
    import app.models  # noqa: F401 - ensemble ORM de base
    try:
        import app.models.acconage  # noqa: F401 - fournit navires, escales...
    except Exception:  # pragma: no cover - module absent/cassable : best-effort
        pass
    from app.core.database import Base
    return Base.metadata


def upgrade() -> None:
    bind = op.get_bind()
    metadata = _orm_metadata()
    existing = set(sa.inspect(bind).get_table_names())

    # Toute table declaree par l'ORM mais absente de la base. Les tables dont
    # le NOM existe deja sous une forme divergente (conteneurs, factures,
    # ecritures_comptables...) sont mecaniquement exclues par le test
    # "not in existing" : on ne touche jamais une table deja presente, donc
    # aucune donnee existante n'est ecrasee.
    wanted = {
        name: table
        for name, table in metadata.tables.items()
        if name not in existing
    }

    # Une table n'est creatible via SQLAlchemy que si CHAQUE cle etrangere
    # pointe vers une table presente dans la MEME metadata (resolvable).
    # Or certain modules ORM (ex. app.models.acconage : navires, escales,
    # conteneurs...) ne sont pas charges par app.models.__init__, donc leurs
    # tables manquent de la metadata ; les tables qui y font reference
    # (ex. cycle_conteneur_cycle.navire_id -> navires) ont une FK "orpheline"
    # que create_all ne peut pas trier. On les met de cote (deferred) au lieu
    # de faire echouer toute la chaine : la consolidation est best-effort et
    # NE JAMAIS casser "alembic upgrade head". Ces tables restent a creer par
    # la vraie tâche dédiée (câblage des modules ORM orphelins).
    creatable, deferred = {}, []
    for name, table in wanted.items():
        unresolved = [
            fk.target_fullname
            for fk in table.foreign_keys
            if fk.target_fullname.split(".")[0] not in metadata.tables
        ]
        if unresolved:
            deferred.append((name, unresolved))
        else:
            creatable[name] = table

    # Point fixe : une table n'est gardée que si toutes ses FK ciblent une
    # table existante (001..013) ou une autre table 'creatable'. Sinon elle
    # dependrait d'une table mise de cote -> FK cassante sur Postgres (la
    # validation SQLite ne la verrait pas). On la recule en deferred.
    while True:
        moved = False
        for name in list(creatable):
            table = creatable[name]
            for fk in table.foreign_keys:
                parent = fk.target_fullname.split(".")[0]
                if parent in existing or parent in creatable:
                    continue
                deferred.append((name, [fk.target_fullname]))
                del creatable[name]
                moved = True
                break
        if not moved:
            break

    for name, unresolved in deferred:
        _log.warning(
            "014_schema_parity: table '%s' non creee (FK non resoluble vers "
            "%s) - module ORM orphelin a cabler dans la tache dediee.",
            name, ", ".join(sorted(set(unresolved))),
        )

    if not creatable:
        return

    # create_all(tables=<sous-ensemble creatible>, checkfirst=True) : meme code
    # que le create_all() de l'app (tri topologique interne, emission DDL par
    # SQLAlchemy) => parite stricte avec le modele ORM, idempotent.
    metadata.create_all(
        bind=bind, tables=list(creatable.values()), checkfirst=True
    )


def downgrade() -> None:
    bind = op.get_bind()
    existing = set(sa.inspect(bind).get_table_names())
    # Suppression en ordre inverse (best-effort) : uniquement les tables de la
    # liste de parite encore presentes. Chaque drop est garde pour tolerer les
    # dependances croisees ; un echec sur une table n'interrompt pas le reste.
    for name in reversed(PARITY_TABLES):
        if name not in existing:
            continue
        try:
            sa.Table(name, sa.MetaData(), autoload_with=bind).drop(
                bind=bind, checkfirst=True
            )
        except Exception:  # pragma: no cover - downgrade best-effort
            pass
