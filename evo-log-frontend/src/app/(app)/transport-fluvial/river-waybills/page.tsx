'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreFluvialWaybill } from '@/components/transport-fluvial/registres';

export default function PageFluvialWaybill() {
  return <RegistreGenerique config={registreFluvialWaybill} />;
}
