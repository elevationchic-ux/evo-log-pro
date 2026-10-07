'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreFluvialCanalSection } from '@/components/transport-fluvial/registres_b';

export default function PageFluvialCanalSection() {
  return <RegistreGenerique config={registreFluvialCanalSection} />;
}
