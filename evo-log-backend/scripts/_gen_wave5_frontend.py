# -*- coding: utf-8 -*-
"""Genere les fichiers frontend wave5 : registres.ts + page.tsx + fragment nav.

Vague 5 = 4 modules expansion :
  pipeline-oleoduc        (10 entites)
  courier-express         (12 entites)
  chaine-froid            (10 entites)
  convoi-exceptionnel     (10 entites)

Idempotent : re-executable sans effet de bord (ecrase).
"""
import os
import re
import sys
import shutil

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
FE = os.path.join(ROOT, "evo-log-frontend")
BE = os.path.join(ROOT, "evo-log-backend")

# Ajouter backend au path pour importer les modeles
sys.path.insert(0, BE)

os.environ.setdefault("DATABASE_URL", "sqlite:///" + os.path.join(BE, "kamlog_erp.db").replace("\\", "/"))
os.environ.setdefault("ENV", "development")
os.environ.setdefault("SECRET_KEY", "smoke-test-key-please-rotate")

# Import des modeles
import app.models  # noqa: F401  (met en place la metadonnee complete)
from app.models.pipeline_deep import (
    PipelineSection, PipelinePumpStation, PipelineStorageTank,
    PipelineMeteringPoint, PipelineProductBatch, PipelinePressureReading,
    PipelineLeakDetection, PipelineMaintenanceWork,
    PipelineInjectionCampaign, PipelineShipNomination,
)
from app.models.courier_deep import (
    CourierParcel, CourierWaybill, CourierHub, CourierDeliveryZone,
    CourierRoute, CourierCourier, CourierPod, CourierSla, CourierLocker,
    CourierVehicule, CourierTarif, CourierException,
)
from app.models.coldchain_deep import (
    ColdChainChamber, ColdChainReefer, ColdChainLogger, ColdChainProduct,
    ColdChainExcursion, ColdChainVaccinBatch, ColdChainHaccpRecord,
    ColdChainDefrostCycle, ColdChainEnergyMeter, ColdChainTransportLeg,
)
from app.models.heavylift_deep import (
    HeavyLiftProject, HeavyLiftCrane, HeavyLiftModularTrailer,
    HeavyLiftRouteSurvey, HeavyLiftLiftPlan, HeavyLiftPermit,
    HeavyLiftEscort, HeavyLiftLashing, HeavyLiftBallast,
    HeavyLiftRiggingMethod,
)

