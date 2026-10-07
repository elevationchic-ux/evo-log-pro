"""Patch port-operations/registres.ts: rename helpers to match typesRegistre schema."""
from pathlib import Path

p = Path("evo-log-frontend/src/components/port-operations/registres.ts")
t = p.read_text(encoding="utf-8")

# Helper signatures: key -> name ; header -> label ; type value renames
t = t.replace("function col(key: string, header: string, headerEn: string, opts: Partial<ColonneRegistre> = {}): ColonneRegistre {\n  return { key, header, headerEn, ...opts } as ColonneRegistre;",
              "function col(name: string, label: string, labelEn: string, opts: Partial<ColonneRegistre> = {}): ColonneRegistre {\n  return { name, label, labelEn, ...opts } as ColonneRegistre;")
t = t.replace('function txt(key: string, label: string, labelEn: string, opts: Partial<ChampRegistre> = {}): ChampRegistre {\n  return { key, label, labelEn, type: "text", ...opts } as ChampRegistre;',
              'function txt(name: string, label: string, labelEn: string, opts: Partial<ChampRegistre> = {}): ChampRegistre {\n  return { name, label, labelEn, type: "texte", ...opts } as ChampRegistre;')
t = t.replace('function num(key: string, label: string, labelEn: string, opts: Partial<ChampRegistre> = {}): ChampRegistre {\n  return { key, label, labelEn, type: "number", ...opts } as ChampRegistre;',
              'function num(name: string, label: string, labelEn: string, opts: Partial<ChampRegistre> = {}): ChampRegistre {\n  return { name, label, labelEn, type: "nombre", ...opts } as ChampRegistre;')
t = t.replace('function dt(key: string, label: string, labelEn: string): ChampRegistre {\n  return { key, label, labelEn, type: "date" } as ChampRegistre;',
              'function dt(name: string, label: string, labelEn: string): ChampRegistre {\n  return { name, label, labelEn, type: "date" } as ChampRegistre;')
t = t.replace('function dtx(key: string, label: string, labelEn: string): ChampRegistre {\n  return { key, label, labelEn, type: "datetime-local" } as ChampRegistre;',
              'function dtx(name: string, label: string, labelEn: string): ChampRegistre {\n  return { name, label, labelEn, type: "date" } as ChampRegistre;')
t = t.replace('function area(key: string, label: string, labelEn: string): ChampRegistre {\n  return { key, label, labelEn, type: "textarea" } as ChampRegistre;',
              'function area(name: string, label: string, labelEn: string): ChampRegistre {\n  return { name, label, labelEn, type: "zone" } as ChampRegistre;')
t = t.replace('function chk(key: string, label: string, labelEn: string): ChampRegistre {\n  return { key, label, labelEn, type: "checkbox" } as ChampRegistre;',
              'function chk(name: string, label: string, labelEn: string): ChampRegistre {\n  return { name, label, labelEn, type: "booleen" } as ChampRegistre;')
t = t.replace('function sel(key: string, label: string, labelEn: string, nomKey: string): ChampRegistre {\n  return { key, label, labelEn, type: "select", nomenclature: nomKey } as ChampRegistre;',
              'function sel(name: string, label: string, labelEn: string, nomKey: string): ChampRegistre {\n  return { name, label, labelEn, type: "select", nomenclature: nomKey } as ChampRegistre;')
t = t.replace('function filtreSel(key: string, label: string, labelEn: string, nomKey: string): FiltreRegistre {\n  return { key, label, labelEn, type: "select", nomenclature: nomKey } as FiltreRegistre;',
              'function filtreSel(name: string, label: string, labelEn: string, nomKey: string): FiltreRegistre {\n  return { name, label, labelEn, type: "select", nomenclature: nomKey } as FiltreRegistre;')

# Drop searchable and rename obligatoire inside inline object literals
t = t.replace(", { searchable: true }", "")
t = t.replace("{ obligatoire: true }", "{ requisCreation: true }")

p.write_text(t, encoding="utf-8")
print(f"patched port-operations/registres.ts len={len(t)}")
