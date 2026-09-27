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


if __name__ == "__main__":
    db = sys.argv[1] if len(sys.argv) > 1 else str(ROOT / "kamlog_erp.db")
    url = db if db.startswith(("sqlite:", "postgresql")) else f"sqlite:///{db}"
    sys.exit(1 if sonder(url) else 0)
