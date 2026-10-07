'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreChambre } from '@/components/chaine-froid/registres';

export default function PageColdChainChamber() {
  return <RegistreGenerique config={registreChambre} />;
}
