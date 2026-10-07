'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreQhseWasteManifest } from '@/components/qhse-securite/registres_b';

export default function PageQhseWasteManifest() {
  return <RegistreGenerique config={registreQhseWasteManifest} />;
}
