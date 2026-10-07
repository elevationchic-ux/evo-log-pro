'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreRailPathOccupancy } from '@/components/transport-ferroviaire/registres_b';

export default function PageRailPathOccupancy() {
  return <RegistreGenerique config={registreRailPathOccupancy} />;
}
