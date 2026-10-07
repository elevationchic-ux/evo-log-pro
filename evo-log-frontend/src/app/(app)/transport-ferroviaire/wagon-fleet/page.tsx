'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreRailWagon } from '@/components/transport-ferroviaire/registres';

export default function PageRailWagon() {
  return <RegistreGenerique config={registreRailWagon} />;
}
