'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreMagcReturnProcessing } from '@/components/portail-magasinier/registres_c';

export default function PageMagcReturnProcessing() {
  return <RegistreGenerique config={registreMagcReturnProcessing} />;
}
