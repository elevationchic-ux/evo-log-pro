"""Patch navigationRegistry.ts: insert expansion subModules entries into existing modules.

Uses a Python brace/bracket counter to find the subModules: [ ... ] of each target
module and inserts new entries before the closing ].
"""
import re
import sys
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))

NAV_TS = ROOT / "evo-log-frontend" / "src" / "config" / "navigationRegistry.ts"


def load(path):
    spec = importlib.util.spec_from_file_location(path.stem, str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.MODULES


MODULES = {}
MODULES.update(load(HERE / "manifests" / "all_modules.py"))
MODULES.update(load(HERE / "manifests" / "wave3_modules.py"))
MODULES.update(load(HERE / "manifests" / "wave4_transports.py"))
MODULES.update(load(HERE / "manifests" / "wave4_logistique.py"))

# Also add port-ops + transit
PORT_OPS_SLUG = "port-operations"
TRANSIT_SLUG = "transit-douane"

EXTRA = {}
# port-ops and transit entries defined in port_operations_deep & transit_deep
# We'll read them from the existing generated registre.ts files
try:
    spec = importlib.util.spec_from_file_location("transit_manifest", HERE / "manifests" / "transit.py")
    tm = importlib.util.module_from_spec(spec); spec.loader.exec_module(tm)
    EXTRA[tm.MANIFEST["module_slug"]] = tm.MANIFEST
except Exception:
    pass

# port-operations (Wave 1A - hand-written)
PORT_OPS = {
    "module_key": "port_ops",
    "module_slug": "port-operations",
    "perm_module": "port_ops",
    "entities": [
        {"slug": "draft-surveys", "titre": "Constats tirant d'eau", "titreEn": "Draft surveys",
         "description": "Constats de tirant d'eau et avaries a l'escale.", "icon": "Ruler", "perm": "draft_survey"},
        {"slug": "stevedoring-crews", "titre": "Equipes de manutention", "titreEn": "Stevedoring gangs",
         "description": "Gangs et chefs d'equipe de manutention.", "icon": "Users", "perm": "stevedoring_crew"},
        {"slug": "cargo-handling-plans", "titre": "Plans dechargement/chargement", "titreEn": "Cargo plans",
         "description": "Plans operationnels de chargement et dechargement.", "icon": "Layers", "perm": "cargo_handling_plan"},
        {"slug": "quay-equipment", "titre": "Equipements de quai", "titreEn": "Quay equipment",
         "description": "Portiques, reach stackers, chariots.", "icon": "Wrench", "perm": "quay_equipment"},
        {"slug": "pilotage-sessions", "titre": "Pilotage", "titreEn": "Pilotage",
         "description": "Sessions de pilotage en rade et chenal.", "icon": "Compass", "perm": "pilotage_session"},
        {"slug": "towage-operations", "titre": "Remorquage", "titreEn": "Towage",
         "description": "Operations de remorquage par remorqueur.", "icon": "Anchor", "perm": "towage_operation"},
        {"slug": "bunkering", "titre": "Soute et ravitaillement", "titreEn": "Bunkering",
         "description": "Bons de soute carburant et eau.", "icon": "Fuel", "perm": "bunkering_order"},
        {"slug": "vessel-waste", "titre": "Dechets MARPOL", "titreEn": "Vessel waste",
         "description": "Reception des dechets navires MARPOL.", "icon": "Recycle", "perm": "vessel_waste"},
        {"slug": "tally-inspection", "titre": "Comptage contradictoire", "titreEn": "Tally",
         "description": "Feuilles de comptage et avaries.", "icon": "ClipboardList", "perm": "tally_sheet"},
        {"slug": "demurrage-storage", "titre": "Surestaries et magasinage", "titreEn": "Demurrage",
         "description": "Dossiers de surestaries et magasinage.", "icon": "Clock", "perm": "demurrage"},
        {"slug": "gate-passes", "titre": "Laissez-passer", "titreEn": "Gate passes",
         "description": "Laissez-pisser de sortie de marchandise.", "icon": "Ticket", "perm": "gate_pass"},
        {"slug": "container-yard", "titre": "Parc a conteneurs", "titreEn": "Container yard",
         "description": "Mouvements et empilement CY.", "icon": "Boxes", "perm": "yard_operation"},
    ],
}
EXTRA["port-operations"] = PORT_OPS


def find_module_block(text: str, module_key: str):
    """Return (start_index, end_index) of the object literal following '<module_key>: {'."""
    pat = re.compile(r"^\s*['\"]?" + re.escape(module_key) + r"['\"]?:\s*\{", re.M)
    m = pat.search(text)
    if not m:
        return None
    start = m.end() - 1  # position of '{'
    depth = 0
    i = start
    while i < len(text):
        c = text[i]
        if c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                return (start, i + 1)
        elif c == "'":
            # skip string
            i += 1
            while i < len(text) and text[i] != "'":
                if text[i] == '\\':
                    i += 1
                i += 1
        elif c == '"':
            i += 1
            while i < len(text) and text[i] != '"':
                if text[i] == '\\':
                    i += 1
                i += 1
        elif c == '`':
            i += 1
            while i < len(text) and text[i] != '`':
                if text[i] == '\\':
                    i += 1
                i += 1
        i += 1
    return None


def find_submodules_array(text: str, mod_start: int, mod_end: int):
    """Return (open_bracket_pos, close_bracket_pos) of the subModules: [...] inside module."""
    sub = text[mod_start:mod_end]
    m = re.search(r"subModules:\s*\[", sub)
    if not m:
        return None
    open_pos = mod_start + m.end() - 1  # position of '['
    depth = 0
    i = open_pos
    while i < mod_end:
        c = text[i]
        if c == '[':
            depth += 1
        elif c == ']':
            depth -= 1
            if depth == 0:
                return (open_pos, i)
        elif c in ("'", '"', '`'):
            q = c
            i += 1
            while i < mod_end and text[i] != q:
                if text[i] == '\\':
                    i += 1
                i += 1
        i += 1
    return None


def build_entry(module_slug: str, ent: dict, perm_module: str) -> str:
    """Emit one SubModuleItem literal. Uses dynamic LUCIDE[name] lookup."""
    label_fr = ent["titre"].replace('"', '\\"')
    label_en = ent["titreEn"].replace('"', '\\"')
    desc = ent["description"].replace('"', '\\"')
    return (
        "      {\n"
        f'        label: "{label_fr}",\n'
        f'        path: "/{module_slug}/{ent["slug"]}",\n'
        f'        icon: (LUCIDE as any)["{ent["icon"]}"],\n'
        f'        badge: "Expansion",\n'
        f'        tcode: "registre-{ent["slug"]}",\n'
        f'        description: "{desc}",\n'
        f'        businessProcess: "Registre genere (expansion)",\n'
        f'        requiredRoles: ["{perm_module}.{ent["perm"]}.read"],\n'
        "      },"
    )


def main():
    txt = NAV_TS.read_text(encoding="utf-8")

    # 1. Add LUCIDE namespace import at top (right after existing import).
    if "import * as LUCIDE from 'lucide-react'" not in txt:
        anchor = "} from 'lucide-react';"
        if anchor in txt:
            txt = txt.replace(anchor, anchor + "\nimport * as LUCIDE from 'lucide-react';", 1)

    # 2. For each module (15 total), find its subModules array and append new entries.
    all_modules = dict(MODULES)
    if EXTRA:
        all_modules.update({v["module_key"]: v for v in EXTRA.values()})

    added = []
    for key, m in all_modules.items():
        slug = m["module_slug"]
        perm_module = m["perm_module"]
        block = find_module_block(txt, slug)
        if not block:
            # Try with quotes variant
            print(f"WARN module block not found for {slug}")
            continue
        sub_arr = find_submodules_array(txt, block[0], block[1])
        if not sub_arr:
            print(f"WARN subModules array not found for {slug}")
            continue
        open_p, close_p = sub_arr
        # Ensure a trailing comma exists on last entry
        insert_at = close_p
        prefix = "\n" if txt[insert_at - 1] == "\n" else ""
        entries = "\n".join(build_entry(slug, e, perm_module) for e in m["entities"])
        txt = txt[:insert_at] + prefix + entries + "\n    " + txt[insert_at:]
        added.append(slug)

    # port-operations entries from port_operations_deep are already registered via port-deep manifest
    # but not present in MODULES. Handle separately below.
    NAV_TS.write_text(txt, encoding="utf-8")
    print(f"Added nav entries for: {added}")


if __name__ == "__main__":
    main()
