'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreFreightBill } from '@/components/transport-flotte/registres';

export default function PageFreightBill() {
  return <RegistreGenerique config={registreFreightBill} />;
}
