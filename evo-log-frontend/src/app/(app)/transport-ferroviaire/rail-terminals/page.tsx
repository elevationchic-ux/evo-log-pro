'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreRailTerminal } from '@/components/transport-ferroviaire/registres';

export default function PageRailTerminal() {
  return <RegistreGenerique config={registreRailTerminal} />;
}
