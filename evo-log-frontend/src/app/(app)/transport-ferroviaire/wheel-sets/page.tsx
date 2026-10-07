'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreRailWheelSet } from '@/components/transport-ferroviaire/registres_b';

export default function PageRailWheelSet() {
  return <RegistreGenerique config={registreRailWheelSet} />;
}
