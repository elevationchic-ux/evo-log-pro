/**
 * generate-ico.js
 * Crée un favicon.ico multi-résolution (16+32+48px) à partir
 * des PNG déjà générés, en pur Node.js sans dépendances tierces.
 *
 * Un fichier ICO = header + répertoire des images + données PNG brutes.
 * Tous les navigateurs modernes acceptent des PNG dans un ICO.
 */
const fs = require('fs');
const path = require('path');

const publicDir = path.join(__dirname, '..', 'public');

// Tailles à inclure dans l'ICO (ordre croissant = standard)
const sizes = [
  { file: path.join(publicDir, 'icons', 'favicon-16x16.png'), w: 16, h: 16 },
  { file: path.join(publicDir, 'icons', 'favicon-32x32.png'), w: 32, h: 32 },
];

// Vérification des fichiers sources
for (const s of sizes) {
  if (!fs.existsSync(s.file)) {
    console.error(`Missing: ${s.file}`);
    process.exit(1);
  }
}

const images = sizes.map(s => ({
  data: fs.readFileSync(s.file),
  w: s.w,
  h: s.h,
}));

const count = images.length;

// ICO header: 6 bytes
// ICONDIR: Reserved(2) + Type(2, 1=ICO) + Count(2)
const headerSize = 6;

// ICONDIRENTRY: 16 bytes each
// Width(1) Height(1) ColorCount(1) Reserved(1) Planes(2) BitCount(2) SizeInBytes(4) FileOffset(4)
const dirEntrySize = 16;
const dirSize = count * dirEntrySize;

// Total header = headerSize + dirSize
const dataOffset = headerSize + dirSize;

// Compute total buffer size
const totalSize = dataOffset + images.reduce((acc, img) => acc + img.data.length, 0);

const buf = Buffer.alloc(totalSize, 0);
let pos = 0;

// Write ICONDIR
buf.writeUInt16LE(0,     pos); pos += 2; // Reserved
buf.writeUInt16LE(1,     pos); pos += 2; // Type = 1 (ICO)
buf.writeUInt16LE(count, pos); pos += 2; // Count

// Compute image offsets
let imageOffset = dataOffset;

for (const img of images) {
  const w = img.w >= 256 ? 0 : img.w; // 256 is encoded as 0 in ICO
  const h = img.h >= 256 ? 0 : img.h;

  buf.writeUInt8(w,               pos); pos += 1; // Width
  buf.writeUInt8(h,               pos); pos += 1; // Height
  buf.writeUInt8(0,               pos); pos += 1; // ColorCount (0 = no palette)
  buf.writeUInt8(0,               pos); pos += 1; // Reserved
  buf.writeUInt16LE(1,            pos); pos += 2; // Planes
  buf.writeUInt16LE(32,           pos); pos += 2; // BitCount (32bpp)
  buf.writeUInt32LE(img.data.length, pos); pos += 4; // SizeInBytes
  buf.writeUInt32LE(imageOffset,  pos); pos += 4; // FileOffset

  imageOffset += img.data.length;
}

// Write image data
for (const img of images) {
  img.data.copy(buf, pos);
  pos += img.data.length;
}

const outFile = path.join(publicDir, 'favicon.ico');
fs.writeFileSync(outFile, buf);

console.log(`favicon.ico generated: ${outFile} (${(buf.length / 1024).toFixed(1)} KB)`);
console.log(`  Contains: ${sizes.map(s => `${s.w}×${s.h}`).join(', ')}`);
