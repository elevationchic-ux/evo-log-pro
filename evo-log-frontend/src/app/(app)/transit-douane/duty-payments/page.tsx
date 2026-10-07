'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreDutyPayment } from '@/components/transit-douane/registres';

export default function PageDutyPayment() {
  return <RegistreGenerique config={registreDutyPayment} />;
}
