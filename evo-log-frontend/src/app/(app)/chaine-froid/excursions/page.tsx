'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreExcursion } from '@/components/chaine-froid/registres';

export default function PageColdChainExcursion() {
  return <RegistreGenerique config={registreExcursion} />;
}