# ----------------------------------------------------------------------------
# Spec par module
# ----------------------------------------------------------------------------
# entite = (ClassName, subpath, permSousModule, unique_field, export_name,
#           titre, titreEn, description, descriptionEn, icon)
MODULES = [
    {
        "dir_name": "pipeline-oleoduc",
        "api_prefix": "pipeline-oleoduc",
        "perm_module": "pipeline",
        "nav_key": "pipeline-oleoduc",
        "nav_title": "🛢️ K-Pipeline Oléoduc-Gazoduc",
        "nav_titleEn": "Pipeline & Hydrocarbons",
        "nav_area": "Pipeline Oléoduc-Gazoduc",
        "nav_phase": "Mode Pipeline: Sections, Stations, Stockage & Metering",
        "entities": [
            ("PipelineSection",           "sections",            "sections",            "code_section",  "registreSection",         "Troncons de pipeline",            "Pipeline sections",             "Sections physiques du reseau (troncon, diametre, produit transporte).", "Physical sections of the network.", "Waypoints"),
            ("PipelinePumpStation",       "pump-stations",       "pump_stations",       "code_station",  "registrePumpStation",     "Stations de pompage",              "Pump stations",                   "Stations de compression/pompage et postes de sectionnement.", "Compression/pumping stations.", "Zap"),
            ("PipelineStorageTank",       "storage-tanks",       "storage_tanks",       "code_cuve",     "registreStorageTank",     "Cuves de stockage",                "Storage tanks",                   "Bacs de stockage hydrocarbures (fixes et flottants).", "Hydrocarbon storage tanks.", "Database"),
            ("PipelineMeteringPoint",     "metering-points",     "metering_points",     "code_point",    "registreMeteringPoint",   "Points de mesure",                 "Metering points",                 "Systemes de comptage fiscal et commercial (turbinex, coriolis).", "Fiscal/commercial metering skids.", "Gauge"),
            ("PipelineProductBatch",      "product-batches",     "product_batches",     "numero_lot",    "registreProductBatch",    "Lot produit",                      "Product batch",                   "Batch de produit (essence, gasoil, jet, brut) injecte.", "Batch of injected product.", "Layers"),
            ("PipelinePressureReading",   "pressure-readings",   "pressure_readings",   "reference",     "registrePressureReading", "Releves de pression",              "Pressure readings",               "Telemétrie pression / debit par section.", "Pressure/flow telemetry per section.", "Activity"),
            ("PipelineLeakDetection",     "leak-detections",     "leak_detections",     "reference",     "registreLeakDetection",   "Detection fuites",                 "Leak detection",                  "Campaignes HG-PVT / aeralia / fibre optique.", "Negative pressure / fibre leak detection.", "Radar"),
            ("PipelineMaintenanceWork",   "maintenance-works",   "maintenance_works",   "reference",     "registreMaintWork",       "Travaux maintenance",              "Maintenance works",               "Pigging, soudures, protections cathodiques.", "Pigging / welding / CP works.", "Wrench"),
            ("PipelineInjectionCampaign", "injection-campaigns", "injection_campaigns", "reference",     "registreInjectCampaign",  "Campagnes d'injection",            "Injection campaigns",             "Campagnes d'admission produit dans le reseau.", "Product admission campaigns.", "Upload"),
            ("PipelineShipNomination",    "ship-nominations",    "ship_nominations",    "reference",     "registreShipNomination",  "Nominations navires (ship-or)"  ,    "Ship nominations",                "Nominations de navires pour chargement (ship-or).", "Vessel nominations (ship-or).", "Ship"),
        ],
    },
    {
        "dir_name": "courier-express",
        "api_prefix": "courier-express",
        "perm_module": "courier",
        "nav_key": "courier-express",
        "nav_title": "📦 K-Courier Messagerie Express",
        "nav_titleEn": "Courier & Parcel Express",
        "nav_area": "Courier Messagerie Express",
        "nav_phase": "Mode Express: Colis, Tournees, Hubs & SLA",
        "entities": [
            ("CourierParcel",    "parcels",        "parcels",        "numero_colis",   "registreParcel",     "Colis",                              "Parcels",                    "Unites de transport suivies du leve a la livraison.", "Units tracked from pickup to delivery.", "Package"),
            ("CourierWaybill",   "waybills",       "waybills",       "numero_lse",     "registreWaybill",    "Lettres de voiture express (LSE)",     "Express waybills",           "Titre de transport multi-colis par client.", "Multi-parcel transport title per client.", "FileText"),
            ("CourierHub",       "hubs",           "hubs",           "code_hub",       "registreHub",        "Hubs / centres de tri",              "Sorting hubs",               "Plates-formes de tri amont/aval.", "Upstream/downstream sort platforms.", "Building2"),
            ("CourierDeliveryZone", "delivery-zones", "delivery_zones", "code_zone",   "registreDeliveryZone","Zones de livraison",                 "Delivery zones",             "Decoupage geographique avec tarification.", "Geographic zoning with pricing.", "Map"),
            ("CourierRoute",     "routes",         "routes",         "code_tournee",   "registreRoute",      "Tournees de livraison",              "Delivery routes",            "Tourneeh tournee du vehicule sur une journee.", "Daily vehicle route plan.", "Route"),
            ("CourierCourier",   "couriers",       "couriers",       "code_coursier",  "registreCourier",    "Coursiers / livreurs",               "Couriers",                   "Personnel de collecte et livraison.", "Pickup & delivery personnel.", "User"),
            ("CourierPod",       "pods",           "pods",           "reference_pod",  "registrePod",        "Preuve de livraison (POD)",          "Proof of delivery",          "Scan signature + photo du destinataire.", "Signature scan + recipient photo.", "CheckCircle"),
            ("CourierSla",       "slas",           "slas",           "code_sla",       "registreSla",        "Accords de niveau service (SLA)",    "Service level agreements",   "Engagements délai + pénalités par client.", "Delay commitment + penalty per client.", "Timer"),
            ("CourierLocker",    "lockers",        "lockers",        "code_locker",    "registreLocker",     "Casiers automatiques",               "Smart lockers",              "Points de retrait libres-service.", "Self-service pickup points.", "Lock"),
            ("CourierVehicule",  "vehicules",      "vehicules",      "plaque",         "registreVehiculeEx", "Vehicules de livraison",             "Delivery vehicles",          "Moto / utilitaire / poids lourd.", "Motorcycle / van / truck.", "Truck"),
            ("CourierTarif",     "tarifs",         "tarifs",         "code_tarif",     "registreTarifEx",    "Tarification express",               "Express tariffs",            "Poids / volume / zone / urgence.", "Weight / volume / zone / urgency.", "Calculator"),
            ("CourierException", "exceptions",     "exceptions",     "reference",      "registreExceptionEx","Exceptions & litiges colis",         "Parcel exceptions",          "Colis perdu / endommage / retard.", "Lost / damaged / delayed parcel.", "AlertOctagon"),
        ],
    },
    {
        "dir_name": "chaine-froid",
        "api_prefix": "chaine-froid",
        "perm_module": "coldchain",
        "nav_key": "chaine-froid",
        "nav_title": "❄️ K-Chaine du Froid",
        "nav_titleEn": "Cold Chain & Reefer Logistics",
        "nav_area": "Chaine du Froid",
        "nav_phase": "Mode Froid: Chambres, Reefers, HACCP & Vaccins",
        "entities": [
            ("ColdChainChamber",       "chambers",        "chambers",         "code_chambre",    "registreChambre",     "Chambres froides",                    "Cold rooms",                  "Entrepots refroidis (positif/negatif).", "Positive/negative cold storage.", "Snowflake"),
            ("ColdChainReefer",        "reefers",         "reefers",          "numero_reefer",   "registreReefer",      "Conteneurs frigorifiques (reefer)",   "Reefer containers",             "Reefer 20/40/45' et gensets.", "20/40/45' reefer + genset.", "Container"),
            ("ColdChainLogger",        "loggers",         "loggers",          "numero_logger",   "registreLogger",      "Enregistreurs temperature",           "Temperature loggers",           "Data logger RFID / NFC / Bluetooth.", "RFID / NFC / Bluetooth loggers.", "Thermometer"),
            ("ColdChainProduct",       "products",        "products",         "code_sku",        "registreSku",         "Produits refrigeres (SKU)",           "Cold products (SKU)",           "Marchandises avec plage temperature.", "Goods with temperature range.", "Boxes"),
            ("ColdChainExcursion",     "excursions",      "excursions",       "reference",       "registreExcursion",   "Excursions temperature",              "Temperature excursions",        "Ecart hors tolerance documente.", "Out-of-tolerance event.", "AlertTriangle"),
            ("ColdChainVaccinBatch",   "vaccin-batches",  "vaccin_batches",   "numero_lot",      "registreVaccinBatch", "Lots de vaccins",                      "Vaccine batches",              "Suivi VPM + phase d'utilisation.", "EPI vaccine batch tracking.", "Syringe"),
            ("ColdChainHaccpRecord",   "haccp-records",   "haccp_records",    "reference",       "registreHaccp",       "Enregistrements HACCP",               "HACCP records",                 "Points critiques et surveillance.", "Critical control point monitoring.", "Shield"),
            ("ColdChainDefrostCycle",  "defrost-cycles",  "defrost_cycles",   "reference",       "registreDefrost",     "Cycles de dégivrage",                 "Defrost cycles",                "Givrage / désinfection périodique.", "Icing / periodic sanitation.", "RefreshCcw"),
            ("ColdChainEnergyMeter",   "energy-meters",   "energy_meters",    "code_compteur",   "registreEnergyMeter", "Compteurs energie",                   "Energy meters",                 "Conso kWh chambres + reefers.", "Cold room + reefer kWh usage.", "Zap"),
            ("ColdChainTransportLeg",  "transport-legs",  "transport_legs",   "reference",       "registreTransportLeg","Segment de transport frigorifique",   "Cold transport leg",            "Leg routier/fer/air avec temperature suivie.", "Truck/rail/air leg with T°.", "Truck"),
        ],
    },
    {
        "dir_name": "convoi-exceptionnel",
        "api_prefix": "convoi-exceptionnel",
        "perm_module": "heavylift",
        "nav_key": "convoi-exceptionnel",
        "nav_title": "🏗️ K-Convoi Exceptionnel (Heavy-lift)",
        "nav_titleEn": "Heavy Lift & Project Cargo",
        "nav_area": "Convoi Exceptionnel / Heavy-lift",
        "nav_phase": "Mode Heavy-Lift: Projets, Levage, Itineraire & Escorte",
        "entities": [
            ("HeavyLiftProject",         "projects",          "projects",          "code_projet",    "registreHLProject",   "Projets project-cargo",               "Project cargo",                 "Colis exceptionnels, tours, reacteurs, eoliennes.", "Turbines, towers, reactors.", "HardHat"),
            ("HeavyLiftCrane",           "cranes",            "cranes",            "numero_grue",    "registreHLCrane",     "Grues & engins de levage",            "Cranes & lifting gear",           "Mobility / crawler / tower.", "Mobile / crawler / tower.", "Construction"),
            ("HeavyLiftModularTrailer",  "modular-trailers",  "modular_trailers",  "plaque",         "registreHLTrailer",   "Remorques modulaires",                "Modular trailers",                "Plateaux SPMT / multi-essieux.", "SPMT / multi-axle flats.", "Truck"),
            ("HeavyLiftRouteSurvey",     "route-surveys",     "route_surveys",     "reference",      "registreHLSurvey",    "Etudes d'itineraire",                 "Route surveys",                  "Reconnaissance ponts/cables/obstacles.", "Bridge/cable/obstacle survey.", "Map"),
            ("HeavyLiftLiftPlan",        "lift-plans",        "lift_plans",        "reference",      "registreHLLiftPlan",  "Plans de levage",                     "Lift plans",                      "Decription methodique du lift.", "Methodical lift description.", "ClipboardList"),
            ("HeavyLiftPermit",          "permits",           "permits",           "numero_permis",  "registreHLPermit",    "Autorisations & permis",              "Permits & authorizations",      "Convoi hors gabarit / voirie / port.", "Overdimension / road / port.", "FileSignature"),
            ("HeavyLiftEscort",          "escorts",           "escorts",           "reference",      "registreHLEscort",    "Escortes & balisage",                 "Escorts & pilotage",              "Vehicules + agents + gendarmerie.", "Vehicle + agents + police.", "Shield"),
            ("HeavyLiftLashing",         "lashings",          "lashings",          "reference",      "registreHLLashing",   "Arrimage / lashing",                  "Lashing",                       "Chaine / sangle / effort.", "Chain / strap / tension.", "Link"),
            ("HeavyLiftBallast",         "ballasts",          "ballasts",          "code_ballast",   "registreHLBallast",   "Lest / ballast",                      "Ballast",                       "Masses additionnelles de stabilisation.", "Extra stabilization mass.", "Weight"),
            ("HeavyLiftRiggingMethod",   "rigging-methods",   "rigging_methods",   "code_methode",   "registreHLRigging",   "Methodes de rigging",                 "Rigging methods",                 "Elingage, palonnage, poutre de charge.", "Slings / spreaders / beams.", "Workflow"),
        ],
    },
]

