'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreFraExpenseBudgetTracking } from '@/components/portail-frais/registres_c';

export default function PageFraExpenseBudgetTracking() {
  return <RegistreGenerique config={registreFraExpenseBudgetTracking} />;
}
