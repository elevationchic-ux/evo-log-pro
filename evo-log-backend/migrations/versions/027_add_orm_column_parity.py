"""027 parite ORM -> base : colonnes, contraintes NOT NULL et dates heritagees.

Revision ID: 027_add_orm_column_parity
Revises: 026_add_2fa_recovery_codes
Create Date: 2026-09-25

Contexte / pourquoi cette revision :
    014_schema_parity_from_orm fait la parite au niveau des TABLES : il cree toute
    table ORM absente de la base, mais ne touche JAMAIS une table dont le nom
    existe deja (garde "name not in existing", assumee dans son docstring). Or,
    rejouee de bout en bout sur une base vierge, la chaine 001..026 laisse 13
    tables sous leur forme ANCIENNE :

      - isolation multi-tenant jamais migratee pour ces tables : company_id
        manque sur camions, conducteurs, entrepots, missions, mouvements_stocks,
        stocks, paiements, factures, comptes, ecritures_comptables ;
        organization_id manque sur users et agencies ; 10 colonnes manquent sur
        companies (rccm, sigle, rib, capital_social, agrement_douane/pad/pak,
        max_camions, modules_actives, suspension_reason) ;
      - renommage OHADA sans migration : comptes.numero/nom -> numero_compte/
        nom_compte, ecritures_comptables.numero_piece -> reference,
        compte_debit_id/compte_credit_id -> compte_debit/compte_credit, montant
        -> montant_debit/montant_credit, factures.numero -> numero_facture ;
      - contraintes NOT NULL heritees que plus rien n'alimente (paiements
        .reference, comptes.numero, factures.numero, ecritures_comptables
        .numero_piece et .montant) ;
      - colonnes declarees Date dans le modele mais DATETIME en base, ayant recu
        des horodatages complets.

    Rien de tout cela n'est cree par la chaine 001..026 : sur toute base pilotee
    par Alembic -- donc la production, ou app/main.py desactive create_all() --
    la premiere lecture leve "no such column: camions.company_id" et meurt en
    500, la premiere ecriture leve "NOT NULL constraint failed", et la relecture
    d'une date leve "Invalid isoformat string". La base de developpement sqlite,
    bootstrappee par create_all puis completee par des ALTER manuels, presente
    l'UNION des deux formes : elle ne revele rien. Un audit de chemins
    frontend/backend ne le voit pas non plus : chaque route repond, et chacune
    casse a la premiere donnee.

Proprietes :
    - IDEMPOTENT et DYNAMIQUE : le manque est recalcule depuis la metadata ORM a
      chaque execution et compare au schema reflecte. Aucune liste de colonnes
      n'est figee ici ; si un modele bouge encore, cette revision rattrape.
      No-op total sur une base deja alignee.
    - NON DESTRUCTIVE : ajoute, ne droppe rien. Une colonne heritee reste en
      place, son contenu est recopie dans la colonne qui la remplace (RENOMMES),
      et elle est seulement rendue NULLable -- sans cela le modele, qui ne
      l'alimente plus, ne pourrait plus inserer une seule ligne.
    - Les colonnes ajoutees le sont NULLables meme si le modele les declare NOT
      NULL (ex. factures.numero_facture) : on n'impose pas a des lignes deja
      la une contrainte qu'elles violent.

Cette revision corrige cote base ; le defaut de modele correspondant
(Column(Date, default=func.now())) est corrige dans app/models/finance.py.
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


def _ajouter_colonnes(insp, tables_en_base):
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
            # create_all() cree l'index demande par le modele (index=True) ; sans
            # lui, tout filtrage sur la cle d'isolation reste sequentiel.
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
    """Le modele a remplace le montant unique par une ecriture double.

    La colonne heritee ne precise pas le sens du mouvement : on suit le compte
    renseigne, a debit, a credit sinon.
    """
    table = "ecritures_comptables"
    if table not in _tables_presentes(insp):
        return 0
    colonnes = _colonnes(insp, table)
    if "montant" not in colonnes or "montant_debit" not in colonnes:
        return 0
    bind = op.get_bind()
    total = 0
    if "compte_debit_id" in colonnes or "compte_debit" in colonnes:
        total += bind.execute(sa.text(
            'UPDATE "%s" SET "montant_debit" = "montant" '
            'WHERE "montant_debit" IS NULL AND "montant" IS NOT NULL '
            'AND COALESCE("compte_debit", "compte_debit_id") IS NOT NULL'
            % table
        )).rowcount
    if "compte_credit_id" in colonnes or "compte_credit" in colonnes:
        total += bind.execute(sa.text(
            'UPDATE "%s" SET "montant_credit" = "montant" '
            'WHERE "montant_credit" IS NULL AND "montant_debit" IS NULL '
            'AND "montant" IS NOT NULL '
            'AND COALESCE("compte_credit", "compte_credit_id") IS NOT NULL'
            % table
        )).rowcount
    return total


def _tables_presentes(insp):
    return set(insp.get_table_names())


def _assouplir(insp, tables_en_base):
    """Rend NULLables les colonnes NOT NULL sans defaut que le modele n'alimente pas.

    Deux cas, meme cause : la colonne a disparu du modele (comptes.numero), ou
    elle y est redevenue nullable (paiements.reference). Dans les deux cas
    l'INSERT emis par l'ORM ne la fournit pas et la contrainte le refuse.

    Postgres connait `ALTER COLUMN ... DROP NOT NULL` : simple ALTER natif.
    SQLite ne sait pas modifier une colonne -> `batch_alter_table` recree la
    table en copiant les donnees (recette documentaire d'Alembic), d'ou la
    convention de nommage fournie pour que contraintes et index ressortent avec
    leur nom d'origine au lieu de noms generes.
    """
    dialect = op.get_context().dialect.name
    metadata = _orm_metadata()
    souplees = []
    for nom, table in sorted(metadata.tables.items()):
        if nom not in tables_en_base:
            continue
        model = {c.name: c for c in table.columns}
        for nom_col, info in sorted(_colonnes(insp, nom).items()):
            if info["nullable"]:
                continue                       # deja NULLable : rien a faire
            if info.get("default") is not None:
                continue                       # un defaut pourvoit a l'absence
            colonne = model.get(nom_col)
            if colonne is not None and not colonne.nullable:
                continue                       # le modele l'exige vraiment
            if dialect == "postgresql":
                op.alter_column(nom, nom_col, existing_type=info["type"],
                                existing_nullable=False, nullable=True)
            else:
                with op.batch_alter_table(
                    nom, naming_convention=NAMING_CONVENTION,
                ) as batch:
                    batch.alter_column(nom_col, existing_type=info["type"],
                                       existing_nullable=False, nullable=True)
            souplees.append("%s.%s" % (nom, nom_col))
    return souplees


def _normaliser_dates(insp, tables_en_base):
    """Borne au jour les horodatages stockes dans une colonne que le modele dit Date.

    Le modele lisait '2026-09-27 19:24:12' via le processeur de resultat Date,
    ce qui leve "Invalid isoformat string" : la ligne ne pouvait plus etre
    relue. La partie heure n'est pas une information que le modele sait
    represente ; la supprimer rend les lignes existantes relisibles.
    """
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
            # Postgres possede le VRAI type date : la tranche ne peut que
            # conforter la donnee, et ne s'applique qu'aux valeurs qui portent
            # effectivement une heure. SQLite ne distingue pas : la valeur est
            # une chaine, les lignes heritees gardent l'heure.
            if dialect == "postgresql":
                # Attention : en SQL les guillemets doubles designent un
                # identifiant, un litteral va en quotes simples.
                requete = 'UPDATE "%s" SET "%s" = "%s"::date ' \
                          "WHERE \"%s\"::text LIKE '____-__-__ __:__:__%%'" % (
                              nom, col.name, col.name, col.name)
            else:
                requete = 'UPDATE "%s" SET "%s" = substr("%s", 1, 10) ' \
                          'WHERE "%s" IS NOT NULL' % (
                              nom, col.name, col.name, col.name)
            op.get_bind().execute(sa.text(requete))
            touchees.append("%s.%s" % (nom, col.name))
    return touchees


def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    tables_en_base = set(insp.get_table_names())

    ajoutees = _ajouter_colonnes(insp, tables_en_base)

    # Les colonnes viennent d'apparaitre : recopier AVANT d'assouplir, sinon la
    # valeur heritee resterait orpheline dans une colonne que plus rien ne lit.
    insp = sa.inspect(bind)
    recopies = 0
    for table, paires in RENOMMES.items():
        if table in tables_en_base:
            for depuis, vers in paires:
                recopies += _recopier(insp, table, depuis, vers) or 0
    recopies += _scinder_montant(insp) or 0

    dates = _normaliser_dates(insp, tables_en_base)
    souplees = _assouplir(sa.inspect(bind), tables_en_base)

    _log.info(
        "027 parite ORM: %d colonne(s) ajoutee(s), %d ligne(s) recopiee(s), "
        "%d contrainte(s) NOT NULL levee(s), %d colonne(s) de date reduite(s) "
        "au jour.",
        len(ajoutees), recopies, len(souplees), len(dates),
    )
    for titre, elements in (("ajoute", ajoutees), ("assoupli", souplees),
                            ("date normalisee", dates)):
        if elements:
            _log.info("027 %s: %s", titre, ", ".join(elements))


def downgrade() -> None:
    """Volontairement sans effet.

    Les colonnes ajoutees peuvent deja porter des donnees ecrites par l'app (un
    numero_compte renseigne, un company_id affecte) : les dropper detruirait ces
    valeurs. Une colonne en trop et NULLable ne casse aucun fonctionnement,
    alors qu'une donnee perdue est irreversible.
    """
    pass
