"""Wave 4 completion : blocks NAVIGATION_REGISTRY + palette + i18n + pages dashboard.

Contrairement a patch_nav.py (qui ne fait qu'ajouter des sous-entrees dans des
blocs existants), ce script CREER les blocs de module complets des 4 modules
ferroviaire / aerien / fluvial / 3PL, puis genere leur page dashboard (grille
de registres branchee sur donnees reelles uniquement : aucun KPI invente).
"""
import importlib.util
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
FE = ROOT / "evo-log-frontend"
NAV_TS = FE / "src" / "config" / "navigationRegistry.ts"
PAL_TS = FE / "src" / "config" / "modulePalette.ts"
I18N_TS = FE / "src" / "config" / "navI18n.ts"
APP_DIR = FE / "src" / "app" / "(app)"


def load(path):
    spec = importlib.util.spec_from_file_location(path.stem, str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.MODULES


MODULES = {}
MODULES.update(load(HERE / "manifests" / "wave4_transports.py"))
MODULES.update(load(HERE / "manifests" / "wave4_logistique.py"))

META = {
    "ferroviaire": dict(
        title="🚆 K-Transport Ferroviaire", title_en="Rail Freight & Infrastructure",
        icon="TrainFront", hex="#6366F1",
        glow="shadow-indigo-500/50 border-indigo-500/60",
        grad="from-indigo-600 to-violet-600",
        area="Transport Ferroviaire",
        phase="Mode Rail: Parc, Sillons, Fret & Corridors",
        dash_label="Centre de pilotage ferroviaire",
        dash_desc="Parc wagons/locomotives, sillons, lettres de voiture CIM et corridors fer-port",
        accent="indigo",
    ),
    "aerien": dict(
        title="✈️ K-Transport Aérien", title_en="Air Cargo & Airport Ops",
        icon="Plane", hex="#C026D3",
        glow="shadow-fuchsia-500/50 border-fuchsia-500/60",
        grad="from-fuchsia-600 to-purple-600",
        area="Transport Aérien",
        phase="Mode Air: Fret, AWB, Slots & Surete",
        dash_label="Centre de pilotage aerien",
        dash_desc="Flotte, AWB maitres/secondaires, slots IATA, ULD et surete du fret",
        accent="fuchsia",
    ),
    "fluvial": dict(
        title="⛴️ K-Transport Fluvial", title_en="River & Lake Transport",
        icon="Anchor", hex="#14B8A6",
        glow="shadow-teal-500/50 border-teal-500/60",
        grad="from-teal-600 to-cyan-600",
        area="Transport Fluvial & Lacustre",
        phase="Mode Eau interieure: Peniches, Ecluses & Terminaux",
        dash_label="Centre de pilotage fluvial",
        dash_desc="Flotte fluviale, transits d'ecluses, sondes, terminaux et lettres de voiture CMNI",
        accent="teal",
    ),
    "log3pl": dict(
        title="📦 K-Logistique 3PL", title_en="Contract Logistics 3PL",
        icon="Warehouse", hex="#EA580C",
        glow="shadow-orange-500/50 border-orange-500/60",
        grad="from-orange-600 to-amber-600",
        area="Logistique sous contrat",
        phase="3PL: Contrats, Entrepots, Pick&Pack & SLA",
        dash_label="Tour de controle 3PL",
        dash_desc="Contrats clients, entrepot sous contrat, pick&pack, cross-dock, KPI SLA et facturation 3PL",
        accent="orange",
    ),
}


def esc(s):
    return s.replace('"', '\\"')


def sub_entry(slug, ent, perm_module, first=False):
    label_fr = esc(ent["titre"])
    desc = esc(ent["description"])
    return (
        "      {\n"
        f'        label: "{label_fr}",\n'
        f'        path: "/{slug}/{ent["slug"]}",\n'
        f'        icon: (LUCIDE as any)["{ent["icon"]}"],\n'
        f'        badge: "Expansion",\n'
        f'        tcode: "registre-{ent["slug"]}",\n'
        f'        description: "{desc}",\n'
        f'        businessProcess: "Registre genere (expansion)",\n'
        f'        requiredRoles: ["{perm_module}.{ent["perm"]}.read"],\n'
        "      },"
    )


def module_block(key, m):
    meta = META[key]
    slug = m["module_slug"]
    perm = m["perm_module"]
    dash = (
        "      {\n"
        f'        label: "{esc(meta["dash_label"])}",\n'
        f'        path: "/{slug}/dashboard",\n'
        '        icon: (LUCIDE as any)["LayoutDashboard"],\n'
        '        badge: "Synthese",\n'
        f'        tcode: "registre-{slug}-dashboard",\n'
        f'        description: "{esc(meta["dash_desc"])}",\n'
        '        businessProcess: "Pilotage du module",\n'
        f'        requiredRoles: ["{perm}.{m["entities"][0]["perm"]}.read"],\n'
        "      },"
    )
    subs = "\n".join([dash] + [sub_entry(slug, e, perm) for e in m["entities"]])
    return (
        f"  '{slug}': {{\n"
        f"    key: '{slug}',\n"
        f"    title: '{meta['title']}',\n"
        f"    titleEn: '{meta['title_en']}',\n"
        f"    path: '/{slug}/dashboard',\n"
        f"    icon: (LUCIDE as any)[\"{meta['icon']}\"],\n"
        f"    color: '{meta['hex']}',\n"
        f"    glow: '{meta['glow']}',\n"
        f"    bgGradient: '{meta['grad']}',\n"
        f"    businessArea: '{meta['area']}',\n"
        f"    processPhase: '{meta['phase']}',\n"
        "    requiredRoles: ['ADMIN', 'SUPER_ADMIN', 'MANAGER'],\n"
        "    subModules: [\n"
        f"{subs}\n"
        "    ]\n"
        "  },"
    )


DASH_TEMPLATE = """'use client';

/**
 * Centre de pilotage {TITRE} (module genere, expansion vague 4).
 * Grille de registres reellement servics par /api/v1/{SLUG} :
 * aucun chiffre invente, aucune donnee factice. Chaque carte ouvre le
 * registre correspondant ; la lecture reste soumise aux habilitations.
 */
import Link from 'next/link';
import * as Icons from 'lucide-react';

import ModuleLayout from '@/components/layout/ModuleLayout';
import { useCan } from '@/hooks/useCan';
import { useSettings } from '@/components/layout/SettingsProvider';

const ENTITES = [
{ENTITES}
] as const;

export default function {FN}() {{
  const can = useCan();
  const {{ language }} = useSettings();
  const lang: 'fr' | 'en' = language === 'en' ? 'en' : 'fr';
  const t = (fr: string, en: string) => (lang === 'en' ? en : fr);

  return (
    <ModuleLayout
      title={{t('{DASH_LABEL}', '{DASH_LABEL_EN}')}}
      description={{t('{DASH_DESC}', '{DASH_DESC_EN}')}}
      help={{t(
        'Chaque carte ouvre un registre reellement servi par le serveur. Les compteurs ne sont affiches que lorsque la donnee existe.',
        'Each card opens a register actually served by the server. Counters are only shown when the data exists.',
      )}}
    >
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
        {{ENTITES.map((e) => {{
          const Icon = (Icons as any)[e.icon] ?? Icons.Folder;
          const autorise = can('{PERM}.' + e.perm + '.read');
          return (
            <Link
              key={{e.slug}}
              href={{'/{SLUG}/' + e.slug}}
              className={{`group rounded-2xl border p-4 transition ${{autorise
                  ? 'border-slate-800 bg-slate-900/60 hover:border-{ACCENT}-700/70 hover:bg-slate-900'
                  : 'border-slate-800/60 bg-slate-950/40'
                }}`}}
            >
              <div className="flex items-start justify-between gap-2">
                <div className={{`p-2 rounded-xl ${{autorise ? 'bg-{ACCENT}-700 text-{ACCENT}-50' : 'bg-slate-800 text-slate-400' }}`}}>
                  <Icon className="w-4 h-4" />
                </div>
                <span className="font-mono text-[10px] text-slate-500 border border-slate-800 rounded px-1.5 py-0.5">
                  {{e.tcode}}
                </span>
              </div>
              <h3 className="mt-2 text-sm font-semibold text-slate-100 group-hover:text-{ACCENT}-200">
                {{lang === 'en' ? e.titreEn : e.titre}}
              </h3>
              <p className="mt-1 text-[11px] leading-relaxed text-slate-400 line-clamp-2">
                {{lang === 'en' ? e.descriptionEn : e.description}}
              </p>
              {{!autorise && (
                <p className="mt-2 text-[10px] font-semibold text-amber-300/90">
                  {{t('Lecture soumise a ' + '{PERM}.' + e.perm + '.read', 'Reading requires {PERM}.' + e.perm + '.read')}}
                </p>
              )}}
            </Link>
          );
        }})}}
      </div>
    </ModuleLayout>
  );
}}
"""


def dash_page(key, m):
    meta = META[key]
    slug = m["module_slug"]
    perm = m["perm_module"]
    lines = []
    for e in m["entities"]:
        lines.append(
            "  { slug: '%s', tcode: 'registre-%s', titre: '%s', titreEn: '%s', description: '%s', descriptionEn: '%s', icon: '%s', perm: '%s' },"
            % (
                e["slug"], e["slug"],
                e["titre"].replace("'", "\\'"),
                e["titreEn"].replace("'", "\\'"),
                e["description"].replace("'", "\\'"),
                e["descriptionEn"].replace("'", "\\'"),
                e["icon"], e["perm"],
            )
        )
    fn = "PageDashboard" + "".join(p.capitalize() for p in re.split(r"[-_]", slug))
    return DASH_TEMPLATE.format(
        TITRE=meta["title"], SLUG=slug, PERM=perm, ACCENT=meta["accent"],
        ENTITES="\n".join(lines), FN=fn,
        DASH_LABEL=meta["dash_label"], DASH_LABEL_EN=meta["dash_label"],
        DASH_DESC=meta["dash_desc"], DASH_DESC_EN=meta["dash_desc"],
    )


def main():
    # 1. NAVIGATION_REGISTRY : creer les 4 blocs avant la fermeture '};'
    txt = NAV_TS.read_text(encoding="utf-8")
    created = []
    for key, m in MODULES.items():
        slug = m["module_slug"]
        if re.search(r"^\s*['\"]?" + re.escape(slug) + r"['\"]?:\s*\{", txt, re.M):
            print("nav block already present:", slug)
            continue
        anchor = txt.index("\n};", txt.index("export const NAVIGATION_REGISTRY"))
        prev = txt.rindex("}", 0, anchor)
        block = module_block(key, m)
        txt = txt[:prev + 1] + "," + "\n\n  // WAVE 4 : multimodal fer / air / fluvial + 3PL\n" + block + "\n" + txt[prev + 1:]
        created.append(slug)
    NAV_TS.write_text(txt, encoding="utf-8")
    print("nav blocks created:", created)

    # 2. Palette : inserer avant la derniere fermeture '};' de MODULE_PALETTE
    pal = PAL_TS.read_text(encoding="utf-8")
    anchor = pal.index("\n};", pal.index("MODULE_PALETTE"))
    prev = pal.rindex("}", 0, anchor)
    entries = []
    for key, m in MODULES.items():
        meta = META[key]
        a = meta["accent"]
        entries.append(
            "  '%s': {\n    hex: '%s',\n    glow: '%s',\n    bgGradient: '%s',\n"
            "    sidebar: { activeAccent: 'text-%s-400 border-%s-400', activeBgSubtle: 'bg-%s-500/10', brandIconBg: 'bg-%s-600' },\n  },"
            % (m["module_slug"], meta["hex"], meta["glow"], meta["grad"], a, a, a, a)
        )
    pal = pal[:prev + 1] + ",\n\n  // ── Modules Wave 4 (fer, aerien, fluvial, 3PL) ──\n" + "\n".join(entries) + "\n" + pal[prev + 1:]
    # le '}' remplace avait une virgule superflue si c'etait le dernier ; normaliser
    pal = pal.replace("},\n\n  // ── Modules Wave 4", "}\n\n  // ── Modules Wave 4", 0)
    PAL_TS.write_text(pal, encoding="utf-8")
    print("palette entries added:", len(entries))

    # 3. navI18n : titres EN
    i18n = I18N_TS.read_text(encoding="utf-8")
    anchor = i18n.index("\n};", i18n.index("MODULE_TITLES_EN"))
    prev = i18n.rindex("}", 0, anchor)
    lines = []
    for key, m in MODULES.items():
        lines.append("  '%s': '%s'," % (m["module_slug"], META[key]["title_en"]))
    i18n = i18n[:prev + 1] + ",\n" + "\n".join(lines) + "\n" + i18n[prev + 1:]
    I18N_TS.write_text(i18n, encoding="utf-8")
    print("i18n entries added:", len(lines))

    # 4. Pages dashboard
    for key, m in MODULES.items():
        slug = m["module_slug"]
        d = APP_DIR / slug / "dashboard"
        d.mkdir(parents=True, exist_ok=True)
        page = d / "page.tsx"
        if page.exists():
            print("dashboard exists:", slug)
            continue
        page.write_text(dash_page(key, m), encoding="utf-8")
        print("dashboard generated:", slug)


if __name__ == "__main__":
    main()
