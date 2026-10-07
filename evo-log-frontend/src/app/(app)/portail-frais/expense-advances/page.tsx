'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreFraExpenseAdvance } from '@/components/portail-frais/registres_c';

export default function PageFraExpenseAdvance() {
  return <RegistreGenerique config={registreFraExpenseAdvance} />;
}
