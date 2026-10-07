'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreRailLoadingGauge } from '@/components/transport-ferroviaire/registres_b';

export default function PageRailLoadingGauge() {
  return <RegistreGenerique config={registreRailLoadingGauge} />;
}
