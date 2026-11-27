"""Tests chef personnel : pipeline recrutement."""
from datetime import datetime, timezone
import pytest

from app.models.chef_personnel_d_deep import ChpCandidateSelection, ChpInterviewSchedule
from app.services.chef_personnel_service import ChefPersonnelService


def _cand(db, candidat, poste, phase, statut, reference):
    c = ChpCandidateSelection(company_id=1, reference=reference,
                              candidat=candidat, poste=poste, phase=phase,
                              statut=statut, is_active=True)
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


def test_pipeline_par_phase(db):
    """2 en CV, 1 en entretien -> phases reparties."""
    _cand(db, "CAND-1", "Chauffeur", "cv", "en_cours", "S1")
    _cand(db, "CAND-2", "Chauffeur", "cv", "en_cours", "S2")
    _cand(db, "CAND-3", "Chauffeur", "entretien", "planifie", "S3")
    r = ChefPersonnelService.pipeline(db, poste="Chauffeur")
    assert r["candidats_total"] == 3
    assert r["par_phase"]["cv"] == 2
    assert r["par_phase"]["entretien"] == 1


def test_filtre_poste(db):
    _cand(db, "C1", "Comptable", "cv", "en_cours", "SP1")
    _cand(db, "C2", "Chauffeur", "cv", "en_cours", "SP2")
    r = ChefPersonnelService.pipeline(db, poste="Comptable")
    assert r["candidats_total"] == 1


def test_vide_honnete(db):
    r = ChefPersonnelService.pipeline(db, poste="PosteVide")
    assert r["candidats"] == 0
