"""027 parite ORM -> base : les COLONNES declarees par le modele et absentes du schema migre.

Revision ID: 027_add_orm_column_parity
Revises: 026_add_2fa_recovery_codes
Create Date: 2026-09-25

Contexte / pourquoi cette revision :
    014_schema_parity_from_orm fait la parite au niveau des TABLES : il cree toute
    table ORM absente de la base, mais ne touche JAMAIS une table dont le nom
    existe deja (garde "name not in existing", assumee dans son docstring). Or,
    rejouee de bout en bout sur une base vierge, la chaine 001..026 produit un
    schema ou 13 tables vivent encore sous leur forme ANCIENNE :

      - isolation multi-tenant ( jamais migratee pour ces tables-la ) :
        company_id   manque sur camions, conducteurs, entrepots, missions,
                       mouvements_stocks, stocks, paiements, factures, comptes,
                       ecritures_comptables
        organization_id manque sur users et agencies
        10 colonnes   manquent sur companies (rccm, sigle, rib, capital_social,
                       agrement_douane/pad/pak, max_camions, modules_actives,
                       suspension_reason)
      - renommage OHADA sans migration : comptes.numero/nom -> numero_compte/
        nom_compte, ecritures_comptables.numero_piece -> reference,
        compte_debit_id/compte_credit_id -> compte_debit/compte_credit,
        montant -> montant_debit/montant_credit, factures.numero ->
        numero_facture.

    Aucune de ces colonnes n'est creee par la chaine 001..026 : sur toute base
    pilotee par Alembic -- donc la production, ou app/main.py desactive
    create_all() -- le premier SELECT qui les traverse leve
    "no such column: camions.company_id" et la page meurt en 500. La base de
    developpement sqlite, bootstrappee par create_all puis completee par des
    ALTER manuels, possede l'union des deux formes : elle ne revele rien. D'ou
    le caractere invisible du defaut pour un audit de chemins frontend/backend,
    qui ne valide que des routes : chaque route repond, et chacune casse a la
    premiere lecture de la colonne qui manque.

Proprietes :
    - IDEMPOTENT et DYNAMIQUE : le manque est recalcule depuis la metadata ORM a
      chaque execution et compare au schema reflecte. Aucune liste de colonnes
      n'est figee dans ce fichier ; si un modele change encore, cette revision
      le rattrape. No-op total sur une base deja alignee (create_all).
    - NON DESTRUCTIVE : ajoute, ne droppe rien. Les colonnes heritees restent en
      place et leur contenu est recopie dans la colonne qui la remplace dans le
      modele, quand une equivalence existe (voir RENOMMES). Elles sont seulement
      rendues NULLables (voir ASSOUPLIR) : sans cela le modele, qui ne les
      alimente plus, ne pourrait plus inserer une seule ligne
      ("NOT NULL constraint failed").
    - Les colonnes ajoutees le sont NULLables meme si le modele les declare
      NOT NULL (ex. factures.numero_facture) : une table deja peuplee ne peut
      pas recevoir une contrainte que ses lignes existantes violent.
"""
from alembic import op
import logging
import sqlalchemy as sa

_log = logging.getLogger("alembic.env")

revision = "027_add_orm_column_parity"
down_revision = "026_add_2fa_recovery_codes"
branch_labels = None
depends_on = None


# Ancienne colonne -> colonne que le modele declare aujourd'hui. Recopie avant
# tout assouplissement, pour qu'aucune donnee existante ne soit perdue.
RENOMMES = {
    "comptes": [("numero", "numero_compte"), ("nom", "nom_compte")],
    "factures": [("numero", "numero_facture")],
    "ecritures_comptables": [
        ("numero_piece", "reference"),
        ("compte_debit_id", "compte_debit"),
        ("compte_credit_id", "compte_credit"),
    ],
}

# Colonnes que le modele ne connait plus mais qui restent NOT NULL sans valeur
# par defaut : tout INSERT emis par l'ORM echouerait tant qu'elles le sont.
ASSOUPLIR = {
    "comptes": ["numero", "nom"],
    "factures": ["numero"],
    "ecritures_comptables": ["numero_piece", "montant"],
}

# Le modele a remplace le montant unique par une ecriture double (debit/credit).
# L'ancienne colonne ne precise pas le sens ; on suit le compte renseigne.
SPLIT_MONTANT = ("ecritures_comptables", "montant", "compte_debit_id",
                 "montant_debit", "compte_credit", "montant_credit")

NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


def _orm_metadata():
    """Meme approche que 014 : la metadata complete de l'app, y compris le
    module acconage que app.models.__init__ ne charge pas."""
    import app.models  # noqa: F401 - ensemble ORM de base
    try:
        import app.models.acconage  # noqa: F401 - fournit navires, escales...
    except Exception:  # pragma: no cover - module cassable : best-effort
        pass
    from app.core.database import Base
    return Base.metadata


def _colonnes(insp, table):
    return {c["name"]: c for c in insp.get_columns(table)}


