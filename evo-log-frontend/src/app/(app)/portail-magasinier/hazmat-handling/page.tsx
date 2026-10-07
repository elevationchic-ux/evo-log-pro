'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreMagcHazmatHandling } from '@/components/portail-magasinier/registres_c';

export default function PageMagcHazmatHandling() {
  return <RegistreGenerique config={registreMagcHazmatHandling} />;
}
