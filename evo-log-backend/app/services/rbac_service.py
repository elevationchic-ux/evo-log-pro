"""
Service RBAC EVO-LOG SaaS
- Hiérarchie : SuperAdmin > Admin > Manager > Superviseur > Opérateur > Chauffeur > ClientB2B
- Permissions atomiques : module.ressource.action
- Matrice de permissions par défaut pour chaque niveau
"""
import json
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session

# ── Matrice de permissions par défaut ─────────────────────────────────────────
PERMISSIONS_PAR_NIVEAU: Dict[str, List[str]] = {
    "SUPER_ADMIN": ["*"],  # Accès total tous modules tous tenants

    "ADMIN": [
        "transport.*", "magasin.*", "finance.*", "comptabilite.*",
        "rh.*", "transit.*", "maintenance.*", "reports.*",
        "rbac.users.read", "rbac.users.create", "rbac.users.update",
        "rbac.roles.read", "rbac.roles.create", "b2b.*"
    ],

    "MANAGER": [
        "transport.mission.read", "transport.mission.create", "transport.mission.validate",
        "transport.tournee.read", "transport.tournee.create",
        "transport.flotte.read", "transport.epod.read",
        "magasin.stock.read", "magasin.mouvement.create", "magasin.picking.create",
        "magasin.inventaire.read",
        "finance.tresorerie.read", "finance.encaissement.read",
        "comptabilite.journal.read", "comptabilite.grand_livre.read",
        "rh.employees.read", "rh.payroll.read",
        "transit.dossier.read", "transit.dossier.create",
        "reports.read", "reports.export"
    ],

    "SUPERVISEUR": [
        "transport.mission.read", "transport.mission.validate",
        "transport.epod.validate",
        "magasin.stock.read", "magasin.mouvement.read", "magasin.picking.read",
        "finance.tresorerie.read",
        "comptabilite.journal.read",
        "transit.dossier.read",
        "reports.read"
    ],

    "OPERATEUR": [
        "transport.mission.read", "transport.mission.create",
        "magasin.stock.read", "magasin.mouvement.create", "magasin.picking.create",
        "transit.dossier.read", "transit.dossier.create",
        "finance.encaissement.create",
        "comptabilite.journal.create"
    ],

    "CHAUFFEUR": [
        "transport.mission.read_own",  # Uniquement ses propres missions
        "transport.epod.create_own",   # Signer ses propres e-POD
        "transport.carburant.create_own",
        "transport.position.update_own"
    ],

    "CLIENT_B2B": [
        "b2b.dossier.read_own",        # Suivi de ses propres dossiers
        "b2b.facture.read_own",
        "b2b.devis.read_own",
        "b2b.document.download_own"
    ]
}


