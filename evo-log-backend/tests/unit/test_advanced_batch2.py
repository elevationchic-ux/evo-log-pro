"""Tests des modules avances Batch 2 : stubs 501 -> logique REELLE (DB/agregats)
ou connecteurs pilotes par la configuration.

On exerce les handlers DIRECTEMENT avec un TenantContext factice (la fixture
`client` authentifie un user sans organization_id/is_superadmin, donc les routers
a ténancy Organization/Company ne sont pas testables via HTTP ici). Les handlers
ne dependant que de (payload, context, db), l'appel direct est deterministe.

Principe Zero-Mock verifie : sur base vide, les aggregations renvoient de VRAIS
zeros (pas de chiffres inventes) ; les fonctions purement externes (LLM, OCR
image, DGI) renvoient une erreur explicite quand rien n'est configure.
"""
import asyncio
import hashlib
import types
from datetime import datetime, timedelta

import pytest
from fastapi import HTTPException

from app.models.documents import Document, SignatureDocument, SceauNumerique, AnalyseOCR
from app.models.advanced_crud import ScheduledReport, EInvoiceSignature, AIChatMessage, AIFeedback
from app.models.transport import Mission, MissionStatus, Conducteur
from app.models.parc import ZoneParc, EmplacementParc, MouvementParc
from app.routers.v1 import ged as ged_router
from app.routers.v1 import bi_advanced as bi_router
from app.routers.v1 import digital_twin as dt_router
from app.routers.v1 import gamification as gami_router
from app.routers.v1 import e_invoicing as ei_router
from app.routers.v1 import ai_assistant as ai_router
from app.routers.v1 import ai_predictive as aip_router


def _ctx(organization_id=None, user_id=1, company_id=None, superadmin=True):
    user = types.SimpleNamespace(
        id=user_id, is_superadmin=superadmin, organization_id=organization_id,
        company_id=company_id,
    )
    return types.SimpleNamespace(organization_id=organization_id, user=user)


class _FakeUpload:
    """Stub UploadFile minimal : async read(), filename, content_type."""
    def __init__(self, data: bytes, filename, content_type):
        self._data = data
        self.filename = filename
        self.content_type = content_type

    async def read(self):
        return self._data


# ---------------------------------------------------------------------------
# GED
# ---------------------------------------------------------------------------

def test_ged_upload_persiste_document_et_calcul_sha256(db):
    content = b"bonjour GED reel\n"
    file = _FakeUpload(content, "note.txt", "text/plain")
    out = asyncio.run(ged_router.upload_ged_document(
        title="Note test", category="CONTRAT", file=file,
        context=_ctx(), db=db,
    ))
    assert out["persiste"] is True
    assert out["checksum"] == hashlib.sha256(content).hexdigest()
    doc = db.query(Document).filter(Document.id == out["id"]).first()
    assert doc is not None
    assert doc.fichier == content
    assert doc.taille_octets == len(content)
    # liste retourne le document (superadmin voit tout)
    rows = ged_router.list_ged_documents(context=_ctx(), db=db)
    assert any(r["id"] == out["id"] for r in rows)


def test_ged_certifier_sceau_reel_non_qualifie(db):
    content = b"\x01\x02\x03 facture scellee"
    file = _FakeUpload(content, "f.bin", "application/octet-stream")
    out = asyncio.run(ged_router.upload_ged_document(
        title="A sceller", category="GENERAL", file=file, context=_ctx(), db=db,
    ))
    res = ged_router.certifier_document_numerique(
        {"document_id": out["id"]}, context=_ctx(), db=db,
    )
    assert res["empreinte_sha256"] == hashlib.sha256(content).hexdigest()
    assert res["type"] == "sceau_integrite_local"
    assert "qualifiee" in res["valeur_legale"].lower() or "AC" in res["valeur_legale"]
    assert db.query(SignatureDocument).filter(SignatureDocument.document_id == out["id"]).first() is not None
    assert db.query(SceauNumerique).filter(SceauNumerique.document_id == out["id"]).first() is not None


def test_ged_ocr_texte_reel_et_pas_d_invention(db):
    content = "livre de bord du 3 octobre\ncontainer TCLU1234567".encode("utf-8")
    file = _FakeUpload(content, "log.txt", "text/plain")
    out = asyncio.run(ged_router.upload_ged_document(
        title="Texte OCR", category="GENERAL", file=file, context=_ctx(), db=db,
    ))
    res = ged_router.extraire_metadonnees_ocr({"document_id": out["id"]}, context=_ctx(), db=db)
    assert "TCLU1234567" in res["texte_extrait"]
    assert res["longueur"] == len(content.decode("utf-8"))
    assert db.query(AnalyseOCR).filter(AnalyseOCR.id == res["analyse_id"]).first() is not None


