'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreExpenseReport } from '@/components/finance-ohada/registres';

export default function PageExpenseReport() {
  return <RegistreGenerique config={registreExpenseReport} />;
}
