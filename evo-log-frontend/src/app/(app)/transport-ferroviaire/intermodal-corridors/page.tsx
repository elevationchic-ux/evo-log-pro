'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreRailCorridor } from '@/components/transport-ferroviaire/registres';

export default function PageRailCorridor() {
  return <RegistreGenerique config={registreRailCorridor} />;
}
