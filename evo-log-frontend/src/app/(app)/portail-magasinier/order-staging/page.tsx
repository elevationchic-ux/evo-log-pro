'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreMagcOrderStaging } from '@/components/portail-magasinier/registres_c';

export default function PageMagcOrderStaging() {
  return <RegistreGenerique config={registreMagcOrderStaging} />;
}
