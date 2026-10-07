'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreSubcontractor } from '@/components/transport-flotte/registres';

export default function PageSubcontractor() {
  return <RegistreGenerique config={registreSubcontractor} />;
}
