'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreFraTransportExpense } from '@/components/portail-frais/registres_c';

export default function PageFraTransportExpense() {
  return <RegistreGenerique config={registreFraTransportExpense} />;
}
