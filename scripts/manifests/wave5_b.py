"""Manifest Vague B : porte 6 modules operationnels a >= 20 sous-modules reels.

EXTENSION (« *_b ») de modules deja generes, meme principe que la Vague A :
  - module_slug / module_path IDENTIQUES au module d'origine -> routeur monte
    sous le MEME prefixe /api/v1/<slug> ;
  - perm_module = module metier reel couvert par le wildcard ROLE_GRANTS
    existant (port_ops_b -> « port.*.* » CHEF_EXPLOITATION ; amenagement_b ->
    « amenagement.*.* » ; transit_b -> « transit.*.* » ; transport_b ->
    « transport.*.* » ; magasin_b -> « magasin.*.* » ; dashboard_b -> « dashboard »
    console plateforme, coherent avec les sous-modules dashboard deja presents) ;
  - module_key / table / class_name / slug / entite DIFFERENTS -> aucun conflit ;
    registre_frontend separe (registres_b).

Honnetete Zero-Mock : chaque entite est un objet metier reel et nomme du domain
(plan de poste d'amarrage VTS, projet de dragage, incoterm, POD, inventaire,
reception marchandise, KPI operationnel, regle d'alerte...), pas un placeholder.

Convention d'honnetete : aucune valeur par defaut fabriquee ; NULL = « non
enregistre » ; statut = cycle de vie metier explicite.
"""


def E(slug, table, cn, entite, perm, titre, titreEn, desc, descEn, aide, aideEn, icon,
      unicite, fields, enums=None):
    return dict(slug=slug, table=table, class_name=cn, entite=entite, perm=perm,
                titre=titre, titreEn=titreEn, description=desc, descriptionEn=descEn,
                aide=aide, aideEn=aideEn, icon=icon, unicite=unicite,
                fields=fields, enums=enums or [])


def F(name, typ, label, labelEn=None, required=False, search=False):
    d = dict(name=name, type=typ, label=label, labelEn=labelEn or label)
    if required:
        d["required"] = True
    if search:
        d["search"] = True
    return d


def EN(name, values, default=None):
    d = dict(name=name, values=values)
    if default:
        d["default"] = default
    return d


MODULES = {}

# ─── port-operations (+2 -> 20) ──────────────────────────────────────────────
MODULES["port_ops_b"] = dict(
    module_key="port_ops_b", module_slug="port-operations",
    module_path="port-operations", perm_module="port",
    registre_filename="registres_b",
    # Re-parente sur 076_heavylift_deep (branche pipeline/courier/coldchain/heavylift
    # restee en attente sur 072) pour garder un seul head lineaire.
    revision="073", down_revision="076_heavylift_deep",
    entities=[
        E("berth-schedules", "portb_berth_schedules", "PortbBerthSchedule", "portb-berth-schedules",
          "berth_schedule", "Plans d'escale et postes d'amarrage", "Berth schedules",
          "Affectation d'un poste d'amarrage et d'un creneau a un navire.",
          "Assignment of a berth and time window to a vessel.",
          "Un poste par creneau ; conflits de quais a eviter.", "One berth per slot; avoid quay conflicts.",
          "Anchor", "reference",
          [F("reference", "str", "Reference escale", "Call reference", required=True, search=True),
           F("navire", "str", "Navire", "Vessel"),
           F("numero_imo", "str", "Numero IMO", "IMO number"),
           F("poste_amarrage", "str", "Poste d'amarrage", "Berth"),
           F("date_arrivee_prevue", "datetime", "ETA", "ETA"),
           F("date_depart_prevu", "datetime", "ETD", "ETD"),
           F("type_cargo", "str", "Type de cargo", "Cargo type"),
           F("pilote", "str", "Pilote", "Pilot"),
           F("statut", "str", "Statut", "Status")],
          [EN("type_cargo", ["CONTENEUR", "VRAQUE_LIQUIDE", "VRAQUE_SEC", "RO_RO", "GENERAL"]),
           EN("statut", ["PLANIFIE", "CONFIRME", "EN_ESCALE", "LIBERE", "ANNULE"])]),

        E("vessel-traffic-logs", "portb_vessel_traffic", "PortbVesselTrafficLog", "portb-vessel-traffic-logs",
          "vessel_traffic_log", "Journal de trafic maritime (VTS)", "Vessel traffic logs",
          "Enregistrement des mouvements de navires dans la zone VTS.",
          "Record of vessel movements within the VTS area.",
          "Chaque mouvement est horodate et verifie par l'operateur VTS.",
          "Each movement is timestamped and checked by the VTS operator.",
          "Ship", "reference",
          [F("reference", "str", "Reference mouvement", "Movement reference", required=True, search=True),
           F("nom_navire", "str", "Nom du navire", "Vessel name"),
           F("numero_imo", "str", "Numero IMO", "IMO number"),
           F("mouvement", "str", "Mouvement", "Movement"),
           F("balise_vts", "str", "Balise VTS", "VTS beacon"),
           F("horodatage", "datetime", "Horodatage", "Timestamp"),
           F("operateur", "str", "Operateur", "Operator"),
           F("statut", "str", "Statut", "Status")],
          [EN("mouvement", ["ENTREE", "SORTIE", "TRANSIT", "MOUILLE"]),
           EN("statut", ["ENREGISTRE", "VERIFIE", "SIGNALE", "ARCHEVE"])]),
    ],
)

