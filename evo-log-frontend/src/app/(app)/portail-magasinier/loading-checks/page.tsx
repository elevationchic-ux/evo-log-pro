'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreMagcLoadingCheck } from '@/components/portail-magasinier/registres_c';

export default function PageMagcLoadingCheck() {
  return <RegistreGenerique config={registreMagcLoadingCheck} />;
}
