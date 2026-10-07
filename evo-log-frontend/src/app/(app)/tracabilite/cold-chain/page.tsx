'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreColdChain } from '@/components/tracabilite/registres';

export default function PageColdChainTrace() {
  return <RegistreGenerique config={registreColdChain} />;
}