# ─── amenagement-portuaire (+2 -> 20) ────────────────────────────────────────
MODULES["amenagement_b"] = dict(
    module_key="amenagement_b", module_slug="amenagement-portuaire",
    module_path="amenagement-portuaire", perm_module="amenagement",
    registre_filename="registres_b",
    revision="074", down_revision="073_port_ops_b_deep",
    entities=[
        E("dredging-projects", "amgtb_dredging_projects", "AmgtbDredgingProject", "amgtb-dredging-projects",
          "dredging_project", "Projets de dragage", "Dredging projects",
          "Suivi des campagnes de dragage des chenaux et zones d'accostage.",
          "Tracking of channel and berth basin dredging campaigns.",
          "Volume rejete vs volume dragre ; exutoire delimite.",
          "Spoil volume vs dredged volume; defined disposal site.",
          "Shovel", "reference",
          [F("reference", "str", "Reference projet", "Project reference", required=True, search=True),
           F("zone", "str", "Zone", "Area"),
           F("objectif_tirant_eau_m", "int", "Objectif tirant d'eau (m)", "Target draft (m)"),
           F("volume_a_draguer_m3", "int", "Volume a draguer (m3)", "Volume to dredge (m3)"),
           F("volume_rejete_m3", "int", "Volume rejete (m3)", "Spoil volume (m3)"),
           F("entreprise", "str", "Entreprise", "Contractor"),
           F("date_debut", "date", "Date debut", "Start date"),
           F("date_fin", "date", "Date fin", "End date"),
           F("statut", "str", "Statut", "Status")],
          [EN("statut", ["ETUDE", "APPEL_OFFRES", "EN_COURS", "ACHEVE", "SUSPENDU"])]),

        E("concession-plots", "amgtb_concession_plots", "AmgtbConcessionPlot", "amgtb-concession-plots",
          "concession_plot", "Parcelles sous concession", "Concession plots",
          "Inventaire des terrains portuaires concodes et de leur echeance.",
          "Inventory of port land plots under concession and their expiry.",
          "Redevance annuelle et echeance suivies par parcelle.",
          "Annual fee and expiry tracked per plot.",
          "LandPlot", "reference",
          [F("reference", "str", "Reference parcelle", "Plot reference", required=True, search=True),
           F("designation", "str", "Designation", "Designation"),
           F("superficie_m2", "int", "Superficie (m2)", "Area (m2)"),
           F("concessionnaire", "str", "Concessionnaire", "Concessionaire"),
           F("date_debut", "date", "Debut concession", "Concession start"),
           F("date_echeance", "date", "Echeance", "Expiry date"),
           F("redevance_annuelle", "num", "Redevance annuelle", "Annual fee"),
           F("statut", "str", "Statut", "Status")],
          [EN("statut", ["LIBRE", "CONCEDE", "RENOUVELABLE", "RESILIE"])]),
    ],
)

