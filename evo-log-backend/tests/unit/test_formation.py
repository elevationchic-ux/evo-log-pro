"""Tests formation : suivi certifications expirees/a renouveler."""
from datetime import date, timedelta
import pytest

from app.models.formation import CertificationUtilisateur, StatutCertification
from app.services.formation_service import FormationService


def _cert(db, user, module, expiration, statut=StatutCertification.REUSSI):
    c = CertificationUtilisateur(utilisateur_id=user, module_id=module,
                                 date_passage=date.today(), score=80,
                                 score_maximum=100, pourcentage=80,
                                 statut=statut, date_expiration=expiration)
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


def test_certifications_expirees(db):
    """1 expiree, 1 a renouveler (20j), 1 valide, 1 sans date."""
    _cert(db, 1, 1, date.today() - timedelta(days=5))
    _cert(db, 2, 1, date.today() + timedelta(days=20))
    _cert(db, 3, 1, date.today() + timedelta(days=200))
    _cert(db, 4, 1, None)
    r = FormationService.suivi_certifications(db)
    assert r["expirees"] == 1
    assert r["a_renouveler"] == 1
    assert r["valides"] == 1
    assert r["sans_date_expiration"] == 1


def test_vide_honnete(db):
    r = FormationService.suivi_certifications(db)
    assert r["total_certifications"] == 0