SKIP_COLS = {"id", "company_id", "created_at", "updated_at", "is_active"}


def label_fr(col_name):
    """French-ish label from snake_case."""
    d = {
        "code": "Code", "reference": "Reference", "statut": "Statut",
        "numero": "Numero", "nom": "Nom", "type": "Type",
        "date_debut": "Date debut", "date_fin": "Date fin",
        "date_fin_prevue": "Fin prevue", "date_depot": "Date depot",
        "zone": "Zone", "description": "Description",
        "client": "Client", "fournisseur": "Fournisseur", "operateur": "Operateur",
        "capacite_tonnes": "Capacite (t)", "capacite_max_t": "Capacite max (t)",
        "poids_max_t": "Poids max (t)", "poids_kg": "Poids (kg)",
        "volume_m3": "Volume (m3)", "distance_km": "Distance (km)",
        "budget_xaf": "Budget (XAF)", "cout_xaf": "Cout (XAF)",
        "montant_ht": "Montant HT", "montant_ttc": "Montant TTC",
        "email": "Email", "telephone": "Telephone",
        "plaque": "Plaque", "immatriculation": "Immatriculation",
    }
    if col_name in d:
        return d[col_name]
    parts = col_name.split("_")
    if parts and parts[0] == "code":
        return "Code " + " ".join(p.title() for p in parts[1:])
    if parts and parts[0] == "numero":
        return "Numero " + " ".join(p.title() for p in parts[1:])
    return " ".join(p.capitalize() for p in parts)


