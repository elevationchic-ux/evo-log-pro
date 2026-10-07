'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreFluvialTerminal } from '@/components/transport-fluvial/registres';

export default function PageFluvialTerminal() {
  return <RegistreGenerique config={registreFluvialTerminal} />;
}
