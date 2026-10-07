'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreLeaseContract } from '@/components/finance-ohada/registres';

export default function PageLeaseContract() {
  return <RegistreGenerique config={registreLeaseContract} />;
}
