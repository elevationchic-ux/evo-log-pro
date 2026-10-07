'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreMagcColdChainCheck } from '@/components/portail-magasinier/registres_c';

export default function PageMagcColdChainCheck() {
  return <RegistreGenerique config={registreMagcColdChainCheck} />;
}
