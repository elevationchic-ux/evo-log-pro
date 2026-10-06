"""Tests des modules avances passés de stub 501 à CRUD réel (Batch 1).

On exerce les handlers directement avec un TenantContext factice : la fixture
`client` fournit un faux user SANS organization_id/is_superadmin, donc les
routers à ténancy Organization ne sont pas testables via HTTP ici. Les handlers
ne dépendent que de (payload, context, db) -> appel direct deterministe.
"""
import hashlib
import types
from datetime import date

import pytest

from app.models.advanced_crud import (
    CRMOpportunity, Project, FixedAsset, FreightOffer, TenantAPIKey,
)
from app.routers.v1 import crm as crm_router
from app.routers.v1 import projects as projects_router
from app.routers.v1 import fixed_assets as fixed_assets_router
from app.routers.v1 import freight_exchange as freight_router
from app.routers.v1 import marketplace as marketplace_router


def _ctx(organization_id=None, user_id=1):
    user = types.SimpleNamespace(id=user_id, is_superadmin=True, organization_id=organization_id)
    return types.SimpleNamespace(organization_id=organization_id, user=user)


def test_crm_create_then_list_persiste(db):
    payload = crm_router.OpportunitySchema(
        client_name="Brasseries du Cameroun",
        title="Contrat annuel vrac",
        estimated_value=45000000.0,
        stage="NEGOTIATION",
        probability=70,
        contact_person="Alain Mbarga",
        contact_email="a@b.cm",
    )
    created = crm_router.create_crm_opportunity(payload, context=_ctx(), db=db)
    assert created.id is not None
    assert created.stage == "NEGOTIATION"
    rows = crm_router.list_crm_opportunities(context=_ctx(), db=db)
    assert any(r.id == created.id for r in rows)
    # reellement en base, pas en memoire volatile
    assert db.query(CRMOpportunity).filter(CRMOpportunity.id == created.id).first() is not None


def test_projects_create_then_list(db):
    payload = projects_router.ProjectSchema(
        title="Extension entrepot", code="PRJ-BNB-01", budget_xaf=120000000.0,
        start_date="2026-08-15", end_date="2026-12-31", manager_name="Thomas Eboa",
        status="EN_COURS",
    )
    created = projects_router.create_project(payload, context=_ctx(), db=db)
    assert created.status == "EN_COURS"
    assert created.spent_xaf == 0  # engage reel : 0 tant que rien n'est saisi
    assert any(r.id == created.id for r in projects_router.list_projects(context=_ctx(), db=db))


def test_fixed_asset_amortization_lineaire_calculee():
    asset = FixedAsset(
        asset_code="IMM-TR-045", name="Tracteur", category="FLEET",
        acquisition_date="2024-01-15", acquisition_value=65000000, residual_value=5000000,
        amortization_years=5, amortization_method="LINEAR",
    )
    # 2 ans exactement ~ 2 * 12 000 000 = 24 000 000 cumule, VNC ~ 41 000 000
    sched = asset.amortization_schedule(as_of=date(2026, 1, 15))
    assert sched["valeur_brute"] == 65000000.0
    assert sched["dotation_annuelle"] == 12000000.0
    assert 23000000 < sched["amortissement_cumule"] < 25000000
    assert 40000000 < sched["valeur_nette"] < 42000000


def test_fixed_asset_amortization_sans_date_ne_rien_invente():
    asset = FixedAsset(
        asset_code="X", name="Sans date", acquisition_value=1000, residual_value=0,
        amortization_years=5, amortization_method="LINEAR", acquisition_date=None,
    )
    sched = asset.amortization_schedule(as_of=date(2026, 1, 1))
    assert sched["dotation_annuelle"] == 200.0  # base/annees connu
    assert sched["amortissement_cumule"] == 0.0  # aucune anciennete -> rien fabrique
    assert sched["valeur_nette"] == 1000.0


def test_fixed_asset_create_calcul_reel(db):
    payload = fixed_assets_router.FixedAssetSchema(
        asset_code="IMM-TR-045", name="Tracteur", category="FLEET",
        acquisition_date="2024-01-15", acquisition_value=65000000.0, residual_value=5000000.0,
        amortization_years=5, amortization_method="LINEAR",
    )
    created = fixed_assets_router.create_fixed_asset(payload, context=_ctx(), db=db, )
    assert created.amortization["valeur_brute"] == 65000000.0
    listed = fixed_assets_router.list_fixed_assets(context=_ctx(), db=db, as_of="2026-01-15")
    assert listed[0].amortization["dotation_annuelle"] == 12000000.0


def test_degressive_calcule_solde_restant():
    asset = FixedAsset(
        asset_code="D", name="Degressif", acquisition_date="2024-01-01",
        acquisition_value=100000, residual_value=0, amortization_years=5,
        amortization_method="DEGRESSIVE",
    )
    s = asset.amortization_schedule(as_of=date(2024, 1, 1))  # jour 0 -> aucun temps ecoule
    assert s["amortissement_cumule"] == 0.0
    assert s["valeur_nette"] == 100000.0


def test_freight_offer_publish_then_list(db):
    payload = freight_router.FreightOfferSchema(
        origin="Douala Quai 10", destination="N'Djamena", cargo_type="40ft HC",
        weight_tons=28.5, offered_price_xaf=2800000.0,
    )
    created = freight_router.publish_freight_offer(payload, context=_ctx(), db=db)
    assert created.status == "PUBLIEE"
    rows = freight_router.list_freight_offers(context=_ctx(), db=db)
    assert any(r.id == created.id for r in rows)


def test_marketplace_api_key_hash_only(db):
    payload = marketplace_router.APIKeyCreateSchema(key_name="Odoo B2B", allowed_ips=["1.2.3.4"])
    created = marketplace_router.create_tenant_api_key(payload, context=_ctx(), db=db)
    assert created.cle_secrete and len(created.cle_secrete) >= 32
    rec = db.query(TenantAPIKey).filter(TenantAPIKey.id == created.id).first()
    # le hash est stocke, JAMAIS la cle claire
    assert rec.key_hash == hashlib.sha256(created.cle_secrete.encode("utf-8")).hexdigest()
    assert created.cle_secrete not in (rec.key_hash, rec.key_prefix)
    # le prefix expose correspond au debut de la cle
    assert created.key_prefix == created.cle_secrete[:16]
    # le modele de reponse (liste) ne divulgue NI cle claire NI hash
    fields = set(marketplace_router.APIKeyMeta.model_fields.keys())
    assert "key_hash" not in fields and "cle_secrete" not in fields
    listed = marketplace_router.list_tenant_api_keys(context=_ctx(), db=db)
    assert any(i.id == created.id for i in listed)
    assert all(getattr(i, "key_prefix", None) for i in listed)