def test_ged_audit_log_reel(db):
    content = b"audit me"
    file = _FakeUpload(content, "a.txt", "text/plain")
    out = asyncio.run(ged_router.upload_ged_document(
        title="Audit", category="GENERAL", file=file, context=_ctx(), db=db,
    ))
    log = ged_router.consulter_coffre_fort_audit(str(out["id"]), context=_ctx(), db=db)
    assert log["document_id"] == out["id"]
    assert any(e["action"] == "creation" for e in log["evenements"])


def test_ged_certifier_document_inexistant_404(db):
    with pytest.raises(HTTPException) as exc:
        ged_router.certifier_document_numerique({"document_id": 999999}, context=_ctx(), db=db)
    assert exc.value.status_code == 404


# ---------------------------------------------------------------------------
# BI advanced
# ---------------------------------------------------------------------------

def test_bi_dashboard_vide_vrais_zeros(db):
    out = bi_router.get_custom_bi_dashboard(period="THIS_MONTH", context=_ctx(), db=db)
    assert out["agrege_depuis_la_base"] is True
    assert out["transport"]["missions_total"] == 0
    assert out["transport"]["cout_reel_total"] == 0.0
    assert out["magasin"]["articles_en_rupture"] == 0


def test_bi_scheduled_report_persiste(db):
    payload = bi_router.ScheduledExportSchema(
        report_name="Mensuel direction", format="PDF", frequency="MONTHLY",
        recipients=["direction@tce.cm"],
    )
    out = bi_router.schedule_bi_export(payload, context=_ctx(organization_id=None), db=db)
    assert out["persiste"] is True
    assert db.query(ScheduledReport).filter(ScheduledReport.id == out["id"]).first() is not None
    assert out["prochaine_execution"] is not None
    rows = bi_router.list_scheduled_reports(context=_ctx(), db=db)
    assert any(r["id"] == out["id"] for r in rows)


def test_bi_predictif_saisonnier_sans_historique_ne_invente_rien(db):
    out = bi_router.predire_flux_saisonniers({"mois_cible": 9}, context=_ctx(), db=db)
    assert out["points_historiques"] == 0
    assert out["base_historique_suffisante"] is False
    assert out["prevision"] in (None, 0)


def test_bi_olap_vide(db):
    out = bi_router.interroger_cube_olap(
        dimension_temps="2026-Q1", dimension_corridor="DOUALA_NDJAMENA",
        context=_ctx(), db=db,
    )
    assert out["mesures"]["nombre_missions"] == 0


# ---------------------------------------------------------------------------
# Digital twin (jumeau numerique du parc)
# ---------------------------------------------------------------------------

def test_digital_twin_agrege_zones_reelles(db):
    z = ZoneParc(code="Z1", nom="Zone tampon", type_zone="stockage",
                 capacite=10, statut="actif", is_active=True)
    db.add(z); db.commit(); db.refresh(z)
    e1 = EmplacementParc(zone_id=z.id, code="E1", statut="occupe", is_active=True)
    e2 = EmplacementParc(zone_id=z.id, code="E2", statut="libre", is_active=True)
    db.add_all([e1, e2]); db.commit()
    db.add(MouvementParc(sens="entree")); db.commit()
    out = dt_router.get_digital_twin_yard_state(context=_ctx(), db=db)
    assert out["agrege_depuis_la_base"] is True
    assert out["total_zones"] >= 1
    assert out["emplacements"]["par_statut"].get("occupe") == 1
    assert out["emplacements"]["par_statut"].get("libre") == 1
    assert out["mouvements"]["entree"] == 1


def test_digital_twin_vide(db):
    out = dt_router.get_digital_twin_yard_state(context=_ctx(), db=db)
    assert out["emplacements"]["total"] == 0
    assert out["emplacements"]["taux_occupation_pct"] == 0.0


# ---------------------------------------------------------------------------
# Gamification (scores conducteurs depuis missions reelles)
# ---------------------------------------------------------------------------

def test_gamification_score_ponctualite_reel(db):
    c = Conducteur(nom="Mbarga", prenom="Alain")
    db.add(c); db.commit(); db.refresh(c)
    now = datetime.utcnow()
    # 2 missions terminees et ponctuelles -> score 100
    for i in range(2):
        m = Mission(
            conducteur_id=c.id, statut=MissionStatus.TERMINEE, distance_km=120.0,
            date_debut_prevue=now - timedelta(days=10 + i),
            date_fin_prevue=now - timedelta(days=9 + i),
            date_fin_reelle=now - timedelta(days=9 + i),  <= now - timedelta(days=9 + i),
        )
        db.add(m)
    db.commit()
    out = gami_router.get_driver_gamification_scores(context=_ctx(), db=db)
    entry = next((r for r in out["classement"] if r["conducteur_id"] == c.id), None)
    assert entry is not None
    assert entry["missions"] == 2
    assert entry["terminees"] == 2
    assert entry["taux_ponctualite"] == 100.0
    assert entry["score"] == 100.0


