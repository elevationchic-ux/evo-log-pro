'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreDefrost } from '@/components/chaine-froid/registres';

export default function PageColdChainDefrostCycle() {
  return <RegistreGenerique config={registreDefrost} />;
}
