'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreBudgetControl } from '@/components/comptabilite-ohada/registres';

export default function PageBudgetControl() {
  return <RegistreGenerique config={registreBudgetControl} />;
}
