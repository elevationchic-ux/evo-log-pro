// Controle: les cles de chaque section doivent etre identiques entre fr et en
// (le typage `as const` du hook fait de ce fichier une union: toute cle absente
// d'un cote casse l'acces t.<section>.<cle>).
const fs = require('fs');
const src = fs.readFileSync(process.argv[2] || 'src/hooks/useI18n.ts', 'utf8');

function blockOf(lang) {
  const start = src.indexOf('  ' + lang + ': {');
  if (start < 0) throw new Error('section ' + lang + ' introuvable');
  let depth = 0, i = src.indexOf('{', start);
  const from = i;
  for (; i < src.length; i++) {
    if (src[i] === '{') depth++;
    else if (src[i] === '}') { depth--; if (depth === 0) break; }
  }
  return src.slice(from, i + 1);
}

// sections + feuilles de niveau 1
function parse(block) {
  const out = {};
  const re = /^    ([A-Za-z][A-Za-z0-9_]*): \{/gm;
  let m;
  while ((m = re.exec(block))) {
    const name = m[1];
    let depth = 0, i = m.index + name.length + 2;
    const from = i;
    for (; i < block.length; i++) {
      if (block[i] === '{') depth++;
      else if (block[i] === '}') { depth--; if (depth === 0) break; }
    }
    const body = block.slice(from, i + 1);
    out[name] = [...body.matchAll(/^      ([A-Za-z][A-Za-z0-9_]*):/gm)].map((x) => x[1]);
  }
  return out;
}

const fr = parse(blockOf('fr'));
const en = parse(blockOf('en'));
let problems = 0;
for (const section of new Set([...Object.keys(fr), ...Object.keys(en)])) {
  const a = fr[section] || [];
  const b = en[section] || [];
  const onlyFr = a.filter((k) => !b.includes(k));
  const onlyEn = b.filter((k) => !a.includes(k));
  if (onlyFr.length || onlyEn.length) {
    problems++;
    console.log(`[DECALAGE] ${section}`);
    if (onlyFr.length) console.log(`   seulement en FR: ${onlyFr.join(', ')}`);
    if (onlyEn.length) console.log(`   seulement en EN: ${onlyEn.join(', ')}`);
  } else {
    console.log(`[OK] ${section}: ${a.length} cles alignees`);
  }
}
console.log(problems === 0 ? 'PARITE COMPLETE' : `${problems} section(s) desalignee(s)`);
process.exit(problems === 0 ? 0 : 1);
