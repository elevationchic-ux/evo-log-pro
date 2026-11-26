'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreFluvialWaterGauge } from '@/components/transport-fluvial/registres_b';

export default function PageFluvialWaterGauge() {
  return <RegistreGenerique config={registreFluvialWaterGauge} />;
}