def label_en(col_name):
    d = {
        "code_section": "Section code", "code_station": "Station code",
        "code_cuve": "Tank code", "code_point": "Point code",
        "numero_lot": "Batch number", "reference": "Reference",
        "numero_colis": "Parcel number", "numero_lse": "Waybill number",
        "code_hub": "Hub code", "code_zone": "Zone code",
        "code_tournee": "Route code", "code_coursier": "Courier code",
        "reference_pod": "POD reference", "code_sla": "SLA code",
        "code_locker": "Locker code", "plaque": "Plate",
        "code_tarif": "Tariff code",
        "code_chambre": "Room code", "numero_reefer": "Reefer number",
        "numero_logger": "Logger number", "code_sku": "SKU code",
        "haccp_ref": "HACCP ref", "code_compteur": "Meter code",
        "code_projet": "Project code", "numero_grue": "Crane number",
        "numero_permis": "Permit number", "code_ballast": "Ballast code",
        "code_methode": "Method code",
        "statut": "Status", "client": "Client",
    }
    if col_name in d:
        return d[col_name]
    return " ".join(p.capitalize() for p in col_name.split("_"))


def col_type(column):
    t = column.type
    name = type(t).__name__
    if name in ("Text",):
        return "area"
    if name in ("Date",):
        return "dt"
    if name in ("DateTime",):
        return "dtx"
    if name in ("Boolean",):
        return "chk"
    if name in ("Integer", "BigInteger", "Numeric", "Float", "DECIMAL"):
        return "num"
    return "txt"


