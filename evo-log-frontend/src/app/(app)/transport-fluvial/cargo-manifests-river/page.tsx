'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreFluvialCargoManifest } from '@/components/transport-fluvial/registres_b';

export default function PageFluvialCargoManifest() {
  return <RegistreGenerique config={registreFluvialCargoManifest} />;
}
