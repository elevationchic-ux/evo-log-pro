'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreFraExpenseReport } from '@/components/portail-frais/registres_c';

export default function PageFraExpenseReport() {
  return <RegistreGenerique config={registreFraExpenseReport} />;
}
