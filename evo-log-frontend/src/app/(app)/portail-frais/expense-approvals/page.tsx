'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreFraExpenseApproval } from '@/components/portail-frais/registres_c';

export default function PageFraExpenseApproval() {
  return <RegistreGenerique config={registreFraExpenseApproval} />;
}
