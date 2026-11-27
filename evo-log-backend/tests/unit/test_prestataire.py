"""Tests prestataires : homologation et cotations."""
import pytest
from decimal import Decimal

from app.models.prestataire import Prestataire, DemandeCotation
from app.services.prestataire_service import PrestataireService


def _prov(db, code, specialite, homologue=True, statut="VALIDE",
          note=4.5, ponct=95.0, reference=None):
    p = Prestataire(company_id=1, code=code, raison_sociale=f"Prov {code}",
                    specialite=specialite, est_homologue=homologue,
                    statut_agrement=statut, note_globale=note,
                    taux_ponctualite=ponct, est_actif=True,
                    contact_telephone="699000000")
    db.add(p)
    db.commit()
    db.refresh(p)
    db.get(Prestataire, p.id)  # ensure persisted
    return p


def _dem(db, numero, budget, reponse=None, statut="EN_ATTENTE"):
    d = DemandeCotation(company_id=1, numero_dossier=numero,
                        prestataire_id=1, demandeur_id=1,
                        titre_besoin="Besoin", description_besoin="Desc",
                        lieu_intervention="Douala",
                        budget_max_estime=Decimal(str(budget)) if budget else None,
                        reponse_montant=Decimal(str(reponse)) if reponse else None,
                        statut=statut)
    db.add(d)
    db.commit()
    db.refresh(d)
    return d


def test_homologues(db):
    """1 homologue valide, 1 non homologue."""
    _prov(db, "PR-1", "Acconage", homologue=True, statut="VALIDE", note=4.8)
    _prov(db, "PR-2", "Acconage", homologue=False, statut="EXPIRE", note=4.0)
    r = PrestataireService.homologues(db, specialite="Acconage")
    assert r["prestataires_total"] == 2
    assert r["homologues_valides"] == 1
    assert r["non_homologues"] == 1
    assert r["par_niveau"][0]["code"] == "PR-1"


def test_cotations_depassement(db):
    """1 depassement budget (150k > 100k)."""
    _dem(db, "DC-1", 100_000, reponse=150_000, statut="CHIFFRE")
    _dem(db, "DC-2", 200_000, reponse=180_000, statut="CHIFFRE")
    _dem(db, "DC-3", 50_000, statut="EN_ATTENTE")
    r = PrestataireService.cotations(db)
    assert r["demandes_total"] == 3
    assert r["depassements_budget"] == 1
    assert r["en_attente"] == 1


def test_vide_honnete(db):
    r = PrestataireService.homologues(db, specialite="Inconnue")
    assert r["prestataires"] == 0
