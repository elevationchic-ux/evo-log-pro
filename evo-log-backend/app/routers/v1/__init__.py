"""V1 API routers"""
from app.routers.v1 import auth, tiers, transport, finance, parc, documents, alerts, magasin, gateway, transactions, master_data, admin, admin_agency, suppliers, notifications, bill_of_loading, purchase, incidents, public_api, rh, acconage, transit, maintenance, qhse, goods_declaration, removal_slip, reception_mag3, shift_planning, port_pricing, gps_tracking, real_customs, port_incidents, auto_invoicing, port_performance, notification_system, container_lifecycle, partner_api

__all__ = [
    "auth", "tiers", "transport", "finance", "parc", "documents", "alerts", "magasin", 
    "gateway", "transactions", "master_data", "admin", "admin_agency", "suppliers", 
    "notifications", "bill_of_loading", "purchase", "incidents", "public_api", "rh", 
    "acconage", "transit", "maintenance", "qhse", "goods_declaration", "removal_slip", 
    "reception_mag3", "shift_planning", "port_pricing", "gps_tracking", "real_customs", 
    "port_incidents", "auto_invoicing", "port_performance", "notification_system", 
    "container_lifecycle", "partner_api"
]