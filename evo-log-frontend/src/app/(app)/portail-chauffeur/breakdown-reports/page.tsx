'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreChfBreakdownReport } from '@/components/portail-chauffeur/registres_c';

export default function PageChfBreakdownReport() {
  return <RegistreGenerique config={registreChfBreakdownReport} />;
}
