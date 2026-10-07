'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreRailWagonTracking } from '@/components/transport-ferroviaire/registres';

export default function PageRailWagonTracking() {
  return <RegistreGenerique config={registreRailWagonTracking} />;
}
