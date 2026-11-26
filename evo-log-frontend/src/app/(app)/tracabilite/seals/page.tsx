'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreSeal } from '@/components/tracabilite/registres';

export default function PageContainerSeal() {
  return <RegistreGenerique config={registreSeal} />;
}