# ─── transit-douane (+2 -> 20) ───────────────────────────────────────────────
MODULES["transit_b"] = dict(
    module_key="transit_b", module_slug="transit-douane",
    module_path="transit-douane", perm_module="transit",
    registre_filename="registres_b",
    revision="075", down_revision="074_amenagement_b_deep",
    entities=[
        E("incoterm-terms", "transitb_incoterms", "TransitbIncoterm", "transitb-incoterms",
          "incoterm_term", "Incoterms applicables", "Incoterm terms",
          "Referentiel des incoterms et de leur version.",
          "Reference of incoterms and their version.",
          "Le transfert de risque et le lieu font la valeur de l'incoterm.",
          "Risk transfer point and place define the incoterm.",
          "Scale", "code",
          [F("code", "str", "Code incoterm", "Incoterm code", required=True, search=True),
           F("libelle", "str", "Libelle", "Label"),
           F("categorie", "str", "Categorie", "Category"),
           F("transfert_risque_lieu", "str", "Lieu transfert risque", "Risk transfer place"),
           F("transport_principal", "str", "Transport principal", "Main carriage"),
           F("version", "str", "Version", "Version"),
           F("statut", "str", "Statut", "Status")],
          [EN("categorie", ["E", "F", "C", "D"]),
           EN("version", ["2010", "2020"]),
           EN("statut", ["ACTIF", "OBSOLETE"])]),

        E("customs-inspection-records", "transitb_inspections", "TransitbInspectionRecord", "transitb-customs-inspections",
          "inspection_record", "Proces-verbaux de visite douaniere", "Customs inspection records",
          "Consigne des visites (documentaire, physique, radiographie) et resultats.",
          "Log of customs examinations (document, physical, x-ray) and outcomes.",
          "Chaque visite a un agent responsable et un resultat trace.",
          "Each inspection has a responsible officer and a recorded outcome.",
          "SearchCheck", "reference",
          [F("reference", "str", "Reference visite", "Inspection reference", required=True, search=True),
           F("declaration", "str", "Declaration", "Declaration"),
           F("type_visite", "str", "Type de visite", "Inspection type"),
           F("agent", "str", "Agent", "Officer"),
           F("bureau", "str", "Bureau", "Office"),
           F("date_inspection", "datetime", "Date inspection", "Inspection date"),
           F("observation", "text", "Observation", "Observation"),
           F("conformite", "bool", "Conforme", "Compliant"),
           F("statut", "str", "Statut", "Status")],
          [EN("type_visite", ["DOCUMENTAIRE", "PHYSIQUE", "RADIOGRAPHIE"]),
           EN("statut", ["CONFORME", "NON_CONFORME", "LITIGE", "EN_ATTENTE"])]),
    ],
)

# ─── transport-flotte (+2 -> 20) ─────────────────────────────────────────────
MODULES["transport_b"] = dict(
    module_key="transport_b", module_slug="transport-flotte",
    module_path="transport-flotte", perm_module="transport",
    registre_filename="registres_b",
    revision="076", down_revision="075_transit_b_deep",
    entities=[
        E("mission-dispatches", "transportb_dispatches", "TransportbDispatch", "transportb-dispatches",
          "dispatch", "Bons de mission / affectation", "Mission dispatches",
          "Affectation d'un vehicule et d'un chauffeur a une mission de transport.",
          "Assignment of a vehicle and driver to a transport mission.",
          "Distance reellement parcourue vs previsonnelle.",
          "Actual distance vs planned.",
          "Navigation", "reference",
          [F("reference", "str", "Reference mission", "Mission reference", required=True, search=True),
           F("chauffeur", "str", "Chauffeur", "Driver"),
           F("vehicule", "str", "Vehicule", "Vehicle"),
           F("point_depart", "str", "Point de depart", "Pickup point"),
           F("point_arrivee", "str", "Point d'arrivee", "Drop-off point"),
           F("date_depart", "datetime", "Depart", "Departure"),
           F("date_arrivee", "datetime", "Arrivee", "Arrival"),
           F("km_parcourus", "int", "Km parcourus", "Km driven"),
           F("statut", "str", "Statut", "Status")],
          [EN("statut", ["AFFECTEE", "EN_ROUTE", "LIVREE", "RETARD", "ANNULEE"])]),

        E("proof-of-delivery", "transportb_pods", "TransportbPod", "transportb-proof-delivery",
          "pod", "Preuves de livraison (POD)", "Proof of delivery",
          "Accuse de livraison signe par le destinataire.",
          "Delivery receipt signed by the consignee.",
          "Signature et nombre de colis livres font foi de la livraison.",
          "Signature and delivered parcel count prove the delivery.",
          "FileSignature", "reference",
          [F("reference", "str", "Reference POD", "POD reference", required=True, search=True),
           F("mission", "str", "Mission", "Mission"),
           F("destinataire", "str", "Destinataire", "Consignee"),
           F("date_livraison", "datetime", "Date livraison", "Delivery date"),
           F("nb_colis_livres", "int", "Colis livres", "Parcels delivered"),
           F("incidents", "str", "Incidents", "Incidents"),
           F("signature_recu", "bool", "Signature recue", "Signature received"),
           F("statut", "str", "Statut", "Status")],
          [EN("statut", ["EN_ATTENTE", "SIGNE", "LITIGE", "REFUSE"])]),
    ],
)

