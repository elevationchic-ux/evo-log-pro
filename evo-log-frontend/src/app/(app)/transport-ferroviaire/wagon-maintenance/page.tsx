'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreRailWagonMaintenance } from '@/components/transport-ferroviaire/registres';

export default function PageRailWagonMaintenance() {
  return <RegistreGenerique config={registreRailWagonMaintenance} />;
}
