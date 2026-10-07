'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreAnnualActivityReport } from '@/components/amenagement-portuaire/registres_expansion';

export default function PageAnnualActivityReport() {
  return <RegistreGenerique config={registreAnnualActivityReport} />;
}
