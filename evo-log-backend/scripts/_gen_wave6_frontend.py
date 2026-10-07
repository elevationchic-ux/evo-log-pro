# -*- coding: utf-8 -*-
"""Genere le frontend wave 6 : registres.ts + page.tsx + dashboards + fragment nav.

Vague 6 = 2 modules expansion :
  maintenance-industrielle  (25 entites)  perm module = maintindustrielle
  tracabilite               (19 entites)  perm module = tracabilite

Idempotent : re-executable sans effet de bord (ecrase). Meme patron que
_gen_wave5_frontend.py (composant generique <RegistreGenerique />).
"""
import os
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
FE = os.path.join(ROOT, "evo-log-frontend")
BE = os.path.join(ROOT, "evo-log-backend")

sys.path.insert(0, BE)
os.environ.setdefault("DATABASE_URL", "sqlite:///" + os.path.join(BE, "kamlog_erp.db").replace("\\", "/"))
os.environ.setdefault("ENV", "development")
os.environ.setdefault("SECRET_KEY", "smoke-test-key-please-rotate")

import app.models  # noqa: F401
from app.models import maintenance_deep as MNT
from app.models import tracabilite_deep as TRC

SKIP_COLS = {"id", "company_id", "created_at", "updated_at", "is_active"}

# entite = (ClassName, subpath, unique_field, export_name, titre, titreEn,
#           description, descriptionEn, icon)
MODULES = [
    {
        "dir_name": "maintenance-industrielle",
        "api_prefix": "maintenance-industrielle",
        "perm_module": "maintindustrielle",
        "nav_key": "maintenance-industrielle",
        "nav_title": "\U0001F527 K-Maintenance Industrielle",
        "nav_titleEn": "Industrial Maintenance (CMMS)",
        "nav_area": "Maintenance Industrielle",
        "nav_phase": "Mode CMMS: Actifs, GMAO, FMEA, RCM & Predictif",
        "module": MNT,
        "entities": [
            ("TechnicalAsset", "assets", "tag_actif", "registreAsset", "Actif technique", "Technical asset", "Equipement maintenable (grue, engin, navire, ligne).", "Maintainable equipment (crane, machine, vessel, line).", "Cog"),
            ("AssetComponent", "components", "code_composant", "registreComponent", "Composant d'actif", "Asset component", "Sous-ensemble technique d'un actif (moteur, verin, reducteur).", "Technical sub-assembly of an asset.", "Layers"),
            ("SparePartCatalog", "spare-parts", "reference_interne", "registreSparePart", "Piece de rechange", "Spare part", "Catalogue des pieces (criticite, fournisseur, seuil stock).", "Parts catalog (criticality, supplier, stock threshold).", "Package"),
            ("BillOfMaterial", "bill-of-material", "position_index", "registreBom", "Nomenclature BOM", "Bill of material", "Arborescence piece/quantite par actif ou composant.", "Part/quantity tree per asset or component.", "ListTree"),
            ("SerializedPart", "serialized-parts", "numero_serial", "registreSerializedPart", "Piece serialisee (singleton)", "Serialized part", "Unite unique tracee par numero de serial (cycle de vie, affectation).", "Unique unit tracked by serial (lifecycle, assignment).", "Tag"),
            ("PartInventory", "inventory", "part_id", "registreInventory", "Stock piece", "Part inventory", "Quantite disponible par piece/magasin/emplacement.", "On-hand qty per part/location.", "Boxes"),
            ("PartMovement", "movements", "reference_mouvement", "registreMovement", "Mouvement de piece", "Part movement", "Entree/sortie/transfert/ajustement de stock.", "In/out/transfer/adjust of stock.", "ArrowLeftRight"),
            ("FailureMode", "failure-modes", "code_fmea", "registreFailureMode", "Mode de defaillance (FMEA)", "Failure mode (FMEA)", "Analyse gravite x occurrence x detection (IPR).", "Severity x occurrence x detection (RPN).", "AlertTriangle"),
            ("MaintenancePlan", "plans", "code_plan", "registrePlan", "Plan de maintenance", "Maintenance plan", "Plan preventif (periodique, heures, km, condition).", "Preventive plan (calendar, hours, km, condition).", "Calendar"),
            ("MaintenanceTask", "tasks", "code_tache", "registreTask", "Tache de maintenance", "Maintenance task", "Pas operatoire d'un plan (gammes, duree, competences).", "Operational step of a plan (range, duration, skills).", "ListChecks"),
            ("WorkOrder", "work-orders", "numero_ot", "registreWorkOrder", "Ordre de travail", "Work order", "OT preventif/correctif/amelioratif avec couts et ressources.", "Preventive/corrective/improvement WO with costs & resources.", "ClipboardList"),
            ("AssetFailure", "asset-failures", "reference_defaillance", "registreAssetFailure", "Panne actif", "Asset failure", "Declaration de panne/dysfonctionnement sur un actif.", "Breakdown reported on an asset.", "AlertOctagon"),
            ("WorkOrderPart", "wo-parts", "work_order_id", "registreWoPart", "OT - pieces", "WO parts", "Consommables affectes a un ordre de travail.", "Consumables issued to a work order.", "Package"),
            ("WorkOrderLabour", "wo-labours", "work_order_id", "registreWoLabour", "OT - main d'oeuvre", "WO labour", "Temps technicien impute a un OT.", "Technician time charged to a WO.", "Users"),
            ("WorkOrderTool", "wo-tools", "work_order_id", "registreWoTool", "OT - outillage", "WO tools", "Outillage mobilise pour un OT.", "Tooling mobilized for a WO.", "Wrench"),
            ("RootCauseAnalysis", "root-causes", "reference_rca", "registreRca", "Analyse cause racine", "Root cause analysis", "5 Pourquoi / Ishikawa / arbre des causes.", "5 Why / Ishikawa / cause tree.", "Search"),
            ("OverhaulCampaign", "overhauls", "code_overhaul", "registreOverhaul", "Campagne revision", "Overhaul campaign", "Revision majeure / reconditionnement moteur.", "Major overhaul / engine recondition.", "Settings"),
            ("LubricationSchedule", "lubrication", "point_lubrifiant", "registreLubrication", "Plaine graissage", "Lubrication schedule", "Points, lubrifiants, frequences et quantites.", "Points, lubricants, frequencies and quantities.", "Droplet"),
            ("ConditionReading", "condition-readings", "reference_lecture", "registreConditionReading", "Releve condition", "Condition reading", "Vibration / thermo / huile / ultrason.", "Vibration / thermal / oil / ultrasound.", "Activity"),
            ("Sensor", "sensors", "code_capteur", "registreSensor", "Capteur IoT", "IoT sensor", "Capteur connecte (type, pas, calibration).", "Connected sensor (type, step, calibration).", "Radio"),
            ("PredictiveModel", "predictive-models", "code_modele", "registrePredictiveModel", "Modele predictif", "Predictive model", "Algorithme PdM (seuil, horizon, confiance).", "PdM algorithm (threshold, horizon, confidence).", "Brain"),
            ("ReliabilityKpi", "reliability-kpis", "periode", "registreReliabilityKpi", "KPI fiabilite", "Reliability KPI", "MTBF / MTTR / MTTF / disponibilite / TRS.", "MTBF / MTTR / MTTF / availability / OEE.", "Gauge"),
            ("RegulatoryInspection", "inspections", "numero_pv", "registreInspection", "Inspection reglementaire", "Regulatory inspection", "Controle obligatoire (BV, APAVE, reglementaire).", "Statutory inspection (BV, APAVE).", "FileCheck"),
            ("MaintenanceBudget", "budgets", "exercice", "registreBudget", "Budget maintenance", "Maintenance budget", "Budget prevu vs realise par actif/exercice.", "Planned vs actual budget per asset/year.", "Wallet"),
            ("MaintenanceVendor", "vendors", "code_prestataire", "registreVendor", "Prestataire maintenance", "Maintenance vendor", "Sous-traitant / specialise (contrat, habilitation).", "Subcontractor (contract, accreditation).", "Building"),
        ],
    },
    {
        "dir_name": "tracabilite",
        "api_prefix": "tracabilite",
        "perm_module": "tracabilite",
        "nav_key": "tracabilite",
        "nav_title": "\U0001F517 K-Traçabilité Bout-en-Bout",
        "nav_titleEn": "End-to-End Traceability",
        "nav_area": "Tracabilite & Confiance Numerique",
        "nav_phase": "Mode Tracabilite: Chaines custody, Merkle, eIDAS & RGPD",
        "module": TRC,
        "entities": [
            ("TraceabilityEvent", "events", "event_uid", "registreTraceEvent", "Evenement tracabilite", "Traceability event", "Evenement immuable signe (hash chain).", "Immutable signed event (hash chain).", "Activity"),
            ("ChainOfCustodyTransfer", "custody-transfers", "reference_transfert", "registreCustody", "Chaine de custody", "Chain of custody", "Transfert de responsabilite entre parties.", "Responsibility handoff between parties.", "ArrowLeftRight"),
            ("BatchGenealogy", "batch-genealogy", "child_lot", "registreBatchGenealogy", "Genealogie lot", "Batch genealogy", "Filiation parent/enfant (melange, conditionnement).", "Parent/child lineage (blend, packing).", "Layers"),
            ("SerialGenealogy", "serial-genealogy", "child_serial", "registreSerialGenealogy", "Genealogie serial", "Serial genealogy", "Filiation par numero de serial unitaire.", "Lineage by unique serial.", "Hash"),
            ("DocumentHash", "document-hashes", "document_ref", "registreDocHash", "Empreinte document", "Document hash", "Hash d'integrite versionne d'un document.", "Versioned integrity hash of a document.", "FileDigit"),
            ("GeolocationTrace", "geolocations", "subject_type", "registreGeolocation", "Trace geolocalisation", "Geolocation trace", "Position GPS horodatee d'un sujet.", "Timestamped GPS position.", "MapPin"),
            ("ColdChainTrace", "cold-chain", "subject_ref", "registreColdChain", "Chaine du froid", "Cold chain trace", "Releves temperature le long du parcours.", "Temperature readings along the journey.", "Snowflake"),
            ("IncidentChainOfCommand", "incidents", "reference_incident", "registreIncident", "Post commandement incident", "Incident chain of command", "Chaine de decision / gestion de crise.", "Decision chain / crisis management.", "Siren"),
            ("RegulatoryTraceExport", "regulatory-exports", "numero_expedition", "registreRegExport", "Export reglementaire", "Regulatory export", "Dossier transmis a une autorite (douane, SAT).", "File sent to an authority (customs).", "FileOutput"),
            ("ImmutableAuditLog", "audit-logs", "action", "registreAuditLog", "Journal audit inalterable", "Immutable audit log", "Log append-only a chaine de hash.", "Append-only hash-chained log.", "ScrollText"),
            ("TimestampAuthority", "timestamps", "token_tsa", "registreTimestamp", "Horodatage qualifie", "Qualified timestamp", "Preuve d'antecidence (eIDAS / CAMPOST).", "Proof of precedence (eIDAS / CAMPOST).", "Clock"),
            ("WitnessSignature", "signatures", "reference_signature", "registreSignature", "Signature / temoin", "Witness signature", "Signature electronique / emargement temoin.", "E-signature / witness countersign.", "PenLine"),
            ("IntegrityMerkleProof", "merkle-proofs", "periode", "registreMerkleProof", "Preuve Merkle", "Merkle proof", "Racine Merkle periodique d'un lot d'evenements.", "Periodic Merkle root over events.", "ShieldCheck"),
            ("ContainerSeal", "seals", "numero_sceau", "registreSeal", "Sceau conteneur ISO 17712", "Container seal", "Sceau haute securite conforme ISO 17712.", "High-security seal (ISO 17712).", "BadgeCheck"),
            ("CargoHandoff", "cargo-handoffs", "reference_handoff", "registreCargoHandoff", "Transfert cargo multimodal", "Cargo handoff", "Changement de mode (mer/rail/route/air).", "Mode change (sea/rail/road/air).", "ArrowRightLeft"),
            ("AccessSecurityLog", "access-logs", "type_evenement", "registreAccessLog", "Journal securite acces", "Access security log", "Trace des acces/tentatives authentification.", "Access/auth attempt trail.", "Lock"),
            ("ConsentGrant", "consents", "reference_consentement", "registreConsent", "Consentement RGPD", "Consent grant", "Consentement loi 2010/041 / RGPD par finalite.", "Consent per purpose (RGPD / Cameroon 2010/041).", "UserCheck"),
            ("AntiTamperingEvent", "anti-tampering", "reference_alerte", "registreAntiTampering", "Evenement anti-falsification", "Anti-tampering event", "Detection d'alteration (hash mismatch).", "Alteration detection (hash mismatch).", "AlertOctagon"),
            ("RetentionPolicy", "retention-policies", "code_politique", "registreRetentionPolicy", "Politique conservation", "Retention policy", "Duree et regle de retention par type d'objet.", "Retention duration/rule per object type.", "Archive"),
        ],
    },
]


