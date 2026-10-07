'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreRailTerminalCrane } from '@/components/transport-ferroviaire/registres_b';

export default function PageRailTerminalCrane() {
  return <RegistreGenerique config={registreRailTerminalCrane} />;
}
