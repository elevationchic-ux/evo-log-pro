'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreFluvialTowboat } from '@/components/transport-fluvial/registres';

export default function PageFluvialTowboat() {
  return <RegistreGenerique config={registreFluvialTowboat} />;
}