def label_fr(col_name):
    d = {
        "code": "Code", "statut": "Statut", "nom": "Nom", "type": "Type",
        "description": "Description", "email": "Email", "telephone": "Telephone",
    }
    if col_name in d:
        return d[col_name]
    parts = col_name.split("_")
    if parts and parts[0] in ("code", "numero", "reference"):
        return parts[0].capitalize() + " ".join(" " + p.title() for p in parts[1:]) if len(parts) > 1 else parts[0].capitalize()
    return " ".join(p.capitalize() for p in parts)


def label_en(col_name):
    return " ".join(p.capitalize() for p in col_name.split("_"))


def col_type(column):
    name = type(column.type).__name__
    if name == "Text":
        return "area"
    if name == "Date":
        return "dt"
    if name == "DateTime":
        return "dtx"
    if name == "Boolean":
        return "chk"
    if name in ("Integer", "BigInteger", "Numeric", "Float", "DECIMAL"):
        return "num"
    return "txt"


def entity_columns(model_cls):
    cols = []
    for c in model_cls.__table__.columns:
        if c.name in SKIP_COLS:
            continue
        cols.append((c.name, col_type(c)))
    return cols


def gen_registres(module):
    lines = []
    lines.append("/**")
    lines.append(f" * Configs Registre pour {module['dir_name']} (expansion wave 6 generee).")
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
    lines.append("function filtreSel(name: string, label: string, labelEn: string, nomKey: string): FiltreRegistre {")
    lines.append('  return { name, label, labelEn, type: "select", nomenclature: nomKey } as FiltreRegistre;')
    lines.append("}")
    lines.append("")

    mod = module["module"]
    for spec in module["entities"]:
        cls_name, subpath, ufield, exp_name, titre, titreEn, desc, descEn, icon = spec
        perm_sub = subpath.replace("-", "_")
        model_cls = getattr(mod, cls_name)
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
        lines.append(f'  aide: "Registre genere (expansion wave 6).",')
        lines.append(f'  aideEn: "Generated register (wave 6 expansion).",')
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
    cls_name, subpath, _uf, exp_name, *_ = spec
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
    lines = []
    lines.append(f"  '{module['nav_key']}': {{")
    lines.append(f"    key: '{module['nav_key']}',")
    lines.append(f"    title: '{module['nav_title']}',")
    lines.append(f"    titleEn: '{module['nav_titleEn']}',")
    lines.append(f"    path: '/{module['dir_name']}/dashboard',")
    lines.append(f"    icon: (LUCIDE as any)[\"{module['entities'][0][8]}\"],")
    lines.append(f"    color: '#8B5CF6',")
    lines.append(f"    glow: 'shadow-violet-500/50 border-violet-500/60',")
    lines.append(f"    bgGradient: 'from-violet-600 to-fuchsia-600',")
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
    lines.append(f'        requiredRoles: ["{module["perm_module"]}.{module["entities"][0][1].replace("-", "_")}.read"],')
    lines.append(f"      }},")
    for spec in module["entities"]:
        cls_name, subpath, _uf, _exp, titre, titreEn, desc, descEn, icon = spec
        perm_sub = subpath.replace("-", "_")
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


