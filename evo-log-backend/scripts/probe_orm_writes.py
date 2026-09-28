"""Preuve avant/apres de la migration 027 sur une base donnee.

Tente, avec les modeles ORM eux-memes, ce que font reellement les endpoints :
lire puis inserer une ligne dans chaque table touchee par le drift. Chaque
tentative est annulee par un rollback : la base sondée n'est jamais modifiee.

La LECTURE prime : c'est elle qui leve "no such column: camions.company_id" sur
une base pilotee par Alembic, bien avant toute ecriture. Sans 027, les tables
recreees par create_all() masquent le probleme en base de developpement.

Usage :
    python scripts/probe_orm_writes.py [chemin/vers/base.db]
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402

import app.models  # noqa: F401,E402  (enregistre toutes les tables)
from app.models.finance import Compte, EcritureComptable, Facture, Paiement  # noqa: E402
from app.models.magasin import Stock  # noqa: E402
from app.models.transport import Camion  # noqa: E402
from app.models.user import User  # noqa: E402


# Colonnes obligees uniquement (nullable=False sans defaut, hors cle primaire),
# d'apres l'ORM : rien n'est garni "pour que cela passe".
SONDES = [
    (Compte, dict(numero_compte="541100", nom_compte="Compte sondes")),
    (Facture, dict(numero_facture="FT-SONDE", montant_ht=1000, montant_ttc=1192)),
    (EcritureComptable, dict(libelle="Ecriture sonde")),
    (Paiement, dict(facture_id=1, montant=1000)),
    (Camion, dict(immatriculation="SONDE-01")),
    (Stock, dict(code_article="SONDE-A1", designation="Article sonde")),
    (User, dict(username="sonde", email="sonde@example.com",
                hashed_password="x")),
]


def sonder(url: str) -> int:
    engine = create_engine(url)
    Session = sessionmaker(bind=engine)
    print(f"base sondée : {url}")
    echecs = 0
    for classe, valeurs in SONDES:
        table = classe.__table__.name
        session = Session()
        erreur = None
        try:
            session.query(classe).limit(1).all()
            session.add(classe(**valeurs))
            session.flush()          # l'INSERT part vraiment en base ici
        except Exception as exc:     # noqa: BLE001 - on rapporte, on ne maquille pas
            erreur = str(exc).splitlines()[0][:170]
            echecs += 1
        finally:
            session.rollback()
            session.close()
        etat = "OK    " if erreur is None else "ECHEC "
        print(f"   {etat} {table}" + (f"\n         {erreur}" if erreur else ""))
    print(f"\n{echecs} table(s) inaccessible(s) sur cette base.")
    return echecs


def sonde_lecture_globale(url: str) -> int:
    """LIT une ligne de CHAQUE table mappee, avec les modeles de l'app.

    Complement indispensable de l'audit de parite : l'audit compare des
    declarations, la sonde execute la requete. Un lien `relationship()` casse,
    une table mappee deux fois ou une colonne absente ne se voient qu'en
    levant la question a la base. C'est aussi le plus court chemin vers un 500 :
    `list(x)=Select(...)` echoue avant la moindre logique metier.

    Chaque module de app/models est importe (memo que audit_schema_drift.py et
    la migration 028) : app.models.__init__ seul ne declare qu'une partie des
    modeles, et le reste resterait silencieusement non sonde.
    """
    import importlib

    for fichier in sorted((ROOT / "app" / "models").glob("*.py")):
        if fichier.name == "__init__.py":
            continue
        try:
            importlib.import_module("app.models.%s" % fichier.name[:-3])
        except Exception as exc:  # noqa: BLE001 - le rapport le dira
            print("   MODULE NON IMPORTABLE app/models/%s : %s" % (fichier.name, exc))

    from sqlalchemy.orm import configure_mappers

    engine = create_engine(url)
    from sqlalchemy.orm import sessionmaker as _fab
    session = _fab(bind=engine)()
    echecs = 0
    try:
        configure_mappers()
    except Exception as exc:  # noqa: BLE001
        print("   MAPPAGE IMPOSSIBLE : %s" % str(exc).splitlines()[0][:200])
        echecs += 1

    from app.core.database import Base
    mappers = list(Base.registry.mappers)
    print("tables mappees sondees : %d" % len(mappers))
    for mapper in sorted(mappers, key=lambda m: m.local_table.name):
        nom = mapper.local_table.name
        try:
            session.query(mapper.class_).limit(1).all()
        except Exception as exc:  # noqa: BLE001
            session.rollback()
            print("   ECHEC LECTURE %-34s %s" % (nom, str(exc).splitlines()[0][:150]))
            echecs += 1
    session.close()
    print("\nSonde de lecture : %d echec(s)." % echecs)
    return echecs


if __name__ == "__main__":
    # Les flags ne sont pas des chemins : sans ce filtre, `--lecture` etait
    # pris pour la base et la sonde creait un fichier SQLite vide nomme
    # '--lecture' a cote du vrai depot.
    options = [a for a in sys.argv[1:] if a.startswith("-")]
    positions = [a for a in sys.argv[1:] if not a.startswith("-")]
    lecture = "--lecture" in options
    db = positions[0] if positions else str(ROOT / "kamlog_erp.db")
    url = db if db.startswith(("sqlite:", "postgresql")) else f"sqlite:///{db}"
    ecarts = sonde_lecture_globale(url) if lecture else sonder(url)
    sys.exit(1 if ecarts else 0)
