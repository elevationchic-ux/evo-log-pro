'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreFraExpenseReceipt } from '@/components/portail-frais/registres_c';

export default function PageFraExpenseReceipt() {
  return <RegistreGenerique config={registreFraExpenseReceipt} />;
}