def main():
    for module in MODULES:
        comp_dir = os.path.join(FE, "src", "components", module["dir_name"])
        os.makedirs(comp_dir, exist_ok=True)
        reg_path = os.path.join(comp_dir, "registres.ts")
        with open(reg_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(gen_registres(module))
        print(f"[OK] registres.ts  {reg_path}")

        app_dir = os.path.join(FE, "src", "app", "(app)", module["dir_name"])
        os.makedirs(app_dir, exist_ok=True)
        for spec in module["entities"]:
            subpath = spec[1]
            page_dir = os.path.join(app_dir, subpath)
            os.makedirs(page_dir, exist_ok=True)
            with open(os.path.join(page_dir, "page.tsx"), "w", encoding="utf-8", newline="\n") as f:
                f.write(gen_page(module, spec))
        print(f"[OK] {len(module['entities'])} pages  {app_dir}")

        dash_dir = os.path.join(app_dir, "dashboard")
        os.makedirs(dash_dir, exist_ok=True)
        with open(os.path.join(dash_dir, "page.tsx"), "w", encoding="utf-8", newline="\n") as f:
            f.write(render_dash(module))
        print(f"[OK] dashboard    {dash_dir}")

    nav_frag = os.path.join(ROOT, "scripts", "_wave6_nav_fragment.txt")
    with open(nav_frag, "w", encoding="utf-8", newline="\n") as f:
        f.write("// <WAVE6-EXPANSION-BEGIN>\n")
        for module in MODULES:
            f.write("  // WAVE 6 : " + module["nav_title"] + "\n")
            f.write(gen_nav_module(module))
            f.write("\n")
        f.write("// <WAVE6-EXPANSION-END>\n")
    print(f"[OK] nav fragment {nav_frag}")


if __name__ == "__main__":
    main()
