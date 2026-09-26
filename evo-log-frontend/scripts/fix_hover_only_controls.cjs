// Les actions de ligne masquees jusqu'au survol (opacity-0 group-hover:...)
// sont inaccessibles sur ecran tactile : elles restent invisibles au doigt.
// Sous md (mobile/tablette) on les affiche toujours ; le survol desktop est
// preserve.
const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..', 'src');
const RE = /opacity-0 (group-hover|hover|focus):opacity-100/g;

function walk(dir, out = []) {
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    const p = path.join(dir, e.name);
    if (e.isDirectory()) walk(p, out);
    else if (e.name.endsWith('.tsx')) out.push(p);
  }
  return out;
}

let files = 0, hits = 0;
for (const f of walk(ROOT)) {
  const src = fs.readFileSync(f, 'utf8');
  const next = src.replace(RE, (m, g) => {
    hits++;
    return `opacity-100 md:opacity-0 md:${g}:opacity-100`;
  });
  if (next !== src) {
    fs.writeFileSync(f, next);
    files++;
    console.log(path.relative(ROOT, f));
  }
}
console.log(`\n${hits} controles rendus visibles au tactile dans ${files} fichiers.`);
