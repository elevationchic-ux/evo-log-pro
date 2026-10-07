'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreRailLocomotive } from '@/components/transport-ferroviaire/registres';

export default function PageRailLocomotive() {
  return <RegistreGenerique config={registreRailLocomotive} />;
}
