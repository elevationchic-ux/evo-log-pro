"""028 parite ORM complete : tous les modules de modeles, plus seulement __init__.

Revision ID: 028_full_orm_parity
Revises: 027_add_orm_column_parity
Create Date: 2026-09-25

Contexte / pourquoi cette revision :
    014 cree les TABLES ORM manquantes et 027 les COLONNES manquantes, mais tous
    deux construisent leur reference avec `import app.models` (+ acconage).
    Or app/models/__init__.py n'expose qu'une partie des 47 modules du paquet :
    les modeles RH (conges, absences, temps_travail, salaires, primes, contrats,
    formations, documents, organigramme, competences, evaluations) entre autres
    n'y figurent pas. Les deux gardes-fous etaient donc AVEUGLES sur ces tables :
    un `alembic upgrade head` sur base vierge produit 259 tables alors que l'ORM
    en declare 329 (mesure : scripts/audit_schema_drift.py --replay).

    Consequence concrete, par table et non par Theorie :
      - 87 tables que seule create_all() materielisait, donc inexistantes en
        production (app/main.py la desactive) : la premiere lecture leve
        "no such table" ;
      - 32 tables existantes mais sous leur forme heritee, privees des colonnes
        que le code reclame (conges.created_at, salaires.* detaillee OHADA,
        absences.heure_debut, primes.periode, contrats_travail.horaire_travail,
        temps_travail.tache...) : "no such column" en 500 ;
      - des colonnes NOT NULL en base que plus rien n'alimente (conges.motif,
        absences.motif, primes.motif, formations.description...) : un refuse une
        raison de congee, ce qui vaut mieux qu'un motif invente pour satisfaire
        la contrainte ;
      - temps_travail.heure_arrivee/heure_depart creees en DATETIME alors que
        tout le code (pointage, paie, planning) les ecrit en "HH:MM" : Postgres
        refuse la valeur, et le type lui-meme est faux ;
      - 13 colonnes NOT NULL sans DEFAULT en base alors que le modele leur
        declare un server_default : l'INSERT omit la colonne, le defaut attendu
        n'existe pas, la contrainte echoue.

Proprietes (les memes que 014 et 027, elargies a toute la metadata) :
    - REFERENCE EXHAUSTIVE : chaque module de app/models est importe, un echec
      d'import est journalise sans casser la chaine.
    - IDEMPOTENT et DYNAMIQUE : le manque est recalcule depuis la metadata a
      chaque execution et compare au schema reflecte ; rien n'est fige. No-op
      total sur une base alignee.
    - NON DESTRUCTIF : ajoute, convertit, assouplit ; ne droppe ni table ni
      colonne, ne supprime aucune donnee. Une valeur d'horodatage devient un
      "HH:MM" par extraction, jamais par effacement.
    - Les colonnes ajoutees le sont NULLables meme si le modele les declare NOT
      NULL : on n'impose pas a des lignes deja la une contrainte qu'elles
      violent. Le modele, lui, continue de les alimenteer a l'ecriture.
"""
from alembic import op
import importlib
import logging
import sqlalchemy as sa

_log = logging.getLogger("alembic.env")

revision = "028_full_orm_parity"
down_revision = "027_add_orm_column_parity"
branch_labels = None
depends_on = None


NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

_FAMILLES_DATE = ("DATE",)
_FAMILLES_HORODATE = ("DATETIME", "TIMESTAMP")


def _charger_tous_les_modeles():
    """Importe CHAQUE module de app/models -- le correctif du point aveugle.

    `import app.models` ne suffit pas (voir docstring) : la moitie du modele
    metabolique n'y est pas declaree. Le scan est celui de
    scripts/audit_schema_drift.py, pour que la migration et l'audit partagent
    exactement la meme reference ; sinon l'audit corrigerait un ecart que la
    migration ne voit pas.

    Un module qui refuse de s'importer ne doit pas faire echouer
    `alembic upgrade head` : il est journalise, et l'audit le signale au vert
    (section 0), ce qui rend le trou visible plutot que fatal en deploiement.
    """
    from pathlib import Path

    dossier = Path(__file__).resolve().parents[2] / "app" / "models"
    charges, echecs = [], []
    for fichier in sorted(dossier.glob("*.py")):
        if fichier.name == "__init__.py":
            continue
        nom = "app.models.%s" % fichier.name[:-3]
        try:
            importlib.import_module(nom)
            charges.append(nom)
        except Exception as exc:  # pragma: no cover - module cassable
            echecs.append((nom, exc))
            _log.warning("028: module de modeles %s inimportable (%s)", nom, exc)
    import app.models  # noqa: F401 - complete les eventuels oublies du paquet
    return charges, echecs