def entity_columns(model_cls):
    """Retourne liste de (col_name, kind, requis)."""
    cols = []
    for c in model_cls.__table__.columns:
        if c.name in SKIP_COLS:
            continue
        kind = col_type(c)
        cols.append((c.name, kind))
    return cols


# ----------------------------------------------------------------------------
# Generation par module
# ----------------------------------------------------------------------------

def gen_registres(module):
    lines = []
    lines.append("/**")
    lines.append(f" * Configs Registre pour {module['dir_name']} (expansion wave 5 generee).")
    lines.append(" *")
    lines.append(" * Chaque ConfigRegistre est passe en prop au composant generique")
    lines.append(" * <RegistreGenerique /> pour rendre table, filtres, formulaire.")
    lines.append(" */")
    lines.append('"use client";')
    lines.append("")
    lines.append("import * as Icons from 'lucide-react';")
    lines.append("import type { ConfigRegistre, ColonneRegistre, ChampRegistre, FiltreRegistre } from '@/components/registre-generique/typesRegistre';")
    lines.append("import { registreAPI } from '@/lib/api-client';")
    lines.append("")
    lines.append(f'const api = registreAPI("{module["api_prefix"]}");')
    lines.append("")
    lines.append("function col(name: string, label: string, labelEn: string, opts: Partial<ColonneRegistre> = {}): ColonneRegistre {")
    lines.append("  return { name, label, labelEn, ...opts } as ColonneRegistre;")
    lines.append("}")
    lines.append("")
    lines.append("function txt(name: string, label: string, labelEn: string, opts: Partial<ChampRegistre> = {}): ChampRegistre {")
    lines.append('  return { name, label, labelEn, type: "texte", ...opts } as ChampRegistre;')
    lines.append("}")
    lines.append("")
    lines.append("function num(name: string, label: string, labelEn: string, opts: Partial<ChampRegistre> = {}): ChampRegistre {")
    lines.append('  return { name, label, labelEn, type: "nombre", ...opts } as ChampRegistre;')
    lines.append("}")
    lines.append("")
    lines.append("function dt(name: string, label: string, labelEn: string): ChampRegistre {")
    lines.append('  return { name, label, labelEn, type: "date" } as ChampRegistre;')
    lines.append("}")
    lines.append("")
    lines.append("function dtx(name: string, label: string, labelEn: string): ChampRegistre {")
    lines.append('  return { name, label, labelEn, type: "date" } as ChampRegistre;')
    lines.append("}")
    lines.append("")
    lines.append("function area(name: string, label: string, labelEn: string): ChampRegistre {")
    lines.append('  return { name, label, labelEn, type: "zone" } as ChampRegistre;')
    lines.append("}")
    lines.append("")
    lines.append("function chk(name: string, label: string, labelEn: string): ChampRegistre {")
    lines.append('  return { name, label, labelEn, type: "booleen" } as ChampRegistre;')
    lines.append("}")
    lines.append("")
    lines.append("function sel(name: string, label: string, labelEn: string, nomKey: string): ChampRegistre {")
    lines.append('  return { name, label, labelEn, type: "select", nomenclature: nomKey } as ChampRegistre;')
    lines.append("}")
    lines.append("")
    lines.append("function filtreSel(name: string, label: string, labelEn: string, nomKey: string): FiltreRegistre {")
    lines.append('  return { name, label, labelEn, type: "select", nomenclature: nomKey } as FiltreRegistre;')
    lines.append("}")
    lines.append("")

    for spec in module["entities"]:
        cls_name, subpath, perm_sub, ufield, exp_name, titre, titreEn, desc, descEn, icon = spec
        model_cls = globals()[cls_name]
        lines.append("")
        lines.append(f"export const {exp_name}: ConfigRegistre = {{")
        lines.append(f'  permModule: "{module["perm_module"]}",')
        lines.append(f'  permSousModule: "{perm_sub}",')
        lines.append(f'  tcode: "registre-{subpath}",')
        lines.append(f"  icon: Icons.{icon},")
        lines.append(f'  titre: "{titre}",')
        lines.append(f'  titreEn: "{titreEn}",')
        lines.append(f'  description: "{desc}",')
        lines.append(f'  descriptionEn: "{descEn}",')
        lines.append(f'  aide: "Registre genere (expansion wave 5).",')
        lines.append(f'  aideEn: "Generated register (wave 5 expansion).",')
        lines.append(f'  lister: (params) => api.lister("{subpath}", params),')
        lines.append(f'  creer: (data) => api.creer("{subpath}", data),')
        lines.append(f'  modifier: (id, data) => api.modifier("{subpath}", id, data),')
        lines.append(f'  unicite: "{ufield}",')
        lines.append(f"  fetchNomenclatures: () => api.getNomenclatures(),")
        lines.append("  colonnes: [")
        cols = entity_columns(model_cls)
        for cn, _kind in cols:
            lines.append(f'    col("{cn}", "{label_fr(cn)}", "{label_en(cn)}"),')
        lines.append("  ],")
        lines.append("  champs: [")
        for cn, kind in cols:
            if cn == ufield:
                lines.append(f'    {kind}("{cn}", "{label_fr(cn)}", "{label_en(cn)}", {{ requisCreation: true }}),')
            else:
                lines.append(f'    {kind}("{cn}", "{label_fr(cn)}", "{label_en(cn)}"),')
        lines.append("  ],")
        lines.append("};")
        lines.append("")

    return "\n".join(lines) + "\n"