def test_gamification_eco_conduite_honnetement_absente(db):
    out = gami_router.get_driver_gamification_scores(context=_ctx(), db=db)
    assert "indisponible" in out["eco_conduite"].lower()


# ---------------------------------------------------------------------------
# E-invoicing (sceau SHA-256 reel + verification honnete)
# ---------------------------------------------------------------------------

def test_einvoice_sign_persiste_hash_reel(db):
    payload = ei_router.EInvoiceSignRequestSchema(
        invoice_number="EVO-INV-2026-0045", client_niu="M081912345678A",
        total_ht=1000000.0, total_tva=192500.0, total_ttc=1192500.0,
    )
    out = ei_router.sign_normalized_e_invoice(payload, context=_ctx(), db=db)
    expected = hashlib.sha256(
        "EVO-INV-2026-0045|M081912345678A|1000000.00|192500.00|1192500.00".encode()
    ).hexdigest()
    assert out["fiscal_hash"] == expected
    assert db.query(EInvoiceSignature).filter(
        EInvoiceSignature.fiscal_hash == expected
    ).first() is not None
    # sans connecteur DGI configure -> provider local, opposable = False
    assert out["provider"] == "local"
    assert out["opposable_dgi"] is False


def test_einvoice_verify_honnete(db):
    payload = ei_router.EInvoiceSignRequestSchema(
        invoice_number="EVO-INV-2026-0099", client_niu="N1", total_ht=100.0,
        total_tva=19.25, total_ttc=119.25,
    )
    signed = ei_router.sign_normalized_e_invoice(payload, context=_ctx(), db=db)
    ok = ei_router.verify_e_invoice(signed["fiscal_hash"], db=db)
    assert ok["valide"] is True and ok["statut"] == "VALID"
    bad = ei_router.verify_e_invoice("deadbeef" * 8, db=db)
    assert bad["valide"] is False and bad["statut"] == "INVALID"


# ---------------------------------------------------------------------------
# AI assistant
# ---------------------------------------------------------------------------

def test_ai_chat_503_sans_fournisseur(db, monkeypatch):
    monkeypatch.setattr("app.routers.v1.ai_assistant.llm_available", lambda: False)
    with pytest.raises(HTTPException) as exc:
        ai_router.chat_with_ai(
            ai_router.ChatMessage(message="combien de missions ?"),
            context=_ctx(), db=db,
        )
    assert exc.value.status_code == 503


def test_ai_chat_persiste_quand_fournisseur_dispo(db, monkeypatch):
    monkeypatch.setattr("app.routers.v1.ai_assistant.llm_available", lambda: True)
    monkeypatch.setattr("app.routers.v1.ai_assistant.ask_llm", lambda prompt, system=None: "42 missions")
    out = ai_router.chat_with_ai(
        ai_router.ChatMessage(message="combien de missions ?", session_id="s1"),
        context=_ctx(), db=db,
    )
    assert out["reponse"] == "42 missions"
    assert db.query(AIChatMessage).filter(AIChatMessage.id == out["message_id"]).first() is not None
    hist = ai_router.get_chat_history(session_id="s1", context=_ctx(), db=db)
    assert any(h["id"] == out["message_id"] for h in hist)


def test_ai_feedback_persiste(db):
    out = ai_router.submit_feedback(
        ai_router.FeedbackMessage(message_id=1, rating=4, commentaire="bien"),
        context=_ctx(), db=db,
    )
    assert out["persiste"] is True
    assert db.query(AIFeedback).filter(AIFeedback.id == out["feedback_id"]).first() is not None


def test_ai_suggestions_et_kpis_vrais_zeros(db):
    sug = ai_router.get_ai_suggestions(context=_ctx(), db=db)
    assert sug["derived_from_live_state"] is True
    kpis = ai_router.ai_kpis_summary(context=_ctx(), db=db)
    assert kpis["agrege_depuis_la_base"] is True
    assert kpis["missions"]["total"] == 0
    assert kpis["finance"]["creances_echues_xaf"] == 0.0


# ---------------------------------------------------------------------------
# AI predictive
# ---------------------------------------------------------------------------

def test_ai_predictive_forecast_sans_historique(db):
    out = aip_router.forecast_transport_demand(context=_ctx(), db=db)
    assert out["points"] == 0
    assert out["base_suffisante"] is False
    assert out["prevision_prochain_mois"] is None


def test_ai_predictive_fuel_anomalies_vide(db):
    out = aip_router.detect_fuel_anomalies(context=_ctx(), db=db)
    assert out["tickets_analyses"] == 0
    assert out["anomalies"] == []
    assert out["source_reelle"] is True


def test_ai_predictive_client_risk_sans_facture(db):
    out = aip_router.evaluate_client_risk_score(999, context=_ctx(), db=db)
    assert out["score"] is None
    assert "Aucune facture" in out["motif"]
