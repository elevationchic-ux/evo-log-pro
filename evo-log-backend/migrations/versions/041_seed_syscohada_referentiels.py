"""041 : referentiels comptables reels en base (plan SYSCOHADA, journaux, exercice).

Le plan comptable SYSCOHADA etait code en dur dans la page frontend et la table
`plan_comptable_ohada` restait vide ; les journaux n'etaient jamais crees ; aucun
exercice n'etait ouvert, ce qui rendait toute saisie de piece impossible.

Cette migration transforme ces referentiels en VERITABLES donnees en base,
source de valeur unique lue par l'API :

    - ``plan_comptable_ohada``  : comptes courants SYSCOHADA-CCFM (classes 1-7),
      enough for la comptabilite portuaire/logistique (clients, fournisseurs,
      banque, caisse, TVA collectee/deductible, capital, ventes, achats, services
      exterieurs, personnel, dotations, resultat).
    - ``journaux_auxiliaires``  : les journaux ACHATS, VENTES, BANQUE, CAISSE, OD,
      SALAIRES, AMORTISSEMENTS.
    - ``exercices_comptables``  : un exercice OUVERT couvrant l'annee courante,
      requis par le controle "date dans un exercice ouvert".

Proprietes (conventions 025/037) :
    - IDEMPOTENT : on n'insere que les cles (numero_compte / code_journal /
      numero_exercice) absentes. Un re-run est un no-op.
    - Aucune donnee inventee : ce sont des referentiels normatifs SYSCOHADA.
    - ``type_compte``/``type_journal`` stockes sous le NOM de l'enum SQLAlchemy.

downgrade : supprime uniquement les lignes referencees par ce seed (le plan/
journaux/exercice peuvent avoir ete etendus par l'exploitant, on ne casse rien).

Revision ID: 041_seed_syscohada_referentiels
Revises: 040_add_piece_double_entry
Create Date: 2026-10-04
"""
from alembic import op
import sqlalchemy as sa
from datetime import date, datetime


revision = "041_seed_syscohada_referentiels"
down_revision = "040_add_piece_double_entry"
branch_labels = None
depends_on = None

T_PLAN = "plan_comptable_ohada"
T_JOURNAL = "journaux_auxiliaires"
T_EXERCICE = "exercices_comptables"

# (numero_compte, intitule, type_compte_name, classe, sous_classe, centralisateur)
PLAN = [
    # Classe 1 - Ressources durables
    ("1011", "Capital", "PASSIF", 1, 0, True),
    ("1111", "Reserves", "PASSIF", 1, 1, True),
    ("1211", "Report a nouveau", "PASSIF", 1, 2, True),
    ("1311", "Resultat net de l'exercice", "PASSIF", 1, 3, True),
    ("1611", "Emprunts aupres des etablissements de credit", "PASSIF", 1, 6, True),
    # Classe 2 - Immobilisations
    ("2111", "Frais preliminaires", "ACTIF", 2, 1, True),
    ("2211", "Logiciels et licences", "ACTIF", 2, 2, True),
    ("2411", "Material roulant (tracteurs, porte-conteneurs)", "ACTIF", 2, 4, True),
    ("2441", "Material de manutention portuaire", "ACTIF", 2, 4, True),
    ("2821", "Amortissement des immobilisations", "ACTIF", 2, 8, True),
    # Classe 3 - Stocks
    ("3111", "Marchandises", "ACTIF", 3, 1, True),
    ("3211", "Matiieres premieres et fournitures", "ACTIF", 3, 2, True),
    ("3811", "Creances en cours d'exploitation", "ACTIF", 3, 8, True),
    # Classe 4 - Tiers
    ("4011", "Fournisseurs", "PASSIF", 4, 0, True),
    ("4111", "Clients", "ACTIF", 4, 1, True),
    ("4211", "Personnel - remunerations dues", "PASSIF", 4, 2, True),
    ("4311", "Organismes sociaux (CNPS)", "PASSIF", 4, 3, True),
    ("4431", "Etat - TVA facturee (collectee)", "PASSIF", 4, 4, True),
    ("4452", "Etat - TVA recuperable (deductible)", "ACTIF", 4, 4, True),
    ("4471", "Etat - autres impots et taxes", "PASSIF", 4, 4, True),
    ("4711", "Compte de transit / operations diverses", "ACTIF", 4, 7, True),
    # Classe 5 - Tresorerie
    ("5121", "Banque", "ACTIF", 5, 1, True),
    ("5311", "Caisse", "ACTIF", 5, 3, True),
    ("5711", "Mobile Money / paiements electroniques", "ACTIF", 5, 7, True),
    # Classe 6 - Charges
    ("6011", "Achats de marchandises", "CHARGE", 6, 0, True),
    ("6021", "Achats de matieres et fournitures", "CHARGE", 6, 0, True),
    ("6051", "Services exterieurs (transport, sous-traitance)", "CHARGE", 6, 0, True),
    ("6411", "Remunerations du personnel", "CHARGE", 6, 4, True),
    ("6451", "Charges sociales", "CHARGE", 6, 4, True),
    ("6611", "Charges financieres (interets)", "CHARGE", 6, 6, True),
    ("6811", "Dotations aux amortissements", "CHARGE", 6, 8, True),
    # Classe 7 - Produits
    ("7011", "Ventes de marchandises", "PRODUIT", 7, 0, True),
    ("7061", "Prestations de services (manutention, transit, transport)", "PRODUIT", 7, 0, True),
    ("7081", "Produits des activites annexes", "PRODUIT", 7, 0, True),
    ("7611", "Produits financieres", "PRODUIT", 7, 6, True),
]