def _orm_metadata():
    charges, echecs = _charger_tous_les_modeles()
    from app.core.database import Base
    _log.info("028: %d module(s) de modeles charge(s), %d en echec, %d table(s) "
              "declarees.", len(charges), len(echecs), len(Base.metadata.tables))
    return Base.metadata


def _colonnes(insp, table):
    return {c["name"]: c for c in insp.get_columns(table)}


def _tables_presentes(insp):
    return set(insp.get_table_names())


def _famille(type_sql):
    return (type_sql or "").split("(")[0].strip().upper()


# ---------------------------------------------------------------------------
# 1. TABLES absentes de la base (algorithme de 014, metadata complete)
# ---------------------------------------------------------------------------
def _creer_tables_absentes(bind, tables_en_base):
    metadata = _orm_metadata()
    wanted = {n: t for n, t in metadata.tables.items() if n not in tables_en_base}
    if not wanted:
        return [], []

    # Une table n'est creatible que si CHAQUE cle etrangere pointe vers une
    # table resoluble : presente en base ou creee ici. Le reste est mis de cote
    # sans jamais rompre la chaine (meme garantie qu 014).
    creatable, deferred = {}, []
    for name, table in wanted.items():
        unresolved = [
            fk.target_fullname for fk in table.foreign_keys
            if fk.target_fullname.split(".")[0] not in metadata.tables
        ]
        if unresolved:
            deferred.append((name, unresolved))
        else:
            creatable[name] = table

    while True:
        moved = False
        for name in list(creatable):
            for fk in creatable[name].foreign_keys:
                parent = fk.target_fullname.split(".")[0]
                if parent in tables_en_base or parent in creatable:
                    continue
                deferred.append((name, [fk.target_fullname]))
                del creatable[name]
                moved = True
                break
            if moved:
                break
        if not moved:
            break

    if creatable:
        # create() emis par SQLAlchemy lui-meme : DDL strictement identique a
        # celui que produisait create_all() en developpement.
        metadata.create_all(bind=bind, tables=list(creatable.values()),
                            checkfirst=True)
    for name, unresolved in deferred:
        _log.warning("028: table '%s' non creee (FK non resoluble vers %s)",
                     name, ", ".join(sorted(set(unresolved))))
    return sorted(creatable), deferred


# ---------------------------------------------------------------------------
# 2. COLONNES du modele absentes d'une table deja presente (algorithme de 027)
# ---------------------------------------------------------------------------
def _ajouter_colonnes(insp, tables_en_base):
    ajoutees = []
    for nom, table in sorted(_orm_metadata().tables.items()):
        if nom not in tables_en_base:
            continue
        presentes = _colonnes(insp, nom)
        index_existants = {i["name"] for i in insp.get_indexes(nom)}
        for col in table.columns:
            if col.name in presentes:
                continue
            op.add_column(nom, sa.Column(col.name, col.type, nullable=True))
            ajoutees.append("%s.%s" % (nom, col.name))
            nom_index = "ix_%s_%s" % (nom, col.name)
            if (col.index or col.unique) and nom_index not in index_existants:
                try:
                    op.create_index(nom_index, nom, [col.name],
                                    unique=bool(col.unique))
                except Exception as exc:  # pragma: no cover - best-effort
                    _log.warning("028: index %s non cree (%s)", nom_index, exc)
    return ajoutees


