const fs = require('fs');
const src = fs.readFileSync('src/config/navigationRegistry.ts', 'utf8');
const lines = src.split(/\r?\n/);
const keys = [];
for (let i = 0; i < lines.length; i++) {
  const m = lines[i].match(/^  '?([a-z][A-Za-z0-9_-]+)'?: \{/);
  if (m) {
    const nxt = lines[i + 1] || '';
    if (nxt.includes("key: '" + m[1] + "'") || nxt.includes('key: "' + m[1] + '"')) keys.push(m[1]);
  }
}
console.log('TOP-LEVEL MODULES (' + keys.length + '): ' + keys.join(', '));
for (const w of ['cotations', 'procurement', 'fuel-guard', 'acconage', 'maintenance', 'fiscalite-cameroun', 'portail-commercial', 'admin-tenant', 'finance-ohada'])
  console.log('  ' + w.padEnd(20) + ' top-level? ' + keys.includes(w));
