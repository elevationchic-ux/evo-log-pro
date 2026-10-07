'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreAirWaybill } from '@/components/transport-aerien/registres';

export default function PageAirWaybill() {
  return <RegistreGenerique config={registreAirWaybill} />;
}
