'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreCustomsValuation } from '@/components/transit-douane/registres';

export default function PageCustomsValuation() {
  return <RegistreGenerique config={registreCustomsValuation} />;
}
