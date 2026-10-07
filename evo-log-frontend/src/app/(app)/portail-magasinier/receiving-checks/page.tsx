'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreMagcReceivingCheck } from '@/components/portail-magasinier/registres_c';

export default function PageMagcReceivingCheck() {
  return <RegistreGenerique config={registreMagcReceivingCheck} />;
}