# ─── magasin-stock (+2 -> 20) ────────────────────────────────────────────────
MODULES["magasin_b"] = dict(
    module_key="magasin_b", module_slug="magasin-stock",
    module_path="magasin-stock", perm_module="magasin",
    registre_filename="registres_b",
    revision="077", down_revision="076_transport_b_deep",
    entities=[
        E("stock-counts", "magasinb_stock_counts", "MagasinbStockCount", "magasinb-stock-counts",
          "stock_count", "Comptages d'inventaire", "Stock counts",
          "Confrontation quantite theorique / quantite physique par emplacement.",
          "Theoretical vs physical quantity check per location.",
          "L'ecart est la difference physique - theorique.",
          "Variance is physical minus theoretical.",
          "ClipboardList", "reference",
          [F("reference", "str", "Reference comptage", "Count reference", required=True, search=True),
           F("article", "str", "Article", "Item"),
           F("emplacement", "str", "Emplacement", "Location"),
           F("quantite_theorique", "int", "Quantite theorique", "Theoretical qty"),
           F("quantite_physique", "int", "Quantite physique", "Physical qty"),
           F("ecart", "int", "Ecart", "Variance"),
           F("date_inventaire", "date", "Date d'inventaire", "Count date"),
           F("agent", "str", "Agent", "Agent"),
           F("statut", "str", "Statut", "Status")],
          [EN("statut", ["PLANIFIE", "EN_COURS", "VALIDE", "ECART_CONSTATE"])]),

        E("goods-receipts", "magasinb_goods_receipts", "MagasinbGoodsReceipt", "magasinb-goods-receipts",
          "goods_receipt", "Receptions marchandise", "Goods receipts",
          "Enregistrement des entrees en magasin suite a commande fournisseur.",
          "Record of warehouse inbound following a purchase order.",
          "La reception peut etre partielle ; controle qualite separe.",
          "Receipt may be partial; QC is separate.",
          "PackageCheck", "reference",
          [F("reference", "str", "Reference reception", "Receipt reference", required=True, search=True),
           F("bon_commande", "str", "Bon de commande", "Purchase order"),
           F("fournisseur", "str", "Fournisseur", "Supplier"),
           F("date_reception", "datetime", "Date reception", "Receipt date"),
           F("nb_articles", "int", "Nombre d'articles", "Line count"),
           F("quantite_recue", "int", "Quantite recue", "Quantity received"),
           F("controles_fait", "bool", "Controles faits", "Checks done"),
           F("statut", "str", "Statut", "Status")],
          [EN("statut", ["EN_ATTENTE", "PARTIEL", "COMPLETE", "REFUSEE"])]),
    ],
)

