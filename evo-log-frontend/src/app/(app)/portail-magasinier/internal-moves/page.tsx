'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreMagcInternalMove } from '@/components/portail-magasinier/registres_c';

export default function PageMagcInternalMove() {
  return <RegistreGenerique config={registreMagcInternalMove} />;
}
