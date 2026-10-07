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
            "qhse": {"label": "QHSE (qualite, hygiene, securite, environnement)", "sub_modules": {"risque": ["create", "modify"], "prevention": ["create", "modify"], "epi": ["create", "modify"], "accident": ["read", "create", "modify"], "investigation": ["read", "create", "modify"], "certification": ["read", "create", "modify"], "audit": ["read", "create", "modify"], "haccp": ["create", "modify"], "controle": ["create", "modify"], "formation": ["read", "create", "modify"], "indicateur": ["create", "modify"], "rapport": ["read"], "enregistrement": ["read", "create", "modify", "delete"], "permis": ["read", "create"], "imdg": ["read"],
                # Expansion QHSE approfondi (routeur qhse_deep). Objets reels du systeme
                # de management (evaluation de risque, action corrective, plan d'urgence,
                # environnement, sante au travail, suivi EPI, conformite reglementaire,
                # audit qualite, revue de direction, dechets, securite chimique). QHSE
                # (« qhse.*.* ») porte, AUDITEUR (« qhse.*.read ») lit.
                "nomenclature": ["read"], "risk_assessment": ["read", "create", "modify"],
                "corrective_action": ["read", "create", "modify"], "emergency_plan": ["read", "create", "modify"],
                "environmental": ["read", "create", "modify"], "occupational_health": ["read", "create", "modify"],
                "ppe_tracking": ["read", "create", "modify"], "regulatory_compliance": ["read", "create", "modify"],
                "quality_audit": ["read", "create", "modify"], "management_review": ["read", "create", "modify"],
                "waste_management": ["read", "create", "modify"], "chemical_safety": ["read", "create", "modify"]}},
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
            "comptabilite": {"label": "Comptabilite SYSCOHADA", "sub_modules": {"journal": ACTIONS, "grand_livre": ["read", "export"], "balance": ["read", "export"], "bilan": ["read", "create", "modify", "approve", "export"], "lettrage": ["read", "modify"], "plan_comptable": ["read", "create", "modify"], "exercice": ["read", "create", "modify", "approve"], "compte_resultat": ["read", "create", "modify"],
                # Expansion comptabilite approfondie (routeur comptabilite_deep). Objets
                # reels du departement (comabilite analytique, piste d'audit, rapprochement
                # bancaire, controle budgetaire, amortissements, actifs immobilises,
                # conventions intragroupe, comptes de paie, provisions, declaration fiscale,
                # comptes de tresorerie) plus la nomenclature. DIRECTEUR_FINANCIER et
                # CHEF_COMPTABLE (« comptabilite.*.* ») pilotent, COMPTABLE garde sa liste
                # explicite, AUDITEUR (« comptabilite.*.read ») lit.
                "nomenclature": ["read"], "analytical_accounting": ["read", "create", "modify"],
                "audit_trail": ["read", "create", "modify"], "bank_reconciliation": ["read", "create", "modify"],
                "budget_control": ["read", "create", "modify"], "depreciation": ["read", "create", "modify"],
                "fixed_asset": ["read", "create", "modify"], "intercompany": ["read", "create", "modify"],
                "payroll_accounts": ["read", "create", "modify"], "provision": ["read", "create", "modify"],
                "tax_declaration": ["read", "create", "modify"], "treasury_accounts": ["read", "create", "modify"]}},
            "tresorerie": {"label": "Tresorerie", "sub_modules": {"mouvement": ACTIONS, "rapprochement": ["read", "modify"],
                # Expansion finance/tresorerie approfondie (routeur finance_deep). Objets
                # reels de la direction financiere (garantie bancaire, gestion budgetaire,
                # cash pooling, ligne de credit, note de frais, previsionnel, gestion FX,
                # suivi des investissements, comptabilite de credit-bail, echeancier de
                # paiement, caisse menue, alertes de tresorerie) plus la nomenclature.
                # DIRECTEUR_FINANCIER (« tresorerie.*.* ») pilote, CHEF_COMPTABLE et
                # AUDITEUR (« tresorerie.*.read ») lisent, CAISSIER garde sa liste explicite.
                "nomenclature": ["read"], "bank_guarantee": ["read", "create", "modify"],
                "budget_management": ["read", "create", "modify"], "cash_pooling": ["read", "create", "modify"],
                "credit_facility": ["read", "create", "modify"], "expense_report": ["read", "create", "modify"],
                "financial_forecast": ["read", "create", "modify"], "fx_management": ["read", "create", "modify"],
                "investment_tracking": ["read", "create", "modify"], "lease_accounting": ["read", "create", "modify"],
                "payment_scheduling": ["read", "create", "modify"], "petty_cash": ["read", "create", "modify"],
                "treasury_alerts": ["read", "create", "modify"]}},
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
            "transit": {"label": "Transit & Douane", "sub_modules": {"dossier": ACTIONS, "declaration": ACTIONS, "tarification": ["read", "modify", "approve"],
                # Expansion transit-douane approfondi (routeur transit_deep). Sous-modules
                # alignes sur les objets reels du circuit (regime, valeur, droits,
                # inspection, garantie, classification SH, marchandise prohibee, ...).
                # Tous en lecture/creation/modification ; TRANSIT_PRINCIPAL (« transit.*.* »)
                # pilote, DECLARANT garde sa liste explicite, AUDITEUR (« transit.*.read ») lit.
                "nomenclature": ["read"], "customs_regime": ["read", "create", "modify"],
                "customs_valuation": ["read", "create", "modify"], "duty_payment": ["read", "create", "modify"],
                "export_declaration": ["read", "create", "modify"], "physical_inspection": ["read", "create", "modify"],
                "transit_guarantee": ["read", "create", "modify"], "bonded_warehouse": ["read", "create", "modify"],
                "hs_classification": ["read", "create", "modify"], "origin_certificate": ["read", "create", "modify"],
                "prohibited_good": ["read", "create", "modify"], "trader_registration": ["read", "create", "modify"],
                "tariff_reference": ["read", "create", "modify"]}},
            "magasin": {"label": "Magasin (WMS)", "sub_modules": {"stock": ["read", "modify"], "mouvement": ACTIONS, "inventaire": ["read", "create", "modify", "approve"], "picking": ["read", "create", "modify"],
                # Expansion WMS approfondi (routeur magasin_deep). Registres reels du
                # depot (catalogue article/fournisseur, peremption FEFO, serial/lot,
                # controle qualite, retours, consignation, valorisation, alertes,
                # analytic). CHEF_MAGASIN (« magasin.*.* ») pilote, MAGASINIER garde sa
                # liste explicite sans validation, AUDITEUR (« magasin.*.read ») lit.
                "nomenclature": ["read"], "article_catalog": ["read", "create", "modify"],
                "supplier_catalog": ["read", "create", "modify"], "packing_unit": ["read", "create", "modify"],
                "expiry_tracking": ["read", "create", "modify"], "serial_tracking": ["read", "create", "modify"],
                "consignment_stock": ["read", "create", "modify"], "quality_control": ["read", "create", "modify"],
                "returns_management": ["read", "create", "modify"], "stock_alert": ["read", "create", "modify"],
                "stock_valuation": ["read", "create", "modify"], "purchase_order": ["read", "create", "modify"],
                "wms_analytics": ["read", "create", "modify"]}},
            "port": {"label": "Operations portuaires", "sub_modules": {"quai": ACTIONS, "pesee": ["read", "create"], "zone": ACTIONS,
                # Expansion operations portuaires approfondies (routeur port_deep). Registres
                # reels de l'escale et du terminal (soutage/bunkering, plan de chargement,
                # surestarie demurrage, releve de tirant d'eau, laissez-pour-circle gate pass,
                # pilotage, equipements de quai, equipe de manutention, tally, remorquage,
                # dechets navires, parc/yard) plus registre navires et nomenclature.
                # CHEF_EXPLOITATION (« port.*.* ») pilote le terminal, AUDITEUR
                # (« port.*.read ») lit. Les codes historiques quai/pesee/zone restent.
                "nomenclature": ["read"], "vessel_registry": ["read"], "bunkering": ["read", "create", "modify"],
                "cargo_plan": ["read", "create", "modify"], "demurrage": ["read", "create", "modify"],
                "draft_survey": ["read", "create", "modify"], "gate_pass": ["read", "create", "modify"],
                "pilotage": ["read", "create", "modify"], "quay_equipment": ["read", "create", "modify"],
                "stevedoring_crew": ["read", "create", "modify"], "tally": ["read", "create", "modify"],
                "towage": ["read", "create", "modify"], "vessel_waste": ["read", "create", "modify"],
                "yard": ["read", "create", "modify"]}},
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
            "amenagement": {"label": "Amenagement portuaire (Douala, Kribi, Limbe)", "sub_modules": {"place": ["read", "create", "modify"], "schema_directeur": ["read", "create", "modify", "approve", "export"], "projet": ACTIONS, "programmation": ["read", "create", "modify", "approve", "export"], "marche": ACTIONS, "titre_domanial": ACTIONS, "concession": ["read", "create", "modify", "approve", "export"], "infrastructure": ACTIONS, "dragage": ACTIONS, "autorisation": ["read", "create", "modify", "approve", "export"],
                # Expansion du departement (routeur amenagement_extra_deep) :
                # registres operationnels reels du domaine. Chaque objet est une
                # piece a valeur documentaire -> le routeur garde le DELETE sous
                # le code « modify » (corriger, jamais effacer), d'ou read/create/
                # modify seulement. CHEF_AMENAGEMENT_PORTUAIRE (« amenagement.*.* »)
                # pilote, INGENIEUR et AUDITEUR (« amenagement.*.read ») consultent.
                "nomenclature": ["read"],
                "construction_tracking": ["read", "create", "modify"],
                "infrastructure_maintenance": ["read", "create", "modify"],
                "port_security_isps": ["read", "create", "modify"],
                "port_pricing": ["read", "create", "modify"],
                "activity_report": ["read", "create", "modify"],
                "domain_cartography": ["read", "create", "modify"],
                "archive_management": ["read", "create", "modify"],
                "development_kpi": ["read", "create", "modify"]}},
        },
    },
    "transport": {
        "label": "Transport & Flotte",
        "modules": {
            "transport": {"label": "Transport", "sub_modules": {"mission": ACTIONS, "dispatch": ["read", "create", "modify", "approve"], "epod": ["read", "create", "modify"], "carburant": ACTIONS,
                # Expansion transport approfondi (routeur transport_deep). Registres reels
                # de l'exploitation du fret (plan de tournee, convoi, matieres dangereuses
                # ADR, facturation fret, checkpoint, penalites, assurance marchandise,
                # sous-traitant, registre/documentation vehicule, dispositif GPS, KPI de
                # performance) plus la nomenclature. CHEF_PARC (« transport.*.* ») pilote
                # le fret, DISPATCHER garde sa liste explicite missions/tournees, AUDITEUR
                # (« transport.*.read ») lit.
                "nomenclature": ["read"], "route_plan": ["read", "create", "modify"],
                "convoy": ["read", "create", "modify"], "dangerous_goods": ["read", "create", "modify"],
                "freight_billing": ["read", "create", "modify"], "checkpoint": ["read", "create", "modify"],
                "penalty": ["read", "create", "modify"], "cargo_insurance": ["read", "create", "modify"],
                "subcontractor": ["read", "create", "modify"], "vehicle_registry": ["read", "create", "modify"],
                "vehicle_document": ["read", "create", "modify"], "gps_device": ["read", "create", "modify"],
                "performance_kpi": ["read", "create", "modify"]}},
            "parc": {"label": "Parc vehicules", "sub_modules": {"flotte": ACTIONS, "maintenance": ACTIONS, "documents": ["read", "create", "modify"],
                # Expansion parc approfondie (routeur parc_deep). Gestion complete du
                # cycle vehicule (inventaire,/immatriculation, visite technique, pneus,
                # pieces detachees, consommation carburant, sinistre assurance, atelier,
                # analyse cout, cycle de vie). CHEF_PARC (« parc.*.* ») pilote.
                "nomenclature": ["read"], "vehicle_inventory": ["read", "create", "modify"],
                "registration_tracking": ["read", "create", "modify"], "technical_visit": ["read", "create", "modify"],
                "tyre_management": ["read", "create", "modify"], "spare_part": ["read", "create", "modify"],
                "fuel_consumption": ["read", "create", "modify"], "insurance_claim": ["read", "create", "modify"],
                "workshop_scheduling": ["read", "create", "modify"], "cost_analysis": ["read", "create", "modify"],
                "vehicle_lifecycle": ["read", "create", "modify"]}},
            "gps": {"label": "Suivi GPS", "sub_modules": {"tracking": ["read"], "alertes": ["read", "modify"]}},
        },
    },
    "ressources_humaines": {
        "label": "Ressources Humaines",
        "modules": {
            "rh": {"label": "Administration du personnel", "sub_modules": {"employes": ACTIONS, "contrat": ACTIONS, "monitoring": ["read", "modify"],
                # Expansion RH approfondie (routeur rh_deep). Fonctions RH reelles
                # (recrutement,entretien d'evaluation, gestion des sorties, disciplinaire,
                # Avantages, masse salariale/planning, organisation, competences, formation,
                # contingent conges, reporting HR, badgeage). ADMIN_RH (« rh.*.* ») pilote,
                # CHEF_DEPARTEMENT garde son perimetre, AUDITEUR ne lit pas rh (hors scope).
                "nomenclature": ["read"], "recruitment": ["read", "create", "modify"],
                "performance_review": ["read", "create", "modify"], "exit_management": ["read", "create", "modify"],
                "disciplinary": ["read", "create", "modify"], "benefits": ["read", "create", "modify"],
                "workforce_planning": ["read", "create", "modify"], "org_chart": ["read", "create", "modify"],
                "skills_matrix": ["read", "create", "modify"], "training": ["read", "create", "modify"],
                "leave_quota": ["read", "create", "modify"], "hr_reports": ["read", "create", "modify"],
                "attendance_device": ["read", "create", "modify"], "contract_management": ["read", "create", "modify"]}},
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
            # Portail client B2B (routeur b2b_deep). Registres propres de la relation
            # commerciale en libre-service client (reservation d'acheminement, suivi
            # contractuel et accords tarifaires, limite de credit, echange de documents,
            # demande de service, reclamation/litige, enquete de satisfaction, rapport de
            # compte, onboarding client, pilotage SLA) plus la nomenclature. RESPONSABLE_
            # COMMERCIAL (« b2b.*.* ») pilote le portail ; les clients externes ne sont pas
            # des roles systeme seeds ici (authentification portail distincte).
            "b2b": {"label": "Portail client B2B", "sub_modules": {"nomenclature": ["read"],
                "shipment_booking": ["read", "create", "modify"], "contract_tracking": ["read", "create", "modify"],
                "pricing_agreement": ["read", "create", "modify"], "credit_limit": ["read", "create", "modify"],
                "document_exchange": ["read", "create", "modify"], "service_request": ["read", "create", "modify"],
                "claim_dispute": ["read", "create", "modify"], "satisfaction_survey": ["read", "create", "modify"],
                "account_report": ["read", "create", "modify"], "client_onboarding": ["read", "create", "modify"],
                "sla_management": ["read", "create", "modify"]}},
        },
    },
    # Consoles de plateforme (SaaS operateur). Ces quatre modules ne sont PAS un
    # perimetre metier : ils sont reservees au proprietaire de la plateforme
    # (SUPER_ADMIN, niveau 0) et a l'administrateur de l'entreprise locataire
    # (ADMIN_ENTREPRISE, niveau 1). Le moteur d'autorisation (permissions.py)
    # fait BYPASSER les niveaux 0/1 : ces routes leurs sont donc ouvertes sans
    # ligne « permissions » accordee, et FERMEES (403) a tout role metier
    # (niveaux 2/3). Volonte explicite, pas un oubli : aucun ROLE_GRANTS metier
    # ne porte ces codes. Ils sont declares ici pour que la table « permissions »,
    # la matrice d'admin et GET /permissions/catalog les rendent VISIBLES et
    # auditable, non pour etre grantes a un departement.
    "plateforme": {
        "label": "Console plateforme (reserves SuperAdmin / Admin-entreprise)",
        "modules": {
            "admin": {"label": "Administration SaaS (tenant)", "sub_modules": {"nomenclature": ["read"],
                "api_key": ["read", "create", "modify"], "billing_engine": ["read", "create", "modify"],
                "data_migration": ["read", "create", "modify"], "feature_flag": ["read", "create", "modify"],
                "onboarding_wizard": ["read", "create", "modify"], "rate_limit": ["read", "create", "modify"],
                "support_ticket": ["read", "create", "modify"], "uptime_monitoring": ["read", "create", "modify"],
                "usage_analytics": ["read", "create", "modify"], "webhook": ["read", "create", "modify"],
                "white_label": ["read", "create", "modify"]}},
            "superadmin": {"label": "Console super administrateur", "sub_modules": {"nomenclature": ["read"],
                "access_review": ["read", "create", "modify"], "compliance_dashboards": ["read", "create", "modify"],
                "data_retention": ["read", "create", "modify"], "disaster_recovery": ["read", "create", "modify"],
                "incident_response": ["read", "create", "modify"], "license_management": ["read", "create", "modify"],
                "partner_network": ["read", "create", "modify"], "platform_audit": ["read", "create", "modify"],
                "revenue_analytics": ["read", "create", "modify"], "system_config": ["read", "create", "modify"]}},
            "dashboard": {"label": "Tableau de bord transverse", "sub_modules": {"nomenclature": ["read"],
                "activity_feed": ["read", "create", "modify"], "calendar_agenda": ["read", "create", "modify"],
                "document_center": ["read", "create", "modify"], "financial_summary": ["read", "create", "modify"],
                "integration_status": ["read", "create", "modify"], "module_health": ["read", "create", "modify"],
                "operational_alerts": ["read", "create", "modify"], "quick_actions": ["read", "create", "modify"],
                "task_center": ["read", "create", "modify"], "team_performance": ["read", "create", "modify"]}},
            "reports": {"label": "BI & analytique", "sub_modules": {"nomenclature": ["read"],
                "anomaly_detection": ["read", "create", "modify"], "benchmark": ["read", "create", "modify"],
                "cohort_analysis": ["read", "create", "modify"], "custom_dashboard": ["read", "create", "modify"],
                "data_warehouse": ["read", "create", "modify"], "drill_down": ["read", "create", "modify"],
                "export_reports": ["read", "create", "modify"], "kpi_definition": ["read", "create", "modify"],
                "predictive_analytics": ["read", "create", "modify"], "regulatory_report": ["read", "create", "modify"],
                "scorecard": ["read", "create", "modify"]}},
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
        # Lecture transversale des operations du terminal (routeur port_deep).
        "port.*.read",
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
    # Portail client B2B (routeur b2b_deep). Le responsable commercial pilote la
    # relation client en libre-service (reservations, contrats/tarifs, credit,
    # documents, reclamations, SLA, rapports de compte). Il lit la facturation
    # pour afficher factures et devis du client dans son portail, sans y toucher.
    ("RESPONSABLE_COMMERCIAL", 2, "Responsable commercial : pilotage du portail client B2B", [
        "b2b.*.*", "facturation.*.read",
    ]),
    ("CHEF_PARC", 2, "Chef de parc : gestion complete de la flotte et du fret", [
        "parc.*.*",
        # Le chef de parc porte aussi l'exploitation du fret (routeur
        # transport_deep : tournees, convois, ADR, facturation fret,
        # checkpoints, penalites, assurance marchandise, sous-traitants,
        # registre/documentation vehicule, KPI). Il etend « transport.*.read »
        # qu'il detient deja en lecture.
        "transport.*.*", "gps.tracking.read", "gps.alertes.modify",
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
    ("CHEF_EXPLOITATION", 2, "Chef d'exploitation du terminal : pilotage complet de l'acconage et des operations de quai", [
        "acconage.*.*",
        # Le chef d'exploitation est le proprietaire metier des operations du
        # terminal (routeur port_deep : escale, soutage, pilotage, remorquage,
        # manutention, demurrage, gate pass, tally, parc, dechets navires).
        "port.*.*",
        "magasin.stock.read", "transport.*.read",
        # Batch 24 : le chef n'est pas officier QHSE, mais c'est lui qui
        # declare les accidents du quai, demande un permis de travail,
        # consulte la segregation IMDG avant co-stivage et signale un risque.
        "qhse.accident.read", "qhse.accident.create", "qhse.accident.modify",
        "qhse.permis.create", "qhse.permis.read", "qhse.imdg.read", "qhse.risque.create",
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