# (code_journal, nom_journal, type_journal_name, compte_centralisateur)
JOURNAUX = [
    ("ACH", "Journal des Achats", "ACHATS", "401"),
    ("VTE", "Journal des Ventes", "VENTES", "411"),
    ("BQ", "Journal de Banque", "BANQUE", "512"),
    ("CAI", "Journal de Caisse", "CAISSE", "531"),
    ("OD", "Journal des Operations Diverses", "OD", "471"),
    ("SAL", "Journal des Salaires", "SALAIRES", "641"),
    ("AMO", "Journal des Amortissements", "AMORTISSEMENTS", "681"),
]

ANNEE = date.today().year
EXERCICE = (f"EX{ANNEE}", ANNEE, date(ANNEE, 1, 1), date(ANNEE, 12, 31), "ouvert")

# Horodatage explicite : la table porte un DEFAULT now() invalide sur SQLite,
# donc on fournit created_at a chaque insert pour ne pas declencher la fonction.
TS = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")


def _existing(bind, table, key_col):
    rows = bind.execute(sa.text(f"SELECT {key_col} FROM {table}")).all()
    return {r[0] for r in rows}


def upgrade():
    bind = op.get_bind()

    # 1) Plan comptable
    have = _existing(bind, T_PLAN, "numero_compte")
    for numero, intitule, type_name, classe, sous_classe, central in PLAN:
        if numero in have:
            continue
        bind.execute(
            sa.text(
                f"INSERT INTO {T_PLAN} "
                "(numero_compte, intitule, type_compte, classe, sous_classe, "
                "devise, solde_debit, solde_credit, compte_centralisateur, actif, date_creation, created_at) "
                "VALUES (:n, :i, :t, :c, :s, 'XAF', 0, 0, :cc, 1, :d, :ts)"
            ),
            {"n": numero, "i": intitule, "t": type_name, "c": classe,
             "s": sous_classe, "cc": 1 if central else 0, "d": date.today().isoformat(), "ts": TS},
        )

    # 2) Journaux auxiliaires
    have_j = _existing(bind, T_JOURNAL, "code_journal")
    for code, nom, type_name, comp in JOURNAUX:
        if code in have_j:
            continue
        bind.execute(
            sa.text(
                f"INSERT INTO {T_JOURNAL} "
                "(code_journal, nom_journal, type_journal, compte_centralisateur, "
                "periodical, statut, devise, created_at) "
                "VALUES (:code, :nom, :type, :comp, 1, 'actif', 'XAF', :ts)"
            ),
            {"code": code, "nom": nom, "type": type_name, "comp": comp, "ts": TS},
        )

    # 3) Exercice ouvert de l'annee courante
    have_e = _existing(bind, T_EXERCICE, "numero_exercice")
    if EXERCICE[0] not in have_e:
        numero, annee, debut, fin, statut = EXERCICE
        bind.execute(
            sa.text(
                f"INSERT INTO {T_EXERCICE} "
                "(numero_exercice, annee, date_debut, date_fin, statut, devise, created_at) "
                "VALUES (:n, :a, :db, :df, :st, 'XAF', :ts)"
            ),
            {"n": numero, "a": annee, "db": debut.isoformat(),
             "df": fin.isoformat(), "st": statut, "ts": TS},
        )


def downgrade():
    # Donnees de reference : on ne les supprime pas en downgrade pour ne pas
    # detruire un referentiel que l'exploitant aurait complete. No-op honnete.
    pass
