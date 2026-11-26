// Releve la taille de police minimale de l'interface : aucun texte utile sous
// 11px sur ecran applicatif (mobile/tablette = critere produit). Les documents
// destines a l'impression sont exclus : leur micro-typographie est deliberee.
const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..', 'src');
const EXCLUDE = [
  'components' + path.sep + 'documents' + path.sep + 'CompanyDocumentHeader.tsx',
];
const MAP = { '8': '10', '9': '11', '10': '11' };

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
  if (EXCLUDE.includes(path.relative(ROOT, f))) continue;
  const src = fs.readFileSync(f, 'utf8');
  const next = src.replace(/text-\[(8|9|10)px\]/g, (m, n) => {
    hits++;
    return `text-[${MAP[n]}px]`;
  });
  if (next !== src) {
    fs.writeFileSync(f, next);
    files++;
    console.log(path.relative(ROOT, f));
  }
}
console.log(`\n${hits} micro-tailles relevees dans ${files} fichiers (plancher 11px).`);
