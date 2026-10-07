'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreCostAnalysis } from '@/components/parc-vehicules/registres';

export default function PageCostAnalysis() {
  return <RegistreGenerique config={registreCostAnalysis} />;
}
