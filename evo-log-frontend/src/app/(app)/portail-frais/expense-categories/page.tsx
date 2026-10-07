'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreFraExpenseCategory } from '@/components/portail-frais/registres_c';

export default function PageFraExpenseCategory() {
  return <RegistreGenerique config={registreFraExpenseCategory} />;
}
