"""Tests acquisition : notation ponderee des offres fournisseurs."""
from datetime import date
from decimal import Decimal

from app.models.acquisition import Offre, CritereEvaluation
from app.services.acquisition_service import OffreService


def _offre(db, numero="OFF-001"):
    o = Offre(numero_offre=numero, appel_offres_id=None, fournisseur_id=None,
              montant_total=Decimal("1000000"), delai_livraison=30,
              statut="recu")
    db.add(o)
    db.commit()
    db.refresh(o)
    return o


def test_evaluer_offre_calcule_note_ponderee(db):
    """note 16 x poids 40 % = note ponderee 6.4."""
    offre = _offre(db)
    ev = OffreService.evaluer_offre(
        db, offre.id, CritereEvaluation.QUALITE,
        note=16.0, poids=40.0, evaluateur="Acheteur A")

    assert float(ev.note) == 16.0
    assert float(ev.poids) == 40.0
    assert float(ev.note_ponderee) == 6.4
    assert ev.date_evaluation == date.today()


def test_evaluer_offre_plusieurs_criteres(db):
    """Prix 20/20 poids 60 % + qualite 12/20 poids 40 % = score 16.8."""
    offre = _offre(db, numero="OFF-002")
    OffreService.evaluer_offre(
        db, offre.id, CritereEvaluation.PRIX, note=20.0, poids=60.0, evaluateur="A")
    OffreService.evaluer_offre(
        db, offre.id, CritereEvaluation.QUALITE, note=12.0, poids=40.0, evaluateur="A")

    from app.models.acquisition import EvaluationOffre
    evals = db.query(EvaluationOffre).filter(EvaluationOffre.offre_id == offre.id).all()
    score = sum(float(e.note_ponderee) for e in evals)
    assert abs(score - 16.8) < 0.01