def gen_page(module, spec):
    cls_name, subpath, _perm_sub, _ufield, exp_name, *_ = spec
    fn_component = "Page" + cls_name
    return (
        "'use client';\n"
        "import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';\n"
        f"import {{ {exp_name} }} from '@/components/{module['dir_name']}/registres';\n"
        "\n"
        f"export default function {fn_component}() {{\n"
        f"  return <RegistreGenerique config={{{exp_name}}} />;\n"
        "}\n"
    ).replace("config={{{}}}".format(exp_name), "config={" + exp_name + "}")


def gen_nav_module(module):
    """Retourne le fragment de NAVIGATION_REGISTRY pour ce module."""
    lines = []
    lines.append(f"  '{module['nav_key']}': {{")
    lines.append(f"    key: '{module['nav_key']}',")
    lines.append(f"    title: '{module['nav_title']}',")
    lines.append(f"    titleEn: '{module['nav_titleEn']}',")
    lines.append(f"    path: '/{module['dir_name']}/dashboard',")
    lines.append(f"    icon: (LUCIDE as any)[\"{module['entities'][0][9]}\"],")
    lines.append(f"    color: '#0EA5E9',")
    lines.append(f"    glow: 'shadow-sky-500/50 border-sky-500/60',")
    lines.append(f"    bgGradient: 'from-sky-600 to-cyan-600',")
    lines.append(f"    businessArea: '{module['nav_area']}',")
    lines.append(f"    processPhase: '{module['nav_phase']}',")
    lines.append(f"    requiredRoles: ['ADMIN', 'SUPER_ADMIN', 'MANAGER'],")
    lines.append(f"    subModules: [")
    lines.append(f"      {{")
    lines.append(f'        label: "Centre de pilotage {module["perm_module"]}",')
    lines.append(f'        path: "/{module["dir_name"]}/dashboard",')
    lines.append(f'        icon: (LUCIDE as any)["LayoutDashboard"],')
    lines.append(f'        badge: "Synthese",')
    lines.append(f'        tcode: "registre-{module["dir_name"]}-dash",')
    lines.append(f'        description: "Pilotage transversal du module {module["dir_name"]}",')
    lines.append(f'        businessProcess: "Pilotage du module",')
    lines.append(f'        requiredRoles: ["{module["perm_module"]}.{module["entities"][0][2]}.read"],')
    lines.append(f"      }},")
    for spec in module["entities"]:
        cls_name, subpath, perm_sub, ufield, exp_name, titre, titreEn, desc, descEn, icon = spec
        lines.append("      {")
        lines.append(f'        label: "{titre}",')
        lines.append(f'        path: "/{module["dir_name"]}/{subpath}",')
        lines.append(f'        icon: (LUCIDE as any)["{icon}"],')
        lines.append(f'        badge: "Expansion",')
        lines.append(f'        tcode: "registre-{subpath}",')
        lines.append(f'        description: "{desc}",')
        lines.append(f'        businessProcess: "Registre genere (expansion)",')
        lines.append(f'        requiredRoles: ["{module["perm_module"]}.{perm_sub}.read"],')
        lines.append("      },")
    lines.append("    ]")
    lines.append("  },")
    return "\n".join(lines) + "\n"


