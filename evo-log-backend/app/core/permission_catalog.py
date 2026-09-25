"""Catalogue central des permissions granulaires EVO-LOG.

Source de verite unique utilisee par :
  - la migration de seed (creation des lignes ``permissions`` + roles metier) ;
  - l'endpoint ``GET /api/v1/permissions/catalog`` (arborescence UI) ;
  - la configuration des roles dans l'admin frontend.

Format d'un code : ``module.sous_module.action`` (jokers ``*`` autorises).
"""
from __future__ import annotations

from typing import Dict, List, Tuple

# Vocabulaire des actions.
ACTIONS = ["read", "create", "modify", "delete", "approve", "export"]

# domain -> label -> modules -> module -> label + sous-modules -> actions
DOMAINS: Dict[str, Dict] = {
    "gouvernance": {
        "label": "Gouvernance & Administration",
        "modules": {
            "users": {"label": "Utilisateurs", "sub_modules": {"comptes": ACTIONS, "statuts": ["read", "modify"]}},
            "roles": {"label": "Roles & permissions", "sub_modules": {"matrice": ["read", "modify"], "accreditations": ACTIONS}},
            "departments": {"label": "Departements", "sub_modules": {"organisation": ACTIONS}},
            "audit": {"label": "Piste d'audit", "sub_modules": {"journal": ["read", "export"]}},
            "settings": {"label": "Parametres entreprise", "sub_modules": {"generaux": ["read", "modify"], "communs": ["read", "modify"]}},
        },
    },
    "finance": {
        "label": "Finance & Comptabilite",
        "modules": {
            "comptabilite": {"label": "Comptabilite SYSCOHADA", "sub_modules": {"journal": ACTIONS, "grand_livre": ["read", "export"], "balance": ["read", "export"], "bilan": ["read", "approve", "export"], "lettrage": ["read", "modify"]}},
            "tresorerie": {"label": "Tresorerie", "sub_modules": {"mouvement": ACTIONS, "rapprochement": ["read", "modify"]}},
            "facturation": {"label": "Facturation", "sub_modules": {"facture": ACTIONS, "devis": ACTIONS, "avoir": ACTIONS}},
            "fiscalite": {"label": "Fiscalite (CEMAC)", "sub_modules": {"tva": ["read", "modify", "approve", "export"], "declarations": ["read", "create", "approve", "export"]}},
            "immobilisations": {"label": "Immobilisations", "sub_modules": {"actif": ACTIONS, "amortissement": ["read", "create", "modify"]}},
        },
    },
    "operations": {
        "label": "Operations portuaires & logistiques",
        "modules": {
            "acconage": {"label": "Acconage", "sub_modules": {"escale": ACTIONS, "manifeste": ["read", "create", "modify"], "stevedoring": ACTIONS}},
            "transit": {"label": "Transit & Douane", "sub_modules": {"dossier": ACTIONS, "declaration": ACTIONS, "tarification": ["read", "modify", "approve"]}},
            "magasin": {"label": "Magasin (WMS)", "sub_modules": {"stock": ["read", "modify"], "mouvement": ACTIONS, "inventaire": ["read", "create", "modify", "approve"], "picking": ["read", "create", "modify"]}},
            "port": {"label": "Operations portuaires", "sub_modules": {"quai": ACTIONS, "pesee": ["read", "create"], "zone": ACTIONS}},
        },
    },
    "transport": {
        "label": "Transport & Flotte",
        "modules": {
            "transport": {"label": "Transport", "sub_modules": {"mission": ACTIONS, "dispatch": ["read", "create", "modify", "approve"], "epod": ["read", "create", "modify"], "carburant": ACTIONS}},
            "parc": {"label": "Parc vehicules", "sub_modules": {"flotte": ACTIONS, "maintenance": ACTIONS, "documents": ["read", "create", "modify"]}},
            "gps": {"label": "Suivi GPS", "sub_modules": {"tracking": ["read"], "alertes": ["read", "modify"]}},
        },
    },
    "ressources_humaines": {
        "label": "Ressources Humaines",
        "modules": {
            "rh": {"label": "Administration du personnel", "sub_modules": {"employes": ACTIONS, "contrat": ACTIONS, "monitoring": ["read", "modify"]}},
            "paie": {"label": "Paie & declarations", "sub_modules": {"bulletin": ACTIONS, "declarations_sociales": ["read", "create", "approve", "export"]}},
            "conges": {"label": "Conges & presences", "sub_modules": {"demande": ["read", "create", "approve"], "pointage": ["read", "create"]}},
        },
    },
    "commerce": {
        "label": "Achats & Commerce",
        "modules": {
            "achats": {"label": "Achats", "sub_modules": {"commande": ACTIONS, "reception": ACTIONS}},
            "fournisseurs": {"label": "Fournisseurs", "sub_modules": {"referentiel": ACTIONS}},
            "cotations": {"label": "Cotation & devis", "sub_modules": {"cotation": ACTIONS}},
        },
    },
}

