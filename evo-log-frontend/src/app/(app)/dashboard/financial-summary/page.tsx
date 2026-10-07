'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreFinancialSummary } from '@/components/dashboard/registres';

export default function PageFinancialSummary() {
  return <RegistreGenerique config={registreFinancialSummary} />;
}
