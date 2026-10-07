'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreCharteredFlight } from '@/components/transport-aerien/registres_b';

export default function PageCharteredFlight() {
  return <RegistreGenerique config={registreCharteredFlight} />;
}
