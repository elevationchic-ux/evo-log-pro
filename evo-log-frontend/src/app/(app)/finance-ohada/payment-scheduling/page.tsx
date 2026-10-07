'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registrePaymentSchedule } from '@/components/finance-ohada/registres';

export default function PagePaymentSchedule() {
  return <RegistreGenerique config={registrePaymentSchedule} />;
}
