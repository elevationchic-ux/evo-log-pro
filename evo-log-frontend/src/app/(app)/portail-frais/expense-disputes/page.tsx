'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreFraExpenseDispute } from '@/components/portail-frais/registres_c';

export default function PageFraExpenseDispute() {
  return <RegistreGenerique config={registreFraExpenseDispute} />;
}
