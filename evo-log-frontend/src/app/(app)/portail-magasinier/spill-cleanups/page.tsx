'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreMagcSpillCleanup } from '@/components/portail-magasinier/registres_c';

export default function PageMagcSpillCleanup() {
  return <RegistreGenerique config={registreMagcSpillCleanup} />;
}
