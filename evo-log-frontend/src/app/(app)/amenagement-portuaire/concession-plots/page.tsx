'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreAmgtbConcessionPlot } from '@/components/amenagement-portuaire/registres_b';

export default function PageAmgtbConcessionPlot() {
  return <RegistreGenerique config={registreAmgtbConcessionPlot} />;
}
