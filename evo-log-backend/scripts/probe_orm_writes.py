"""Preuve avant/apres de la migration 027 sur une base donnee.

Tente, via les modeles ORM eux-memes, ce que font reellement les endpoints :
lire et inserer une ligne dans chaque table touchee par le drift (comptes,
factures, ecritures_comptables, camions, stocks, users, companies). Chaque
operation est rollbockee : la base n'est jamais modifiee.

Sortie : une ligne par table, OK ou le message d'erreur SQL brut.

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
from app.models.comptabilite import Compte, EcritureComptable, Facture, Paiement  # noqa: E402
from app.models.tenant import Camion, Stock, User  # noqa: E402


# (libelle, fabrique d'instance) -- uniquement des colonnes reellement exigees
# par le modele ; aucun champ n'est garni "pour que ça passe".
ECRITURES = [
    ("comptes", lambda: Compte(numero_compte="541100", nom_compte="Client test")),
    ("factures", lambda: Facture(numero_facture="FA-TEST-0001")),
    ("ecritures_comptables", lambda: EcritureComptable(
        reference="EC-TEST-0001", compte_debit=1, compte_credit=1,
        montant_debit=1000)),
    ("paiements", lambda: Paiement(montant=1000)),
    ("camions", lambda: Camion(immatriculation="PROBE-01")),
    ("stocks", lambda: Stock(nom="Probe stock")),
    ("users", lambda: User(email="probe@example.com", hashed_password="x")),
]


def sonder(url: str):
    engine = create_engine(url)
    Session = sessionmaker(bind=engine)
    print(f"base sondée : {url}")
    echecs = 0
    for table, fabrique in ECRITURES:
        session = Session()
        try:
            # LECTURE : c'est elle qui leve "no such column" sur les bases
            # migratees, bien avant toute ecriture.
            session.query(table).limit(1).all()
            session.add(fabrique())
            session.flush()          # l'INSERT part really a la base ici
            echec = None
        except Exception as exc:     # noqa: BLE001 - on rapporte, on ne reussit pas
            echec = str(exc).splitlines()[0][:160]
            echecs += 1
        finally:
            session.rollback()
            session.close()
        print(("   OK      " if echec is None else "   ECHEC   ") + table
              + (f"\n            {echec}" if echec else ""))
    print(f"\n{echecs} table(s) inaccessible(s) sur cette base.")
    return echecs


if __name__ == "__main__":
    db = sys.argv[1] if len(sys.argv) > 1 else str(ROOT / "kamlog_erp.db")
    url = db if db.startswith(("sqlite", "postgresql")) else f"sqlite:///{db}"
    sys.exit(1 if sonder(url) else 0)
