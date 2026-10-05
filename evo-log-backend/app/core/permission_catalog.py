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
            # Batch 24 : le routeur /qhse (38 endpoints + 3 endpoints publics
            # reconvertis) n'avait AUCUN code. Sous-modules alignes sur les
            # objets reels du routeur : analyse de risque, plan/action de
            # prevention, EPI, accident du travail (declarer = acte en soi),
            # investigation, certification, audit interne, HACCP (plan + CCP
            # = un seul objet, le plan ; les enregistrements de controle
            # quotidien sont un objet separate), formation, indicateur,
            # rapport annuel, enregistrements generiques, permis de travail
            # et consultation de la matrice IMDG.
            "qhse": {"label": "QHSE (qualite, hygiene, securite, environnement)", "sub_modules": {"risque": ["create", "modify"], "prevention": ["create", "modify"], "epi": ["create", "modify"], "accident": ["read", "create", "modify"], "investigation": ["read", "create", "modify"], "certification": ["read", "create", "modify"], "audit": ["read", "create", "modify"], "haccp": ["create", "modify"], "controle": ["create", "modify"], "formation": ["read", "create", "modify"], "indicateur": ["create", "modify"], "rapport": ["read"], "enregistrement": ["read", "create", "modify", "delete"], "permis": ["create"], "imdg": ["read"]}},
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
            # portuaires, dockers)  les plaquer sur « escale » aurait ete du
            # bricolage et un wildcard acconage.*.* sans nuance.
            "acconage": {"label": "Acconage", "sub_modules": {"escale": ACTIONS, "manifeste": ["read", "create", "modify"], "stevedoring": ACTIONS, "navire": ["read", "create", "modify"], "stowage": ["create", "modify", "approve"], "moyen": ["read", "create", "modify"], "reservation": ["create", "modify"], "conteneur": ["create", "modify"], "connaissement": ["create", "modify"], "packing_list": ["create"], "frais": ["read", "create", "modify"], "nettoyage": ["create", "modify"], "dockers": ["read", "create", "modify", "delete", "approve"]}},
            "transit": {"label": "Transit & Douane", "sub_modules": {"dossier": ACTIONS, "declaration": ACTIONS, "tarification": ["read", "modify", "approve"]}},
            "magasin": {"label": "Magasin (WMS)", "sub_modules": {"stock": ["read", "modify"], "mouvement": ACTIONS, "inventaire": ["read", "create", "modify", "approve"], "picking": ["read", "create", "modify"]}},
            "port": {"label": "Operations portuaires", "sub_modules": {"quai": ACTIONS, "pesee": ["read", "create"], "zone": ACTIONS}},
        },
    },
    # Departement autonome : l'amenagement portuaire n'est pas l'exploitation
    # du quai. Le module porte les objets juridiques reels du circuit
    # camerounais (schema directeur APN ; programmation : fiche technique, visa
    # de maturite (decret 2018/0492), PIP/CDMT, engagement vise par le controle
    # financier ; marches COLIFE/CIP
    # et PPP loi 2023/008, titres domaniaux, concessions, ouvrages, dragage,
    # autorisations EIES). Pas de « delete » sur les pieces a valeur
    # documentaire : un schema directeur est abroge, une fiche technique annulee,
    # une concession resilie  jamais efface. Le sous-module « place » ne porte
    # pas de delete pour la meme raison : ports_cameroun est le referentiel
    # national partage (tarification, perimetres, terminaux), une place qui sort
    # du perimetre est desactivee (est_actif), pas detruite.
    "amenagement_portuaire": {
        "label": "Amenagement portuaire & domaine public",
        "modules": {
            "amenagement": {"label": "Amenagement portuaire (Douala, Kribi, Limbe)", "sub_modules": {"place": ["read", "create", "modify"], "schema_directeur": ["read", "create", "modify", "approve", "export"], "projet": ACTIONS, "programmation": ["read", "create", "modify", "approve", "export"], "marche": ACTIONS, "titre_domanial": ACTIONS, "concession": ["read", "create", "modify", "approve", "export"], "infrastructure": ACTIONS, "dragage": ACTIONS, "autorisation": ["read", "create", "modify", "approve", "export"]}},
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
        # L'engagement des credits d'investissement passe par la fiche technique
        # visa de maturite puis le visa du controle financier : le DAF instruit
        # la ligne et l'approuve, il ne gere ni les travaux ni le domaine.
        "amenagement.projet.read", "amenagement.marche.read",
        "amenagement.concession.read", "amenagement.programmation.read",
        "amenagement.programmation.approve", "amenagement.programmation.export",
        # La synthese et les formulaires lisent le referentiel des places : sans
        # ce code, un DAF qui ouvre le departement verrait des listes vides.
        "amenagement.place.read",
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
        # Batch 24 : meme lecture transversale sur le QHSE (rapports annuels
        # includes), sans jamais d'ecriture.
        "qhse.*.read",
        # L'auditeur verifie le domaine : lire les pieces a valeur (programmation,
        # marches, titres, concessions) sans pouvoir y toucher.
        "amenagement.*.read",
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
    ("QHSE", 3, "Officier QHSE : conformite, incidents et pilotage du systeme", [
        "gouvernance.*.read", "transport.*.read", "parc.documents.read",
        # Batch 24 : l'officier porte desormais tout le module qhse. Pas
        # d'action « approve » n'expose ici : declarer un accident ou mener
        # une investigation sont deja des actes completes, pas des brouillons
        # a valider par un tiers.
        "qhse.*.*",
    ]),
    # Batch 23 : le circuit d'acconage (navire -> escale -> arrimage ->
    # manutention -> connaissements -> frais) est pilote par le chef
    # d'exploitation ; l'operateur execute au quai sans jamais approuver
    # (valider le plan d'arrimage, cloturer les dockers, emettre un
    # connaissement ou contester un frais restent des actes du chef).
    ("CHEF_EXPLOITATION", 2, "Chef d'exploitation du terminal : pilotage complet de l'acconage", [
        "acconage.*.*",
        "magasin.stock.read", "transport.*.read",
        # Batch 24 : le chef n'est pas officier QHSE, mais c'est lui qui
        # declare les accidents du quai, demande un permis de travail,
        # consulte la segregation IMDG avant co-stivage et signale un risque.
        "qhse.accident.read", "qhse.accident.create", "qhse.accident.modify",
        "qhse.permis.create", "qhse.imdg.read", "qhse.risque.create",
        # Un chantier d'amenagement ferme un poste ou change la portance d'une
        # aire : le chef d'exploitation doit voir l'avancement et les arretes
        # domaniaux, sans les rediger.
        "amenagement.infrastructure.read", "amenagement.dragage.read",
        "amenagement.projet.read", "amenagement.titre_domanial.read",
        # Un poste ferme ou une aire changeee se refere a la place portuaire :
        # lecture du referentiel, jamais declaration d'une place.
        "amenagement.place.read",
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
    # Departement amenagement portuaire. Le chef de departement porte les
    # actes d'engagement (approbation d'un schema directeur, visa de maturite,
    # attribution d'un marche, delivrance d'un titre domanial) ; l'ingenieur
    # preparatoire instruit et tient l'inventaire sans jamais trancher.
    ("CHEF_AMENAGEMENT_PORTUAIRE", 2, "Chef du departement amenagement portuaire : pilotage complet du domaine et des operations", [
        "amenagement.*.*",
        # Le chef d'amenagement instruit les dossiers qui engagent la caisse
        # et doit donc lire la programmation finance ; il n'approuve rien cote
        # comptable.
        "comptabilite.journal.read", "tresorerie.mouvement.read",
        "port.quai.read", "port.zone.read",
        "qhse.certification.read", "qhse.enregistrement.read",
    ]),
    ("INGENIEUR_AMENAGEMENT", 3, "Ingenieur genie portuaire : etudes, suivi des travaux et inventaire du domaine", [
        "amenagement.*.read",
        # Regle du role : il tient les neuf registres (saisie et correction), il
        # ne tranche rien. Les create/modify couvrent donc les NEUF sous-modules
        # -- concession comprise, le cahier des charges et la consistance des
        # biens reversibles etant des pieces techniques --, tandis que les
        # approve (actes d'engagement) et les delete restent du chef.
        "amenagement.schema_directeur.create", "amenagement.schema_directeur.modify",
        "amenagement.projet.create", "amenagement.projet.modify",
        "amenagement.programmation.create", "amenagement.programmation.modify",
        "amenagement.marche.create", "amenagement.marche.modify",
        "amenagement.titre_domanial.create", "amenagement.titre_domanial.modify",
        "amenagement.concession.create", "amenagement.concession.modify",
        "amenagement.infrastructure.create", "amenagement.infrastructure.modify",
        "amenagement.dragage.create", "amenagement.dragage.modify",
        "amenagement.autorisation.create", "amenagement.autorisation.modify",
        # Le referentiel des places n'est alimente par aucune autre route de
        # l'application : c'est l'ingenieur qui releve code, denomination,
        # autorite concessionnaire et tirant d'eau sur les documents officiels.
        # Il ne supprime jamais une place (table partagee) : il la desactive.
        "amenagement.place.create", "amenagement.place.modify",
        # Un quai mis hors service pour travaux se coordonne avec l'exploitation :
        # lecture utile, pas decision.
        "port.quai.read",
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