# ─── dashboard (+5 -> 20) ────────────────────────────────────────────────────
MODULES["dashboard_b"] = dict(
    module_key="dashboard_b", module_slug="dashboard",
    module_path="dashboard", perm_module="dashboard",
    registre_filename="registres_b",
    revision="078", down_revision="077_magasin_b_deep",
    entities=[
        E("operational-kpis", "dashb_operational_kpis", "DashboardbOperationalKpi", "dashb-operational-kpis",
          "operational_kpi", "Indicateurs de performance operationnelle", "Operational KPIs",
          "Valeur mesuree d'un indicateur pour une periode donnee.",
          "Measured value of an indicator for a given period.",
          "La valeur est confrontee a l'objectif et au seuil d'alerte.",
          "Value is compared to target and alert threshold.",
          "Gauge", "reference",
          [F("reference", "str", "Reference indicateur", "KPI reference", required=True, search=True),
           F("libelle", "str", "Libelle", "Label"),
           F("module_source", "str", "Module source", "Source module"),
           F("valeur", "num", "Valeur", "Value"),
           F("unite", "str", "Unite", "Unit"),
           F("periode", "date", "Periode", "Period"),
           F("objectif", "num", "Objectif", "Target"),
           F("statut", "str", "Statut", "Status")],
          [EN("statut", ["NORMAL", "ATTENTION", "CRITIQUE"])]),

        E("executive-scorecards", "dashb_scorecards", "DashboardbScorecard", "dashb-executive-scorecards",
          "scorecard", "Tableaux de bord direction", "Executive scorecards",
          "Synthese periodique des indicateurs d'une direction.",
          "Periodic roll-up of a department's indicators.",
          "Le score global agrege les indicateurs follows.",
          "Global score aggregates the tracked indicators.",
          "Trophy", "reference",
          [F("reference", "str", "Reference tableau", "Scorecard reference", required=True, search=True),
           F("direction", "str", "Direction", "Department"),
           F("periode", "date", "Periode", "Period"),
           F("score_global", "num", "Score global", "Global score"),
           F("nb_indicateurs", "int", "Nombre d'indicateurs", "Indicator count"),
           F("tendance", "str", "Tendance", "Trend"),
           F("statut", "str", "Statut", "Status")],
          [EN("tendance", ["HAUSSE", "BAISSE", "STABLE"]),
           EN("statut", ["BROUILLON", "PUBLIE", "ARCHEVE"])]),

        E("alert-rules", "dashb_alert_rules", "DashboardbAlertRule", "dashb-alert-rules",
          "alert_rule", "Regles d'alerte", "Alert rules",
          "Condition declenchant une notification sur un indicateur.",
          "Condition triggering a notification on an indicator.",
          "Regle = indicateur + operateur + seuil + destinataires.",
          "Rule = indicator + operator + threshold + recipients.",
          "BellRing", "reference",
          [F("reference", "str", "Reference regle", "Rule reference", required=True, search=True),
           F("indicateur", "str", "Indicateur", "Indicator"),
           F("condition", "str", "Condition", "Condition"),
           F("seuil", "num", "Seuil", "Threshold"),
           F("destinataires", "str", "Destinataires", "Recipients"),
           F("canal", "str", "Canal", "Channel"),
           F("actif", "bool", "Active", "Active"),
           F("statut", "str", "Statut", "Status")],
          [EN("condition", ["SUPERIEUR", "INFERIEUR", "EGAL"]),
           EN("canal", ["EMAIL", "SMS", "PUSH", "NOTIFICATION"]),
           EN("statut", ["ACTIVE", "SUSPENDUE", "EN_TEST"])]),

        E("data-refresh-jobs", "dashb_refresh_jobs", "DashboardbRefreshJob", "dashb-data-refresh-jobs",
          "refresh_job", "Taches de rafraichissement", "Data refresh jobs",
          "Execution periodique du rafraichissement des donnees agrgees.",
          "Periodic execution of aggregated-data refresh.",
          "Duree et lignes traitees caracterisent la fraicheur.",
          "Duration and rows processed characterize freshness.",
          "RefreshCw", "reference",
          [F("reference", "str", "Reference tache", "Job reference", required=True, search=True),
           F("source", "str", "Source", "Source"),
           F("frequence", "str", "Frequence", "Frequency"),
           F("derniere_execution", "datetime", "Derniere execution", "Last run"),
           F("duree_sec", "int", "Duree (s)", "Duration (s)"),
           F("lignes_traitees", "int", "Lignes traitees", "Rows processed"),
           F("statut", "str", "Statut", "Status")],
          [EN("frequence", ["MANUEL", "HOURLY", "QUOTIDIEN", "HEBDOMADAIRE"]),
           EN("statut", ["EN_ATTENTE", "EN_COURS", "SUCCES", "ECHEC"])]),

        E("saved-views", "dashb_saved_views", "DashboardbSavedView", "dashb-saved-views",
          "saved_view", "Vues enregistrees", "Saved views",
          "Sauvegarde d'un parametrage de visualisation (filtres + type).",
          "Persistence of a visualization setup (filters + type).",
          "Une vue est privee sauf partage explicite.",
          "A view is private unless explicitly shared.",
          "Bookmark", "reference",
          [F("reference", "str", "Reference vue", "View reference", required=True, search=True),
           F("nom", "str", "Nom", "Name"),
           F("owner", "str", "Proprietaire", "Owner"),
           F("type_visuel", "str", "Type visuel", "Visual type"),
           F("filtres", "text", "Filtres", "Filters"),
           F("partage", "bool", "Partagee", "Shared"),
           F("statut", "str", "Statut", "Status")],
          [EN("type_visuel", ["TABLEAU", "GRAPIQUE", "CARTE", "LISTE"]),
           EN("statut", ["PRIVE", "PARTAGE"])]),
    ],
)
