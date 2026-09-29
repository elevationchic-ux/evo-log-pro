import os
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
from datetime import date
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base, get_db
import app.main  # noqa: enregistre TOUS les modeles (lecon conftest)
from app.models.magasin import Stock, Entrepot
from app.models.magasin_avance import (
    BonReception, CommandeFournisseur, LigneCommandeFournisseur)
from app.models.tiers import Fournisseur
from app.routers.v1 import magasin_avance as rv
from app.core.security import get_current_user

engine = create_engine("sqlite://", connect_args={"check_same_thread": False},
                       poolclass=__import__("sqlalchemy.pool", fromlist=["StaticPool"]).StaticPool)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine, autoflush=True)
db = Session()

app = FastAPI()
app.include_router(rv.router, prefix="/api/v1/magasin-avance")
app.dependency_overrides[get_current_user] = lambda: type(
    "U", (), {"id": 1, "company_id": None, "is_superuser": True, "role_level": 0})()
app.dependency_overrides[get_db] = lambda: db
c = TestClient(app)

ent = Entrepot(code="E1", nom="n"); db.add(ent); db.commit()
frs = Fournisseur(code="F1", name="n"); db.add(frs); db.commit()
st = Stock(code_article="A1", designation="d", quantite_disponible=0,
           entrepot_id=ent.id); db.add(st); db.commit()
cmd = CommandeFournisseur(numero_commande="C1", fournisseur_id=frs.id,
                          statut="en_cours"); db.add(cmd); db.commit()
lc = LigneCommandeFournisseur(commande_id=cmd.id, stock_id=st.id,
                              quantite_commandee=20, prix_unitaire=1500,
                              quantite_recue=0, statut="en_attente")
db.add(lc); db.commit()

b = c.post("/api/v1/magasin-avance/receptions",
           json={"fournisseur_id": frs.id, "entrepot_id": ent.id,
                 "commande_fournisseur_id": cmd.id})
print("bon:", b.status_code)
bid = b.json()["id"]
l = c.post(f"/api/v1/magasin-avance/receptions/{bid}/lignes",
           json={"stock_id": st.id, "quantite_recue": 20,
                 "quantite_commandee": 20})
print("ligne:", l.status_code)
v = c.put(f"/api/v1/magasin-avance/receptions/{bid}/valider")
print("valider:", v.status_code, v.json().get("statut") if v.status_code == 200 else v.text)

db.expire_all()
lc2 = db.query(LigneCommandeFournisseur).get(lc.id)
print("lc.statut:", lc2.statut, "lc.quantite_recue:", lc2.quantite_recue)
cmd2 = db.query(CommandeFournisseur).get(cmd.id)
print("cmd.statut:", cmd2.statut)
remaining = db.query(LigneCommandeFournisseur).filter(
    LigneCommandeFournisseur.commande_id == cmd.id,
    LigneCommandeFournisseur.statut != "recu").count()
print("remaining != recu:", remaining)
print("all lines:", [(x.statut, float(x.quantite_recue or 0))
                     for x in db.query(LigneCommandeFournisseur).filter(
                         LigneCommandeFournisseur.commande_id == cmd.id).all()])
