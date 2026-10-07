'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreTransportLeg } from '@/components/chaine-froid/registres';

export default function PageColdChainTransportLeg() {
  return <RegistreGenerique config={registreTransportLeg} />;
}
