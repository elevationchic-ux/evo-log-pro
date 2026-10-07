'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreRailWaybill } from '@/components/transport-ferroviaire/registres';

export default function PageRailWaybill() {
  return <RegistreGenerique config={registreRailWaybill} />;
}
