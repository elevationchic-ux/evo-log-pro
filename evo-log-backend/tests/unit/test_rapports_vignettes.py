"""Tests rapports notifications/documents : vides honnetes."""
from app.services.notifications_service import NotificationsReportingService
from app.services.documents_service import DocumentsReportingService


def test_rapport_notifications_vide(db):
    r = NotificationsReportingService.rapport_notifications(db, utilisateur_id=999999)
    assert r["total_notifications"] == 0
    assert r["par_canal"] == {}
    assert r["par_statut"] == {}
    assert r["non_lues"] == 0


def test_rapport_documents_vide(db):
    r = DocumentsReportingService.rapport_documents(db, dossier_id=999999)
    assert r["total_documents"] == 0
    assert r["par_type"] == {}
    assert r["taille_totale"] == 0
