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
            # Batch 22 : le routeur /finance expose plan comptable, exercices,
            # bilans et comptes de resultat  des realites metier qui n'avaient
            # encore AUCUN code dans le catalogue (le routeur etait en auth
            # simple faute de droit applicable). Plutot que de les plaquer de
            # force sur « journal », sous-modules dedies, alignes sur les
            # ecrans. bilan etendu car creer/modifier un bilan est distinct de
            # l'approuver.
            "comptabilite": {"label": "Comptabilite SYSCOHADA", "sub_modules": {"journal": ACTIONS, "grand_livre": ["read", "export"], "balance": ["read", "export"], "bilan": ["read", "create", "modify", "approve", "export"], "lettrage": ["read", "modify"], "plan_comptable": ["read", "create", "modify"], "exercice": ["read", "create", "modify", "approve"], "compte_resultat": ["read", "create", "modify"]}},
            "tresorerie": {"label": "Tresorerie", "sub_modules": {"mouvement": ACTIONS, "rapprochement": ["read", "modify"]}},
            "facturation": {"label": "Facturation", "sub_modules": {"facture": ACTIONS, "devis": ACTIONS, "avoir": ACTIONS}},
            # declarations + modify : une declaration fiscale se corrige avant
            # d'être depotree ; le depot lui-meme reste l'approve (501 tant que
            # GUCE/SYDONIA n'existe pas  batches precedents).
            "fiscalite": {"label": "Fiscalite (CEMAC)", "sub_modules": {"tva": ["read", "modify", "approve", "export"], "declarations": ["read", "create", "modify", "approve", "export"]}},
            "immobilisations": {"label": "Immobilisations", "sub_modules": {"actif": ACTIONS, "amortissement": ["read", "create", "modify"]}},
        },
    },
    "operations": {
        "label": "Operations portuaires & logistiques",
        "modules": {
            # Batch 23 : sous-modules dedies a l'activite reelle du quai
            # (navires, arrimage, moyens, reservations, connaissements, frais
            # portuaires, dockers) — les plaquer sur « escale » aurait ete du
            # bricolage et un wildcard acconage.*.* sans nuance.
            "acconage": {"label": "Acconage", "sub_modules": {"escale": ACTIONS, "manifeste": ["read", "create", "modify"], "stevedoring": ACTIONS, "navire": ["read", "create", "modify"], "stowage": ["create", "modify", "approve"], "moyen": ["read", "create", "modify"], "reservation": ["create", "modify"], "conteneur": ["create", "modify"], "connaissement": ["create", "modify"], "packing_list": ["create"], "frais": ["read", "create", "modify"], "nettoyage": ["create", "modify"], "dockers": ["read", "create", "modify", "delete", "approve"]}},
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
        "facturation.facture.create", "facturation.facture.modify",
        "fiscalite.*.read", "fiscalite.declarations.create", "fiscalite.declarations.modify",
        "fiscalite.declarations.approve", "immobilisations.*.read",
    ]),
    ("COMPTABLE", 3, "Comptable : saisie et consultation de ses ecritures", [
        "comptabilite.journal.read", "comptabilite.journal.create", "comptabilite.journal.modify",
        "comptabilite.grand_livre.read", "comptabilite.balance.read", "comptabilite.lettrage.read",
        "comptabilite.lettrage.modify",
        # Batch 22 : le comptable consulte le plan et les exercices, corrige
        # reglements et factures, telecharge les PDF  mais ne valide
        # (journal.approve), ne clot pas l'exercice et ne signe pas.
        "comptabilite.plan_comptable.read", "comptabilite.exercice.read",
        "tresorerie.mouvement.read", "tresorerie.mouvement.create", "tresorerie.mouvement.modify",
        "facturation.facture.read", "facturation.facture.create", "facturation.facture.modify",
        "facturation.facture.export", "fiscalite.tva.read",
    ]),
    ("CAISSIER", 3, "Caissier : encaissements, reglements et soldes de tresorerie", [
        "tresorerie.mouvement.read", "tresorerie.mouvement.create", "tresorerie.mouvement.modify",
        "facturation.facture.read",
    ]),
    ("AUDITEUR", 3, "Auditeur : lecture transversale, aucune ecriture", [
        "comptabilite.*.read", "tresorerie.*.read", "facturation.*.read",
        "fiscalite.*.read",
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
    # Batch 21 : le magasinier execute tout le circuit magasin sans jamais
    # approuver (valider reception, traiter retour, approuver inventaire,
    # resoudre litige, exporter les KPI restent la competence du chef).
    ("MAGASINIER", 3, "Magasinier : execution complete des circuits magasin, sans validation", [
        "magasin.stock.read", "magasin.stock.modify",
        "magasin.mouvement.read", "magasin.mouvement.create", "magasin.mouvement.modify",
        "magasin.picking.read", "magasin.picking.create", "magasin.picking.modify",
        "magasin.inventaire.read", "magasin.inventaire.create", "magasin.inventaire.modify",
        "achats.reception.read", "achats.reception.create", "achats.reception.modify",
    ]),
    ("CHEF_MAGASIN", 2, "Chef de magasin : pilotage et validation complete du depot", [
        "magasin.*.*",
        # Le chef execute aussi les receptions et doit pouvoir les valider ;
        # seul le declenchement de commande d'achat (reappro auto) reste
        # un acte d'achat qu'il porte, jamais le magasinier.
        "achats.reception.read", "achats.reception.create", "achats.reception.modify",
        "achats.reception.approve",
        "achats.commande.read", "achats.commande.create",
        "fournisseurs.referentiel.read",
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
    # Batch 23 : le circuit d'acconage (navire -> escale -> arrimage ->
    # manutention -> connaissements -> frais) est pilote par le chef
    # d'exploitation ; l'operateur execute au quai sans jamais approuver
    # (valider le plan d'arrimage, cloturer les dockers, emettre un
    # connaissement ou contester un frais restent des actes du chef).
    ("CHEF_EXPLOITATION", 2, "Chef d'exploitation du terminal : pilotage complet de l'acconage", [
        "acconage.*.*",
        "magasin.stock.read", "transport.*.read",
    ]),
    ("OPERATEUR_ACCONAGE", 3, "Operateur d'acconage : execution au quai, sans validation", [
        "acconage.navire.read", "acconage.escale.read", "acconage.escale.create",
        "acconage.escale.modify",
        "acconage.stowage.create", "acconage.stowage.modify",
        "acconage.moyen.read", "acconage.reservation.create", "acconage.reservation.modify",
        "acconage.conteneur.create", "acconage.conteneur.modify",
        "acconage.manifeste.read", "acconage.manifeste.create", "acconage.manifeste.modify",
        "acconage.packing_list.create",
        "acconage.frais.read", "acconage.frais.create",
        "acconage.nettoyage.create", "acconage.nettoyage.modify",
        "acconage.dockers.read", "acconage.dockers.create", "acconage.dockers.modify",
        "acconage.dockers.delete",
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
