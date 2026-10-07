'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreMultiyearBudget } from '@/components/finance-ohada/registres';

export default function PageMultiyearBudget() {
  return <RegistreGenerique config={registreMultiyearBudget} />;
}
