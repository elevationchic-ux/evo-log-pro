"""
EVO-LOG EM-ERP API - Main Application Entry Point
ERP Logistique Portuaire - Système de gestion complet pour le port de Douala
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlalchemy import text
from sqlalchemy.engine import Engine
import asyncio
import logging
import sentry_sdk
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from prometheus_client import make_asgi_app

from app.core.config import settings
from app.core.database import engine, get_db
from app.core.security import limiter
from app.middleware.audit import AuditMiddleware
from app.middleware.idempotency import IdempotencyMiddleware
from app.middleware.tracing import TracingMiddleware
from app.utils.error_handlers import setup_error_handlers, setup_monitoring
from app.services.events.event_service import event_service
from app.services.events.workflow_orchestrator import register_all_handlers

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global startup errors for health check
startup_errors = []
heartbeat_task = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    global heartbeat_task
    
    # Startup
    logger.info("Starting EVO-LOG EM-ERP API...")

    # Realtime fanout and WebRTC signaling are cross-process features: do not
    # start a partially functional instance when their broker is unavailable.
    try:
        await event_service.start()
        logger.info("Redis realtime bus connected")
    except Exception as e:
        logger.error("Redis realtime bus is required: %s", e)
        raise
    
    try:
        # Test database connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Database connection established successfully")
    except Exception as e:
        err_msg = f"Database connection failed: {e}"
        logger.error(f"? {err_msg}")
        startup_errors.append(err_msg)
    
    # Register cross-module workflow orchestrator handlers
    try:
        register_all_handlers()
        logger.info("✅ Cross-module workflow orchestrator registered")
    except Exception as e:
        logger.error(f"❌ Orchestrator registration failed: {e}")
    
    # Start heartbeat task for WebSocket connections
    heartbeat_task = asyncio.create_task(_heartbeat_loop())
    
    yield
    
    # Shutdown: close connections
    engine.dispose()
    await event_service.stop()
    
    # Stop heartbeat task
    if heartbeat_task:
        heartbeat_task.cancel()
        try:
            await heartbeat_task
        except asyncio.CancelledError:
            pass


async def _heartbeat_loop():
    """Background task to send periodic heartbeats to all tenant WebSocket connections"""
    while True:
        try:
            await asyncio.sleep(25)  # Every 25 seconds, matching WS router ping interval
            await event_service.broadcast_heartbeat()
            logger.debug("Sent WebSocket heartbeat to all tenants")
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Error in heartbeat loop: {e}")
            await asyncio.sleep(5)  # Wait before retrying


app = FastAPI(
    title="EVO-LOG EM-ERP API",
    description="""ERP Logistique Portuaire - Système de gestion complet pour le port de Douala.

    ## Modules disponibles

    * **Auth** - Authentification et gestion des utilisateurs
    * **Tiers** - Gestion des clients, fournisseurs et partenaires
    * **Transport** - Suivi des véhicules, conducteurs et missions
    * **Finance** - Comptabilité, facturation et gestion financière
    * **Parc** - Gestion du parc automobile et des équipements
    * **Documents** - Génération et gestion des documents logistiques
    * **Alerts** - Système d'alertes et de notifications en temps réel
    * **Magasin** - Gestion des stocks et entrepôts
    * **Gateway** - Intégration avec les systèmes externes
    * **Transactions** - Suivi des opérations commerciales
    * **Master Data** - Données de référence (articles, incoterms, types de conteneurs)
    * **Administratif** - Gestion des agences et paramètres système
    * **Notifications** - Centre de notifications
    * **Achats** - Gestion des achats et approvisionnements
    * **Incidents** - Signalement et suivi des incidents
    * **Public API** - Endpoints publics accessibles sans authentification
    * **RH** - Gestion des ressources humaines
    * **Acconage** - Gestion des opérations d'accostage
    * **Transit** - Gestion des opérations de transit
    * **Maintenance** - Gestion de la maintenance
    * **QHSE** - Qualité, Hygiène, Sécurité, Environnement
    * **Magasin Avancé** - Gestion avancée (FEFO, réservations, kits, inventaires tournants)
    * **Transport Avancé** - Optimisation tournées, GPS, sous-traitants, maintenance préventive

    ## Nouveaux Modules Version 2.0

    * **Shift Planning** - Planification des shifts et ressources
    * **Port Pricing** - Tarification des services portuaires
    * **GPS Tracking** - Tracking temps réel de la flotte
    * **Real Customs Integration** - Intégration SYDONIA+ et GUICHET UNIQUE
    * **Port Incidents** - Gestion des incidents portuaires
    * **Auto Invoicing** - Facturation automatique OHADA
    * **Port Performance Dashboard** - Dashboard de performance
    * **Multi-Channel Notifications** - Notifications multi-canal
    * **Container Lifecycle** - Cycle de vie des conteneurs
    * **Partner API** - API pour intégration B2B

    ## Modules Cameroun/CEMAC

    * **Cameroon Integration** - Intégration BSC, CSC, SYGED, APE (CNCC, INS, Douane)
    * **Local Payments** - Paiements locaux (Orange Money, MTN Mobile Money, Banques locales)
    * **Cameroon Taxation** - Fiscalité Cameroun/OHADA (IRPP, IS, TCF, TDR, TVA)

    ## Authentification

    La plupart des endpoints nécessitent une authentification JWT. Utilisez l'endpoint `/api/v1/auth/login` pour obtenir un token d'accès.

    ## Versioning

    Cet API utilise le versioning par URL. La version actuelle est v1 disponible sous `/api/v1/*`.
    Les endpoints sous `/api/*` sont maintenus pour la compatibilité ascendante mais sont dépréciés.

    ## Rate Limiting

    Des limites de taux sont appliquées pour protéger contre les abus:
    * Authentification: 5 requêtes/minute
    * Connexion: 10 requêtes/minute
    * Utilisateurs réguliers: 1000 requêtes/heure
    * Administrateurs: 2000 requêtes/heure
    * Opérations en lot: 10 requêtes/heure
    """,
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
    contact={
        "name": "Équipe EVO-LOG",
        "url": "https://EVO-LOG.cm",
        "email": "tech@EVO-LOG.cm",
    },
    license_info={
        "name": "Propriétaire",
        "url": "https://EVO-LOG.cm/license",
    },
    terms_of_service="https://EVO-LOG.cm/terms",
)

# Setup Prometheus Metrics (safely bypassed to prevent _IncludedRouter AttributeError in FastAPI 0.115+)
# instrumentator = Instrumentator().instrument(app)

# Sentry initialization (if DSN provided)
if getattr(settings, "SENTRY_DSN", None):
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        traces_sample_rate=0.2,
        integrations=[
            SqlalchemyIntegration(),
            RedisIntegration(),
            CeleryIntegration(),
        ],
    )
    app.add_middleware(SentryAsgiMiddleware)

# Rate limiting protection brute force
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Setup error handlers
setup_error_handlers(app)

# Setup monitoring (must be called outside lifespan because it adds a middleware)
setup_monitoring(app)

# Middleware de traçage des requêtes avec ID de corrélation
app.add_middleware(TracingMiddleware)

# Middlewares de Sécurité et Audit (Niveau World Pro)
app.add_middleware(AuditMiddleware)
app.add_middleware(IdempotencyMiddleware, redis_url=settings.REDIS_URL)

# CORS autoriser le frontend Next.js sur tous les ports de dev et Vercel previews
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:3002",
        "https://EVO-LOG-erp.cm",
    ],
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1)(:\d+)?|https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["Content-Type", "Authorization", "X-Requested-With", "X-Idempotency-Key", "X-Request-ID", "trace-id", "baggage", "sentry-trace"],
)

# Prometheus metrics endpoint for monitoring
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


@app.middleware("http")
async def api_v1_rewrite_middleware(request: Request, call_next):
    """Transparently route legacy /api/* requests to /api/v1/*"""
    path = request.url.path
    if path.startswith("/api/") and not path.startswith("/api/v1/") and not path.startswith("/api/health") and not path.startswith("/api/docs") and not path.startswith("/api/redoc") and not path.startswith("/api/openapi.json"):
        new_path = path.replace("/api/", "/api/v1/", 1)
        request.scope["path"] = new_path
    return await call_next(request)

# Import routers safely
def safe_include_router(router, **kwargs):
    """Include router safely with error handling"""
    try:
        app.include_router(router, **kwargs)
    except Exception as e:
        logger.warning(f"Failed to include router {kwargs.get('prefix', 'unknown')}: {e}")

from app.routers.v1 import auth, tiers, transport, finance, parc, documents, alerts, magasin, gateway, transactions, master_data, admin, admin_agency, suppliers, notifications, bill_of_loading, purchase, incidents, public_api, rh, acconage, transit, maintenance, qhse, goods_declaration, removal_slip, reception_mag3, chat, prestataires, chef_personnel

safe_include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
safe_include_router(chat.router, prefix="/api/v1/chat", tags=["Collaboration Chat"])
safe_include_router(prestataires.router, prefix="/api/v1/prestataires", tags=["Annuaire Prestataires"])
safe_include_router(chef_personnel.router, prefix="/api/v1/chef-personnel", tags=["Chef du Personnel"])
safe_include_router(tiers.router, prefix="/api/v1/tiers", tags=["Tiers"])
safe_include_router(transport.router, prefix="/api/v1/transport", tags=["Transport"])
safe_include_router(finance.router, prefix="/api/v1/finance", tags=["Finance"])
safe_include_router(parc.router, prefix="/api/v1/parc", tags=["Parc"])
safe_include_router(parc.router, prefix="/api/v1/fleet", tags=["Fleet compatibility"])
safe_include_router(documents.router, prefix="/api/v1/documents", tags=["Documents"])
safe_include_router(alerts.router, prefix="/api/v1/alerts", tags=["Alerts"])
safe_include_router(magasin.router, prefix="/api/v1/magasin", tags=["EVO-Magasin"])
safe_include_router(gateway.router, prefix="/api/v1/gateway", tags=["Gateway"])
safe_include_router(transactions.router, prefix="/api/v1/transactions", tags=["Transactions"])
safe_include_router(goods_declaration.router, prefix="/api/v1/transport/goods-declarations", tags=["Goods Declaration"])
safe_include_router(removal_slip.router, prefix="/api/v1/magasin/removal-slips", tags=["Removal Slip"])
safe_include_router(reception_mag3.router, prefix="/api/v1/magasin/receptions-mag3", tags=["Reception Mag3"])
safe_include_router(master_data.router, prefix="/api/v1/master-data", tags=["Master Data"])
safe_include_router(admin.router, prefix="/api/v1/admin", tags=["Admin"])
safe_include_router(admin_agency.router, prefix="/api/v1/admin/agencies", tags=["Admin Agencies"])
safe_include_router(suppliers.router, prefix="/api/v1/suppliers", tags=["Suppliers"])
safe_include_router(notifications.router, prefix="/api/v1/notifications", tags=["Notifications"])
safe_include_router(bill_of_loading.router, prefix="/api/v1/bill-of-loading", tags=["Bill of Loading"])
safe_include_router(purchase.router, prefix="/api/v1/purchase", tags=["Achats"])
safe_include_router(incidents.router, prefix="/api/v1/incidents", tags=["Incidents"])
safe_include_router(public_api.router, prefix="/api/v1/public", tags=["Public API"])
safe_include_router(rh.router, prefix="/api/v1/rh", tags=["Ressources Humaines"])
safe_include_router(acconage.router, prefix="/api/v1/acconage", tags=["Accostage"])
safe_include_router(transit.router, prefix="/api/v1/transit", tags=["Transit"])
safe_include_router(maintenance.router, prefix="/api/v1/maintenance", tags=["Maintenance"])
safe_include_router(qhse.router, prefix="/api/v1/qhse", tags=["QHSE"])

# Advanced modules routers
try:
    from app.routers.v1 import magasin_avance, transport_avance, acconage_avance, transit_avance, magasin_douane, transport_international, acquisition, finance, qhse, documents, maintenance_gmao, integration, notifications, reporting, tenant, role, b2b, comptabilite_avance, transport_avance_complete, finance_avance, rh_avance, transit_douane_avance, magasin_wms_avance, maintenance_gmao_avance
    safe_include_router(magasin_avance.router, prefix="/api/v1/magasin-avance", tags=["Magasin Avancé"])
    safe_include_router(transport_avance.router, prefix="/api/v1/transport-avance", tags=["Transport Avancé"])
    safe_include_router(acconage_avance.router, prefix="/api/v1/acconage-avance", tags=["Acconage Avancé"])
    safe_include_router(transit_avance.router, prefix="/api/v1/transit-avance", tags=["Transit Avancé"])
    safe_include_router(magasin_douane.router, prefix="/api/v1/magasin-douane", tags=["Magasin Douane"])
    safe_include_router(transport_international.router, prefix="/api/v1/transport-international", tags=["Transport International"])
    safe_include_router(acquisition.router, prefix="/api/v1/acquisition", tags=["Acquisition"])
    safe_include_router(finance.router, prefix="/api/v1/finance", tags=["Finance"])
    safe_include_router(qhse.router, prefix="/api/v1/qhse", tags=["QHSE"])
    safe_include_router(documents.router, prefix="/api/v1/documents", tags=["Documents"])
    safe_include_router(maintenance_gmao.router, prefix="/api/v1/maintenance-gmao", tags=["Maintenance GMAO"])
    safe_include_router(integration.router, prefix="/api/v1/integration", tags=["Integration"])
    safe_include_router(notifications.router, prefix="/api/v1/notifications", tags=["Notifications"])
    safe_include_router(reporting.router, prefix="/api/v1/reporting", tags=["Reporting"])
    safe_include_router(tenant.router, prefix="/api/v1/tenant", tags=["Tenant Management"])
    safe_include_router(role.router, prefix="/api/v1/roles", tags=["Role Management"])
    safe_include_router(b2b.router, prefix="/api/v1/b2b", tags=["B2B Portal"])
    safe_include_router(comptabilite_avance.router, prefix="/api/v1/comptabilite-avance", tags=["Comptabilité Avancée"])
    safe_include_router(transport_avance_complete.router, prefix="/api/v1/transport-avance-complete", tags=["Transport Avancé Complet"])
    safe_include_router(finance_avance.router, prefix="/api/v1/finance-avance", tags=["Finance Avancée"])
    safe_include_router(rh_avance.router, prefix="/api/v1/rh-avance", tags=["RH Avancé"])
    safe_include_router(transit_douane_avance.router, prefix="/api/v1/transit-douane-avance", tags=["Transit & Douane Avancé"])
    safe_include_router(magasin_wms_avance.router, prefix="/api/v1/magasin-wms-avance", tags=["Magasin WMS Avancé"])
    safe_include_router(maintenance_gmao_avance.router, prefix="/api/v1/maintenance-gmao-avance", tags=["Maintenance GMAO Avancée"])
    from app.routers.v1 import rbac_avance, b2b_portal, audit, security_escalation
    safe_include_router(rbac_avance.router, prefix="/api/v1/rbac", tags=["RBAC & Multi-Tenant"])
    safe_include_router(b2b_portal.router, prefix="/api/v1/b2b-portal", tags=["Portail B2B Client"])
    safe_include_router(audit.router, prefix="/api/v1/audit", tags=["Piste d'Audit Immuable"])
    safe_include_router(security_escalation.router, prefix="/api/v1/security", tags=["Sécurité & Escalade"])
    from app.routers.v1 import frais_missions
    safe_include_router(frais_missions.router, prefix="/api/v1", tags=["Notes de Frais & Avances Missions"])
except ImportError as e:
    logger.warning(f"Advanced modules not yet implemented: {e}")

# New Version 2.0 Modules
try:
    from app.routers.v1 import shift_planning, port_pricing, gps_tracking, real_customs, port_incidents, auto_invoicing, port_performance, notification_system, container_lifecycle, partner_api
    
    safe_include_router(shift_planning.router, prefix="/api/v1/shift-planning", tags=["Shift Planning"])
    safe_include_router(port_pricing.router, prefix="/api/v1/port-pricing", tags=["Port Pricing"])
    safe_include_router(gps_tracking.router, prefix="/api/v1/gps-tracking", tags=["GPS Tracking"])
    safe_include_router(real_customs.router, prefix="/api/v1/real-customs", tags=["Real Customs"])
    safe_include_router(port_incidents.router, prefix="/api/v1/port-incidents", tags=["Port Incidents"])
    safe_include_router(auto_invoicing.router, prefix="/api/v1/auto-invoicing", tags=["Auto Invoicing"])
    safe_include_router(port_performance.router, prefix="/api/v1/port-performance", tags=["Port Performance"])
    safe_include_router(notification_system.router, prefix="/api/v1/notification-system", tags=["Notification System"])
    safe_include_router(container_lifecycle.router, prefix="/api/v1/container-lifecycle", tags=["Container Lifecycle"])
    safe_include_router(partner_api.router, prefix="/api/v1/partner-api", tags=["Partner API"])
except ImportError as e:
    logger.warning(f"Version 2.0 modules not yet implemented: {e}")

# Cameroon/CEMAC Specific Modules
try:
    from app.routers.v1 import integration_cameroun, paiement_local, fiscalite_cameroun
    
    safe_include_router(integration_cameroun.router, prefix="/api/v1/integration-cameroun", tags=["Cameroon Integration"])
    safe_include_router(paiement_local.router, prefix="/api/v1/paiement-local", tags=["Local Payments"])
    safe_include_router(fiscalite_cameroun.router, prefix="/api/v1/fiscalite-cameroun", tags=["Cameroon Taxation"])
except ImportError as e:
    logger.warning(f"Cameroon/CEMAC modules not yet implemented: {e}")

# WebSocket and additional routers
try:
    from app.routers import ws, collaboration, iot, webhook_whatsapp, telematics
    
    safe_include_router(ws.router, prefix="/api/v1/ws", tags=["WebSockets"])
    safe_include_router(collaboration.router, prefix="/api/v1/collaboration", tags=["Collaboration"])
    safe_include_router(iot.router, prefix="/api/v1/iot", tags=["IoT"])
    safe_include_router(webhook_whatsapp.router, prefix="/api/v1/webhook-whatsapp", tags=["Webhook WhatsApp"])
    safe_include_router(telematics.router, prefix="/api/v1/telematics", tags=["Telematics"])
except ImportError as e:
    logger.warning(f"Additional routers not yet implemented: {e}")

# Fused Kamlog Extended Modules (Superadmin, Onboarding, Subscription, CRM, GED, E-Invoicing, AI, Digital Twin, etc.)
try:
    from app.routers.v1 import (
        superadmin, subscription, onboarding, privacy, ohada_accounting,
        crm, projects, fixed_assets, ged, e_invoicing,
        ai_predictive, ai_assistant, bi_advanced, marketplace, freight_exchange,
        digital_twin, gamification, sectoral_features, status, new_k_modules
    )
    safe_include_router(getattr(superadmin, 'router', superadmin), prefix="/api/v1/superadmin", tags=["SuperAdmin Multi-Tenant"])
    safe_include_router(getattr(subscription, 'router', subscription), prefix="/api/v1/saas/subscription", tags=["SaaS Subscription & Billing"])
    safe_include_router(getattr(onboarding, 'router', onboarding), prefix="/api/v1/auth/onboarding", tags=["Self-Service Onboarding"])
    safe_include_router(getattr(privacy, 'router', privacy), prefix="/api/v1/privacy", tags=["Data Privacy Law 2024/017"])
    safe_include_router(getattr(ohada_accounting, 'router', ohada_accounting), prefix="/api/v1/accounting/ohada", tags=["Comptabilité SYSCOHADA Extended"])
    safe_include_router(getattr(crm, 'router', crm), prefix="/api/v1/crm", tags=["CRM & Pipeline Commercial"])
    safe_include_router(getattr(projects, 'router', projects), prefix="/api/v1/projects", tags=["Gestion de Projets & Chantiers"])
    safe_include_router(getattr(fixed_assets, 'router', fixed_assets), prefix="/api/v1/assets", tags=["Immobilisations & Amortissements OHADA"])
    safe_include_router(getattr(ged, 'router', ged), prefix="/api/v1/ged", tags=["GED Coffre-fort Numérique"])
    safe_include_router(getattr(e_invoicing, 'router', e_invoicing), prefix="/api/v1/e-invoicing", tags=["Facturation Électronique DGI"])
    safe_include_router(getattr(ai_predictive, 'router', ai_predictive), prefix="/api/v1/ai/predictive", tags=["Moteur IA Prédictive"])
    safe_include_router(getattr(ai_assistant, 'router', ai_assistant), prefix="/api/v1/ai/assistant", tags=["Assistant IA"])
    safe_include_router(getattr(bi_advanced, 'router', bi_advanced), prefix="/api/v1/bi/advanced", tags=["Business Intelligence Avancée"])
    safe_include_router(getattr(marketplace, 'router', marketplace), prefix="/api/v1/marketplace", tags=["Marketplace & API Keys"])
    safe_include_router(getattr(freight_exchange, 'router', freight_exchange), prefix="/api/v1/freight-exchange", tags=["Bourse de Fret CEMAC"])
    safe_include_router(getattr(digital_twin, 'router', digital_twin), prefix="/api/v1/digital-twin", tags=["Jumeau Numérique Entrepôt/Parc"])
    safe_include_router(getattr(gamification, 'router', gamification), prefix="/api/v1/gamification", tags=["Gamification & Éco-conduite"])
    safe_include_router(getattr(sectoral_features, 'router', sectoral_features), prefix="/api/v1/sectoral", tags=["Paramétrage Sectoriel (Bascule, Phyto, FDS)"])
    safe_include_router(getattr(status, 'router', status), prefix="/api/v1/status", tags=["Statut Public & SLA"])
    safe_include_router(getattr(new_k_modules, 'router', new_k_modules), prefix="/api/v1/k-modules", tags=["Modules Spécialisés"])
except ImportError as e:
    logger.warning(f"Fused Kamlog modules not yet loaded: {e}")


# Backward compatibility - Original API endpoints (deprecated, will be removed in v2)
safe_include_router(auth.router, prefix="/api/auth", tags=["Auth - DEPRECATED"])
safe_include_router(tiers.router, prefix="/api/tiers", tags=["Tiers - DEPRECATED"])
safe_include_router(transport.router, prefix="/api/transport", tags=["Transport - DEPRECATED"])
safe_include_router(finance.router, prefix="/api/finance", tags=["Finance - DEPRECATED"])
safe_include_router(parc.router, prefix="/api/parc", tags=["Parc - DEPRECATED"])
safe_include_router(documents.router, prefix="/api/documents", tags=["Documents - DEPRECATED"])
safe_include_router(alerts.router, prefix="/api/alerts", tags=["Alerts - DEPRECATED"])
safe_include_router(magasin.router, prefix="/api/magasin", tags=["EVO-Magasin - DEPRECATED"])
safe_include_router(gateway.router, prefix="/api/gateway", tags=["Gateway - DEPRECATED"])
safe_include_router(transactions.router, prefix="/api/transactions", tags=["Transactions - DEPRECATED"])

@app.get('/api/health')
async def health_check():
    """Health check basique - utilisé par Railway."""
    if startup_errors:
        return {
            "status": "degraded",
            "service": "EVO-LOG EM-ERP",
            "version": "2.0.0",
            "errors": startup_errors
        }
    return {"status": "ok", "service": "EVO-LOG EM-ERP", "version": "2.0.0"}


@app.get("/", response_class=HTMLResponse)
async def root_gateway():
    """Root endpoint for browser visits on http://127.0.0.1:8000"""
    return HTMLResponse(content="""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EVO-LOG EM-ERP • Passerelle API & Système Portuaire CADC</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;800;900&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            background: radial-gradient(circle at center, #07152b 0%, #030d1d 55%, #01060e 100%);
            color: #f8fafc;
            font-family: 'Outfit', sans-serif;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 24px;
        }
        .card {
            max-width: 680px;
            width: 100%;
            background: rgba(15, 23, 42, 0.85);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(245, 158, 11, 0.25);
            border-radius: 24px;
            padding: 40px;
            box-shadow: 0 25px 60px -15px rgba(0, 0, 0, 0.9), 0 0 40px rgba(245, 158, 11, 0.15);
            text-align: center;
        }
        .badge {
            display: inline-block;
            background: rgba(245, 158, 11, 0.15);
            border: 1px solid rgba(245, 158, 11, 0.4);
            color: #fbbf24;
            font-size: 11px;
            font-weight: 800;
            letter-spacing: 2px;
            padding: 6px 16px;
            border-radius: 9999px;
            text-transform: uppercase;
            margin-bottom: 20px;
        }
        h1 {
            font-size: 38px;
            font-weight: 900;
            letter-spacing: -1px;
            margin-bottom: 8px;
            background: linear-gradient(180deg, #ffffff 0%, #fef08a 30%, #f59e0b 80%, #d97706 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        p.sub {
            color: #94a3b8;
            font-size: 14px;
            margin-bottom: 28px;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 16px;
            margin-bottom: 32px;
        }
        .metric {
            background: rgba(2, 12, 27, 0.7);
            border: 1px solid rgba(51, 65, 85, 0.6);
            border-radius: 16px;
            padding: 16px;
            text-align: left;
        }
        .metric-title { font-size: 11px; color: #64748b; text-transform: uppercase; font-family: 'JetBrains Mono', monospace; }
        .metric-val { font-size: 18px; font-weight: 700; color: #38bdf8; margin-top: 4px; }
        .status-ok { color: #34d399; }
        .links {
            display: flex;
            flex-direction: column;
            gap: 12px;
        }
        .btn {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            padding: 14px 20px;
            border-radius: 14px;
            font-weight: 700;
            font-size: 14px;
            text-decoration: none;
            transition: all 0.2s ease;
        }
        .btn-primary {
            background: linear-gradient(90deg, #d97706, #f59e0b, #d97706);
            color: #020c1b;
            box-shadow: 0 10px 25px -5px rgba(245, 158, 11, 0.4);
        }
        .btn-primary:hover { transform: translateY(-2px); box-shadow: 0 14px 30px -5px rgba(245, 158, 11, 0.6); }
        .btn-sec {
            background: rgba(30, 41, 59, 0.8);
            color: #e2e8f0;
            border: 1px solid rgba(71, 85, 105, 0.6);
        }
        .btn-sec:hover { background: rgba(51, 65, 85, 0.8); border-color: #94a3b8; }
        .footer {
            margin-top: 24px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 11px;
            color: #475569;
        }
    </style>
</head>
<body>
    <div class="card">
        <div class="badge">Passerelle API Centralisée CADC</div>
        <h1>EVO-LOG EM-ERP</h1>
        <p class="sub">Moteur Applicatif & Passerelle Portuaire Douala / Kribi / CEMAC</p>
        
        <div class="grid">
            <div class="metric">
                <div class="metric-title">Statut API</div>
                <div class="metric-val status-ok">● Opérationnel (200 OK)</div>
            </div>
            <div class="metric">
                <div class="metric-title">Modules Actifs</div>
                <div class="metric-val">82 Routers v1</div>
            </div>
            <div class="metric">
                <div class="metric-title">Base de Données</div>
                <div class="metric-val status-ok">PostgreSQL OHADA</div>
            </div>
            <div class="metric">
                <div class="metric-title">Mode SaaS</div>
                <div class="metric-val">Multi-Tenants Isolé</div>
            </div>
        </div>

        <div class="links">
            <a href="http://localhost:3000" class="btn btn-primary">
                🖥️ Accéder à l'Application Frontend EVO-LOG (Port 3000)
            </a>
            <a href="/api/docs" class="btn btn-sec">
                📚 Documentation Interactive des APIs (Swagger UI)
            </a>
            <a href="/api/health" class="btn btn-sec">
                🩺 Diagnostic Santé Système (/api/health)
            </a>
        </div>

        <div class="footer">
            CADC • Code Axis Digital Cameroun • Port de Douala • v2.0.0
        </div>
    </div>
</body>
</html>
""")


@app.get("/docs", include_in_schema=False)
async def redirect_docs():
    """Redirect /docs to /api/docs"""
    return RedirectResponse(url="/api/docs")


@app.get("/health", tags=["Health"])
@app.get("/api/health", tags=["Health"])
@app.get("/api/v1/health", tags=["Health"])
async def detailed_health_check():
    """Health check détaillé avec vérification des dépendances."""
    checks = {
        "status": "ok",
        "service": "EVO-LOG EM-ERP",
        "version": "2.0.0",
        "checks": {}
    }

    # Vérifier la base de données
    try:
        def check_db():
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
        await asyncio.to_thread(check_db)
        checks["checks"]["database"] = {"status": "ok", "message": "PostgreSQL connecté"}
    except Exception as e:
        checks["checks"]["database"] = {"status": "error", "message": str(e)}
        checks["status"] = "degraded"

    # Vérifier Redis (si configuré)
    try:
        import redis.asyncio as aioredis
        redis_client = aioredis.from_url(settings.REDIS_URL)
        await redis_client.ping()
        await redis_client.aclose()
        checks["checks"]["redis"] = {"status": "ok", "message": "Redis connecté"}
    except Exception as e:
        checks["checks"]["redis"] = {"status": "warning", "message": f"Redis indisponible: {str(e)}"}

    # Vérifier MinIO (si activé)
    if settings.MINIO_ENABLED:
        try:
            from minio import Minio
            minio_client = Minio(
                settings.MINIO_ENDPOINT,
                access_key=settings.MINIO_ACCESS_KEY,
                secret_key=settings.MINIO_SECRET_KEY,
                secure=settings.MINIO_SECURE
            )
            minio_client.bucket_exists(settings.MINIO_BUCKET_DOCUMENTS)
            checks["checks"]["minio"] = {"status": "ok", "message": "MinIO connecté"}
        except Exception as e:
            checks["checks"]["minio"] = {"status": "warning", "message": f"MinIO indisponible: {str(e)}"}
    else:
        checks["checks"]["minio"] = {"status": "disabled", "message": "MinIO désactivé"}

    # Vérifier Celery Workers
    try:
        from app.worker import celery_app
        i = celery_app.control.inspect()
        active = i.active()
        if active is None:
            checks["checks"]["celery"] = {"status": "warning", "message": "Aucun worker Celery actif"}
        else:
            checks["checks"]["celery"] = {"status": "ok", "message": "Workers Celery actifs"}
    except Exception as e:
        checks["checks"]["celery"] = {"status": "error", "message": str(e)}
        checks["status"] = "degraded"
    
    return checks


# Prometheus metrics disabled - instrumentator incompatible with current FastAPI version
# @app.on_event('startup')
# async def expose_metrics():
#     instrumentator.expose(app)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)