def _ajouter_colonnes(bind, insp, tables_en_base):
    """Emet, pour chaque table DEJA presente, les colonnes reclamees par l'ORM.

    Le type vient de la colonne du modele elle-meme (`col.type`), jamais recrit
    ici : le DDL emis est donc strictement celui qu'aurait produit create_all().
    """
    ajoutees = []
    for nom, table in sorted(_orm_metadata().tables.items()):
        if nom not in tables_en_base:
            continue  # table absente : c'est 014 qui la cree
        presentes = _colonnes(insp, nom)
        index_existants = {i["name"] for i in insp.get_indexes(nom)}
        for col in table.columns:
            if col.name in presentes:
                continue
            op.add_column(nom, sa.Column(col.name, col.type, nullable=True))
            ajoutees.append("%s.%s" % (nom, col.name))
            # create_all() cree l'index demande par le modele (index=True) ;
            # sans lui, toute requete filtrant la cle d'isolation reste seqentielle.
            nom_index = "ix_%s_%s" % (nom, col.name)
            if (col.index or col.unique) and nom_index not in index_existants:
                try:
                    op.create_index(nom_index, nom, [col.name], unique=False)
                except Exception as exc:  # pragma: no cover - best-effort
                    _log.warning("027: index %s non cree (%s)", nom_index, exc)
    return ajoutees


def _recopier(insp, table, depuis, vers):
    """`UPDATE t SET vers = depuis WHERE vers IS NULL AND depuis IS NOT NULL`.

    Garde : les deux colonnes doivent exister, sinon la recopie n'a pas de sens
    (base creee par create_all : l'heritee n'y a jamais existe). La clause WHERE
    ne touche jamais une valeur deja renseignee, donc l'operation est rejouable.
    """
    colonnes = _colonnes(insp, table)
    if depuis not in colonnes or vers not in colonnes:
        return 0
    return op.get_bind().execute(sa.text(
        'UPDATE "%s" SET "%s" = "%s" WHERE "%s" IS NULL AND "%s" IS NOT NULL'
        % (table, vers, depuis, vers, depuis)
    )).rowcount


def _scinder_montant(insp):
    table, montant, c_debit, vers_debit, c_credit, vers_credit = SPLIT_MONTANT
    colonnes = _colonnes(insp, table)
    if montant not in colonnes or vers_debit not in colonnes:
        return 0
    bind = op.get_bind()
    total = 0
    if c_debit in colonnes:
        total += bind.execute(sa.text(
            'UPDATE "%s" SET "%s" = "%s" WHERE "%s" IS NULL AND "%s" IS NOT NULL'
            % (table, vers_debit, montant, vers_debit, c_debit)
        )).rowcount
    if c_credit in colonnes:
        total += bind.execute(sa.text(
            'UPDATE "%s" SET "%s" = "%s" WHERE "%s" IS NULL AND "%s" IS NULL AND "%s" IS NOT NULL'
            % (table, vers_credit, montant, vers_credit, vers_debit, c_credit)
        )).rowcount
    return total


def _assouplir(insp, tables_en_base):
    """Rend NULLables les colonnes heritees que l'ORM n'alimente plus.

    Postgres connait `ALTER COLUMN ... DROP NOT NULL` : simple ALTER natif.
    SQLite ne sait pas modifier une colonne -> `batch_alter_table` recree la
    table en copiant les donnees (recette documentaire d'Alembic), d'ou la
    convention de nommage fournie pour que contraintes et index ressortent avec
    leur nom d'origine au lieu de noms generes.
    """
    dialect = op.get_context().dialect.name
    souplonees = []
    for table, colonnes in ASSOUPLIR.items():
        if table not in tables_en_base:
            continue
        existantes = _colonnes(insp, table)
        for nom in colonnes:
            info = existantes.get(nom)
            if info is None or info["nullable"]:
                continue  # deja assouplie (ou base creee par create_all)
            if dialect == "postgresql":
                op.alter_column(table, nom, existing_type=info["type"],
                                nullable=True)
            else:
                with op.batch_alter_table(
                    table, naming_convention=NAMING_CONVENTION,
                    copy_from=sa.table(table, sa.MetaData(), autoload_with=op.get_bind()),
                ) as batch:
                    batch.alter_column(nom, existing_type=info["type"],
                                       nullable=True)
            souplonees.append("%s.%s" % (table, nom))
    return souplonees


def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    tables_en_base = set(insp.get_table_names())

    ajoutees = _ajouter_colonnes(bind, insp, tables_en_base)

    # Les colonnes viennent d'apparaitre : on recopie AVANT d'assouplir, sinon
    # la valeur heritee resterait orpheline dans une colonne que rien ne lit.
    insp = sa.inspect(bind)
    recopies = 0
    for table, paires in RENOMMES.items():
        for depuis, vers in paires:
            recopies += _recopier(insp, table, depuis, vers) or 0
    recopies += _scinder_montant(insp) or 0

    souplonees = _assouplir(sa.inspect(bind), tables_en_base)

    _log.info(
        "027 parite ORM: %d colonne(s) ajoutee(s), %d ligne(s) recopiee(s), "
        "%d contrainte(s) NOT NULL levee(s).",
        len(ajoutees), recopies, len(souplonees),
    )
    if ajoutees:
        _log.info("027 ajoute: %s", ", ".join(ajoutees))
    if souplonees:
        _log.info("027 assoupli: %s", ", ".join(souplonees))


def downgrade() -> None:
    """Volontairement sans effet.

    Les colonnes ajoutees peuvent deja porter des donnees ecrites par l'app
    (un numero_compte renseigne, un company_id affecte) : les dropper detruirait
    ces valeurs. Une colonne en trop et NULLable ne casse aucun fonctionnement,
    alors qu'une donnee perdue est irreversible.
    """
    pass
