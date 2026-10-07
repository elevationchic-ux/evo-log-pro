'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreFincCashFlowForecast } from '@/components/finance-ohada/registres_c';

export default function PageFincCashFlowForecast() {
  return <RegistreGenerique config={registreFincCashFlowForecast} />;
}