# Roles metier granulaires (systemes, company_id=NULL). Chaque entree :
#   (nom, niveau, description, [codes de permission])
# Niveaux : 2 = Chef de departement, 3 = utilisateur operateur.
ROLE_GRANTS: List[Tuple[str, int, str, List[str]]] = [
    ("DIRECTEUR_FINANCIER", 2, "Direction financiere : pilotage et validation de tous les modules finance", [
        "comptabilite.*.*", "tresorerie.*.*", "facturation.*.*", "fiscalite.*.*",
        "immobilisations.*.*", "achats.commande.approve",
    ]),
    ("CHEF_COMPTABLE", 2, "Chef comptable : voir et valider tout le departement comptable", [
        "comptabilite.*.*", "tresorerie.*.read", "tresorerie.mouvement.approve",
        "facturation.*.read", "facturation.facture.approve", "facturation.*.export",
        "fiscalite.*.read", "fiscalite.declarations.approve", "immobilisations.*.read",
    ]),
    ("COMPTABLE", 3, "Comptable : saisie et consultation de ses ecritures", [
        "comptabilite.journal.read", "comptabilite.journal.create", "comptabilite.journal.modify",
        "comptabilite.grand_livre.read", "comptabilite.balance.read", "comptabilite.lettrage.read",
        "comptabilite.lettrage.modify", "tresorerie.mouvement.read", "tresorerie.mouvement.create",
        "facturation.facture.read", "facturation.facture.create", "fiscalite.tva.read",
    ]),
    ("AUDITEUR", 3, "Auditeur : lecture transversale, aucune ecriture", [
        "comptabilite.*.read", "tresorerie.*.read", "facturation.*.read",
        "transport.*.read", "magasin.*.read", "transit.*.read", "audit.journal.read",
    ]),
    ("TRANSIT_PRINCIPAL", 2, "Transitaire principal : gestion et validation des dossiers", [
        "transit.*.*", "acconage.*.read", "magasin.stock.read", "fiscalite.declarations.read",
    ]),
    ("DECLARANT", 3, "Declarant en douane : preparation des declarations", [
        "transit.dossier.read", "transit.dossier.create", "transit.dossier.modify",
        "transit.declaration.read", "transit.declaration.create", "transit.declaration.modify",
        "acconage.manifeste.read",
    ],),
    ("MAGASINIER", 3, "Magasinier : mouvements de stock et inventaires", [
        "magasin.stock.read", "magasin.stock.modify", "magasin.mouvement.create",
        "magasin.picking.read", "magasin.picking.create", "magasin.inventaire.read",
    ]),
    ("CHEF_PARC", 2, "Chef de parc : gestion complete de la flotte", [
        "parc.*.*", "transport.*.read", "gps.tracking.read", "gps.alertes.modify",
    ]),
    ("DISPATCHER", 3, "Dispatcher transport : missions et tournes", [
        "transport.mission.read", "transport.mission.create", "transport.dispatch.read",
        "transport.dispatch.create", "transport.dispatch.modify", "parc.flotte.read",
    ]),
    ("ADMIN_RH", 2, "Administrateur RH : gestion complete du personnel", [
        "rh.*.*", "paie.*.read", "paie.bulletin.create", "conges.*.*",
    ]),
    ("QHSE", 3, "Officier QHSE : conformite et incidents", [
        "gouvernance.*.read", "transport.*.read", "parc.documents.read",
    ]),
]

# Roles de niveau 0/1 : bypass automatique dans le moteur, pas de seed granulaire
# (SUPER_ADMIN / ADMIN_ENTREPRISE / CHEF_DEPARTEMENT / USER_STANDARD).


def iter_permission_rows():
    """Yield (code, domaine, module, sub_module, action) pour tout le catalogue."""
    seen = set()
    for domaine, ddata in DOMAINS.items():
        for module, mdata in ddata["modules"].items():
            for sub, actions in mdata["sub_modules"].items():
                for action in actions:
                    code = f"{module}.{sub}.{action}"
                    if code in seen:
                        continue
                    seen.add(code)
                    yield code, domaine, module, sub, action


def build_catalog_tree() -> List[Dict]:
    """Arborescence domaine > module > sous-module > actions pour l'UI."""
    tree = []
    for dom_key, ddata in DOMAINS.items():
        modules = []
        for mod_key, mdata in ddata["modules"].items():
            subs = [
                {"key": sub_key, "actions": actions}
                for sub_key, actions in mdata["sub_modules"].items()
            ]
            modules.append({"key": mod_key, "label": mdata["label"], "subModules": subs})
        tree.append({"key": dom_key, "label": ddata["label"], "modules": modules})
    return tree