def main():
    # 1) registres.ts par module
    for module in MODULES:
        comp_dir = os.path.join(FE, "src", "components", module["dir_name"])
        os.makedirs(comp_dir, exist_ok=True)
        reg_path = os.path.join(comp_dir, "registres.ts")
        content = gen_registres(module)
        with open(reg_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(content)
        print(f"[OK] registres.ts  {reg_path}")

        # 2) page.tsx par entite + 1 dashboard
        app_dir = os.path.join(FE, "src", "app", "(app)", module["dir_name"])
        os.makedirs(app_dir, exist_ok=True)
        for spec in module["entities"]:
            cls_name, subpath, *_rest = spec
            page_dir = os.path.join(app_dir, subpath)
            os.makedirs(page_dir, exist_ok=True)
            page_path = os.path.join(page_dir, "page.tsx")
            with open(page_path, "w", encoding="utf-8", newline="\n") as f:
                f.write(gen_page(module, spec))
        print(f"[OK] {len(module['entities'])} pages  {app_dir}")

        # dashboard minimal
        dash_dir = os.path.join(app_dir, "dashboard")
        os.makedirs(dash_dir, exist_ok=True)
        with open(os.path.join(dash_dir, "page.tsx"), "w", encoding="utf-8", newline="\n") as f:
            f.write(render_dash(module))
        print(f"[OK] dashboard    {dash_dir}")

    # 3) fragment de navigation (ecrit dans un fichier a part pour inspection)
    nav_frag_path = os.path.join(ROOT, "scripts", "_wave5_nav_fragment.txt")
    with open(nav_frag_path, "w", encoding="utf-8", newline="\n") as f:
        for module in MODULES:
            f.write("  // WAVE 5 : " + module["nav_title"] + "\n")
            f.write(gen_nav_module(module))
            f.write("\n")
    print(f"[OK] nav fragment {nav_frag_path}")


DASH_TEMPLATE = """'use client';
// Dashboard module __TITLE__
import Link from 'next/link';

const MODULE_DIR = '__MODULE_DIR__';
const PERM = '__PERM__';

export default function PageDashboard() {
  return (
    <div className="p-6 space-y-4">
      <h1 className="text-2xl font-bold">__TITLE__</h1>
      <p className="text-sm text-gray-500">Centre de pilotage — selectionnez un registre ci-dessous.</p>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="rounded-xl border bg-white dark:bg-slate-900 p-4 shadow-sm">
          <div className="text-sm text-gray-500">Module</div>
          <div className="text-lg font-semibold">{PERM}</div>
        </div>
      </div>
    </div>
  );
}
"""


def render_dash(module):
    return (
        DASH_TEMPLATE
        .replace("__TITLE__", module["nav_title"])
        .replace("__MODULE_DIR__", module["dir_name"])
        .replace("__PERM__", module["perm_module"])
    )

if __name__ == "__main__":
    main()
