// Audit: libellés de sous-modules déclarés dans NAVIGATION_REGISTRY sans traduction EN.
const fs = require('fs');
const path = require('path');
const root = path.join(__dirname, '..', 'evo-log-frontend', 'src', 'config');

const reg = fs.readFileSync(path.join(root, 'navigationRegistry.ts'), 'utf8');
const i18n = fs.readFileSync(path.join(root, 'navI18n.ts'), 'utf8');

// 1. Tous les label: '...' ou label: "..." de la registry
const labels = new Set();
for (const m of reg.matchAll(/label:\s*'([^']*)'/g)) labels.add(m[1]);
for (const m of reg.matchAll(/label:\s*"([^"]*)"/g)) labels.add(m[1]);

// 2. Clés de SUBMODULE_LABELS_EN (entre "export const SUBMODULE_LABELS_EN" et le "};")
const block = i18n.split('export const SUBMODULE_LABELS_EN')[1] || '';
const body = block.split('\n};')[0];
const known = new Set();
for (const m of body.matchAll(/^\s{2}'((?:[^'\\]|\\.)*)':\s*/gm)) known.add(m[1].replace(/\\'/g, "'"));
for (const m of body.matchAll(/^\s{2}"((?:[^"\\]|\\.)*)":\s*/gm)) known.add(m[1].replace(/\\"/g, '"'));
// clés non quotées (ex: "Vue d'Ensemble Executive" avec apostrophe -> quotée double)
for (const m of body.matchAll(/^\s{2}([A-ZÉÈÀÔÙ][^'":]*):\s*/gm)) known.add(m[1].trim());

const missing = [...labels].filter((l) => l && !known.has(l));
console.log('labels registry:', labels.size, '| cles EN:', known.size, '| MANQUANTS:', missing.length);
missing.sort().forEach((l) => console.log('  - ' + l));
