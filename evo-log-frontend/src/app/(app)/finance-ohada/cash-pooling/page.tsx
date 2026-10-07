'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreCashPool } from '@/components/finance-ohada/registres';

export default function PageCashPool() {
  return <RegistreGenerique config={registreCashPool} />;
}