# ---------------------------------------------------------------------------
# 3. TYPES : une colonne d'heure de saisie n'est pas un horodatage
# ---------------------------------------------------------------------------
def _reconvertir_heures(insp, tables_en_base):
    """Ramene en VARCHAR les colonnes que le modele declare String(5).

    temps_travail.heure_arrivee/heure_depart ont ete creees en DATETIME : une
    migration ne peut pas se contenter d'ajouter les colonnes absentes, car le
    premier pointage ("08:30") echoue alors cote Postgres. La valeur existante
    est CONVERTIE (partie heure extraite), pas supprimee.
    """
    dialect = op.get_context().dialect.name
    metadata = _orm_metadata()
    converties = []
    for nom, table in sorted(metadata.tables.items()):
        if nom not in tables_en_base:
            continue
        base = _colonnes(insp, nom)
        for col in table.columns:
            if col.name not in base:
                continue
            if not isinstance(col.type, sa.String):
                continue
            type_sql = str(base[col.name]["type"]).upper()
            fam = _famille(type_sql)
            if fam not in _FAMILLES_DATE + _FAMILLES_HORODATE:
                continue
            if dialect == "postgresql":
                sens = ("to_char(\"%s\", 'HH24:MI')" % col.name
                        if fam in _FAMILLES_HORODATE else "\"%s\"::text" % col.name)
                # Le type cible est compile depuis le dialecte REEL de la
                # migration : la declaration sort exactement comme un create()
                # de l'ORM l'aurait emise, sans dialecte importe a la main.
                type_cible = col.type.compile(dialect=op.get_context().dialect)
                op.get_bind().execute(sa.text(
                    'ALTER TABLE "%s" ALTER COLUMN "%s" TYPE %s USING %s'
                    % (nom, col.name, type_cible, sens)))
            else:
                # SQLite : la donnee est deja une chaine, on garde les cinq
                # caracteres de l'heure avant de changer la declaration.
                op.get_bind().execute(sa.text(
                    'UPDATE "%s" SET "%s" = substr("%s", 12, 5) '
                    'WHERE "%s" IS NOT NULL AND length("%s") > 10'
                    % (nom, col.name, col.name, col.name, col.name)))
                with op.batch_alter_table(nom, naming_convention=NAMING_CONVENTION) as batch:
                    batch.alter_column(col.name, existing_type=base[col.name]["type"],
                                       type_=col.type,
                                       existing_nullable=base[col.name]["nullable"],
                                       nullable=col.nullable)
            converties.append("%s.%s" % (nom, col.name))
    return converties


# ---------------------------------------------------------------------------
# 4. DEFAULTS : la contrainte NOT NULL doit trouver sa valeur en base
# ---------------------------------------------------------------------------
def _aligner_defauts(insp, tables_en_base):
    """Repose le DEFAULT que le modele annonce mais qu'aucune migration n'a cree.

    Sans lui, un INSERT ORM qui omit la colonne (puisque le modele lui prevoit
    un server_default) heurte "NOT NULL constraint failed" : le defaut etait une
    promesse du modele que la base ne tenait pas. CURRENT_TIMESTAMP /
    CURRENT_DATE sont les deux seules expressions necessaires ici ; SQLite
    exige des parentheses autour de CURRENT_DATE, Postgres les accepte aussi.
    """
    dialect = op.get_context().dialect.name
    metadata = _orm_metadata()
    poses = []
    for nom, table in sorted(metadata.tables.items()):
        if nom not in tables_en_base:
            continue
        base = _colonnes(insp, nom)
        for col in table.columns:
            info = base.get(col.name)
            if info is None or info["nullable"] or info.get("default") is not None:
                continue
            if col.server_default is None:
                continue
            fam = _famille(str(info["type"]).upper())
            if fam in _FAMILLES_HORODATE:
                expression = "CURRENT_TIMESTAMP"
            elif fam in _FAMILLES_DATE:
                expression = ("(CURRENT_DATE)" if dialect != "postgresql"
                              else "CURRENT_DATE")
            else:
                continue
            defaut = sa.text(expression)
            if dialect == "postgresql":
                op.alter_column(nom, col.name, existing_type=info["type"],
                                existing_nullable=False, server_default=defaut)
            else:
                with op.batch_alter_table(nom, naming_convention=NAMING_CONVENTION) as batch:
                    batch.alter_column(col.name, existing_type=info["type"],
                                       existing_nullable=False,
                                       server_default=defaut)
            poses.append("%s.%s" % (nom, col.name))
    return poses


