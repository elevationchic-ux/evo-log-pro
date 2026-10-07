'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreFinancialInvestment } from '@/components/finance-ohada/registres';

export default function PageFinancialInvestment() {
  return <RegistreGenerique config={registreFinancialInvestment} />;
}
