// Diagnostic temporaire : compare primaryColor de chaque ecran de chargement
// a la teinte accordee par modulePalette (source de verite).
const fs = require('fs');

function blocks(file, keyRe) {
  const lines = fs.readFileSync(file, 'utf8').split(/\r?\n/);
  const out = {};
  let cur = null;
  for (const l of lines) {
    const k = l.match(keyRe);
    if (k) { cur = k[1]; out[cur] = {}; continue; }
    if (!cur) continue;
    const h = l.match(/hex: '([^']+)'/); if (h) out[cur].hex = h[1];
    const p = l.match(/primaryColor: '([^']+)'/); if (p) out[cur].primary = p[1];
    const a = l.match(/^\s*'?([A-Za-z0-9_-]+)'?: '([A-Za-z0-9_-]+)',/); if (a) out[cur].alias = { from: a[1], to: a[2] };
  }
  return out;
}

const palSrc = fs.readFileSync('src/config/modulePalette.ts', 'utf8');
const PAL = {}, ALIAS = {};
{
  const lines = palSrc.split(/\r?\n/);
  let mode = null, cur = null;
  for (const l of lines) {
    if (/^export const MODULE_PALETTE/.test(l)) { mode = 'P'; continue; }
    if (/^export const LEGACY_ALIAS/.test(l)) { mode = 'A'; continue; }
    if (/^export function/.test(l)) { mode = null; continue; }
    const k = l.match(/^  '?([A-Za-z0-9_-]+)'?: \{/);
    if (k && mode === 'P') { cur = k[1]; PAL[cur] = null; continue; }
    if (mode === 'P' && cur) { const h = l.match(/hex: '([^']+)'/); if (h) PAL[cur] = h[1]; continue; }
    if (mode === 'A') { const a = l.match(/^\s*'?([A-Za-z0-9_-]+)'?: '([A-Za-z0-9_-]+)',/); if (a) ALIAS[a[1]] = a[2]; }
  }
}
const gp = (k) => PAL[k] || (ALIAS[k] && PAL[ALIAS[k]]) || PAL.dashboard;

const src = fs.readFileSync('src/config/domainLoadingConfig.ts', 'utf8');
const LOAD = {};
{
  const lines = src.split(/\r?\n/); let cur = null;
  for (const l of lines) {
    const k = l.match(/^  '?([A-Za-z0-9_-]+)'?: \{/);
    if (k) { cur = k[1]; LOAD[cur] = null; continue; }
    if (!cur) continue;
    const p = l.match(/primaryColor: '([^']+)'/); if (p) LOAD[cur] = p[1];
  }
}
const MAP = {};
const ltm = src.match(/LOADING_TO_MODULE: Record<string, string> = \{([\s\S]*?)\n\};/)[1];
for (const m of ltm.matchAll(/^\s*'?([A-Za-z0-9_-]+)'?: '([A-Za-z0-9_-]+)',/gm)) MAP[m[1]] = m[2];

let drift = 0, ok = 0; const unmapped = [];
for (const [b, v] of Object.entries(LOAD)) {
  if (!v) continue;
  const mod = MAP[b] || b;
  if (!MAP[b] && !PAL[mod] && !ALIAS[mod]) unmapped.push(b + ' (repli dashboard)');
  const want = gp(mod);
  if (v.toUpperCase() !== want.toUpperCase()) { drift++; console.log('DRIFT ' + b.padEnd(22) + ' chargement=' + v + '  palette=' + want + '  module=' + mod); }
  else ok++;
}
console.log('---');
console.log('ecrans=' + Object.keys(LOAD).length + '  deja-conformes=' + ok + '  derives-corrigees-par-la-boucle=' + drift);
console.log('sans entree palette explicite :', unmapped.length ? unmapped : 'aucun');

// Doublons exacts dans la palette (regle « une couleur unique par module »)
const parHex = {};
for (const [k, h] of Object.entries(PAL)) (parHex[h] = parHex[h] || []).push(k);
const dup = Object.entries(parHex).filter(([, ks]) => ks.length > 1);
console.log('teintes partagees par plusieurs modules :', dup.length ? dup : 'aucune');
