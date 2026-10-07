"""Tests Batch 3/4 : surfaces auparavant stubs 501 / succes fabrique, desormais
REELLES (persistance DB / agregation) ou connecteurs pilotes par la config.

Discipline Zero-Mock verifiee :
  - rh_avance : offres/candidatures/formations/inscriptions sont ecrites en base
    (ids auto-increments reels, plus jamais "id":101/501/12) ;
  - qhse permis de travail : aucune signature simulee, le permis ne devient ACTIF
    qu'apres la signature reelle du designe ;
  - bilan CSST/CNPS : aucun taux invente sans denominateur saisi ;
  - connecteur externe non configure -> 503 explicite (jamais un faux 200).

On exerce les SERVICES directement avec un utilisateur factice et la fixture
`db` (SQLite memoire, FK non enforcees) : deterministe, sans dependance HTTP.
"""
import types
from datetime import date, timedelta

import pytest
from fastapi import HTTPException

from app.models.rh import (
    Formation, ParticipationFormation, OffreEmploi, Candidature,
)
from app.models.qhse import PermisTravail, SignaturePermis
from app.models.user import User
from app.services.rh_avance_service import RecrutementService, FormationService
from app.services.qhse_service import WorkPermitsIMDGService
from app.utils.external import call_provider


def _user(db, uid, username, company_id=1, active=True):
    u = User(
        id=uid, username=username, email=f"{username}@test.local",
        hashed_password="x", full_name=username.title(), is_active=active,
        company_id=company_id,
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


# ── RH AVANCE : persistance reelle (plus de faux ids) ────────────────────────
def test_creer_offre_persiste_reellement(db):
    offre = RecrutementService.creer_offre_emploi(
        db, titre="Chef de quai", departement="Exploitation",
        description="Pilote les operations", type_contrat="CDI",
        competences_requises=["ISPS", "HSE"],
    )
    assert offre.id is not None and offre.id > 0
    assert offre.statut == "PUBLIEE"
    # relisible en base
    relu = db.query(OffreEmploi).filter(OffreEmploi.id == offre.id).first()
    assert relu is not None and relu.titre == "Chef de quai"


def test_candidature_sur_offre_inexistante_refusee(db):
    with pytest.raises(ValueError):
        RecrutementService.enregistrer_candidature(
            db, offre_id=99999, candidat_nom="X", email="x@y.z", telephone="600")


def test_candidature_persistee_et_traitee(db):
    offre = RecrutementService.creer_offre_emploi(
        db, titre="Manutentionnaire", departement="Quai", description="...")
    cand = RecrutementService.enregistrer_candidature(
        db, offre_id=offre.id, candidat_nom="A", email="a@b.c", telephone="699")
    assert cand.statut == "RECU"
    # decision reelle ecrite en base
    traite = RecrutementService.traiter_candidature(db, cand.id, "EMBAUCHE", notes="OK")
    assert traite.statut == "EMBAUCHE" and traite.date_decision == date.today()
    # decision invalide refusee
    with pytest.raises(ValueError):
        RecrutementService.traiter_candidature(db, cand.id, "FAKE")


def test_plan_formation_persiste(db):
    f = Formation(
        titre="Habilitation électrique", description="[SECURITE_PORTUAIRE] recyclage",
        date_debut=date(2026, 10, 1), date_fin=date(2026, 10, 2),
        duree_heures=14, cout=50000, formateur="Organisme X", statut="planifiee",
    )
    db.add(f)
    db.commit()
    db.refresh(f)
    assert f.id > 0
    assert db.query(Formation).filter(Formation.id == f.id).first() is not None


def test_inscrire_formation_reelle_et_doublon(db):
    u = _user(db, 501, "stagiaire1")
    f = Formation(
        titre="Securite-incendie", description="d", date_debut=date(2026, 11, 1),
        date_fin=date(2026, 11, 1), duree_heures=7, cout=0, statut="planifiee",
    )
    db.add(f)
    db.commit()
    db.refresh(f)

    part = FormationService.inscrire_formation(db, u.id, f.id)
    assert part.id > 0 and part.formation_id == f.id
    # doublon honnetement signale, compteur non gonfle
    with pytest.raises(RuntimeError):
        FormationService.inscrire_formation(db, u.id, f.id)
    # employe inexistant signale
    with pytest.raises(ValueError):
        FormationService.inscrire_formation(db, 999999, f.id)


# ── QHSE PERMIS : aucune signature simulee ───────────────────────────────────
def _current_user(db):
    return _user(db, 700, "officier700")


def test_permis_cre_en_attente_puis_actif_apres_signature_reelle(db):
    cu = _current_user(db)
    out = WorkPermitsIMDGService.creer_permis_travail(
        db,
        {"type_permis": "feu", "zone": "Quai 3", "description": "Soudure",
         "mesures_preventives": "Extincteur"},
        cu,
    )
    assert out["statut"] == "EN_ATTENTE_SIGN"
    assert out["signatures"] == []  # rien n'est appose a la creation

    signe = WorkPermitsIMDGService.signer_permis(db, out["id"], cu)
    assert signe["statut"] == "ACTIF"
    assert len(signe["signatures"]) == 1
    assert signe["signatures"][0]["signataire_id"] == cu.id

    # re-signature du meme user -> conflit, pas de doublon
    with pytest.raises(HTTPException) as exc:
        WorkPermitsIMDGService.signer_permis(db, out["id"], cu)
    assert exc.value.status_code == 409


def test_permis_refuse_champs_manquants(db):
    cu = _current_user(db)
    with pytest.raises(HTTPException) as exc:
        WorkPermitsIMDGService.creer_permis_travail(db, {"type_permis": "feu"}, cu)
    assert exc.value.status_code == 400


def test_bilan_sans_heures_aucun_taux_invente(db):
    bilan = WorkPermitsIMDGService.bilan_annuel_csst_cnps(db, 2026)
    assert bilan.get("heures_non_saisies") is True
    assert bilan.get("taux_frequence_TF_par_million_h") is None
    assert bilan.get("taux_gravite_TG_par_million_h") is None
    assert "avertissement" in bilan


# ── Connecteurs externes : non configure -> 503, jamais un faux succes ───────
def test_fournisseur_non_configure_503(monkeypatch):
    from app.core import config
    # S'assurer qu'aucun fournisseur SMS n'est declare dans ce contexte de test.
    monkeypatch.setattr(config.settings, "SMS_ENABLED", False, raising=False)
    monkeypatch.setattr(config.settings, "SMS_API_URL", "", raising=False)
    monkeypatch.setattr(config.settings, "SMS_API_KEY", "", raising=False)
    with pytest.raises(HTTPException) as exc:
        call_provider("SMS", "Envoi d'un SMS de notification", payload={"to": "+237"})
    assert exc.value.status_code == 503
