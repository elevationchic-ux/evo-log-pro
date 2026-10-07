'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreMagcCycleCount } from '@/components/portail-magasinier/registres_c';

export default function PageMagcCycleCount() {
  return <RegistreGenerique config={registreMagcCycleCount} />;
}
