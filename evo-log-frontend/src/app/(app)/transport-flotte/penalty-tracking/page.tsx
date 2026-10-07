'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreTrafficPenalty } from '@/components/transport-flotte/registres';

export default function PageTrafficPenalty() {
  return <RegistreGenerique config={registreTrafficPenalty} />;
}
