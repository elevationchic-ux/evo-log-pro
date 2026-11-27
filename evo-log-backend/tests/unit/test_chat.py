"""Tests chat : annonces et signalements."""
import pytest

from app.models.chat_d5_deep import ChtAnnouncement, ChtContentReport
from app.services.chat_service import ChatService


def _ann(db, reference, cible, epingle=False):
    a = ChtAnnouncement(company_id=1, reference=reference, titre="Annonce",
                        cible=cible, epingle=epingle, is_active=True)
    db.add(a)
    db.commit()
    db.refresh(a)
    return a


def _rep(db, reference, statut="en_attente"):
    r = ChtContentReport(company_id=1, reference=reference, statut=statut,
                         is_active=True)
    db.add(r)
    db.commit()
    db.refresh(r)
    return r


def test_annonces_par_cible(db):
    """2 pour tous, 1 pour transport, 1 epinglee."""
    _ann(db, "AN-1", "tous")
    _ann(db, "AN-2", "tous", epingle=True)
    _ann(db, "AN-3", "transport")
    r = ChatService.annonces(db)
    assert r["annonces_total"] == 3
    assert r["par_cible"]["tous"] == 2
    assert r["epinglees"] == 1


def test_annonces_filtre(db):
    _ann(db, "AN-4", "magasin")
    r = ChatService.annonces(db, cible="magasin")
    assert r["annonces_total"] == 1


def test_signalements(db):
    _rep(db, "SR-1", "en_attente")
    _rep(db, "SR-2", "traite")
    r = ChatService.signalements(db)
    assert r["signalements_total"] == 2
    assert r["en_attente"] == 1
