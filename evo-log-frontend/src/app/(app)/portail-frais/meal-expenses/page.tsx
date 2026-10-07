'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreFraMealExpense } from '@/components/portail-frais/registres_c';

export default function PageFraMealExpense() {
  return <RegistreGenerique config={registreFraMealExpense} />;
}
