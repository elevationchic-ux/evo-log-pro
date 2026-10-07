'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreLogger } from '@/components/chaine-froid/registres';

export default function PageColdChainLogger() {
  return <RegistreGenerique config={registreLogger} />;
}