# ---------------------------------------------------------------------------
# 5. NOT NULL heritees que le modele n'alimente plus (algorithme de 027)
# ---------------------------------------------------------------------------
def _assouplir(insp, tables_en_base):
    dialect = op.get_context().dialect.name
    metadata = _orm_metadata()
    souplees = []
    for nom, table in sorted(metadata.tables.items()):
        if nom not in tables_en_base:
            continue
        model = {c.name: c for c in table.columns}
        for nom_col, info in sorted(_colonnes(insp, nom).items()):
            if info["nullable"]:
                continue
            if info.get("default") is not None:
                continue
            colonne = model.get(nom_col)
            if colonne is not None and not colonne.nullable:
                continue
            if dialect == "postgresql":
                op.alter_column(nom, nom_col, existing_type=info["type"],
                                existing_nullable=False, nullable=True)
            else:
                with op.batch_alter_table(nom, naming_convention=NAMING_CONVENTION) as batch:
                    batch.alter_column(nom_col, existing_type=info["type"],
                                       existing_nullable=False, nullable=True)
            souplees.append("%s.%s" % (nom, nom_col))
    return souplees


# ---------------------------------------------------------------------------
# 6. DATES : borner au jour les horodatages relus dans une colonne Date (027)
# ---------------------------------------------------------------------------
def _normaliser_dates(insp, tables_en_base):
    dialect = op.get_context().dialect.name
    touchees = []
    for nom, table in sorted(_orm_metadata().tables.items()):
        if nom not in tables_en_base:
            continue
        base = _colonnes(insp, nom)
        for col in table.columns:
            if col.name not in base:
                continue
            if not isinstance(col.type, sa.Date):
                continue
            if not isinstance(base[col.name]["type"], sa.DateTime):
                continue
            if dialect == "postgresql":
                requete = ('UPDATE "%s" SET "%s" = "%s"::date '
                           "WHERE \"%s\"::text LIKE '____-__-__ __:__:__%%'"
                           % (nom, col.name, col.name, col.name))
            else:
                requete = ('UPDATE "%s" SET "%s" = substr("%s", 1, 10) '
                           'WHERE "%s" IS NOT NULL'
                           % (nom, col.name, col.name, col.name))
            op.get_bind().execute(sa.text(requete))
            touchees.append("%s.%s" % (nom, col.name))
    return touchees


def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    tables_en_base = _tables_presentes(insp)

    creees, en_attente = _creer_tables_absentes(bind, tables_en_base)

    insp = sa.inspect(bind)
    tables_en_base = _tables_presentes(insp)
    ajoutees = _ajouter_colonnes(insp, tables_en_base)

    insp = sa.inspect(bind)
    converties = _reconvertir_heures(insp, tables_en_base)
    poses = _aligner_defauts(insp, tables_en_base)
    dates = _normaliser_dates(insp, tables_en_base)
    souplees = _assouplir(sa.inspect(bind), tables_en_base)

    _log.info(
        "028 parite ORM complete: %d table(s) creee(s), %d colonne(s) ajoutee(s), "
        "%d colonne(s) d'heure reconvertie(s), %d defaut(s) repose(s), "
        "%d contrainte(s) NOT NULL levee(s), %d date(s) bornee(s) au jour, "
        "%d table(s) en attente de FK resoluble.",
        len(creees), len(ajoutees), len(converties), len(poses),
        len(souplees), len(dates), len(en_attente),
    )
    for titre, elements in (
        ("tables creees", creees), ("colonnes ajoutees", ajoutees),
        ("heures reconverties", converties), ("defauts repos", poses),
        ("contraintes levees", souplees), ("dates normalisees", dates),
    ):
        if elements:
            _log.info("028 %s: %s", titre, ", ".join(elements))


def downgrade() -> None:
    """Volontairement sans effet (meme raisonnement que 027).

    Dropper une table ou une colonne creee ici detruirait des donnees que
    l'application a deja ecrites dedans ; un defaut ou une colonne en trop ne
    casse rien, une valeur perdue est irreversible. Les tables creees par cette
    revision sont d'ailleurs reprises telles quelles par create_all() en
    developpement : le retour en arriere n'a aucun sens metier.
    """
    pass