class RBACService:
    """Service de gestion des rôles, permissions et tenants"""

    @staticmethod
    def get_all_tenants(db: Session) -> List[Dict[str, Any]]:
        return [
            {
                "id": 1, "code": "EVOLOGS-CMR", "nom_entreprise": "EVO-LOG Cameroun SARL",
                "pays": "Cameroun", "ville": "Douala", "plan": "ENTERPRISE",
                "modules_actives": "transport,magasin,finance,comptabilite,rh,transit,maintenance,reports",
                "nb_utilisateurs_max": 100, "actif": True,
                "created_at": "2026-01-15T08:00:00"
            },
            {
                "id": 2, "code": "BOCOM-CI", "nom_entreprise": "Bolloré Côte d'Ivoire",
                "pays": "Côte d'Ivoire", "ville": "Abidjan", "plan": "PROFESSIONNEL",
                "modules_actives": "transport,magasin,transit",
                "nb_utilisateurs_max": 30, "actif": True,
                "created_at": "2026-03-01T08:00:00"
            },
            {
                "id": 3, "code": "CAMSHIP-CMR", "nom_entreprise": "Cameroon Shipping Lines",
                "pays": "Cameroun", "ville": "Kribi", "plan": "STARTER",
                "modules_actives": "transport,transit",
                "nb_utilisateurs_max": 10, "actif": True,
                "created_at": "2026-05-10T08:00:00"
            }
        ]

    @staticmethod
    def get_all_roles(db: Session) -> List[Dict[str, Any]]:
        roles = []
        for niveau, perms in PERMISSIONS_PAR_NIVEAU.items():
            roles.append({
                "id": list(PERMISSIONS_PAR_NIVEAU.keys()).index(niveau) + 1,
                "nom": niveau.replace("_", " "),
                "niveau": niveau,
                "description": _description_niveau(niveau),
                "permissions_json": json.dumps(perms),
                "nb_permissions": len(perms),
                "actif": True
            })
        return roles

    @staticmethod
    def check_permission(db: Session, user_id: int, tenant_id: int, permission_code: str) -> Dict[str, Any]:
        """Vérifie si un utilisateur a une permission donnée"""
        # Simulation : user 1 = SUPER_ADMIN, user 2 = ADMIN, etc.
        user_niveau = {1: "SUPER_ADMIN", 2: "ADMIN", 3: "MANAGER",
                       4: "SUPERVISEUR", 5: "OPERATEUR", 6: "CHAUFFEUR"}.get(user_id, "OPERATEUR")

        perms = PERMISSIONS_PAR_NIVEAU.get(user_niveau, [])
        autorise = (
            "*" in perms or
            permission_code in perms or
            any(p.endswith(".*") and permission_code.startswith(p[:-2]) for p in perms)
        )

        return {
            "user_id": user_id,
            "permission_code": permission_code,
            "autorise": autorise,
            "niveau_role": user_niveau,
            "raison": f"Autorisé via rôle {user_niveau}" if autorise else f"Non autorisé pour le rôle {user_niveau}"
        }

    @staticmethod
    def get_users_by_tenant(db: Session, tenant_id: int) -> List[Dict[str, Any]]:
        return [
            {"id": 1, "nom": "Christophe OUSSIBELA", "email": "c.oussibela@evo-log.cm",
             "role": "SUPER_ADMIN", "tenant_id": tenant_id, "actif": True, "derniere_connexion": "2026-08-27T17:30:00"},
            {"id": 2, "nom": "Marie-Claire EKWALLA", "email": "m.ekwalla@evo-log.cm",
             "role": "ADMIN", "tenant_id": tenant_id, "actif": True, "derniere_connexion": "2026-08-27T16:45:00"},
            {"id": 3, "nom": "Paul MBARGA", "email": "p.mbarga@evo-log.cm",
             "role": "MANAGER", "tenant_id": tenant_id, "actif": True, "derniere_connexion": "2026-08-27T14:20:00"},
            {"id": 4, "nom": "Sylvie NKODO", "email": "s.nkodo@evo-log.cm",
             "role": "SUPERVISEUR", "tenant_id": tenant_id, "actif": True, "derniere_connexion": "2026-08-27T12:00:00"},
            {"id": 5, "nom": "Thomas BELLA BELLA", "email": "t.bellabella@evo-log.cm",
             "role": "OPERATEUR", "tenant_id": tenant_id, "actif": True, "derniere_connexion": "2026-08-27T09:10:00"},
            {"id": 6, "nom": "André KOUBE", "email": "a.koube@evo-log.cm",
             "role": "CHAUFFEUR", "tenant_id": tenant_id, "actif": True, "derniere_connexion": "2026-08-27T07:00:00"},
        ]


def _description_niveau(niveau: str) -> str:
    return {
        "SUPER_ADMIN": "Accès total multi-tenant  équipe EVO-LOG SaaS uniquement",
        "ADMIN": "Accès complet à tous les modules du tenant, gestion des utilisateurs",
        "MANAGER": "Accès étendu avec validation des opérations et lecture des rapports",
        "SUPERVISEUR": "Validation des opérations terrain, lecture des indicateurs",
        "OPERATEUR": "Saisie et consultation dans les modules assignés",
        "CHAUFFEUR": "Interface mobile : missions, e-POD, rapport carburant",
        "CLIENT_B2B": "Portail client : consultation de ses dossiers, factures et documents"
    }.get(niveau, "")
